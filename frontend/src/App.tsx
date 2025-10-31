import React, { useEffect, useState } from 'react';
import Chat from './components/Chat';
import Upload from './components/Upload';

export default function App() {
  const [tab, setTab] = useState<'chat'|'upload'>(() => {
    if (typeof window === 'undefined') {
      return 'chat';
    }
    const stored = window.localStorage.getItem('rag-ui-tab');
    return stored === 'upload' ? 'upload' : 'chat';
  });

  useEffect(() => {
    if (typeof window !== 'undefined') {
      window.localStorage.setItem('rag-ui-tab', tab);
    }
  }, [tab]);

  return (
    <div className="max-w-4xl mx-auto p-6">
      <h1 className="text-2xl font-bold mb-4">RAG Chatbot</h1>
      <div className="flex gap-2 mb-6">
        <button
          className={`px-3 py-1 rounded ${tab==='chat'?'bg-blue-600 text-white':'bg-slate-200'}`}
          onClick={()=>setTab('chat')}
        >
          Chat
        </button>
        <button
          className={`px-3 py-1 rounded ${tab==='upload'?'bg-blue-600 text-white':'bg-slate-200'}`}
          onClick={()=>setTab('upload')}
        >
          Upload
        </button>
      </div>
      <div className={tab === 'chat' ? '' : 'hidden'}>
        <Chat/>
      </div>
      <div className={tab === 'upload' ? '' : 'hidden'}>
        <Upload/>
      </div>
    </div>
  );
}
