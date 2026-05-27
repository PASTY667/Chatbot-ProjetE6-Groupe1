import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  async redirects() {
    return [
      { source: '/logs', destination: '/admin/logs', permanent: false },
      { source: '/files', destination: '/admin/files', permanent: false },
      { source: '/stats', destination: '/admin/stats', permanent: false },
      { source: '/users', destination: '/admin/users', permanent: false },
    ];
  },
};

export default nextConfig;
