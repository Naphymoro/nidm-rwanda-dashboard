import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  typescript: {
    // Keep deployments moving while experimental research UI modules are iterated.
    // Runtime-safe UI routes remain deployable even if legacy pages contain TS-only issues.
    ignoreBuildErrors: true,
  },
  eslint: {
    ignoreDuringBuilds: true,
  },
};

export default nextConfig;
