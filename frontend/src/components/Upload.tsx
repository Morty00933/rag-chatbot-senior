import React, { useState } from 'react';
import { api } from '../api/client';

export default function Upload(){
  const [file, setFile] = useState<File|null>(null);
  const [res, setRes] = useState('');
  const [err, setErr] = useState<string|null>(null);
  const [loading, setLoading] = useState(false);

  const send = async ()=>{
    if(!file || loading) return;
    setLoading(true);
    setErr(null);
    try {
      const fd = new FormData();
      fd.append('file', file);
      const { data } = await api.post('/ingest', fd, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setRes(JSON.stringify(data, null, 2));
    } catch (e:any){
      const detail = e?.response?.data?.detail;
      setErr(Array.isArray(detail) ? JSON.stringify(detail) : detail || e?.message || 'Ошибка загрузки');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-3">
      <input
        type="file"
        onChange={e=>setFile(e.target.files?.[0] ?? null)}
      />
      <button
        onClick={send}
        disabled={loading || !file}
        className={`px-4 py-2 rounded ${loading ? 'bg-slate-400' : 'bg-blue-600 hover:bg-blue-700'} text-white`}
      >
        {loading ? 'Загружаю…' : 'Загрузить'}
      </button>
      {err && <div className="bg-red-50 border border-red-200 text-red-700 rounded p-3">{err}</div>}
      {res && <pre className="bg-white p-3 rounded shadow text-sm whitespace-pre-wrap">{res}</pre>}
    </div>
  );
}
