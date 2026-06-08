import { createBrowserClient } from '@supabase/ssr'

export const supabase = createBrowserClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
)

export type Profile = {
  id: string
  full_name: string | null
  company_name: string | null
  crea_cau: string | null
  phone: string | null
  plan: 'free' | 'pro' | 'escritorio'
  plan_expires_at: string | null
  projects_count: number
  created_at: string
  updated_at: string
}

export type Project = {
  id: string
  user_id: string
  nome: string
  endereco: string | null
  divisao: string
  area: number
  pavimentos: number
  altura: number
  subterraneo: boolean
  populacao: number | null
  carga_incendio: number | null
  sistemas: string[]
  calculos: Record<string, unknown>
  status: 'em_andamento' | 'concluido' | 'arquivado'
  created_at: string
  updated_at: string
}
