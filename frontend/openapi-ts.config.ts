import { defineConfig } from "@hey-api/openapi-ts";

export default defineConfig({
  input: "http://localhost:8000/openapi.json",
  plugins: ["@hey-api/client-fetch"],
  output: {
    path: "src/client",
    format: "prettier",
    lint: "eslint",
  },
});
