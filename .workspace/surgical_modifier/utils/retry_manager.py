import time
import random
import functools
from typing import Callable, Any, Optional, Tuple, Dict
from utils import logger

class ExponentialBackoffRetry:
    """
    Sistema de retry con backoff exponencial para operaciones determinísticas.
    
    Implementa retry automático con delays crecientes exponencialmente,
    tracking detallado de reintentos y estadísticas completas.
    """
    
    def __init__(self, max_attempts: int = 3, base_delay: float = 1.0, 
                 max_delay: float = 60.0, backoff_factor: float = 2.0):
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.backoff_factor = backoff_factor
        self.statistics = {
            'total_attempts': 0,
            'successful_operations': 0,
            'failed_operations': 0,
            'total_retry_time': 0.0
        }
    
    def calculate_delay(self, attempt: int) -> float:
        """Calcula delay con backoff exponencial y jitter."""
        delay = min(self.base_delay * (self.backoff_factor ** attempt), self.max_delay)
        # Agregar jitter para evitar thundering herd
        jitter = random.uniform(0.1, 0.3) * delay
        return delay + jitter
    
    def retry_operation(self, func: Callable, *args, **kwargs) -> Any:
        """
        Ejecuta operación con retry automático y tracking completo.
        
        Returns:
            Resultado de la función exitosa
            
        Raises:
            Exception: La última excepción si todos los intentos fallan
        """
        start_time = time.time()
        last_exception = None
        
        for attempt in range(self.max_attempts):
            try:
                logger.info(f"Attempt {attempt + 1}/{self.max_attempts} for {func.__name__}")
                result = func(*args, **kwargs)
                
                # Operación exitosa
                execution_time = time.time() - start_time
                self.statistics['successful_operations'] += 1
                self.statistics['total_attempts'] += attempt + 1
                self.statistics['total_retry_time'] += execution_time
                
                if attempt > 0:
                    logger.success(f"Operation {func.__name__} succeeded on attempt {attempt + 1}")
                
                return result
                
            except Exception as e:
                last_exception = e
                logger.warning(f"Attempt {attempt + 1} failed for {func.__name__}: {str(e)}")
                
                # Si no es el último intento, aplicar delay
                if attempt < self.max_attempts - 1:
                    delay = self.calculate_delay(attempt)
                    logger.info(f"Retrying in {delay:.2f} seconds...")
                    time.sleep(delay)
        
        # Todos los intentos fallaron
        execution_time = time.time() - start_time
        self.statistics['failed_operations'] += 1
        self.statistics['total_attempts'] += self.max_attempts
        self.statistics['total_retry_time'] += execution_time
        
        logger.error(f"All {self.max_attempts} attempts failed for {func.__name__}")
        raise last_exception

def retry_with_backoff(max_attempts: int = 3, base_delay: float = 1.0,
                      max_delay: float = 60.0, backoff_factor: float = 2.0):
    """
    Decorador para retry automático con backoff exponencial.
    
    Args:
        max_attempts: Número máximo de intentos
        base_delay: Delay base en segundos
        max_delay: Delay máximo en segundos
        backoff_factor: Factor de multiplicación para backoff
    """
    def decorator(func: Callable) -> Callable:
        retry_manager = ExponentialBackoffRetry(
            max_attempts=max_attempts,
            base_delay=base_delay,
            max_delay=max_delay,
            backoff_factor=backoff_factor
        )
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return retry_manager.retry_operation(func, *args, **kwargs)
        
        # Agregar statistics al wrapper para acceso externo
        wrapper.statistics = retry_manager.statistics
        
        return wrapper
    return decorator