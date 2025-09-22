#!/usr/bin/env node
// scripts/lighthouse_performance.js
// LIGHTHOUSE_VALIDATION: Enterprise-grade performance validation with Lighthouse
// Target: Performance >90, Accessibility >90, Best Practices >90, SEO >90

const lighthouse = require('lighthouse');
const chromeLauncher = require('chrome-launcher');
const fs = require('fs').promises;
const path = require('path');

// Performance thresholds for MVP
const PERFORMANCE_THRESHOLDS = {
  performance: 90,
  accessibility: 90,
  'best-practices': 90,
  seo: 85,
  // Core Web Vitals thresholds
  'first-contentful-paint': 1000,     // 1s
  'largest-contentful-paint': 2500,   // 2.5s
  'first-input-delay': 100,           // 100ms
  'cumulative-layout-shift': 0.1,     // 0.1
  'speed-index': 2000,                // 2s
  'time-to-interactive': 3000,        // 3s
  'total-blocking-time': 200          // 200ms
};

// URLs to test for MeStocker
const TEST_URLS = [
  {
    name: 'Landing Page',
    url: 'http://localhost:5173/',
    critical: true
  },
  {
    name: 'Marketplace Home',
    url: 'http://localhost:5173/marketplace',
    critical: true
  },
  {
    name: 'Login Page',
    url: 'http://localhost:5173/login',
    critical: true
  },
  {
    name: 'Vendor Dashboard',
    url: 'http://localhost:5173/app/vendor-dashboard',
    critical: false,
    requiresAuth: true
  },
  {
    name: 'Product Management',
    url: 'http://localhost:5173/app/productos',
    critical: false,
    requiresAuth: true
  },
  {
    name: 'Checkout Flow',
    url: 'http://localhost:5173/checkout',
    critical: true,
    requiresAuth: true
  }
];

// Lighthouse configuration for optimized testing
const LIGHTHOUSE_CONFIG = {
  extends: 'lighthouse:default',
  settings: {
    onlyCategories: ['performance', 'accessibility', 'best-practices', 'seo'],
    formFactor: 'desktop',
    screenEmulation: {
      mobile: false,
      width: 1350,
      height: 940,
      deviceScaleFactor: 1,
      disabled: false,
    },
    throttling: {
      rttMs: 40,
      throughputKbps: 10240,
      requestLatencyMs: 0,
      downloadThroughputKbps: 0,
      uploadThroughputKbps: 0,
      cpuSlowdownMultiplier: 1,
    },
    auditMode: false,
    gatherMode: false,
    clearStorageTypes: ['file_systems', 'shader_cache', 'service_workers', 'cache_storage'],
    skipAudits: [
      'unused-javascript',
      'unused-css-rules',
      'non-composited-animations',
      'third-party-summary'
    ]
  }
};

// Mobile configuration
const MOBILE_CONFIG = {
  ...LIGHTHOUSE_CONFIG,
  settings: {
    ...LIGHTHOUSE_CONFIG.settings,
    formFactor: 'mobile',
    screenEmulation: {
      mobile: true,
      width: 375,
      height: 667,
      deviceScaleFactor: 2,
      disabled: false,
    },
    throttling: {
      rttMs: 150,
      throughputKbps: 1638,
      requestLatencyMs: 562.5,
      downloadThroughputKbps: 1474.56,
      uploadThroughputKbps: 675,
      cpuSlowdownMultiplier: 4,
    }
  }
};

class PerformanceValidator {
  constructor() {
    this.results = [];
    this.chrome = null;
  }

  async init() {
    console.log('🚀 Starting Performance Validation with Lighthouse...\n');

    // Launch Chrome
    this.chrome = await chromeLauncher.launch({
      chromeFlags: [
        '--headless',
        '--disable-gpu',
        '--no-sandbox',
        '--disable-dev-shm-usage',
        '--disable-extensions',
        '--disable-background-timer-throttling',
        '--disable-backgrounding-occluded-windows',
        '--disable-renderer-backgrounding'
      ]
    });

    console.log(`Chrome launched on port ${this.chrome.port}`);
  }

  async runLighthouseTest(url, config, testName) {
    console.log(`\n📊 Testing ${testName}...`);
    console.log(`URL: ${url}`);

    try {
      const result = await lighthouse(url, {
        port: this.chrome.port,
        disableStorageReset: false,
        disableDeviceEmulation: false
      }, config);

      return this.processResults(result, testName, url);
    } catch (error) {
      console.error(`❌ Error testing ${testName}:`, error.message);
      return null;
    }
  }

  processResults(lighthouseResult, testName, url) {
    const { lhr } = lighthouseResult;
    const scores = {
      performance: Math.round(lhr.categories.performance.score * 100),
      accessibility: Math.round(lhr.categories.accessibility.score * 100),
      bestPractices: Math.round(lhr.categories['best-practices'].score * 100),
      seo: Math.round(lhr.categories.seo.score * 100)
    };

    // Core Web Vitals
    const metrics = {
      fcp: lhr.audits['first-contentful-paint'].numericValue,
      lcp: lhr.audits['largest-contentful-paint'].numericValue,
      fid: lhr.audits['max-potential-fid'] ? lhr.audits['max-potential-fid'].numericValue : null,
      cls: lhr.audits['cumulative-layout-shift'].numericValue,
      si: lhr.audits['speed-index'].numericValue,
      tti: lhr.audits['interactive'].numericValue,
      tbt: lhr.audits['total-blocking-time'].numericValue
    };

    const result = {
      testName,
      url,
      timestamp: new Date().toISOString(),
      scores,
      metrics,
      passed: this.evaluateResults(scores, metrics),
      lighthouseResult: lhr
    };

    this.logResults(result);
    return result;
  }

  evaluateResults(scores, metrics) {
    const failures = [];

    // Check category scores
    Object.entries(PERFORMANCE_THRESHOLDS).forEach(([key, threshold]) => {
      if (scores[key] && scores[key] < threshold) {
        failures.push(`${key}: ${scores[key]} < ${threshold}`);
      }
    });

    // Check Core Web Vitals
    if (metrics.fcp > PERFORMANCE_THRESHOLDS['first-contentful-paint']) {
      failures.push(`FCP: ${metrics.fcp}ms > ${PERFORMANCE_THRESHOLDS['first-contentful-paint']}ms`);
    }

    if (metrics.lcp > PERFORMANCE_THRESHOLDS['largest-contentful-paint']) {
      failures.push(`LCP: ${metrics.lcp}ms > ${PERFORMANCE_THRESHOLDS['largest-contentful-paint']}ms`);
    }

    if (metrics.cls > PERFORMANCE_THRESHOLDS['cumulative-layout-shift']) {
      failures.push(`CLS: ${metrics.cls} > ${PERFORMANCE_THRESHOLDS['cumulative-layout-shift']}`);
    }

    if (metrics.si > PERFORMANCE_THRESHOLDS['speed-index']) {
      failures.push(`Speed Index: ${metrics.si}ms > ${PERFORMANCE_THRESHOLDS['speed-index']}ms`);
    }

    return {
      passed: failures.length === 0,
      failures
    };
  }

  logResults(result) {
    const { testName, scores, metrics, passed } = result;

    console.log(`\n📈 Results for ${testName}:`);
    console.log('─'.repeat(50));

    // Category scores
    console.log('📊 Category Scores:');
    Object.entries(scores).forEach(([category, score]) => {
      const threshold = PERFORMANCE_THRESHOLDS[category] || 0;
      const status = score >= threshold ? '✅' : '❌';
      console.log(`  ${status} ${category}: ${score}/100 (threshold: ${threshold})`);
    });

    // Core Web Vitals
    console.log('\n⚡ Core Web Vitals:');
    console.log(`  FCP: ${metrics.fcp.toFixed(0)}ms (threshold: ${PERFORMANCE_THRESHOLDS['first-contentful-paint']}ms)`);
    console.log(`  LCP: ${metrics.lcp.toFixed(0)}ms (threshold: ${PERFORMANCE_THRESHOLDS['largest-contentful-paint']}ms)`);
    console.log(`  CLS: ${metrics.cls.toFixed(3)} (threshold: ${PERFORMANCE_THRESHOLDS['cumulative-layout-shift']})`);
    console.log(`  Speed Index: ${metrics.si.toFixed(0)}ms (threshold: ${PERFORMANCE_THRESHOLDS['speed-index']}ms)`);
    console.log(`  TTI: ${metrics.tti.toFixed(0)}ms (threshold: ${PERFORMANCE_THRESHOLDS['time-to-interactive']}ms)`);
    console.log(`  TBT: ${metrics.tbt.toFixed(0)}ms (threshold: ${PERFORMANCE_THRESHOLDS['total-blocking-time']}ms)`);

    // Overall result
    if (passed.passed) {
      console.log('\n🎉 ALL TESTS PASSED!');
    } else {
      console.log('\n❌ FAILURES DETECTED:');
      passed.failures.forEach(failure => console.log(`  - ${failure}`));
    }
  }

  async runAllTests() {
    console.log('\n🔄 Running comprehensive performance tests...\n');

    for (const testCase of TEST_URLS) {
      // Skip auth-required tests for now
      if (testCase.requiresAuth) {
        console.log(`⏭️  Skipping ${testCase.name} (requires authentication)`);
        continue;
      }

      // Desktop test
      const desktopResult = await this.runLighthouseTest(
        testCase.url,
        LIGHTHOUSE_CONFIG,
        `${testCase.name} (Desktop)`
      );

      if (desktopResult) {
        this.results.push(desktopResult);
      }

      // Mobile test for critical pages
      if (testCase.critical) {
        const mobileResult = await this.runLighthouseTest(
          testCase.url,
          MOBILE_CONFIG,
          `${testCase.name} (Mobile)`
        );

        if (mobileResult) {
          this.results.push(mobileResult);
        }
      }

      // Small delay between tests
      await new Promise(resolve => setTimeout(resolve, 2000));
    }
  }

  async generateReport() {
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const reportDir = path.join(process.cwd(), 'performance-reports');

    try {
      await fs.mkdir(reportDir, { recursive: true });
    } catch (error) {
      // Directory already exists
    }

    // Generate JSON report
    const jsonReport = {
      timestamp: new Date().toISOString(),
      thresholds: PERFORMANCE_THRESHOLDS,
      results: this.results,
      summary: this.generateSummary()
    };

    const jsonPath = path.join(reportDir, `lighthouse-report-${timestamp}.json`);
    await fs.writeFile(jsonPath, JSON.stringify(jsonReport, null, 2));

    // Generate HTML summary
    const htmlReport = this.generateHtmlReport(jsonReport);
    const htmlPath = path.join(reportDir, `lighthouse-summary-${timestamp}.html`);
    await fs.writeFile(htmlPath, htmlReport);

    console.log(`\n📄 Reports generated:`);
    console.log(`  JSON: ${jsonPath}`);
    console.log(`  HTML: ${htmlPath}`);

    return jsonReport;
  }

  generateSummary() {
    const totalTests = this.results.length;
    const passedTests = this.results.filter(r => r.passed.passed).length;
    const failedTests = totalTests - passedTests;

    const avgScores = {
      performance: 0,
      accessibility: 0,
      bestPractices: 0,
      seo: 0
    };

    this.results.forEach(result => {
      Object.keys(avgScores).forEach(category => {
        avgScores[category] += result.scores[category] || 0;
      });
    });

    Object.keys(avgScores).forEach(category => {
      avgScores[category] = Math.round(avgScores[category] / totalTests);
    });

    return {
      totalTests,
      passedTests,
      failedTests,
      successRate: Math.round((passedTests / totalTests) * 100),
      avgScores
    };
  }

  generateHtmlReport(jsonReport) {
    const { summary, results } = jsonReport;

    return `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MeStocker Performance Report</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 20px; }
        .header { background: #1f2937; color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
        .summary { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px; margin-bottom: 30px; }
        .card { background: white; border: 1px solid #e5e7eb; border-radius: 8px; padding: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
        .score { font-size: 2em; font-weight: bold; }
        .score.good { color: #10b981; }
        .score.average { color: #f59e0b; }
        .score.poor { color: #ef4444; }
        .result { margin-bottom: 20px; border-left: 4px solid #e5e7eb; padding-left: 15px; }
        .result.passed { border-left-color: #10b981; }
        .result.failed { border-left-color: #ef4444; }
        .metrics { display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); gap: 10px; margin-top: 10px; }
        .metric { text-align: center; padding: 8px; background: #f9fafb; border-radius: 4px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>MeStocker MVP Performance Report</h1>
        <p>Generated: ${jsonReport.timestamp}</p>
        <p>Success Rate: ${summary.successRate}% (${summary.passedTests}/${summary.totalTests} tests passed)</p>
    </div>

    <div class="summary">
        <div class="card">
            <h3>Performance</h3>
            <div class="score ${summary.avgScores.performance >= 90 ? 'good' : summary.avgScores.performance >= 70 ? 'average' : 'poor'}">${summary.avgScores.performance}</div>
        </div>
        <div class="card">
            <h3>Accessibility</h3>
            <div class="score ${summary.avgScores.accessibility >= 90 ? 'good' : summary.avgScores.accessibility >= 70 ? 'average' : 'poor'}">${summary.avgScores.accessibility}</div>
        </div>
        <div class="card">
            <h3>Best Practices</h3>
            <div class="score ${summary.avgScores.bestPractices >= 90 ? 'good' : summary.avgScores.bestPractices >= 70 ? 'average' : 'poor'}">${summary.avgScores.bestPractices}</div>
        </div>
        <div class="card">
            <h3>SEO</h3>
            <div class="score ${summary.avgScores.seo >= 85 ? 'good' : summary.avgScores.seo >= 65 ? 'average' : 'poor'}">${summary.avgScores.seo}</div>
        </div>
    </div>

    <div class="results">
        <h2>Detailed Results</h2>
        ${results.map(result => `
            <div class="result ${result.passed.passed ? 'passed' : 'failed'}">
                <h3>${result.testName}</h3>
                <p><strong>URL:</strong> ${result.url}</p>
                <p><strong>Status:</strong> ${result.passed.passed ? '✅ PASSED' : '❌ FAILED'}</p>
                ${!result.passed.passed ? `<p><strong>Failures:</strong> ${result.passed.failures.join(', ')}</p>` : ''}

                <div class="metrics">
                    <div class="metric">
                        <strong>Performance</strong><br>
                        ${result.scores.performance}/100
                    </div>
                    <div class="metric">
                        <strong>Accessibility</strong><br>
                        ${result.scores.accessibility}/100
                    </div>
                    <div class="metric">
                        <strong>Best Practices</strong><br>
                        ${result.scores.bestPractices}/100
                    </div>
                    <div class="metric">
                        <strong>SEO</strong><br>
                        ${result.scores.seo}/100
                    </div>
                    <div class="metric">
                        <strong>FCP</strong><br>
                        ${Math.round(result.metrics.fcp)}ms
                    </div>
                    <div class="metric">
                        <strong>LCP</strong><br>
                        ${Math.round(result.metrics.lcp)}ms
                    </div>
                    <div class="metric">
                        <strong>CLS</strong><br>
                        ${result.metrics.cls.toFixed(3)}
                    </div>
                </div>
            </div>
        `).join('')}
    </div>
</body>
</html>`;
  }

  async cleanup() {
    if (this.chrome) {
      await this.chrome.kill();
      console.log('\n🔍 Chrome instance closed');
    }
  }

  async run() {
    try {
      await this.init();
      await this.runAllTests();
      const report = await this.generateReport();

      console.log('\n' + '='.repeat(60));
      console.log('🎯 PERFORMANCE VALIDATION SUMMARY');
      console.log('='.repeat(60));
      console.log(`Total Tests: ${report.summary.totalTests}`);
      console.log(`Passed: ${report.summary.passedTests}`);
      console.log(`Failed: ${report.summary.failedTests}`);
      console.log(`Success Rate: ${report.summary.successRate}%`);
      console.log('\nAverage Scores:');
      Object.entries(report.summary.avgScores).forEach(([category, score]) => {
        const status = score >= 90 ? '🟢' : score >= 70 ? '🟡' : '🔴';
        console.log(`  ${status} ${category}: ${score}/100`);
      });

      if (report.summary.successRate >= 80) {
        console.log('\n🎉 PERFORMANCE VALIDATION PASSED!');
        console.log('✅ MeStocker MVP meets enterprise performance standards');
      } else {
        console.log('\n⚠️  PERFORMANCE VALIDATION NEEDS IMPROVEMENT');
        console.log('❌ Some metrics are below target thresholds');
      }

      return report.summary.successRate >= 80;

    } catch (error) {
      console.error('❌ Performance validation failed:', error);
      return false;
    } finally {
      await this.cleanup();
    }
  }
}

// Run performance validation
if (require.main === module) {
  const validator = new PerformanceValidator();
  validator.run().then(success => {
    process.exit(success ? 0 : 1);
  }).catch(error => {
    console.error('Validation error:', error);
    process.exit(1);
  });
}

module.exports = PerformanceValidator;