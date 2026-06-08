import type { NextConfig } from 'next'

const nextConfig: NextConfig = {
  // Permite servir arquivos HTML estáticos da pasta public
  async headers() {
    return [
      {
        source: '/ppci-app.html',
        headers: [
          { key: 'X-Frame-Options', value: 'SAMEORIGIN' },
          { key: 'Content-Type', value: 'text/html; charset=utf-8' },
        ],
      },
    ]
  },
}

export default nextConfig
