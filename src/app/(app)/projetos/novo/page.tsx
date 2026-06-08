'use client'
import { useState, useMemo } from 'react'
import { useRouter } from 'next/navigation'
import { supabase } from '@/lib/supabase'
import { GRUPOS, POP_M2, CARGA } from '@/lib/normas'
import { ArrowLeft, ArrowRight, Check } from 'lucide-react'

type F = {
  nome: string; endereco: string; area: string; pavimentos: string
  altura: string; grupo: string; divisao: string; populacao: string
  carga_incendio: string; subterraneo: boolean
}

export default function NovoProjetoPage() {
  const router = useRouter()
  const [step, setStep] = useState(0)
  const [saving, setSaving] = useState(false)
  const [saveErr, setSaveErr] = useState('')
  const [f, setF] = useState<F>({
    nome: '', endereco: '', area: '', pavimentos: '1', altura: '3',
    grupo: '', divisao: '', populacao: '', carga_incendio: '', subterraneo: false,
  })
  const [errors, setErrors] = useState<Partial<F>>({})

  const set = (k: keyof F, v: string | boolean) => {
    setF(p => ({ ...p, [k]: v }))
    setErrors(p => { const n = { ...p }; delete n[k]; return n })
  }

  const grupoData = GRUPOS[f.grupo]
  const divOpts = grupoData ? Object.entries(grupoData.divisoes).map(([k, v]) => ({ value: k, label: `${k} — ${v}` })) : []

  const calcPop = useMemo(() =>
    f.divisao && f.area ? Math.ceil(Number(f.area) * (POP_M2[f.divisao] || 0.1)) : 0,
    [f.divisao, f.area])

  const calcCarga = useMemo(() =>
    f.divisao ? (CARGA[f.divisao] || 300) : 0, [f.divisao])

  const validate = (s: number) => {
    const e: Partial<F> = {}
    if (s === 0) {
      if (!f.nome) e.nome = 'Obrigatório'
      if (!f.area || Number(f.area) <= 0) e.area = 'Informe a área'
    }
    if (s === 1) {
      if (!f.grupo) e.grupo = 'Selecione o grupo'
      if (!f.divisao) e.divisao = 'Selecione a divisão'
    }
    setErrors(e)
    return Object.keys(e).length === 0
  }

  const criar = async () => {
    setSaveErr(''); setSaving(true)
    try {
      const { data: { user } } = await supabase.auth.getUser()
      if (!user) throw new Error('Sessão expirada. Faça login novamente.')

      const { data: prof } = await supabase.from('profiles').select('plan').eq('id', user.id).single()
      if (prof?.plan === 'free') {
        const { count } = await supabase.from('projects').select('*', { count: 'exact', head: true }).eq('user_id', user.id)
        if ((count || 0) >= 3) throw new Error('Limite do plano gratuito: 3 projetos. Faça upgrade para o Plano Pro.')
      }

      const { error } = await supabase.from('projects').insert({
        user_id: user.id,
        nome: f.nome, endereco: f.endereco || null, divisao: f.divisao,
        area: Number(f.area), pavimentos: Number(f.pavimentos) || 1,
        altura: Number(f.altura) || 3, subterraneo: f.subterraneo,
        populacao: Number(f.populacao) || calcPop || null,
        carga_incendio: Number(f.carga_incendio) || calcCarga || null,
        status: 'em_andamento',
      })
      if (error) throw error
      router.push('/dashboard')
    } catch (e: unknown) {
      setSaveErr(e instanceof Error ? e.message : 'Erro ao salvar.')
    } finally { setSaving(false) }
  }

  const inputClass = (err?: string) =>
    `w-full border ${err ? 'border-red-400' : 'border-slate-200'} rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-orange-400`

  const steps = ['Dados Gerais', 'Ocupação', 'Revisão']

  return (
    <div className="max-w-2xl space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-800">Novo Projeto PPCI</h1>
        <p className="text-slate-500 text-sm mt-1">Preencha os dados para classificação automática</p>
      </div>

      {/* Steps */}
      <div className="flex items-center gap-2">
        {steps.map((s, i) => (
          <div key={i} className="flex items-center gap-2">
            <div className={`w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold ${i <= step ? 'bg-orange-500 text-white' : 'bg-slate-200 text-slate-500'}`}>
              {i < step ? <Check size={12} /> : i + 1}
            </div>
            <span className={`text-sm ${i === step ? 'font-semibold text-slate-800' : 'text-slate-400'}`}>{s}</span>
            {i < steps.length - 1 && <div className={`w-8 h-0.5 ${i < step ? 'bg-orange-400' : 'bg-slate-200'}`} />}
          </div>
        ))}
      </div>

      <div className="bg-white rounded-xl border border-slate-200 p-6">
        {/* Step 0: Dados Gerais */}
        {step === 0 && (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Nome do Projeto *</label>
              <input value={f.nome} onChange={e => set('nome', e.target.value)} placeholder="Ex: Ed. Comercial Salvador Center"
                className={inputClass(errors.nome)} />
              {errors.nome && <p className="text-xs text-red-500 mt-1">{errors.nome}</p>}
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Endereço</label>
              <input value={f.endereco} onChange={e => set('endereco', e.target.value)} placeholder="Rua, número, bairro, cidade"
                className={inputClass()} />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Área construída (m²) *</label>
                <input type="number" value={f.area} onChange={e => set('area', e.target.value)}
                  className={inputClass(errors.area)} />
                {errors.area && <p className="text-xs text-red-500 mt-1">{errors.area}</p>}
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Nº de pavimentos</label>
                <input type="number" min="1" value={f.pavimentos} onChange={e => set('pavimentos', e.target.value)}
                  className={inputClass()} />
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Altura (m)</label>
                <input type="number" value={f.altura} onChange={e => set('altura', e.target.value)}
                  className={inputClass()} />
              </div>
              <div className="flex items-end pb-2">
                <label className="flex items-center gap-2 cursor-pointer">
                  <input type="checkbox" checked={f.subterraneo} onChange={e => set('subterraneo', e.target.checked)}
                    className="w-4 h-4 accent-orange-500" />
                  <span className="text-sm text-slate-700">Possui subsolo</span>
                </label>
              </div>
            </div>
          </div>
        )}

        {/* Step 1: Ocupação */}
        {step === 1 && (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Grupo de Ocupação *</label>
              <select value={f.grupo} onChange={e => { set('grupo', e.target.value); set('divisao', '') }}
                className={inputClass(errors.grupo)}>
                <option value="">Selecione o grupo...</option>
                {Object.entries(GRUPOS).map(([k, v]) => (
                  <option key={k} value={k}>{k} — {v.nome}</option>
                ))}
              </select>
              {errors.grupo && <p className="text-xs text-red-500 mt-1">{errors.grupo}</p>}
            </div>
            {divOpts.length > 0 && (
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Divisão / Ocupação Específica *</label>
                <select value={f.divisao} onChange={e => set('divisao', e.target.value)}
                  className={inputClass(errors.divisao)}>
                  <option value="">Selecione a divisão...</option>
                  {divOpts.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
                </select>
                {errors.divisao && <p className="text-xs text-red-500 mt-1">{errors.divisao}</p>}
              </div>
            )}
            {f.divisao && (
              <div className="grid grid-cols-2 gap-4 p-3 bg-slate-50 rounded-lg">
                <div>
                  <p className="text-xs text-slate-500">População estimada</p>
                  <p className="font-semibold text-slate-800">{calcPop} pessoas</p>
                  <input type="number" value={f.populacao} onChange={e => set('populacao', e.target.value)}
                    placeholder="Ajustar..." className="mt-1 text-xs border border-slate-200 rounded px-2 py-1 w-full" />
                </div>
                <div>
                  <p className="text-xs text-slate-500">Carga de incêndio</p>
                  <p className="font-semibold text-slate-800">{calcCarga} MJ/m²</p>
                  <input type="number" value={f.carga_incendio} onChange={e => set('carga_incendio', e.target.value)}
                    placeholder="Ajustar..." className="mt-1 text-xs border border-slate-200 rounded px-2 py-1 w-full" />
                </div>
              </div>
            )}
          </div>
        )}

        {/* Step 2: Revisão */}
        {step === 2 && (
          <div className="space-y-3">
            <h3 className="font-semibold text-slate-800 mb-3">Confirme os dados do projeto</h3>
            {[
              ['Nome', f.nome],
              ['Endereço', f.endereco || '—'],
              ['Área', `${Number(f.area).toLocaleString('pt-BR')} m²`],
              ['Pavimentos', f.pavimentos],
              ['Altura', `${f.altura} m`],
              ['Subsolo', f.subterraneo ? 'Sim' : 'Não'],
              ['Grupo', f.grupo ? `${f.grupo} — ${GRUPOS[f.grupo]?.nome}` : '—'],
              ['Divisão', f.divisao || '—'],
              ['População', `${Number(f.populacao) || calcPop} pessoas`],
              ['Carga de incêndio', `${Number(f.carga_incendio) || calcCarga} MJ/m²`],
            ].map(([k, v]) => (
              <div key={k as string} className="flex justify-between py-1.5 border-b border-slate-100 text-sm">
                <span className="text-slate-500">{k}</span>
                <span className="font-medium text-slate-800">{v}</span>
              </div>
            ))}
          </div>
        )}

        {saveErr && <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700">{saveErr}</div>}

        {/* Navigation */}
        <div className="flex justify-between mt-8 pt-5 border-t border-slate-200">
          {step > 0
            ? <button onClick={() => setStep(s => s - 1)} disabled={saving}
                className="flex items-center gap-2 px-4 py-2 border border-slate-200 rounded-xl text-sm font-medium hover:bg-slate-50 transition-colors">
                <ArrowLeft size={14} /> Anterior
              </button>
            : <div />}
          {step < 2
            ? <button onClick={() => validate(step) && setStep(s => s + 1)}
                className="flex items-center gap-2 bg-orange-500 text-white px-4 py-2 rounded-xl text-sm font-semibold hover:bg-orange-600 transition-colors">
                Próximo <ArrowRight size={14} />
              </button>
            : <button onClick={criar} disabled={saving}
                className="flex items-center gap-2 bg-emerald-500 text-white px-4 py-2 rounded-xl text-sm font-semibold hover:bg-emerald-600 transition-colors disabled:opacity-50">
                {saving ? 'Salvando...' : <><Check size={14} /> Criar e Calcular</>}
              </button>}
        </div>
      </div>
    </div>
  )
}
