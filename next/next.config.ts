import path from 'path';
import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
  // Avoid picking an unrelated lockfile outside this app when multiple exist on disk.
  outputFileTracingRoot: path.join(__dirname),
};

export default nextConfig;
