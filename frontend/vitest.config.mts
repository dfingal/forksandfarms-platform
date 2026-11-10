import { fileURLToPath } from "node:url";
import { defineConfig } from "vitest/config";

export default defineConfig({
  resolve: {
    // Mirror tsconfig.json's "@/*" import alias so tests can import app
    // code (e.g. app/api/revalidate/route.ts) the same way the app does.
    alias: { "@": fileURLToPath(new URL(".", import.meta.url)) },
  },
});
