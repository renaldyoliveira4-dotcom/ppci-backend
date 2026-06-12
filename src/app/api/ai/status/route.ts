import { NextResponse } from 'next/server'

export async function GET() {
  const apiKeySet = !!process.env.ANTHROPIC_API_KEY
  return NextResponse.json({
    ai_enabled: apiKeySet,
    api_key_configured: apiKeySet,
    sdk_installed: true,
    model_default: 'claude-sonnet-4-6',
  })
}
