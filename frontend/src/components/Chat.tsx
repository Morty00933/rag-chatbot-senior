import React, { useState } from 'react'
import { api } from '../api/client'
import type { ChatResponse } from '../types'

export default function Chat() {
  const [q, setQ] = useState('')
  const [answer, setAnswer] = useState<string>('')
  const [refs, setRefs] = useState<ChatResponse['references']>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string>('')

  const ask = async () => {
    if (!q.trim()) return
    setLoading(true)
    setError('')
    setAnswer('')
    setRefs([])
    try {
      const { data } = await api.post<ChatResponse>('/chat', { question: q, top_k: 6 })
      setAnswer(data.answer ?? '')
      setRefs(data.references ?? [])
    } catch (e: any) {
      setError(e?.message || 'Ошибка запроса')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex gap-2">
        <input
          value={q}
          onChange={e=>setQ(e.target.value)}
          className="border px-3 py-2 flex-1 rounded"
          placeholder="Задайте вопрос..."
        />
        <button
          onClick={ask}
          disabled={loading}
          className="px-4 py-2 rounded bg-blue-600 text-white disabled:opacity-60"
        >
          {loading ? '...' : 'Спросить'}
        </button>
      </div>

      {/* Окно ответа ВСЕГДА видно */}
      <div className="bg-white rounded p-4 shadow min-h-[120px]">
        <div className="font-semibold mb-2">Ответ</div>
        {loading && <div className="text-slate-500">Мыслю…</div>}
        {!loading && error && <div className="text-red-600">{error}</div>}
        {!loading && !error && !answer && <div className="text-slate-400">Пока нет ответа.</div>}
        {!loading && !error && !!answer && (
          <div className="whitespace-pre-wrap">{answer}</div>
        )}
      </div>

      {/* Ссылки/референсы */}
      <div className="bg-white rounded p-4 shadow">
        <div className="font-semibold mb-2">Ссылки</div>
        {refs.length === 0
          ? <div className="text-slate-400">Пока пусто.</div>
          : (
            <ul className="list-disc pl-5 space-y-1">
              {refs.map((r,i)=> (
                <li key={i}>
                  <span className="text-slate-500">[{r.chunk_ord}]</span> {r.preview.slice(0,120)}...{' '}
                  <span className="text-slate-400">({r.score.toFixed(3)})</span>
                </li>
              ))}
            </ul>
          )
        }
      </div>
    </div>
  )
}
