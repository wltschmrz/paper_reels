import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";
export default defineConfig(({ mode }) => {
  // Only the dev proxy reads this token. Never export it via define or VITE_*.
  const serverEnv = loadEnv(mode, "backend", "");
  return {
    plugins: [react()],
    base: "./",
    server: {
      host: "0.0.0.0",
      port: 5173,
      strictPort: true,
      watch: { usePolling: true, interval: 500 },
      proxy: {
        "/api": {
          target: "http://127.0.0.1:8000",
          changeOrigin: true,
          headers: { "x-ss-token": serverEnv.SS_API_TOKEN || "" },
        },
      },
    },
  };
});
