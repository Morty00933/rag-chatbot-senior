import React, { useEffect, useMemo, useState } from 'react'
import { api } from '../api/client'
import type { ChatResponse } from '../types'

type ConversationEntry = {
  id: string
  question: string
  answer: string
  references: ChatResponse['references']
  status: 'pending' | 'success' | 'error'
  errorMessage?: string
}

const HISTORY_KEY = 'rag-ui-chat-history'

const loadHistory = (): ConversationEntry[] => {
  if (typeof window === 'undefined') {
    return []
  }
  try {
    const stored = window.localStorage.getItem(HISTORY_KEY)
    if (!stored) return []
    const parsed = JSON.parse(stored)
    if (!Array.isArray(parsed)) return []
    return parsed.map((item) => ({
      ...item,
      references: item.references ?? []
    })) as ConversationEntry[]
  } catch (error) {
    console.warn('Не удалось восстановить историю чата', error)
    return []
  }
}

const persistHistory = (history: ConversationEntry[]) => {
  if (typeof window === 'undefined') return
  try {
    window.localStorage.setItem(HISTORY_KEY, JSON.stringify(history))
  } catch (error) {
    console.warn('Не удалось сохранить историю чата', error)
  }
}

export default function Chat() {
  const [q, setQ] = useState('')
  const [loading, setLoading] = useState(false)
  const [history, setHistory] = useState<ConversationEntry[]>(() => loadHistory())

  useEffect(() => {
    persistHistory(history)
  }, [history])

  const ask = async () => {
    if (!q.trim() || loading) return
    const question = q.trim()
    setLoading(true)
    const entryId = `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`
    setHistory(prev => ([
      ...prev,
      {
        id: entryId,
        question,
        answer: '',
        references: [],
        status: 'pending'
      }
    ]))
    setQ('')
    try {
      const { data } = await api.post<ChatResponse>('/chat', { question, top_k: 6 })
      setHistory(prev => prev.map(item => item.id === entryId ? {
        ...item,
        answer: data.answer ?? '',
        references: data.references ?? [],
        status: 'success'
      } : item))
    } catch (e: any) {
      const message = e?.response?.data?.detail || e?.message || 'Ошибка запроса'
      setHistory(prev => prev.map(item => item.id === entryId ? {
        ...item,
        status: 'error',
        errorMessage: message
      } : item))
    } finally {
      setLoading(false)
    }
  }

  const hasHistory = history.length > 0
  const lastEntry = useMemo(() => history[history.length - 1], [history])

  return (
    <div className="space-y-6">
      <div className="flex gap-2">
        <input
          value={q}
          onChange={e=>setQ(e.target.value)}
          className="border px-3 py-2 flex-1 rounded"
          placeholder="Задайте вопрос..."
          onKeyDown={e => {
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault()
              ask()
            }
          }}
        />
        <button
          onClick={ask}
          disabled={loading}
          className="px-4 py-2 rounded bg-blue-600 text-white disabled:opacity-60"
        >
          {loading ? '...' : 'Спросить'}
        </button>
      </div>

      {!hasHistory && (
        <div className="bg-white rounded p-6 shadow text-slate-500">
          Задайте вопрос, чтобы начать диалог. История сообщений появится ниже.
        </div>
      )}

      {hasHistory && (
        <div className="space-y-4">
          {history.map(entry => (
            <div key={entry.id} className="bg-white rounded shadow">
              <div className="border-b border-slate-100 px-4 py-3">
                <div className="text-xs uppercase tracking-wide text-slate-400">Вы</div>
                <div className="text-slate-800 whitespace-pre-wrap">{entry.question}</div>
              </div>
              <div className="px-4 py-3 space-y-3">
                <div className="text-xs uppercase tracking-wide text-slate-400">Бот</div>
                {entry.status === 'pending' && (
                  <div className="text-slate-500">Мыслю…</div>
                )}
                {entry.status === 'error' && (
                  <div className="text-red-600">{entry.errorMessage}</div>
                )}
                {entry.status === 'success' && (
                  <div className="whitespace-pre-wrap text-slate-800">{entry.answer || 'Ответ пустой.'}</div>
                )}

                {entry.references && entry.references.length > 0 && (
                  <div className="bg-slate-50 rounded p-3">
                    <div className="font-medium text-sm text-slate-600 mb-2">Ссылки</div>
                    <ul className="list-disc pl-5 space-y-1 text-sm text-slate-600">
                      {entry.references.map((r, i) => (
                        <li key={`${entry.id}-${i}`}>
                          <span className="text-slate-500">[{r.chunk_ord}]</span> {r.preview.slice(0, 160)}...{' '}
                          <span className="text-slate-400">({r.score.toFixed(3)})</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {lastEntry?.status === 'error' && (
        <div className="text-sm text-red-600">
          Последний запрос завершился с ошибкой. Проверьте сообщение выше.
        </div>
      )}
    </div>
  )
}
