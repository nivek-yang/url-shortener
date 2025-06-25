import eslintPluginPrettier from 'eslint-plugin-prettier';

export default [
  {
    files: ['**/*.js', '**/*.jsx'],
    ignores: ['**/node_modules/**', '**/.venv/**', '**/static/**', '**/staticfiles/**', '**/media/**', '**/dist/**', '**/build/**', '**/migrations/**', '**/site-packages/**', '**/__pycache__/**', '**/django/**'],
    languageOptions: {
      ecmaVersion: 2021,
      sourceType: 'module',
    },
    plugins: {
      prettier: eslintPluginPrettier,
    },
    rules: {
      'no-undef': 'error',
      'no-unused-vars': 'warn',
      semi: ['error', 'always'],
      'prettier/prettier': 'error',
    },
  },
];
