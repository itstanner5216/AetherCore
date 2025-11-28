module.exports = {
  root: true,
  env: {
    node: true,
    es2022: true,
  },
  parserOptions: {
    ecmaVersion: 2022,
    sourceType: "module",
  },
  extends: [
    "eslint:recommended",
    "plugin:import/recommended",
    "plugin:jsdoc/recommended",
    "prettier",
  ],
  plugins: ["import", "jsdoc"],
  rules: {
    "no-unused-vars": ["warn", { argsIgnorePattern: "^_" }],
    "import/order": [
      "warn",
      {
        groups: [
          "builtin",
          "external",
          "internal",
          "parent",
          "sibling",
          "index",
        ],
        "newlines-between": "always",
        alphabetize: { order: "asc", caseInsensitive: true },
      },
    ],
    "jsdoc/require-jsdoc": "off",
    "jsdoc/require-param-description": "off",
    "jsdoc/require-returns-description": "off",
  },
  ignorePatterns: [
    "node_modules/",
    "dist/",
    "build/",
    "coverage/",
    "*.min.js",
  ],
  settings: {
    "import/resolver": {
      node: {
        extensions: [".js", ".cjs", ".mjs"],
      },
    },
  },
};
