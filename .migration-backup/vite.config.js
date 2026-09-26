import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  root: "frontend",
  build: {
    outDir: "../static/react",
    emptyOutDir: true,
    manifest: true,
  },
  server: {
    host: "0.0.0.0",
    allowedHosts: true,
    proxy: {
      "/upload": "http://127.0.0.1:5000",
      "/check-promo-code": "http://127.0.0.1:5000",
      "/free-analysis": "http://127.0.0.1:5000",
      "/create-checkout-session": "http://127.0.0.1:5000",
    },
  },
  test: {
    environment: "jsdom",
    setupFiles: "./src/test-setup.js",
  },
});