/**
 * Retry Logic Utility
 * Provides retry functionality for failed requests with exponential backoff
 */

export interface RetryOptions {
  maxRetries?: number;
  initialDelay?: number;
  maxDelay?: number;
  backoffMultiplier?: number;
  shouldRetry?: (error: any, attemptNumber: number) => boolean;
  onRetry?: (error: any, attemptNumber: number) => void;
}

const DEFAULT_OPTIONS: Required<Omit<RetryOptions, 'shouldRetry' | 'onRetry'>> = {
  maxRetries: 3,
  initialDelay: 1000,
  maxDelay: 10000,
  backoffMultiplier: 2
};

/**
 * Default retry condition - retry on network errors and 5xx server errors
 */
const defaultShouldRetry = (error: any, attemptNumber: number): boolean => {
  // Don't retry client errors (4xx)
  if (error.response && error.response.status >= 400 && error.response.status < 500) {
    return false;
  }

  // Retry on network errors or server errors (5xx)
  return !error.response || error.response.status >= 500;
};

/**
 * Calculate delay with exponential backoff
 */
const calculateDelay = (
  attemptNumber: number,
  initialDelay: number,
  maxDelay: number,
  backoffMultiplier: number
): number => {
  const delay = initialDelay * Math.pow(backoffMultiplier, attemptNumber - 1);
  return Math.min(delay, maxDelay);
};

/**
 * Sleep for a specified duration
 */
const sleep = (ms: number): Promise<void> => {
  return new Promise(resolve => setTimeout(resolve, ms));
};

/**
 * Retry a function with exponential backoff
 * @param fn - The async function to retry
 * @param options - Retry configuration options
 * @returns Promise resolving to the function result
 */
export const retryRequest = async <T>(
  fn: () => Promise<T>,
  options: RetryOptions = {}
): Promise<T> => {
  const {
    maxRetries = DEFAULT_OPTIONS.maxRetries,
    initialDelay = DEFAULT_OPTIONS.initialDelay,
    maxDelay = DEFAULT_OPTIONS.maxDelay,
    backoffMultiplier = DEFAULT_OPTIONS.backoffMultiplier,
    shouldRetry = defaultShouldRetry,
    onRetry
  } = options;

  let lastError: any;
  let attemptNumber = 0;

  while (attemptNumber <= maxRetries) {
    try {
      attemptNumber++;

      // Try to execute the function
      const result = await fn();

      // Success - return result
      return result;
    } catch (error) {
      lastError = error;

      // Check if we should retry
      if (attemptNumber > maxRetries || !shouldRetry(error, attemptNumber)) {
        throw error;
      }

      // Calculate delay before next retry
      const delay = calculateDelay(attemptNumber, initialDelay, maxDelay, backoffMultiplier);

      // Call retry callback if provided
      if (onRetry) {
        onRetry(error, attemptNumber);
      }

      // Log retry attempt in development
      if (import.meta.env.MODE === 'development') {
        console.warn(
          `Retry attempt ${attemptNumber}/${maxRetries} after ${delay}ms`,
          { error }
        );
      }

      // Wait before retrying
      await sleep(delay);
    }
  }

  // All retries failed
  throw lastError;
};

/**
 * Retry with jitter to avoid thundering herd problem
 * Adds random variation to delay times
 */
export const retryWithJitter = async <T>(
  fn: () => Promise<T>,
  options: RetryOptions = {}
): Promise<T> => {
  const jitterFactor = 0.3; // 30% random variation

  return retryRequest(fn, {
    ...options,
    onRetry: (error, attemptNumber) => {
      // Add jitter to the internal sleep
      const baseDelay = calculateDelay(
        attemptNumber,
        options.initialDelay || DEFAULT_OPTIONS.initialDelay,
        options.maxDelay || DEFAULT_OPTIONS.maxDelay,
        options.backoffMultiplier || DEFAULT_OPTIONS.backoffMultiplier
      );

      const jitter = baseDelay * jitterFactor * (Math.random() - 0.5) * 2;
      const delayWithJitter = Math.max(0, baseDelay + jitter);

      if (import.meta.env.MODE === 'development') {
        console.warn(
          `Retry with jitter: attempt ${attemptNumber}, delay ${delayWithJitter.toFixed(0)}ms`,
          { error }
        );
      }

      // Call original onRetry if provided
      if (options.onRetry) {
        options.onRetry(error, attemptNumber);
      }
    }
  });
};

/**
 * Retry wrapper for axios requests
 */
export const retryAxiosRequest = async <T>(
  axiosRequest: () => Promise<T>,
  options: RetryOptions = {}
): Promise<T> => {
  return retryRequest(axiosRequest, {
    maxRetries: 3,
    initialDelay: 1000,
    ...options,
    shouldRetry: (error, attemptNumber) => {
      // Custom retry logic for axios
      if (error.response) {
        const status = error.response.status;

        // Don't retry client errors except 408 (timeout) and 429 (rate limit)
        if (status >= 400 && status < 500 && status !== 408 && status !== 429) {
          return false;
        }

        // Retry server errors and specific client errors
        return status >= 500 || status === 408 || status === 429;
      }

      // Retry network errors
      if (error.request) {
        return attemptNumber <= (options.maxRetries || 3);
      }

      // Don't retry other errors
      return false;
    }
  });
};

/**
 * Create a retryable version of a function
 * Returns a new function that wraps the original with retry logic
 */
export const makeRetryable = <T extends (...args: any[]) => Promise<any>>(
  fn: T,
  options: RetryOptions = {}
): T => {
  return ((...args: any[]) => {
    return retryRequest(() => fn(...args), options);
  }) as T;
};

/**
 * Retry with circuit breaker pattern
 * Stops retrying if failures exceed threshold in a time window
 */
export class CircuitBreaker {
  private failureCount = 0;
  private lastFailureTime = 0;
  private state: 'closed' | 'open' | 'half-open' = 'closed';

  constructor(
    private threshold: number = 5,
    private timeout: number = 60000, // 1 minute
    private resetTimeout: number = 30000 // 30 seconds
  ) {}

  async execute<T>(fn: () => Promise<T>, options: RetryOptions = {}): Promise<T> {
    // Check if circuit is open
    if (this.state === 'open') {
      const timeSinceLastFailure = Date.now() - this.lastFailureTime;

      if (timeSinceLastFailure < this.resetTimeout) {
        throw new Error('Circuit breaker is open - too many failures');
      }

      // Try to close circuit
      this.state = 'half-open';
    }

    try {
      const result = await retryRequest(fn, options);

      // Success - reset circuit
      if (this.state === 'half-open') {
        this.state = 'closed';
        this.failureCount = 0;
      }

      return result;
    } catch (error) {
      this.recordFailure();
      throw error;
    }
  }

  private recordFailure(): void {
    this.failureCount++;
    this.lastFailureTime = Date.now();

    // Check if threshold exceeded
    if (this.failureCount >= this.threshold) {
      this.state = 'open';

      if (import.meta.env.MODE === 'development') {
        console.error('Circuit breaker opened - too many failures');
      }
    }
  }

  reset(): void {
    this.failureCount = 0;
    this.lastFailureTime = 0;
    this.state = 'closed';
  }

  getState(): 'closed' | 'open' | 'half-open' {
    return this.state;
  }

  getFailureCount(): number {
    return this.failureCount;
  }
}

/**
 * Global circuit breaker instance for API calls
 */
export const apiCircuitBreaker = new CircuitBreaker(5, 60000, 30000);

/**
 * Retry API request with circuit breaker
 */
export const retryWithCircuitBreaker = async <T>(
  fn: () => Promise<T>,
  options: RetryOptions = {}
): Promise<T> => {
  return apiCircuitBreaker.execute(fn, options);
};
