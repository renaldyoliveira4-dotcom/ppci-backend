'use client'
import { useEffect, useState } from 'react'
import { supabase, type Profile } from '@/lib/supabase'
import { Check, Zap, Info } from 'lucide-react'

const PLANOS = [
  {
    id: 'free', nome: 'Gratuito', preco: 'R$ 0', periodo: '/sempre',
    itens: ['Até 3 projetos', 'Todos os calculadores', 'Consulta ITs CBMBA', 'Dashboard básico', 'Sem exportação PDF'],
    link: null,
  },
  {
    id: 'pro', nome: 'Profissional', preco: 'R$ 99', periodo: '/mês', destaque: true,
    itens: ['Projetos ilimitados', 'Todos os calculadores', 'Exportação PDF completa', 'Análise de planta com IA', 'Suporte por e-mail'],
    link: 'https://pagar.me/', // Substituir pelo link real do Pagar.me
  },
  {
    id: 'escritorio', nome: 'Escritório', preco: 'R$ 279', periodo: '/mês',
    itens: ['Tudo do Pro', 'Até 5 usuários', 'Logo do escritório no PDF', 'Projetos compartilhados', 'Suporte prioritário'],
    link: 'https://pagar.me/', // Substituir pelo link real do Pagar.me
  },
]

export default function PlanosPage() {
  const [profile, setProfile] = useState<Profile | null>(null)
  const [msg, setMsg] = useState('')

  useEffect(() => {
    supabase.auth.getUser().then(({ data: { user } }) => {
      if (!user) return
      supabase.from('profiles').select('*').eq('id', user.id).single()
        .then(({ data }) => { if (data) setProfile(data as Profile) })
    })

    const upgraded = new URLSearchParams(window.location.search).get('upgraded')
    if (upgraded && ['pro', 'escritorio'].includes(upgraded)) {
      setMsg(`Pagamento confirmado! Plano atualizado para ${upgraded === 'pro' ? 'Pro' : 'Escritório'}.`)
      supabase.auth.getUser().then(({ data: { user } }) => {
        if (user) supabase.from('profiles').update({ plan: upgraded }).eq('id', user.id).then(() => {
          setProfile(p => p ? { ...p, plan: upgraded as 'pro' | 'escritorio' } : p)
        })
      })
      window.history.replaceState({}, '', window.location.pathname)
    }
  }, [])

  const plano = profile?.plan || 'free'

  return (
    <div className="max-w-5xl space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-slate-800">Planos & Upgrade</h1>
        <p className="text-slate-500 text-sm mt-1">Plano atual: <strong>{plano === 'free' ? 'Gratuito' : plano === 'pro' ? 'Profissional' : 'Escritório'}</strong></p>
      </div>

      {msg && (
        <div className="p-4 bg-emerald-50 border border-emerald-200 rounded-xl flex items-center gap-2 text-sm text-emerald-800">
          <Check size={16} className="text-emerald-600 flex-shrink-0" /> {msg}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        {PLANOS.map(pl => {
          const atual = plano === pl.id
          return (
            <div key={pl.id} className={`relative rounded-2xl border-2 p-6 flex flex-col ${pl.destaque ? 'border-orange-400 shadow-lg' : 'border-slate-200'} ${atual ? 'ring-2 ring-offset-2 ring-orange-300' : ''}`}>
              {pl.destaque && (
                <div className="absolute -top-3.5 left-1/2 -translate-x-1/2 bg-gradient-to-r from-orange-500 to-red-500 text-white text-[10px] font-bold px-4 py-1 rounded-full uppercase tracking-wider">
                  Mais popular
                </div>
              )}
              <div className="mb-5">
                <h3 className="font-bold text-slate-800 text-lg">{pl.nome}</h3>
                <div className="flex items-baseline gap-1 mt-2">
                  <span className="text-3xl font-bold text-slate-900">{pl.preco}</span>
                  <span className="text-slate-500 text-sm">{pl.periodo}</span>
                </div>
              </div>
              <ul className="space-y-2.5 flex-1 mb-6">
                {pl.itens.map((it, i) => (
                  <li key={i} className="flex items-start gap-2 text-sm">
                    <Check size={14} className={`mt-0.5 flex-shrink-0 ${it.startsWith('Sem ') ? 'text-slate-300' : 'text-emerald-500'}`} />
                    <span className={it.startsWith('Sem ') ? 'text-slate-400 line-through' : 'text-slate-700'}>{it}</span>
                  </li>
                ))}
              </ul>
              <button
                disabled={atual || !pl.link}
                onClick={() => {
                  if (!pl.link || atual) return
                  const ret = `${window.location.origin}/planos?upgraded=${pl.id}`
                  window.open(`${pl.link}?redirect_url=${encodeURIComponent(ret)}`, '_blank')
                }}
                className={`w-full py-2.5 rounded-xl text-sm font-semibold transition-all ${atual ? 'bg-slate-100 text-slate-400 cursor-default' : pl.destaque ? 'bg-gradient-to-r from-orange-500 to-red-500 text-white hover:from-orange-600 hover:to-red-600' : 'bg-slate-800 text-white hover:bg-slate-900'}`}>
                {atual ? 'Plano atual' : 'Assinar agora'}
              </button>
              {!atual && pl.link && (
                <p className="text-[10px] text-slate-400 text-center mt-2">Cobrado mensalmente · Cancele quando quiser</p>
              )}
            </div>
          )
        })}
      </div>

      <div className="p-5 border border-amber-200 bg-amber-50/40 rounded-xl">
        <div className="flex gap-3 items-start">
          <Info size={18} className="text-amber-600 flex-shrink-0 mt-0.5" />
          <div>
            <p className="text-sm font-semibold text-slate-700 mb-1">Como configurar o checkout Pagar.me</p>
            <ol className="text-xs text-slate-600 space-y-1 list-decimal ml-4">
              <li>Crie uma conta em <strong>pagar.me</strong> e acesse o painel.</li>
              <li>Crie um <strong>Plano de Assinatura</strong> para cada plano com os valores acima.</li>
              <li>Substitua o valor de <code className="bg-slate-100 px-1 rounded">link</code> nos planos nesta página.</li>
              <li>Após o pagamento o cliente é redirecionado e o plano é atualizado automaticamente.</li>
            </ol>
          </div>
        </div>
      </div>
    </div>
  )
}
