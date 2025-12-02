import { defineConfig } from "@hey-api/openapi-ts";

export default defineConfig({
  client: "@hey-api/client-fetch",
  input: "../openapi/openapi.json",
  output: {
    path: "src/lib/api-client",
    format: "prettier",
  },
  plugins: ["@hey-api/typescript"],
});
