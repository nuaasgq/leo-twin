import react from "@vitejs/plugin-react";
import cesium from "vite-plugin-cesium";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [react(), cesium()],
  server: {
    port: 5173,
    strictPort: false,
    proxy: {
      "/stream": {
        target: "http://127.0.0.1:8765",
        ws: true
      },
      "/metrics": {
        target: "http://127.0.0.1:8765"
      },
      "/scenario": {
        target: "http://127.0.0.1:8765"
      }
    }
  }
});
