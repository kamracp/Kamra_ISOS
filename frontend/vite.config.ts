import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

// Each product segment builds to its own folder, because deployment rsyncs
// dist-benas and dist-manufactureos to two different nginx roots. Without
// this, every mode wrote to dist/ and the segment folders silently kept
// whatever stale bundle was there last - which nearly shipped a two-week-old
// build to production on 20 Aug 2026.
const OUT_DIRS: Record<string, string> = {
  benas: "dist-benas",
  manufactureos: "dist-manufactureos",
};

export default defineConfig(({ mode }) => ({
  plugins: [
    react(),
    tailwindcss(),
  ],
  build: {
    outDir: OUT_DIRS[mode] ?? "dist",
    emptyOutDir: true,
  },
}));
