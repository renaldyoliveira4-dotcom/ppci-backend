import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'PPCI SaaS — Dimensionamento CBMBA',
  description: 'Plataforma de dimensionamento de projetos PPCI conforme as Instruções Técnicas do CBMBA',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="pt-BR">
      <body>{children}</body>
    </html>
  )
}
