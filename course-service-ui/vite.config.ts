import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "path";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
  plugins: [react(), tailwindcss()],

  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },

  // Output build files where your backend can serve them
  build: {
    outDir: path.resolve(
      __dirname,
      "../share/e2x_course_hub/static/course-service-ui",
    ),
    emptyOutDir: true,
    rollupOptions: {
      input: path.resolve(__dirname, "src/main.tsx"),
      output: {
        entryFileNames: "main.js",
        chunkFileNames: "chunks/[name].js",
        assetFileNames: "assets/[name].[ext]",
      },
    },
  },

  // (Optional) Proxy API calls during development
  server: {
    proxy: {
      "/api": "http://localhost:8000",
    },
  },
});
