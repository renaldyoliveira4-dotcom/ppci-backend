'use client'
import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { supabase, type Project, type Profile } from '@/lib/supabase'
import { Building, Plus, Calculator, Eye, Trash2, Zap, FolderOpen } from 'lucide-react'

const STATUS_BADGE: Record<string, string> = {
  em_andamento: 'bg-blue-100 text-blue-700',
  concluido: 'bg-emerald-100 text-emerald-700',
  arquivado: 'bg-slate-100 text-slate-500',
}
const STATUS_LABEL: Record<string, string> = {
  em_andamento: 'Em andamento', concluido: 'Concluído', arquivado: 'Arquivado',
}

export default function DashboardPage() {
  const router = useRouter()
  const [projects, setProjects] = useState<Project[]>([])
  const [profile, setProfile] = useState<Profile | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const load = async () => {
      const { data: { user } } = await supabase.auth.getUser()
      if (!user) return
      const [{ data: prof }, { data: projs }] = await Promise.all([
        supabase.from('profiles').select('*').eq('id', user.id).single(),
        supabase.from('projects').select('*').eq('user_id', user.id).order('updated_at', { ascending: false }),
      ])
      if (prof) setProfile(prof as Profile)
      if (projs) setProjects(projs as Project[])
      setLoading(false)
    }
    load()
  }, [])

  const handleDelete = async (id: string, nome: string) => {
    if (!confirm(`Excluir o projeto "${nome}"? Esta ação não pode ser desfeita.`)) return
    await supabase.from('projects').delete().eq('id', id)
    setProjects(prev => prev.filter(p => p.id !== id))
  }

  const plano = profile?.plan || 'free'
  const atLimite = plano === 'free' && projects.length >= 3

  if (loading) return (
    <div className="flex items-center justify-center h-64">
      <div className="text-slate-400 text-sm">Carregando projetos...</div>
    </div>
  )

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-800">Dashboard</h1>
          <p className="text-slate-500 text-sm mt-1">Visão geral dos seus projetos PPCI</p>
        </div>
        {!atLimite && (
          <Link href="/projetos/novo" className="flex items-center gap-2 bg-orange-500 hover:bg-orange-600 text-white px-4 py-2 rounded-xl text-sm font-semibold transition-colors">
            <Plus size={16} /> Novo Projeto
          </Link>
        )}
      </div>

      {/* Banner limite */}
      {atLimite && (
        <div className="p-4 bg-gradient-to-r from-orange-50 to-red-50 border border-orange-200 rounded-xl flex items-center justify-between gap-4 flex-wrap">
          <div className="flex items-center gap-3">
            <Zap size={20} className="text-orange-500 flex-shrink-0" />
            <div>
              <p className="text-sm font-semibold text-slate-800">Limite do plano gratuito atingido</p>
              <p className="text-xs text-slate-500">Faça upgrade para criar projetos ilimitados e exportar PDFs profissionais.</p>
            </div>
          </div>
          <Link href="/planos" className="flex items-center gap-1 bg-orange-500 text-white px-3 py-1.5 rounded-lg text-xs font-semibold hover:bg-orange-600 transition-colors flex-shrink-0">
            <Zap size={12} /> Ver planos
          </Link>
        </div>
      )}

      {/* Stats */}
      <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
        <div className="bg-white rounded-xl p-4 border border-slate-200">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-lg bg-blue-100 flex items-center justify-center">
              <Building size={18} className="text-blue-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-slate-800">{projects.length}</p>
              <p className="text-xs text-slate-500">Total de projetos</p>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-xl p-4 border border-slate-200">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-lg bg-emerald-100 flex items-center justify-center">
              <Calculator size={18} className="text-emerald-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-slate-800">{projects.filter(p => p.status === 'em_andamento').length}</p>
              <p className="text-xs text-slate-500">Em andamento</p>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-xl p-4 border border-slate-200 col-span-2 sm:col-span-1">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-lg bg-orange-100 flex items-center justify-center">
              <FolderOpen size={18} className="text-orange-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-slate-800">{projects.filter(p => p.status === 'concluido').length}</p>
              <p className="text-xs text-slate-500">Concluídos</p>
            </div>
          </div>
        </div>
      </div>

      {/* Tabela de projetos */}
      <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
        <div className="flex items-center justify-between px-5 py-4 border-b border-slate-200">
          <h2 className="text-base font-bold text-slate-800">Projetos Recentes</h2>
        </div>
        {projects.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-16 text-slate-400">
            <Building size={40} className="mb-3 opacity-30" />
            <p className="text-sm">Nenhum projeto ainda.</p>
            <Link href="/projetos/novo" className="mt-4 text-orange-500 text-sm font-medium hover:underline">Criar primeiro projeto</Link>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-slate-100">
                  {['Projeto', 'Divisão', 'Área (m²)', 'Status', ''].map(h => (
                    <th key={h} className="text-left text-xs font-semibold text-slate-500 uppercase tracking-wider px-5 py-3">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {projects.map(p => (
                  <tr key={p.id} className="border-b border-slate-50 hover:bg-slate-50 transition-colors">
                    <td className="px-5 py-3 font-medium text-slate-800">{p.nome}</td>
                    <td className="px-5 py-3 text-slate-500">{p.divisao}</td>
                    <td className="px-5 py-3 text-slate-500">{p.area.toLocaleString('pt-BR')}</td>
                    <td className="px-5 py-3">
                      <span className={`text-[11px] px-2 py-1 rounded-full font-semibold ${STATUS_BADGE[p.status]}`}>
                        {STATUS_LABEL[p.status]}
                      </span>
                    </td>
                    <td className="px-5 py-3">
                      <div className="flex items-center gap-1 justify-end">
                        <button onClick={() => router.push(`/calculos?projeto=${p.id}`)}
                          className="p-1.5 rounded-lg hover:bg-orange-50 text-slate-400 hover:text-orange-500 transition-colors" title="Calcular">
                          <Calculator size={15} />
                        </button>
                        <button className="p-1.5 rounded-lg hover:bg-blue-50 text-slate-400 hover:text-blue-500 transition-colors" title="Revisar">
                          <Eye size={15} />
                        </button>
                        <button onClick={() => handleDelete(p.id, p.nome)}
                          className="p-1.5 rounded-lg hover:bg-red-50 text-slate-400 hover:text-red-500 transition-colors" title="Excluir">
                          <Trash2 size={15} />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}
