import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  cacheComponents: true, // opt in to `use cache` + partial prerendering
};

export default nextConfig;
