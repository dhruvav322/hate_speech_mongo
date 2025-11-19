import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  devIndicators: {
    appIsrStatus: false, // Hides the static/dynamic indicator
    buildActivity: false, // Hides the building indicator
    turbopack: false, // Hides the Turbopack info
  },
};

export default nextConfig;
