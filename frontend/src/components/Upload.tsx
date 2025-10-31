import React, { useState } from 'react';
import { api } from '../api/client';

type UploadError = {
  message: string;
  hints: string[];
};

export default function Upload(){
  const [file, setFile] = useState<File|null>(null);
  const [res, setRes] = useState('');
  const [err, setErr] = useState<UploadError|null>(null);
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState<number|null>(null);

  const resetResult = () => {
    setRes('');
    setErr(null);
    setProgress(null);
  };

  const send = async ()=>{
    if(!file || loading) return;
    setLoading(true);
    setErr(null);
    setProgress(0);
    try {
      const fd = new FormData();
      fd.append('file', file);
      const { data } = await api.post('/ingest', fd, {
        headers: { 'Content-Type': 'multipart/form-data' },
        onUploadProgress: (evt) => {
          if (!evt) return;
          const total = evt.total ?? file.size;
          if (!total) return;
          const percent = Math.min(100, Math.round((evt.loaded / total) * 100));
          setProgress(percent);
        }
      });
      setProgress(100);
      setRes(JSON.stringify(data, null, 2));
    } catch (e:any){
      const status = e?.response?.status as number | undefined;
      const detail = e?.response?.data?.detail;
      const detailText = Array.isArray(detail) ? JSON.stringify(detail, null, 2) : detail;
      const baseMessage = status ? `Ошибка загрузки (HTTP ${status})` : 'Ошибка загрузки';
      const message = detailText ? `${baseMessage}: ${detailText}` : (e?.message || baseMessage);

      const hints: string[] = [];
      if (status === 400) {
        hints.push('Убедитесь, что файл не пустой и содержит текст в кодировке UTF-8.');
      }
      if (status === 413) {
        hints.push('Размер файла слишком большой. Разделите документ на части и попробуйте снова.');
      }
      if (status === 415) {
        hints.push('Проверьте формат файла. Поддерживаются текстовые форматы (TXT, MD, JSON и пр.).');
      }
      if (file && file.size > 10 * 1024 * 1024) {
        hints.push('Для больших файлов загрузка может занимать время — попробуйте уменьшить размер файла.');
      }
      if (!hints.length) {
        hints.push('Повторите попытку позже или проверьте лог-файлы сервера.');
      }

      setErr({ message, hints });
      setRes('');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-4">
      <div className="space-y-2">
        <input
          type="file"
          onChange={e=>{
            setFile(e.target.files?.[0] ?? null);
            resetResult();
          }}
        />
        {file && (
          <div className="text-sm text-slate-600">
            Выбран файл: <span className="font-medium">{file.name}</span>
          </div>
        )}
      </div>
      <button
        onClick={send}
        disabled={loading || !file}
        className={`px-4 py-2 rounded ${loading ? 'bg-slate-400' : 'bg-blue-600 hover:bg-blue-700'} text-white disabled:opacity-60`}
      >
        {loading ? 'Загружаю…' : 'Загрузить'}
      </button>

      {progress !== null && (
        <div>
          <div className="flex justify-between text-sm text-slate-600 mb-1">
            <span>Прогресс загрузки</span>
            <span>{progress}%</span>
          </div>
          <div className="h-2 w-full bg-slate-200 rounded">
            <div
              className="h-2 bg-blue-600 rounded"
              style={{ width: `${progress}%`, transition: 'width 0.2s ease-in-out' }}
            />
          </div>
        </div>
      )}

      {err && (
        <div className="bg-red-50 border border-red-200 text-red-700 rounded p-3 space-y-2">
          <div className="font-semibold">{err.message}</div>
          {err.hints.length > 0 && (
            <ul className="list-disc pl-5 space-y-1 text-sm text-red-600">
              {err.hints.map((hint, idx) => (
                <li key={idx}>{hint}</li>
              ))}
            </ul>
          )}
        </div>
      )}

      {res && (
        <pre className="bg-white p-3 rounded shadow text-sm whitespace-pre-wrap overflow-auto max-h-96">
          {res}
        </pre>
      )}
    </div>
  );
}
