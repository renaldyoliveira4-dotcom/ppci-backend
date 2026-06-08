'use client'
import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { supabase } from '@/lib/supabase'
import { Flame } from 'lucide-react'

type Mode = 'login' | 'signup'

const ERR: Record<string, string> = {
  'Invalid login credentials': 'E-mail ou senha incorretos.',
  'User already registered': 'Este e-mail já está cadastrado. Faça login.',
  'Password should be at least 6 characters': 'A senha deve ter pelo menos 6 caracteres.',
  'Email not confirmed': 'Confirme seu e-mail antes de entrar.',
}

export default function LoginPage() {
  const router = useRouter()
  const [mode, setMode] = useState<Mode>('login')
  const [email, setEmail] = useState('')
  const [pass, setPass] = useState('')
  const [nome, setNome] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [msg, setMsg] = useState('')

  const handleSubmit = async () => {
    setError(''); setMsg('')
    if (!email || !pass) { setError('Preencha e-mail e senha.'); return }
    setLoading(true)
    try {
      if (mode === 'login') {
        const { error: err } = await supabase.auth.signInWithPassword({ email, password: pass })
        if (err) throw err
        router.push('/dashboard')
      } else {
        if (!nome) { setError('Informe seu nome completo.'); return }
        const { data, error: err } = await supabase.auth.signUp({
          email, password: pass, options: { data: { full_name: nome } }
        })
        if (err) throw err
        if (data.session) router.push('/dashboard')
        else { setMsg('Cadastro realizado! Verifique seu e-mail para confirmar a conta.'); setMode('login') }
      }
    } catch (e: unknown) {
      const message = e instanceof Error ? e.message : 'Erro desconhecido'
      setError(ERR[message] || message)
    } finally { setLoading(false) }
  }

  const handleForgotPassword = async () => {
    if (!email) { setError('Informe o e-mail para redefinir a senha.'); return }
    const { error: err } = await supabase.auth.resetPasswordForEmail(email)
    if (!err) setMsg('Link de redefinição enviado para ' + email)
    else setError(err.message)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl p-8 w-full max-w-md">
        <div className="flex items-center gap-3 mb-8 justify-center">
          <div className="w-11 h-11 rounded-xl bg-gradient-to-br from-orange-500 to-red-500 flex items-center justify-center">
            <Flame size={22} className="text-white" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-slate-800">PPCI SaaS</h1>
            <p className="text-[10px] text-slate-400 uppercase tracking-widest">Corpo de Bombeiros — Bahia</p>
          </div>
        </div>

        <h2 className="text-lg font-bold text-slate-800 text-center mb-6">
          {mode === 'login' ? 'Entrar na sua conta' : 'Criar sua conta grátis'}
        </h2>

        {error && <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700">{error}</div>}
        {msg && <div className="mb-4 p-3 bg-emerald-50 border border-emerald-200 rounded-lg text-sm text-emerald-700">{msg}</div>}

        <div className="space-y-4" onKeyDown={e => e.key === 'Enter' && handleSubmit()}>
          {mode === 'signup' && (
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Nome completo</label>
              <input value={nome} onChange={e => setNome(e.target.value)} placeholder="Seu nome e sobrenome"
                className="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-orange-400" />
            </div>
          )}
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">E-mail</label>
            <input type="email" value={email} onChange={e => setEmail(e.target.value)} placeholder="seu@email.com"
              className="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-orange-400" />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Senha</label>
            <input type="password" value={pass} onChange={e => setPass(e.target.value)} placeholder="Mínimo 6 caracteres"
              className="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-orange-400" />
          </div>
          <button onClick={handleSubmit} disabled={loading}
            className="w-full bg-gradient-to-r from-orange-500 to-red-500 text-white rounded-xl py-2.5 font-semibold hover:from-orange-600 hover:to-red-600 transition-all disabled:opacity-50">
            {loading ? 'Aguarde...' : mode === 'login' ? 'Entrar' : 'Criar conta'}
          </button>
        </div>

        {mode === 'login' && (
          <p className="text-center text-xs text-slate-400 mt-3">
            <button onClick={handleForgotPassword} className="text-orange-500 hover:underline">Esqueci minha senha</button>
          </p>
        )}

        <p className="text-center text-sm text-slate-500 mt-4">
          {mode === 'login' ? 'Não tem conta? ' : 'Já tem conta? '}
          <button onClick={() => { setMode(mode === 'login' ? 'signup' : 'login'); setError(''); setMsg('') }}
            className="text-orange-500 font-semibold hover:underline">
            {mode === 'login' ? 'Cadastre-se grátis' : 'Fazer login'}
          </button>
        </p>
        <p className="text-center text-[10px] text-slate-400 mt-4">Plano gratuito: até 3 projetos · Sem cartão necessário</p>
      </div>
    </div>
  )
}
