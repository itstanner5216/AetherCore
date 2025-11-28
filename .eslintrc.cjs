module.exports = {
  env: { es2022: true, node: true, browser: true },
  extends: ["eslint:recommended"],
  parserOptions: { ecmaVersion: 2022, sourceType: "module" },
  rules: {
    "no-unused-vars": ["warn", { argsIgnorePattern: "^_" }],
    "no-console": "off",
  },
};
