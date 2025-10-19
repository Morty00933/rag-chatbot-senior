import React, { useState } from 'react';
import Chat from './components/Chat';
import Upload from './components/Upload';

export default function App() {
  const [tab, setTab] = useState<'chat'|'upload'>('chat');
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
      {tab==='chat' ? <Chat/> : <Upload/>}
    </div>
  );
}
