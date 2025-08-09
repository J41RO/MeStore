export default {
  // Básicas
  semi: true,
  singleQuote: true,
  trailingComma: 'es5',

  // Layout
  printWidth: 80,
  tabWidth: 2,
  useTabs: false,

  // Objetos y arrays
  bracketSpacing: true,
  bracketSameLine: false,

  // Arrow functions
  arrowParens: 'avoid',

  // Líneas
  endOfLine: 'lf',

  // JSX específico
  jsxSingleQuote: true,

  // Archivos soportados
  overrides: [
    {
      files: '*.json',
      options: {
        singleQuote: false,
      },
    },
  ],
};
