import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "path";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig(() => {
  return {
    plugins: [react(), tailwindcss()],

    resolve: {
      alias: {
        "@": path.resolve(__dirname, "./src"),
        "@api": path.resolve(__dirname, "src/api"),
        "@domain": path.resolve(__dirname, "src/domain"),
        "@hooks": path.resolve(__dirname, "src/hooks"),
        "@components": path.resolve(__dirname, "src/components"),
      },
    },

    // Output build files where your backend can serve them
    build: {
      sourcemap: true,
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

    server: {
      port: 5174,
    },
  };
});
