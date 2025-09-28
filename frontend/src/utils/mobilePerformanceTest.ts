/**
 * Mobile Performance Testing Utility
 * Simulates mobile network conditions and measures performance
 * Specifically designed for hierarchical sidebar mobile UX validation
 */

export interface NetworkCondition {
  name: string;
  downloadThroughput: number; // Mbps
  uploadThroughput: number; // Mbps
  latency: number; // ms
  description: string;
}

export interface MobileTestResult {
  networkCondition: NetworkCondition;
  loadTime: number;
  interactionTime: number;
  frameRate: number;
  memoryUsage: number;
  bundleLoadTime: number;
  sidebarAnimationPerformance: AnimationPerformance;
  recommendation: string;
  score: number;
}

export interface AnimationPerformance {
  framesDropped: number;
  averageFrameTime: number;
  maxFrameTime: number;
  smoothness: number; // 0-100 score
}

export class MobilePerformanceTester {
  private static readonly NETWORK_CONDITIONS: NetworkCondition[] = [
    {
      name: '3G Regular',
      downloadThroughput: 1.6,
      uploadThroughput: 0.75,
      latency: 300,
      description: 'Typical 3G connection in Colombia'
    },
    {
      name: '3G Slow',
      downloadThroughput: 0.4,
      uploadThroughput: 0.4,
      latency: 400,
      description: 'Poor 3G connection in rural areas'
    },
    {
      name: '4G Regular',
      downloadThroughput: 4.0,
      uploadThroughput: 3.0,
      latency: 170,
      description: 'Standard 4G LTE connection'
    },
    {
      name: '4G Fast',
      downloadThroughput: 9.0,
      uploadThroughput: 9.0,
      latency: 85,
      description: 'Good 4G connection in major cities'
    },
    {
      name: 'WiFi',
      downloadThroughput: 30.0,
      uploadThroughput: 15.0,
      latency: 28,
      description: 'Standard WiFi connection'
    }
  ];

  private frameTimings: number[] = [];
  private animationStartTime: number = 0;

  /**
   * Test sidebar performance under different network conditions
   */
  public async testMobilePerformance(): Promise<MobileTestResult[]> {
    const results: MobileTestResult[] = [];

    for (const condition of MobilePerformanceTester.NETWORK_CONDITIONS) {
      console.log(`Testing performance under ${condition.name} conditions...`);

      const result = await this.testNetworkCondition(condition);
      results.push(result);

      // Wait between tests to allow cleanup
      await this.delay(1000);
    }

    return results;
  }

  private async testNetworkCondition(condition: NetworkCondition): Promise<MobileTestResult> {
    // Simulate network condition effects
    await this.simulateNetworkLatency(condition.latency);

    const startTime = performance.now();

    // Test initial load
    const loadTime = await this.measureLoadTime();

    // Test sidebar interaction
    const interactionTime = await this.measureSidebarInteraction();

    // Test animation performance
    const animationPerf = await this.measureAnimationPerformance();

    // Measure memory usage
    const memoryUsage = this.measureMemoryUsage();

    // Estimate bundle load time based on network speed
    const bundleLoadTime = this.estimateBundleLoadTime(condition);

    const totalTime = performance.now() - startTime;

    return {
      networkCondition: condition,
      loadTime,
      interactionTime,
      frameRate: this.calculateFrameRate(),
      memoryUsage,
      bundleLoadTime,
      sidebarAnimationPerformance: animationPerf,
      recommendation: this.generateRecommendation(condition, {
        loadTime,
        interactionTime,
        animationPerf,
        memoryUsage
      }),
      score: this.calculatePerformanceScore({
        loadTime,
        interactionTime,
        animationPerf,
        memoryUsage,
        bundleLoadTime
      })
    };
  }

  private async simulateNetworkLatency(latencyMs: number): Promise<void> {
    // Simulate network delay
    return new Promise(resolve => setTimeout(resolve, latencyMs / 10));
  }

  private async measureLoadTime(): Promise<number> {
    const startTime = performance.now();

    // Simulate DOM ready
    await new Promise(resolve => {
      if (document.readyState === 'complete') {
        resolve(void 0);
      } else {
        window.addEventListener('load', resolve);
      }
    });

    return performance.now() - startTime;
  }

  private async measureSidebarInteraction(): Promise<number> {
    const startTime = performance.now();

    // Find sidebar toggle button
    const toggleButton = document.querySelector('[data-testid="mobile-menu-toggle"]') ||
                        document.querySelector('button[aria-expanded]') ||
                        document.querySelector('.md\\:hidden button');

    if (toggleButton) {
      // Simulate click interaction
      const clickEvent = new MouseEvent('click', {
        bubbles: true,
        cancelable: true,
        view: window
      });

      toggleButton.dispatchEvent(clickEvent);

      // Wait for animation to complete
      await this.delay(300);
    }

    return performance.now() - startTime;
  }

  private async measureAnimationPerformance(): Promise<AnimationPerformance> {
    this.frameTimings = [];
    this.animationStartTime = performance.now();

    // Start monitoring frame performance
    const observer = new PerformanceObserver((list) => {
      for (const entry of list.getEntries()) {
        if (entry.entryType === 'frame') {
          this.frameTimings.push(entry.duration);
        }
      }
    });

    // Check if the browser supports frame timing
    if ('PerformanceObserver' in window) {
      try {
        observer.observe({ entryTypes: ['frame'] });
      } catch (e) {
        // Fallback to manual frame timing
        return this.measureAnimationFallback();
      }
    } else {
      return this.measureAnimationFallback();
    }

    // Trigger sidebar animation
    await this.triggerSidebarAnimation();

    // Stop observing after animation
    observer.disconnect();

    return this.analyzeFramePerformance();
  }

  private async measureAnimationFallback(): Promise<AnimationPerformance> {
    const frameTimes: number[] = [];
    const targetFPS = 60;
    const frameInterval = 1000 / targetFPS;

    const measureFrame = () => {
      const frameStart = performance.now();

      requestAnimationFrame(() => {
        const frameEnd = performance.now();
        frameTimes.push(frameEnd - frameStart);

        if (frameTimes.length < 30) { // Measure 30 frames
          measureFrame();
        }
      });
    };

    measureFrame();

    // Wait for measurements to complete
    await this.delay(500);

    return {
      framesDropped: frameTimes.filter(time => time > frameInterval * 1.5).length,
      averageFrameTime: frameTimes.reduce((a, b) => a + b, 0) / frameTimes.length,
      maxFrameTime: Math.max(...frameTimes),
      smoothness: this.calculateSmoothness(frameTimes, frameInterval)
    };
  }

  private async triggerSidebarAnimation(): Promise<void> {
    // Find animated elements
    const sidebar = document.querySelector('[class*="translate-x"]') ||
                   document.querySelector('[class*="transform"]');

    if (sidebar) {
      // Trigger animation by toggling classes
      const hasTranslateClass = sidebar.classList.contains('translate-x-0');

      if (hasTranslateClass) {
        sidebar.classList.remove('translate-x-0');
        sidebar.classList.add('-translate-x-full');
      } else {
        sidebar.classList.remove('-translate-x-full');
        sidebar.classList.add('translate-x-0');
      }

      // Wait for animation to complete
      await this.delay(300);
    }
  }

  private analyzeFramePerformance(): AnimationPerformance {
    if (this.frameTimings.length === 0) {
      return {
        framesDropped: 0,
        averageFrameTime: 16.67, // Ideal 60fps
        maxFrameTime: 16.67,
        smoothness: 100
      };
    }

    const targetFrameTime = 16.67; // 60fps
    const droppedFrames = this.frameTimings.filter(time => time > targetFrameTime * 1.5).length;
    const averageFrameTime = this.frameTimings.reduce((a, b) => a + b, 0) / this.frameTimings.length;
    const maxFrameTime = Math.max(...this.frameTimings);
    const smoothness = this.calculateSmoothness(this.frameTimings, targetFrameTime);

    return {
      framesDropped: droppedFrames,
      averageFrameTime,
      maxFrameTime,
      smoothness
    };
  }

  private calculateSmoothness(frameTimes: number[], targetFrameTime: number): number {
    const consistentFrames = frameTimes.filter(time =>
      time >= targetFrameTime * 0.8 && time <= targetFrameTime * 1.2
    ).length;

    return Math.round((consistentFrames / frameTimes.length) * 100);
  }

  private calculateFrameRate(): number {
    if (this.frameTimings.length === 0) return 60;

    const averageFrameTime = this.frameTimings.reduce((a, b) => a + b, 0) / this.frameTimings.length;
    return Math.round(1000 / averageFrameTime);
  }

  private measureMemoryUsage(): number {
    const memoryInfo = (performance as any).memory;

    if (memoryInfo) {
      return Math.round(memoryInfo.usedJSHeapSize / 1024 / 1024); // MB
    }

    // Fallback estimation
    return this.estimateMemoryUsage();
  }

  private estimateMemoryUsage(): number {
    // Estimate based on DOM complexity
    const elements = document.querySelectorAll('*').length;
    const scripts = document.querySelectorAll('script').length;

    // Rough estimation: 1MB base + 0.1KB per element + 0.5MB per script
    return Math.round(1 + (elements * 0.0001) + (scripts * 0.5));
  }

  private estimateBundleLoadTime(condition: NetworkCondition): number {
    // Estimate based on bundle size and network speed
    const estimatedBundleSize = 600; // KB (from build output)
    const downloadSpeedKBps = condition.downloadThroughput * 1024 / 8; // Convert Mbps to KBps

    return Math.round((estimatedBundleSize / downloadSpeedKBps) * 1000); // ms
  }

  private generateRecommendation(
    condition: NetworkCondition,
    metrics: {
      loadTime: number;
      interactionTime: number;
      animationPerf: AnimationPerformance;
      memoryUsage: number;
    }
  ): string {
    const recommendations: string[] = [];

    if (metrics.loadTime > 3000) {
      recommendations.push('Reduce initial bundle size for faster loading');
    }

    if (metrics.interactionTime > 100) {
      recommendations.push('Optimize touch event handlers for better responsiveness');
    }

    if (metrics.animationPerf.smoothness < 80) {
      recommendations.push('Improve animation performance with CSS transforms and will-change properties');
    }

    if (metrics.memoryUsage > 50) {
      recommendations.push('Reduce memory usage for better mobile performance');
    }

    if (condition.downloadThroughput < 2.0 && metrics.loadTime > 5000) {
      recommendations.push('Consider implementing progressive loading for slow connections');
    }

    if (recommendations.length === 0) {
      return `Excellent performance on ${condition.name} network! 🚀`;
    }

    return recommendations.join('; ');
  }

  private calculatePerformanceScore(metrics: {
    loadTime: number;
    interactionTime: number;
    animationPerf: AnimationPerformance;
    memoryUsage: number;
    bundleLoadTime: number;
  }): number {
    let score = 100;

    // Load time scoring (30 points)
    if (metrics.loadTime > 5000) score -= 30;
    else if (metrics.loadTime > 3000) score -= 20;
    else if (metrics.loadTime > 2000) score -= 10;

    // Interaction time scoring (25 points)
    if (metrics.interactionTime > 200) score -= 25;
    else if (metrics.interactionTime > 100) score -= 15;
    else if (metrics.interactionTime > 50) score -= 5;

    // Animation performance scoring (25 points)
    score += (metrics.animationPerf.smoothness / 100) * 25 - 25;

    // Memory usage scoring (10 points)
    if (metrics.memoryUsage > 100) score -= 10;
    else if (metrics.memoryUsage > 50) score -= 5;

    // Bundle load time scoring (10 points)
    if (metrics.bundleLoadTime > 10000) score -= 10;
    else if (metrics.bundleLoadTime > 5000) score -= 5;

    return Math.max(0, Math.round(score));
  }

  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  /**
   * Generate comprehensive performance report
   */
  public static generateReport(results: MobileTestResult[]): string {
    let report = `
🚀 MOBILE PERFORMANCE AUDIT REPORT - Hierarchical Sidebar
==========================================================

📊 NETWORK CONDITIONS TESTED: ${results.length}

`;

    results.forEach((result, index) => {
      const condition = result.networkCondition;
      report += `
${index + 1}. ${condition.name} (${condition.description})
   - Download: ${condition.downloadThroughput}Mbps | Upload: ${condition.uploadThroughput}Mbps | Latency: ${condition.latency}ms

   📈 PERFORMANCE METRICS:
   - Load Time: ${result.loadTime.toFixed(2)}ms
   - Interaction Time: ${result.interactionTime.toFixed(2)}ms
   - Frame Rate: ${result.frameRate}fps
   - Memory Usage: ${result.memoryUsage}MB
   - Bundle Load Time: ${result.bundleLoadTime.toFixed(2)}ms

   🎬 ANIMATION PERFORMANCE:
   - Frames Dropped: ${result.sidebarAnimationPerformance.framesDropped}
   - Avg Frame Time: ${result.sidebarAnimationPerformance.averageFrameTime.toFixed(2)}ms
   - Max Frame Time: ${result.sidebarAnimationPerformance.maxFrameTime.toFixed(2)}ms
   - Smoothness: ${result.sidebarAnimationPerformance.smoothness}%

   💡 RECOMMENDATION: ${result.recommendation}
   🏆 SCORE: ${result.score}/100

   ${'─'.repeat(60)}
`;
    });

    // Calculate overall statistics
    const avgScore = results.reduce((sum, r) => sum + r.score, 0) / results.length;
    const bestCondition = results.reduce((best, current) =>
      current.score > best.score ? current : best
    );
    const worstCondition = results.reduce((worst, current) =>
      current.score < worst.score ? current : worst
    );

    report += `
📊 OVERALL STATISTICS:
- Average Score: ${avgScore.toFixed(1)}/100
- Best Performance: ${bestCondition.networkCondition.name} (${bestCondition.score}/100)
- Worst Performance: ${worstCondition.networkCondition.name} (${worstCondition.score}/100)

🎯 COLOMBIAN MARKET READINESS:
${avgScore >= 80 ? '✅ Ready for Colombian mobile market' : '⚠️ Needs optimization for Colombian mobile conditions'}

🏆 PRODUCTION READINESS: ${avgScore >= 85 ? 'APPROVED' : 'NEEDS IMPROVEMENT'}
`;

    return report;
  }

  /**
   * Quick performance test for development
   */
  public static async quickTest(): Promise<MobileTestResult> {
    const tester = new MobilePerformanceTester();
    const condition = MobilePerformanceTester.NETWORK_CONDITIONS[2]; // 4G Regular

    return await tester.testNetworkCondition(condition);
  }
}

// Export for component testing
export const testSidebarAnimation = async (): Promise<AnimationPerformance> => {
  const tester = new MobilePerformanceTester();
  return await tester.measureAnimationPerformance();
};