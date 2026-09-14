import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  poweredByHeader: false,
  images: {
    // Allow-list: the image optimizer must not fetch arbitrary URLs for strangers.
    remotePatterns: [new URL("https://cdn.careerpilot.app/logos/**")],
    formats: ["image/avif", "image/webp"],
  },
};

export default nextConfig;
