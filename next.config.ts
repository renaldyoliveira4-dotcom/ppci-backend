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
  async rewrites() {
    return [
      {
        source: '/api/ai/status',
        destination: '/api/ai-status',
      },
      {
        source: '/api/ai/analyze-plant',
        destination: '/api/analyze-plant',
      },
    ]
  },
}

export default nextConfig
