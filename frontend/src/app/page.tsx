'use client';

import { useState, useRef, useEffect } from 'react';

type Message = {
  role: 'user' | 'bot';
  content: string;
  citations?: string[];
};

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'bot',
      content:
        'Hello! I am your NCERT Doubt Solver. Select your Class and Subject, then ask me anything!',
    },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [classLevel, setClassLevel] = useState<number>(6);
  const [subject, setSubject] = useState<string>('Science');

  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMsg: Message = { role: 'user', content: input };
    setMessages((prev) => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      // ✅ CORRECT BACKEND URL
      const API_URL = 'https://ncert-rag-service.onrender.com';

      // ✅ CORRECT ENDPOINT: /rag/query
      const res = await fetch(`${API_URL}/rag/query`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: userMsg.content,
          class: classLevel,
          subject: subject,
        }),
      });

      if (!res.ok) {
        throw new Error(`Request failed with status ${res.status}`);
      }

      const data = await res.json();

      const botMsg: Message = {
        role: 'bot',
        content: data.answer || 'No answer received.',
        citations: data.citations || [],
      };

      setMessages((prev) => [...prev, botMsg]);
    } catch (error) {
      console.error(error);
      setMessages((prev) => [
        ...prev,
        {
          role: 'bot',
          content:
            'Sorry, I encountered an error connecting to the server. Please try again.',
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <main className="flex min-h-screen flex-col bg-slate-50 text-slate-900">
      {/* Header */}
      <header className="bg-blue-700 text-white p-4 shadow-md">
        <div className="max-w-4xl mx-auto flex items-center justify-between">
          <h1 className="text-2xl font-bold flex items-center gap-2">
            📚 NCERT Doubt Solver
            <span className="text-xs bg-blue-500 px-2 py-1 rounded">
              AI Powered
            </span>
          </h1>
          <div className="text-sm opacity-80">v2.0 (Productized)</div>
        </div>
      </header>

      {/* Settings Bar */}
      <div className="bg-white border-b border-slate-200 p-4 sticky top-0 z-10">
        <div className="max-w-4xl mx-auto flex flex-wrap gap-4 items-center justify-center sm:justify-start">
          <div className="flex items-center gap-2">
            <label className="text-sm font-semibold text-slate-600">
              Class:
            </label>
            <select
              value={classLevel}
              onChange={(e) => setClassLevel(Number(e.target.value))}
              className="border rounded p-1 text-sm bg-white"
            >
              {[6, 7, 8, 9, 10, 11, 12].map((c) => (
                <option key={c} value={c}>
                  Class {c}
                </option>
              ))}
            </select>
          </div>

          <div className="flex items-center gap-2">
            <label className="text-sm font-semibold text-slate-600">
              Subject:
            </label>
            <select
              value={subject}
              onChange={(e) => setSubject(e.target.value)}
              className="border rounded p-1 text-sm bg-white"
            >
              {[
                'Science',
                'Mathematics',
                'Social Science',
                'English',
                'Hindi',
              ].map((s) => (
                <option key={s} value={s}>
                  {s}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Chat Area */}
      <div className="flex-1 w-full max-w-4xl mx-auto p-4 mb-20">
        <div className="flex flex-col gap-6">
          {messages.map((msg, idx) => (
            <div
              key={idx}
              className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'
                }`}
            >
              <div
                className={`max-w-[80%] rounded-2xl p-4 shadow-sm ${msg.role === 'user'
                  ? 'bg-blue-600 text-white rounded-tr-none'
                  : 'bg-white border border-slate-200 text-slate-800 rounded-tl-none'
                  }`}
              >
                <div className="whitespace-pre-wrap leading-relaxed">
                  {msg.content}
                </div>

                {msg.citations && msg.citations.length > 0 && (
                  <div className="mt-4 pt-4 border-t border-slate-100">
                    <p className="text-xs font-bold text-slate-500 mb-2 uppercase tracking-wide">
                      Sources Verified:
                    </p>
                    <ul className="space-y-1">
                      {msg.citations.map((cit, cIdx) => (
                        <li
                          key={cIdx}
                          className="text-xs flex gap-2 items-start bg-slate-50 p-2 rounded border border-slate-100"
                        >
                          <span className="text-green-600 font-bold">✓</span>
                          <span>{cit}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </div>
          ))}

          {loading && (
            <div className="flex justify-start">
              <div className="bg-white p-4 rounded-2xl rounded-tl-none border border-slate-200 shadow-sm animate-pulse">
                <div className="flex gap-1">
                  <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" />
                  <div
                    className="w-2 h-2 bg-slate-400 rounded-full animate-bounce"
                    style={{ animationDelay: '0.1s' }}
                  />
                  <div
                    className="w-2 h-2 bg-slate-400 rounded-full animate-bounce"
                    style={{ animationDelay: '0.2s' }}
                  />
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input Area */}
      <div className="fixed bottom-0 left-0 right-0 bg-white border-t border-slate-200 p-4">
        <div className="max-w-4xl mx-auto flex gap-2">
          <input
            type="text"
            className="flex-1 border border-slate-300 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500 shadow-sm"
            placeholder="Ask a question from NCERT..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={loading}
          />
          <button
            onClick={sendMessage}
            disabled={loading || !input.trim()}
            className="bg-blue-600 hover:bg-blue-700 disabled:bg-slate-400 text-white px-6 py-3 rounded-lg font-semibold transition-colors shadow-sm"
          >
            Send
          </button>
        </div>
      </div>
    </main>
  );
}
