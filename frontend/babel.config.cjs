module.exports = {
  presets: [
    ['@babel/preset-env', { targets: { node: 'current' } }],
    ['@babel/preset-react', { runtime: 'automatic' }],
    '@babel/preset-typescript',
  ],
  plugins: [
    [
      'babel-plugin-transform-import-meta',
      {
        module: 'ES6',
        getUrl: () => 'file://localhost/test',
        getEnv: () => ({
          VITE_API_BASE_URL: 'http://localhost:8000',
          VITE_BUILD_NUMBER: '1',
          MODE: 'test',
          DEV: false,
          PROD: false,
          BASE_URL: '/',
        }),
      },
    ],
  ],
};