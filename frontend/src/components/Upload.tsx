import React, { useState } from 'react';
import { api } from '../api/client';

export default function Upload(){
  const [files, setFiles] = useState<FileList|null>(null);
  const [res, setRes] = useState('');
  const [err, setErr] = useState<string|null>(null);
  const [loading, setLoading] = useState(false);

  const send = async ()=>{
    if(!files || files.length===0 || loading) return;
    setLoading(true);
    setErr(null);
    try {
      const fd = new FormData();
      Array.from(files).forEach(f=>fd.append('files', f));
      const { data } = await api.post('/ingest', fd, { headers: { 'Content-Type': 'multipart/form-data' }});
      setRes(JSON.stringify(data, null, 2));
    } catch (e:any){
      setErr(e?.response?.data?.detail || e?.message || 'Ошибка загрузки');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-3">
      <input type="file" multiple onChange={e=>setFiles(e.target.files)} />
      <button
        onClick={send}
        disabled={loading || !files || files.length===0}
        className={`px-4 py-2 rounded ${loading ? 'bg-slate-400' : 'bg-blue-600 hover:bg-blue-700'} text-white`}
      >
        {loading ? 'Загружаю…' : 'Загрузить'}
      </button>
      {err && <div className="bg-red-50 border border-red-200 text-red-700 rounded p-3">{err}</div>}
      {res && <pre className="bg-white p-3 rounded shadow text-sm whitespace-pre-wrap">{res}</pre>}
    </div>
  );
}
