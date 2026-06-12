import type { NextConfig } from 'next'

const nextConfig: NextConfig = {
  async headers() {
    return [
      {
        source: '/ppci-app.html',
        headers: [
          { key: 'Content-Type', value: 'text/html; charset=utf-8' },
        ],
      },
    ]
  },
  experimental: {
    serverActions: {
      bodySizeLimit: '20mb',
    },
  },
}

export default nextConfig
