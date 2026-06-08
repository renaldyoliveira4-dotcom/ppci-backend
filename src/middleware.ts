import { NextResponse, type NextRequest } from 'next/server'

export async function middleware(request: NextRequest) {
  // Deixa o HTML passar livremente — ele já tem auth própria via Supabase
  return NextResponse.next()
}

export const config = {
  matcher: ['/((?!_next/static|_next/image|favicon.ico|api|.*\\.html).*)'],
}
