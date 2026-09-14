import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "standalone", // self-contained server for Docker
};

export default nextConfig;
