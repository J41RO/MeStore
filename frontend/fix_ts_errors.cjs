#!/usr/bin/env node

/**
 * Script to fix common TypeScript unused variable/import errors
 * Adds underscore prefix to unused parameters and removes unused imports
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// Get TypeScript errors
console.log('Getting TypeScript errors...');
let errors = [];
try {
  execSync('npx tsc --noEmit', { encoding: 'utf-8' });
} catch (error) {
  errors = error.stdout.split('\n').filter(line => line.includes('TS6133'));
}

console.log(`Found ${errors.length} unused variable/import errors`);

// Process each error
const fixes = new Map();

for (const error of errors) {
  const match = error.match(/^([^:]+):(\d+):(\d+): error TS6133: '(.+?)' is declared but its value is never read\./);
  if (!match) continue;
  
  const [, filePath, line, col, varName] = match;
  const fullPath = path.resolve(filePath);
  
  if (!fixes.has(fullPath)) {
    fixes.set(fullPath, []);
  }
  
  fixes.get(fullPath).push({
    line: parseInt(line),
    col: parseInt(col),
    varName: varName
  });
}

console.log(`Processing ${fixes.size} files...`);

// Apply fixes
for (const [filePath, fileErrors] of fixes) {
  try {
    let content = fs.readFileSync(filePath, 'utf-8');
    const lines = content.split('\n');
    
    // Sort errors by line number in reverse order to avoid line number shifts
    fileErrors.sort((a, b) => b.line - a.line);
    
    for (const { line, varName } of fileErrors) {
      const lineIndex = line - 1;
      if (lineIndex < 0 || lineIndex >= lines.length) continue;
      
      const originalLine = lines[lineIndex];
      
      // Skip if variable is already prefixed with underscore
      if (varName.startsWith('_')) continue;
      
      // Different patterns for different contexts
      let newLine = originalLine;
      
      // Function parameters: (varName) => (_ varName)
      newLine = newLine.replace(
        new RegExp(`\\b${varName}\\b(?=\\s*[,)])`, 'g'),
        `_${varName}`
      );
      
      // Destructuring: { varName } => { varName: _varName }
      newLine = newLine.replace(
        new RegExp(`\\{([^}]*?)\\b${varName}\\b([^}]*?)\\}`, 'g'),
        (match, before, after) => {
          if (before.includes(':') || after.includes(':')) return match;
          return `{${before}${varName}: _${varName}${after}}`;
        }
      );
      
      // Variable declarations: const varName => const _varName  
      newLine = newLine.replace(
        new RegExp(`\\b(const|let|var)\\s+${varName}\\b`, 'g'),
        `$1 _${varName}`
      );
      
      // Array destructuring: [varName] => [_varName]
      newLine = newLine.replace(
        new RegExp(`\\[([^\\]]*?)\\b${varName}\\b([^\\]]*?)\\]`, 'g'),
        `[$1_${varName}$2]`
      );
      
      if (newLine !== originalLine) {
        lines[lineIndex] = newLine;
        console.log(`Fixed ${varName} in ${path.relative(process.cwd(), filePath)}:${line}`);
      }
    }
    
    const newContent = lines.join('\n');
    if (newContent !== content) {
      fs.writeFileSync(filePath, newContent);
    }
    
  } catch (error) {
    console.error(`Error processing ${filePath}:`, error.message);
  }
}

console.log('Done fixing unused variables!');