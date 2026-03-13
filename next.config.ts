// Ensure the Node 25+ web storage fix runs in every Node process that loads
// the Next config (dev, build, start). This removes the need for NODE_OPTIONS.
import "./node-compat.cjs";

import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  devIndicators: false,
};

export default nextConfig;
