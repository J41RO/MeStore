#!/usr/bin/env node

/**
 * Production Safety Validator
 *
 * Este script verifica que NO haya elementos de debug/desarrollo
 * que puedan ser visibles en producción.
 *
 * Ejecutar antes del build de producción:
 * node scripts/validate-production-safety.js
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Configuración
const SRC_DIR = path.join(__dirname, '../src');
const ERRORS = [];
const WARNINGS = [];

// Patrones peligrosos que NO deberían estar en producción sin condiciones
const DANGEROUS_PATTERNS = [
  {
    pattern: /className=["'][^"']*\bfixed\b[^"']*\bbottom-\d+\b[^"']*\bright-\d+\b[^"']*["']/g,
    message: 'Fixed bottom-right element detected - Ensure it\'s wrapped in DevOnly or properly conditioned',
    severity: 'error'
  },
  {
    pattern: /console\.(log|debug|info)\(/g,
    message: 'Console statement detected - Should use DevOnlyConsole or be removed',
    severity: 'warning'
  },
  {
    pattern: /(Skip\s+payment|skipPayment|DEBUG|TESTING)/gi,
    message: 'Debug/testing keyword detected',
    severity: 'error'
  },
  {
    pattern: /z-\d{2,}/g,
    message: 'Very high z-index detected - Ensure it\'s necessary and properly scoped',
    severity: 'warning'
  }
];

// Archivos/directorios a ignorar
const IGNORE_PATTERNS = [
  'node_modules',
  '.test.',
  '.spec.',
  '__tests__',
  'DevOnly.tsx',
  'test/',
  '.git',
  'dist',
  'build'
];

/**
 * Verifica si un archivo debe ser ignorado
 */
function shouldIgnore(filePath) {
  return IGNORE_PATTERNS.some(pattern => filePath.includes(pattern));
}

/**
 * Escanea un archivo buscando patrones peligrosos
 */
function scanFile(filePath) {
  const content = fs.readFileSync(filePath, 'utf-8');
  const relativePath = path.relative(SRC_DIR, filePath);

  DANGEROUS_PATTERNS.forEach(({ pattern, message, severity }) => {
    const matches = content.match(pattern);

    if (matches) {
      // Verificar si está dentro de un bloque DevOnly o import.meta.env.DEV
      const lines = content.split('\n');
      const matchLines = [];

      lines.forEach((line, index) => {
        if (pattern.test(line)) {
          matchLines.push(index + 1);
        }
      });

      matchLines.forEach(lineNumber => {
        const context = getContext(lines, lineNumber);

        // Verificar si está protegido
        const isProtected =
          context.includes('<DevOnly>') ||
          context.includes('import.meta.env.DEV &&') ||
          context.includes('process.env.NODE_ENV === \'development\'') ||
          context.includes('isDevelopment &&');

        if (!isProtected) {
          const issue = {
            file: relativePath,
            line: lineNumber,
            message,
            severity,
            context: lines[lineNumber - 1].trim()
          };

          if (severity === 'error') {
            ERRORS.push(issue);
          } else {
            WARNINGS.push(issue);
          }
        }
      });
    }
  });
}

/**
 * Obtiene el contexto de una línea (5 líneas antes y después)
 */
function getContext(lines, lineNumber) {
  const start = Math.max(0, lineNumber - 5);
  const end = Math.min(lines.length, lineNumber + 5);
  return lines.slice(start, end).join('\n');
}

/**
 * Escanea recursivamente todos los archivos
 */
function scanDirectory(dir) {
  const items = fs.readdirSync(dir);

  items.forEach(item => {
    const itemPath = path.join(dir, item);

    if (shouldIgnore(itemPath)) {
      return;
    }

    const stat = fs.statSync(itemPath);

    if (stat.isDirectory()) {
      scanDirectory(itemPath);
    } else if (stat.isFile() && /\.(tsx?|jsx?)$/.test(item)) {
      scanFile(itemPath);
    }
  });
}

/**
 * Imprime el reporte
 */
function printReport() {
  console.log('\n🔍 Production Safety Validation Report\n');
  console.log('='.repeat(60));

  if (ERRORS.length === 0 && WARNINGS.length === 0) {
    console.log('\n✅ No issues found! Your code is production-safe.\n');
    return true;
  }

  if (ERRORS.length > 0) {
    console.log('\n❌ ERRORS (Must be fixed before production):\n');
    ERRORS.forEach((error, index) => {
      console.log(`${index + 1}. ${error.file}:${error.line}`);
      console.log(`   ${error.message}`);
      console.log(`   Code: ${error.context}`);
      console.log('');
    });
  }

  if (WARNINGS.length > 0) {
    console.log('\n⚠️  WARNINGS (Review recommended):\n');
    WARNINGS.forEach((warning, index) => {
      console.log(`${index + 1}. ${warning.file}:${warning.line}`);
      console.log(`   ${warning.message}`);
      console.log(`   Code: ${warning.context}`);
      console.log('');
    });
  }

  console.log('='.repeat(60));
  console.log(`\nTotal: ${ERRORS.length} errors, ${WARNINGS.length} warnings\n`);

  return ERRORS.length === 0;
}

/**
 * Main
 */
function main() {
  console.log('🚀 Starting production safety validation...\n');

  try {
    scanDirectory(SRC_DIR);
    const passed = printReport();

    if (!passed) {
      console.log('❌ Validation failed. Please fix the errors before building for production.\n');
      process.exit(1);
    }

    console.log('✅ Validation passed! Safe to build for production.\n');
    process.exit(0);
  } catch (error) {
    console.error('Error during validation:', error);
    process.exit(1);
  }
}

main();
