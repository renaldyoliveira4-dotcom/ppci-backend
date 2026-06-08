'use client'
import { useEffect, useState } from 'react'
import { useRouter, usePathname } from 'next/navigation'
import Link from 'next/link'
import { supabase, type Profile } from '@/lib/supabase'
import {
  Flame, LayoutDashboard, FolderPlus, Scan, Calculator, FileText,
  Download, Zap, ChevronLeft, ChevronRight, LogOut, Menu, X
} from 'lucide-react'

const NAV = [
  { href: '/dashboard', label: 'Dashboard', icon: LayoutDashboard, grupo: 'main' },
  { href: '/projetos/novo', label: 'Novo Projeto', icon: FolderPlus, grupo: 'main' },
  { href: '/analise-planta', label: 'Análise de Planta', icon: Scan, grupo: 'main' },
  { href: '/calculos', label: 'Cálculos', icon: Calculator, grupo: 'proj' },
  { href: '/exportar', label: 'Exportar PDF', icon: Download, grupo: 'proj' },
  { href: '/planos', label: 'Planos & Upgrade', icon: Zap, grupo: 'extra' },
]

const PLAN_BADGE: Record<string, string> = {
  free: 'bg-slate-100 text-slate-600',
  pro: 'bg-orange-100 text-orange-700',
  escritorio: 'bg-violet-100 text-violet-700',
}
const PLAN_LABEL: Record<string, string> = { free: 'Grátis', pro: 'Pro', escritorio: 'Escritório' }

export default function AppLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter()
  const pathname = usePathname()
  const [profile, setProfile] = useState<Profile | null>(null)
  const [collapsed, setCollapsed] = useState(false)
  const [mobOpen, setMobOpen] = useState(false)

  useEffect(() => {
    supabase.auth.getUser().then(({ data: { user } }) => {
      if (!user) { router.push('/login'); return }
      supabase.from('profiles').select('*').eq('id', user.id).single()
        .then(({ data }) => { if (data) setProfile(data as Profile) })
    })
  }, [router])

  const handleLogout = async () => {
    await supabase.auth.signOut()
    router.push('/login')
  }

  const plano = profile?.plan || 'free'

  const SidebarContent = () => (
    <div className="flex flex-col h-full bg-slate-900 text-white">
      {/* Logo */}
      <div className={`flex items-center gap-3 px-4 py-4 border-b border-slate-700/50 ${collapsed ? 'justify-center' : ''}`}>
        <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-orange-500 to-red-500 flex items-center justify-center flex-shrink-0">
          <Flame size={16} className="text-white" />
        </div>
        {!collapsed && <span className="font-bold text-sm">PPCI SaaS</span>}
      </div>

      {/* Nav */}
      <nav className="flex-1 p-3 space-y-1 overflow-y-auto">
        {NAV.map(({ href, label, icon: Icon }) => {
          const active = pathname === href || pathname.startsWith(href + '/')
          return (
            <Link key={href} href={href} onClick={() => setMobOpen(false)}
              className={`flex items-center gap-3 px-3 py-2 rounded-xl text-sm transition-all ${active ? 'bg-orange-500/20 text-orange-400' : 'text-slate-400 hover:bg-slate-800 hover:text-white'} ${collapsed ? 'justify-center' : ''}`}
              title={collapsed ? label : undefined}>
              <Icon size={18} className="flex-shrink-0" />
              {!collapsed && <span>{label}</span>}
            </Link>
          )
        })}
      </nav>

      {/* Footer: usuário + logout */}
      {!collapsed && profile && (
        <div className="px-4 py-3 border-t border-slate-700/50">
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-full bg-orange-500/20 flex items-center justify-center flex-shrink-0">
              <span className="text-orange-400 text-[10px] font-bold">
                {(profile.full_name || 'U')[0].toUpperCase()}
              </span>
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-[11px] text-slate-300 truncate">{profile.full_name || profile.id}</p>
              <span className={`text-[9px] px-1.5 py-0.5 rounded font-semibold ${PLAN_BADGE[plano]}`}>{PLAN_LABEL[plano]}</span>
            </div>
            <button onClick={handleLogout} title="Sair" className="text-slate-500 hover:text-red-400 transition-colors p-1">
              <LogOut size={14} />
            </button>
          </div>
        </div>
      )}

      {/* Collapse button (desktop) */}
      <button onClick={() => setCollapsed(!collapsed)}
        className="hidden lg:flex items-center justify-center w-full py-2 border-t border-slate-700/50 text-slate-500 hover:text-white transition-colors">
        {collapsed ? <ChevronRight size={16} /> : <ChevronLeft size={16} />}
      </button>
    </div>
  )

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Mobile header */}
      <div className="lg:hidden fixed top-0 left-0 right-0 h-14 bg-white border-b border-slate-200 flex items-center px-4 z-50 gap-3">
        <button onClick={() => setMobOpen(!mobOpen)} className="p-2 rounded-lg hover:bg-slate-100">
          {mobOpen ? <X size={20} /> : <Menu size={20} />}
        </button>
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-orange-500 to-red-500 flex items-center justify-center">
            <Flame size={14} className="text-white" />
          </div>
          <span className="font-bold text-sm text-slate-800">PPCI SaaS</span>
        </div>
        {profile && (
          <div className="ml-auto flex items-center gap-2">
            <span className={`text-[10px] px-2 py-0.5 rounded-full font-semibold ${PLAN_BADGE[plano]}`}>{PLAN_LABEL[plano]}</span>
            <button onClick={handleLogout} className="text-xs text-slate-500 hover:text-red-500 px-2 py-1 rounded hover:bg-red-50 transition-colors">Sair</button>
          </div>
        )}
      </div>

      {/* Mobile overlay */}
      {mobOpen && <div className="lg:hidden fixed inset-0 bg-black/50 z-40" onClick={() => setMobOpen(false)} />}
      {/* Mobile sidebar */}
      {mobOpen && (
        <div className="lg:hidden fixed left-0 top-0 h-full w-64 z-50">
          <SidebarContent />
        </div>
      )}

      {/* Desktop sidebar */}
      <div className={`hidden lg:block fixed top-0 left-0 h-full z-40 transition-all duration-300 ${collapsed ? 'w-[68px]' : 'w-64'}`}>
        <SidebarContent />
      </div>

      {/* Main content */}
      <main className={`transition-all duration-300 pt-14 lg:pt-0 ${collapsed ? 'lg:ml-[68px]' : 'lg:ml-64'}`}>
        <div className="p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto">
          {children}
        </div>
      </main>
    </div>
  )
}
