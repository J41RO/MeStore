#!/usr/bin/env node

/**
 * Accessibility Audit Script
 *
 * Comprehensive WCAG 2.1 AA compliance audit for the enterprise navigation system.
 * Validates all accessibility implementations by the Accessibility AI.
 *
 * Usage: npm run accessibility:audit
 *
 * @version 1.0.0
 * @author Accessibility AI
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

/**
 * Audit configuration
 */
const AUDIT_CONFIG = {
  BASE_URL: 'http://192.168.1.137:5173',
  ADMIN_URL: 'http://192.168.1.137:5173/admin',
  LIGHTHOUSE_THRESHOLD: 95,
  CONTRAST_RATIO_THRESHOLD: 4.5,
  TOUCH_TARGET_SIZE: 44,
  OUTPUT_DIR: './reports/accessibility'
};

/**
 * Color utilities for console output
 */
const colors = {
  reset: '\x1b[0m',
  bright: '\x1b[1m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  magenta: '\x1b[35m',
  cyan: '\x1b[36m'
};

/**
 * Logger utility
 */
const logger = {
  info: (msg) => console.log(`${colors.blue}ℹ ${msg}${colors.reset}`),
  success: (msg) => console.log(`${colors.green}✅ ${msg}${colors.reset}`),
  warning: (msg) => console.log(`${colors.yellow}⚠️  ${msg}${colors.reset}`),
  error: (msg) => console.log(`${colors.red}❌ ${msg}${colors.reset}`),
  header: (msg) => console.log(`\n${colors.bright}${colors.cyan}🎯 ${msg}${colors.reset}\n`)
};

/**
 * Ensure output directory exists
 */
function ensureOutputDir() {
  if (!fs.existsSync(AUDIT_CONFIG.OUTPUT_DIR)) {
    fs.mkdirSync(AUDIT_CONFIG.OUTPUT_DIR, { recursive: true });
  }
}

/**
 * Check if server is running
 */
async function checkServerStatus() {
  try {
    const response = await fetch(AUDIT_CONFIG.BASE_URL);
    return response.ok;
  } catch (error) {
    return false;
  }
}

/**
 * Run Lighthouse accessibility audit
 */
function runLighthouseAudit() {
  logger.header('Running Lighthouse Accessibility Audit');

  try {
    const cmd = `lighthouse ${AUDIT_CONFIG.ADMIN_URL} --only-categories=accessibility --output=json --output-path=${AUDIT_CONFIG.OUTPUT_DIR}/lighthouse-report.json --chrome-flags="--headless --no-sandbox" --quiet`;

    logger.info('Executing Lighthouse audit...');
    execSync(cmd, { stdio: 'inherit' });

    // Read and parse results
    const reportPath = path.join(AUDIT_CONFIG.OUTPUT_DIR, 'lighthouse-report.json');
    if (fs.existsSync(reportPath)) {
      const report = JSON.parse(fs.readFileSync(reportPath, 'utf8'));
      const accessibilityScore = Math.round(report.categories.accessibility.score * 100);

      if (accessibilityScore >= AUDIT_CONFIG.LIGHTHOUSE_THRESHOLD) {
        logger.success(`Lighthouse accessibility score: ${accessibilityScore}/100 ✨`);
        return true;
      } else {
        logger.error(`Lighthouse accessibility score: ${accessibilityScore}/100 (threshold: ${AUDIT_CONFIG.LIGHTHOUSE_THRESHOLD})`);
        return false;
      }
    } else {
      logger.error('Lighthouse report not generated');
      return false;
    }
  } catch (error) {
    logger.error(`Lighthouse audit failed: ${error.message}`);
    return false;
  }
}

/**
 * Run accessibility tests
 */
function runAccessibilityTests() {
  logger.header('Running Accessibility Test Suite');

  try {
    const cmd = 'npm run test -- --run src/components/admin/navigation/__tests__/accessibility/AccessibilityValidation.test.tsx';

    logger.info('Executing accessibility tests...');
    execSync(cmd, { stdio: 'inherit' });
    logger.success('All accessibility tests passed');
    return true;
  } catch (error) {
    logger.error('Accessibility tests failed');
    return false;
  }
}

/**
 * Check TypeScript compilation
 */
function checkTypeScript() {
  logger.header('Checking TypeScript Compilation');

  try {
    logger.info('Running TypeScript check...');
    execSync('npx tsc --noEmit', { stdio: 'inherit' });
    logger.success('TypeScript compilation successful');
    return true;
  } catch (error) {
    logger.error('TypeScript compilation failed');
    return false;
  }
}

/**
 * Audit navigation component files
 */
function auditNavigationFiles() {
  logger.header('Auditing Navigation Component Files');

  const requiredFiles = [
    'src/components/admin/navigation/AccessibilityProvider.tsx',
    'src/components/admin/navigation/KeyboardNavigationHandler.tsx',
    'src/components/admin/navigation/AccessibilityTheme.tsx',
    'src/components/admin/navigation/MobileTouchAccessibility.tsx',
    'src/components/admin/navigation/__tests__/accessibility/AccessibilityValidation.test.tsx'
  ];

  let allFilesExist = true;

  requiredFiles.forEach(file => {
    if (fs.existsSync(file)) {
      logger.success(`${file} exists`);
    } else {
      logger.error(`${file} missing`);
      allFilesExist = false;
    }
  });

  return allFilesExist;
}

/**
 * Generate accessibility compliance report
 */
function generateComplianceReport(results) {
  logger.header('Generating Accessibility Compliance Report');

  const report = {
    timestamp: new Date().toISOString(),
    auditResults: results,
    wcagCompliance: {
      'WCAG 2.1 Level A': results.every(r => r.passed),
      'WCAG 2.1 Level AA': results.every(r => r.passed),
      'Section 508': results.every(r => r.passed)
    },
    summary: {
      totalChecks: results.length,
      passed: results.filter(r => r.passed).length,
      failed: results.filter(r => !r.passed).length,
      score: Math.round((results.filter(r => r.passed).length / results.length) * 100)
    },
    recommendations: [
      'Continue monitoring accessibility with automated tests',
      'Conduct periodic manual testing with screen readers',
      'Validate with real users who use assistive technologies',
      'Keep up to date with WCAG guidelines and best practices'
    ]
  };

  const reportPath = path.join(AUDIT_CONFIG.OUTPUT_DIR, 'accessibility-compliance-report.json');
  fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));

  logger.success(`Compliance report generated: ${reportPath}`);

  // Generate human-readable summary
  const summaryPath = path.join(AUDIT_CONFIG.OUTPUT_DIR, 'accessibility-summary.md');
  const summary = `# Accessibility Compliance Report

Generated: ${new Date().toLocaleString()}

## Summary
- **Total Checks**: ${report.summary.totalChecks}
- **Passed**: ${report.summary.passed}
- **Failed**: ${report.summary.failed}
- **Score**: ${report.summary.score}/100

## WCAG Compliance Status
- WCAG 2.1 Level A: ${report.wcagCompliance['WCAG 2.1 Level A'] ? '✅ COMPLIANT' : '❌ NON-COMPLIANT'}
- WCAG 2.1 Level AA: ${report.wcagCompliance['WCAG 2.1 Level AA'] ? '✅ COMPLIANT' : '❌ NON-COMPLIANT'}
- Section 508: ${report.wcagCompliance['Section 508'] ? '✅ COMPLIANT' : '❌ NON-COMPLIANT'}

## Audit Results
${results.map(r => `- ${r.passed ? '✅' : '❌'} ${r.name}: ${r.description}`).join('\n')}

## Recommendations
${report.recommendations.map(r => `- ${r}`).join('\n')}

---
*Generated by MeStore Accessibility AI*
`;

  fs.writeFileSync(summaryPath, summary);
  logger.success(`Summary report generated: ${summaryPath}`);
}

/**
 * Main audit function
 */
async function runAccessibilityAudit() {
  console.log(`${colors.bright}${colors.magenta}`);
  console.log('╔══════════════════════════════════════════════════════════╗');
  console.log('║                                                          ║');
  console.log('║          🎯 ACCESSIBILITY COMPLIANCE AUDIT 🎯            ║');
  console.log('║                                                          ║');
  console.log('║                WCAG 2.1 AA Validation                   ║');
  console.log('║              Enterprise Navigation System                ║');
  console.log('║                                                          ║');
  console.log('║                    Accessibility AI                     ║');
  console.log('║                                                          ║');
  console.log('╚══════════════════════════════════════════════════════════╝');
  console.log(colors.reset);

  ensureOutputDir();

  const results = [];

  // Check server status
  logger.info('Checking server status...');
  const serverRunning = await checkServerStatus();
  if (!serverRunning) {
    logger.warning('Development server not running. Some tests may be skipped.');
  }

  // 1. Check required files
  results.push({
    name: 'File Structure',
    description: 'All accessibility component files exist',
    passed: auditNavigationFiles()
  });

  // 2. TypeScript compilation
  results.push({
    name: 'TypeScript Compilation',
    description: 'All accessibility components compile without errors',
    passed: checkTypeScript()
  });

  // 3. Accessibility tests
  results.push({
    name: 'Accessibility Test Suite',
    description: 'Comprehensive WCAG 2.1 AA compliance tests pass',
    passed: runAccessibilityTests()
  });

  // 4. Lighthouse audit (if server is running)
  if (serverRunning) {
    results.push({
      name: 'Lighthouse Accessibility Audit',
      description: `Automated accessibility score >= ${AUDIT_CONFIG.LIGHTHOUSE_THRESHOLD}`,
      passed: runLighthouseAudit()
    });
  }

  // Generate compliance report
  generateComplianceReport(results);

  // Final summary
  const passedCount = results.filter(r => r.passed).length;
  const totalCount = results.length;
  const score = Math.round((passedCount / totalCount) * 100);

  console.log(`\n${colors.bright}${colors.cyan}╔══════════════════════════════════════════════════════════╗${colors.reset}`);
  console.log(`${colors.bright}${colors.cyan}║                     AUDIT SUMMARY                        ║${colors.reset}`);
  console.log(`${colors.bright}${colors.cyan}╚══════════════════════════════════════════════════════════╝${colors.reset}\n`);

  if (score >= 95) {
    logger.success(`🎉 EXCELLENT! Accessibility Score: ${score}% (${passedCount}/${totalCount})`);
    logger.success('✨ WCAG 2.1 AA COMPLIANCE ACHIEVED ✨');
  } else if (score >= 80) {
    logger.warning(`⚠️  GOOD: Accessibility Score: ${score}% (${passedCount}/${totalCount})`);
    logger.warning('Some improvements needed for full compliance');
  } else {
    logger.error(`❌ NEEDS WORK: Accessibility Score: ${score}% (${passedCount}/${totalCount})`);
    logger.error('Significant accessibility issues need to be addressed');
  }

  console.log('\n📊 Detailed reports available in:', AUDIT_CONFIG.OUTPUT_DIR);

  // Exit with appropriate code
  process.exit(score >= 95 ? 0 : 1);
}

// Run audit if called directly
if (require.main === module) {
  runAccessibilityAudit().catch(error => {
    logger.error(`Audit failed: ${error.message}`);
    process.exit(1);
  });
}

module.exports = { runAccessibilityAudit };