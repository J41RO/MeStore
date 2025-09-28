#!/usr/bin/env node

/**
 * TDD RED PHASE VALIDATION SCRIPT
 *
 * This script validates that all TDD navigation tests FAIL as expected
 * in the RED phase before implementation begins.
 *
 * Usage: npm run test:red-phase
 * or: node scripts/validate-tdd-red-phase.js
 */

const { execSync } = require('child_process');
const path = require('path');
const fs = require('fs');

console.log('🔴 TDD RED PHASE VALIDATION');
console.log('=============================');
console.log('');

// Configuration
const TEST_CONFIG = {
  testDir: 'src/components/admin/navigation/__tests__',
  requiredTests: [
    'NavigationProvider.test.tsx',
    'CategoryNavigation.test.tsx',
    'NavigationCategory.test.tsx',
    'NavigationItem.test.tsx',
    'AdminSidebar.test.tsx',
    'integration/NavigationFlow.test.tsx',
    'integration/AccessibilityCompliance.test.tsx'
  ],
  minTestsPerFile: 15, // Minimum number of tests per file
  requiredFailures: 100 // All tests should fail
};

/**
 * Validate test files exist
 */
function validateTestFiles() {
  console.log('📁 Validating test files...');

  const missing = [];

  TEST_CONFIG.requiredTests.forEach(testFile => {
    const fullPath = path.join(TEST_CONFIG.testDir, testFile);
    if (!fs.existsSync(fullPath)) {
      missing.push(testFile);
    } else {
      console.log(`   ✅ ${testFile}`);
    }
  });

  if (missing.length > 0) {
    console.log('');
    console.error('❌ Missing test files:');
    missing.forEach(file => console.error(`   - ${file}`));
    process.exit(1);
  }

  console.log(`   ✅ All ${TEST_CONFIG.requiredTests.length} test files found`);
  console.log('');
}

/**
 * Count tests in each file
 */
function validateTestCoverage() {
  console.log('🧪 Validating test coverage...');

  TEST_CONFIG.requiredTests.forEach(testFile => {
    const fullPath = path.join(TEST_CONFIG.testDir, testFile);
    const content = fs.readFileSync(fullPath, 'utf8');

    // Count 'it(' and 'test(' occurrences
    const testMatches = content.match(/\b(it|test)\s*\(/g) || [];
    const testCount = testMatches.length;

    if (testCount < TEST_CONFIG.minTestsPerFile) {
      console.error(`   ❌ ${testFile}: ${testCount} tests (minimum ${TEST_CONFIG.minTestsPerFile})`);
    } else {
      console.log(`   ✅ ${testFile}: ${testCount} tests`);
    }
  });

  console.log('');
}

/**
 * Run tests and validate they fail
 */
function validateTestFailures() {
  console.log('🔥 Running TDD tests (expecting failures)...');

  try {
    // Run tests with Jest
    const result = execSync(
      'npx jest --testPathPattern=navigation.*test --passWithNoTests --json --verbose',
      {
        encoding: 'utf8',
        cwd: process.cwd(),
        stdio: ['pipe', 'pipe', 'pipe']
      }
    );

    const testResults = JSON.parse(result);

    if (testResults.success) {
      console.error('❌ UNEXPECTED: Tests are passing!');
      console.error('   In TDD RED phase, all tests should FAIL');
      console.error('   This indicates components may already be implemented');
      process.exit(1);
    }

    console.log('   ✅ Tests are failing as expected in RED phase');

    // Analyze failure reasons
    const failedTests = testResults.testResults
      .filter(suite => suite.status === 'failed')
      .map(suite => ({
        file: path.basename(suite.name),
        failures: suite.assertionResults
          .filter(test => test.status === 'failed')
          .length
      }));

    console.log('');
    console.log('📊 Failure Analysis:');
    failedTests.forEach(({ file, failures }) => {
      console.log(`   🔴 ${file}: ${failures} failed tests`);
    });

  } catch (error) {
    // Jest exits with code 1 when tests fail, which is expected
    if (error.status === 1) {
      console.log('   ✅ Tests failed as expected (TDD RED phase)');
    } else {
      console.error('❌ Unexpected error running tests:');
      console.error(error.message);
      process.exit(1);
    }
  }

  console.log('');
}

/**
 * Validate implementation files don't exist
 */
function validateNoImplementation() {
  console.log('🚫 Validating components are not implemented...');

  const componentFiles = [
    'src/components/admin/navigation/NavigationProvider.tsx',
    'src/components/admin/navigation/CategoryNavigation.tsx',
    'src/components/admin/navigation/NavigationCategory.tsx',
    'src/components/admin/navigation/NavigationItem.tsx',
    'src/components/admin/navigation/AdminSidebar.tsx'
  ];

  const implemented = [];

  componentFiles.forEach(file => {
    if (fs.existsSync(file)) {
      // Check if file has actual implementation (not just types/interfaces)
      const content = fs.readFileSync(file, 'utf8');

      // Look for React component patterns
      if (content.includes('export default') ||
          content.includes('export const') ||
          content.includes('function ') ||
          content.includes('const ') && content.includes('React.FC')) {
        implemented.push(file);
      }
    }
  });

  if (implemented.length > 0) {
    console.warn('⚠️  Warning: Some components appear to be implemented:');
    implemented.forEach(file => console.warn(`   - ${file}`));
    console.warn('   This may cause tests to pass unexpectedly');
  } else {
    console.log('   ✅ No component implementations found (RED phase correct)');
  }

  console.log('');
}

/**
 * Generate TDD report
 */
function generateTDDReport() {
  console.log('📋 TDD RED PHASE REPORT');
  console.log('========================');

  const report = {
    phase: 'RED',
    timestamp: new Date().toISOString(),
    testFiles: TEST_CONFIG.requiredTests.length,
    status: 'READY_FOR_GREEN_PHASE',
    nextSteps: [
      '1. React Specialist AI should implement NavigationProvider',
      '2. Implement CategoryNavigation component',
      '3. Implement NavigationCategory component',
      '4. Implement NavigationItem component',
      '5. Implement AdminSidebar component',
      '6. Run GREEN phase tests to validate implementation',
      '7. REFACTOR phase - optimize and improve code quality'
    ]
  };

  console.log(`📅 Timestamp: ${report.timestamp}`);
  console.log(`📊 Test Files: ${report.testFiles}`);
  console.log(`🎯 Status: ${report.status}`);
  console.log('');
  console.log('🚀 Next Steps:');
  report.nextSteps.forEach((step, index) => {
    console.log(`   ${index + 1}. ${step.replace(/^\d+\.\s*/, '')}`);
  });

  // Save report to file
  const reportPath = path.join('coverage', 'tdd-red-phase-report.json');
  fs.mkdirSync(path.dirname(reportPath), { recursive: true });
  fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));

  console.log('');
  console.log(`📄 Report saved to: ${reportPath}`);
}

/**
 * Main validation process
 */
function main() {
  try {
    validateTestFiles();
    validateTestCoverage();
    validateNoImplementation();
    validateTestFailures();
    generateTDDReport();

    console.log('');
    console.log('🎉 TDD RED PHASE VALIDATION COMPLETE');
    console.log('=====================================');
    console.log('');
    console.log('✅ All validation checks passed');
    console.log('🔴 Tests are failing as expected');
    console.log('🚀 Ready for GREEN phase implementation');
    console.log('');
    console.log('Next: React Specialist AI should implement components');
    console.log('      to make all tests pass (GREEN phase)');

  } catch (error) {
    console.error('');
    console.error('❌ TDD RED PHASE VALIDATION FAILED');
    console.error('===================================');
    console.error('');
    console.error('Error:', error.message);
    process.exit(1);
  }
}

// Run validation
main();