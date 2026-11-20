import { createRequire } from "node:module";
import { realpathSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

// Resolve packages from the ESLint installation running this config.
const requireFromEslint = createRequire(realpathSync(process.argv[1]));

const { defineConfig } = requireFromEslint("eslint/config");
const typescriptEslint = requireFromEslint("@typescript-eslint/eslint-plugin");
const globals = requireFromEslint("globals");
const tsParser = requireFromEslint("@typescript-eslint/parser");
const js = requireFromEslint("@eslint/js");
const { FlatCompat } = requireFromEslint("@eslint/eslintrc");

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const compat = new FlatCompat({
    baseDirectory: __dirname,
    recommendedConfig: js.configs.recommended,
    allConfig: js.configs.all
});

export default defineConfig([{
    extends: compat.extends("eslint:recommended"),

    plugins: {
        "@typescript-eslint": typescriptEslint,
    },

    languageOptions: {
        globals: {
            ...globals.browser,
            ...globals.jest,
            ...globals.amd,
            Atomics: "readonly",
            SharedArrayBuffer: "readonly",
            splunkjs: "readonly",
        },

        parser: tsParser,
        ecmaVersion: 2018,
        sourceType: "module",
    },

    rules: {
        eqeqeq: "error",
        "no-var": "error",
        "prefer-const": "error",
        "no-implicit-globals": "error",
        "no-eval": "error",
        "no-implied-eval": "error",
        "no-return-await": "warn",
        "no-throw-literal": "error",
        radix: "error",
        semi: ["error", "always"],
        quotes: ["error", "single"],
        indent: ["error", 2],
        "comma-dangle": ["error", "always-multiline"],
        "no-extra-semi": "error",
    },
}]);