"use client";
import { useState, useRef, useEffect, useCallback } from "react";
import { v4 as uuidv4 } from "uuid";
import {
  Send, Upload, FileText, Loader2, Bot, User, ChevronDown, AlertCircle, Database,
} from "lucide-react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

type Source  = { source: string; page: number; similarity: number };
type Doc     = { id: string; name: string; total_chunks: number };
type Message = {
  id:       string;
  role:     "user" | "assistant";
  content:  string;
  sources?: Source[];
  loading?: boolean;
  error?:   boolean;
};

const SUGGESTED = [
  "What is the main topic of these documents?",
  "Summarise the key findings",
  "What risks are mentioned?",
  "What role does AI play in finance?",
];

export default function ChatPage() {
  const [messages,    setMessages]    = useState<Message[]>([]);
  const [input,       setInput]       = useState("");
  const [sessionId]                   = useState(() => uuidv4());
  const [uploading,   setUploading]   = useState(false);
  const [streaming,   setStreaming]   = useState(false);
  const [docs,        setDocs]        = useState<Doc[]>([]);
  const [showDocs,    setShowDocs]    = useState(false);
  const [uploadError, setUploadError] = useState("");

  const bottomRef = useRef<HTMLDivElement>(null);
  const fileRef   = useRef<HTMLInputElement>(null);
  const inputRef  = useRef<HTMLInputElement>(null);

  // Load existing documents from backend on startup
  useEffect(() => {
    fetch(`${API_URL}/api/upload/documents`)
      .then(r => r.json())
      .then(data => { if (data.documents) setDocs(data.documents); })
      .catch(() => {}); // silently fail if backend not ready
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const updateLastAssistant = useCallback((updater: (m: Message) => Message) => {
    setMessages(prev => {
      const copy = [...prev];
      const idx  = copy.map(m => m.role).lastIndexOf("assistant");
      if (idx !== -1) copy[idx] = updater(copy[idx]);
      return copy;
    });
  }, []);

  // ── Upload ────────────────────────────────────────────────────────────
  const uploadFile = async (file: File) => {
    setUploadError("");
    if (!file.name.match(/\.(pdf|txt)$/i)) {
      setUploadError("Only PDF and TXT files are supported.");
      return;
    }
    setUploading(true);
    const form = new FormData();
    form.append("file", file);
    try {
      const res  = await fetch(`${API_URL}/api/upload/`, { method: "POST", body: form });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Upload failed");
      setDocs(prev => [...prev, { id: data.document_id, name: data.filename, total_chunks: data.chunks }]);
      setMessages(prev => [...prev, {
        id:      uuidv4(),
        role:    "assistant",
        content: `✅ **${data.filename}** uploaded! Indexed ${data.chunks} chunks across ${data.pages} pages. Ask me anything about it.`,
      }]);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Upload failed. Is the backend running?";
      setUploadError(msg);
    } finally {
      setUploading(false);
      if (fileRef.current) fileRef.current.value = "";
    }
  };

  // ── Chat ──────────────────────────────────────────────────────────────
  const sendMessage = async (overrideQuery?: string) => {
    const query = (overrideQuery ?? input).trim();
    if (!query || streaming) return;
    setInput("");

    const userMsg: Message      = { id: uuidv4(), role: "user",      content: query };
    const assistantMsg: Message = { id: uuidv4(), role: "assistant", content: "", loading: true };
    setMessages(prev => [...prev, userMsg, assistantMsg]);
    setStreaming(true);

    try {
      const res = await fetch(`${API_URL}/api/chat/`, {
        method:  "POST",
        headers: { "Content-Type": "application/json" },
        body:    JSON.stringify({ query, session_id: sessionId, top_k: 5 }),
      });
      if (!res.ok || !res.body) throw new Error("Backend error. Is uvicorn running?");

      const reader  = res.body.getReader();
      const decoder = new TextDecoder();
      let   buffer  = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() ?? "";
        for (const line of lines) {
          const trimmed = line.trim();
          if (!trimmed.startsWith("data: ")) continue;
          try {
            const payload = JSON.parse(trimmed.slice(6));
            if (payload.type === "sources") {
              updateLastAssistant(m => ({ ...m, sources: payload.sources, loading: false }));
            } else if (payload.type === "token") {
              updateLastAssistant(m => ({ ...m, content: m.content + payload.content, loading: false }));
            }
          } catch { /* skip malformed */ }
        }
      }
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Something went wrong.";
      updateLastAssistant(m => ({ ...m, content: `❌ ${msg}`, loading: false, error: true }));
    } finally {
      setStreaming(false);
      inputRef.current?.focus();
    }
  };

  const hasDocuments = docs.length > 0;

  // ── Render ────────────────────────────────────────────────────────────
  return (
    <div className="flex flex-col h-screen bg-gray-950 text-gray-100">

      {/* Header */}
      <header className="border-b border-gray-800 px-5 py-3 flex items-center justify-between gap-4 shrink-0">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-emerald-500 flex items-center justify-center shrink-0">
            <Bot size={17} className="text-white" />
          </div>
          <div>
            <h1 className="font-semibold text-white text-sm leading-tight">DocChat RAG</h1>
            <p className="text-xs text-gray-500">Groq · Gemini · Supabase pgvector</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          {hasDocuments && (
            <button onClick={() => setShowDocs(v => !v)}
              className="flex items-center gap-1.5 text-xs bg-gray-800 hover:bg-gray-700 px-3 py-1.5 rounded-full transition-colors">
              <Database size={12} className="text-emerald-400" />
              {docs.length} doc{docs.length > 1 ? "s" : ""} in DB
              <ChevronDown size={12} className={`transition-transform ${showDocs ? "rotate-180" : ""}`} />
            </button>
          )}
          <button onClick={() => fileRef.current?.click()} disabled={uploading}
            className="flex items-center gap-1.5 text-xs font-medium bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 disabled:cursor-not-allowed px-4 py-1.5 rounded-full transition-colors">
            {uploading ? <><Loader2 size={13} className="animate-spin" /> Processing…</> : <><Upload size={13} /> Upload PDF</>}
          </button>
          <input ref={fileRef} type="file" accept=".pdf,.txt" className="hidden"
            onChange={e => e.target.files?.[0] && uploadFile(e.target.files[0])} />
        </div>
      </header>

      {/* Upload error */}
      {uploadError && (
        <div className="px-5 py-2 bg-red-950 border-b border-red-800 flex items-center gap-2 text-xs text-red-300">
          <AlertCircle size={13} />{uploadError}
          <button onClick={() => setUploadError("")} className="ml-auto text-red-400 hover:text-red-200">✕</button>
        </div>
      )}

      {/* Docs list */}
      {showDocs && (
        <div className="border-b border-gray-800 bg-gray-900 px-5 py-3 shrink-0">
          <p className="text-xs text-gray-500 mb-2">Documents indexed in Supabase</p>
          <div className="flex flex-wrap gap-2">
            {docs.map(doc => (
              <span key={doc.id} className="flex items-center gap-1.5 text-xs bg-gray-800 text-gray-300 px-3 py-1 rounded-full">
                <FileText size={11} className="text-emerald-400" />
                {doc.name}
                <span className="text-gray-500">· {doc.total_chunks} chunks</span>
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-6">
        {messages.length === 0 && (
          <div className="text-center py-16 max-w-md mx-auto">
            <div className="w-14 h-14 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center mx-auto mb-4">
              <Bot size={26} className="text-emerald-400" />
            </div>
            {hasDocuments ? (
              <>
                <h2 className="text-base font-medium text-white mb-2">
                  {docs.length} document{docs.length > 1 ? "s" : ""} ready — ask anything
                </h2>
                <p className="text-sm text-gray-400 mb-6 leading-relaxed">
                  Your documents are indexed in Supabase. Ask a question or try one below.
                </p>
              </>
            ) : (
              <>
                <h2 className="text-base font-medium text-white mb-2">Upload a document to start</h2>
                <p className="text-sm text-gray-400 mb-6 leading-relaxed">
                  Upload any PDF — research papers, financial reports, legal documents.
                  Answers come with page citations from your documents only.
                </p>
              </>
            )}
            <div className="flex flex-wrap gap-2 justify-center">
              {SUGGESTED.map(q => (
                <button key={q} onClick={() => { setInput(q); inputRef.current?.focus(); }}
                  className="text-xs bg-gray-800 hover:bg-gray-700 text-gray-300 px-3 py-1.5 rounded-full transition-colors">
                  {q}
                </button>
              ))}
            </div>
          </div>
        )}

        <div className="space-y-5 max-w-3xl mx-auto">
          {messages.map(msg => (
            <div key={msg.id} className={`flex gap-3 ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
              {msg.role === "assistant" && (
                <div className="w-7 h-7 rounded-lg bg-emerald-500/20 border border-emerald-500/30 flex items-center justify-center shrink-0 mt-1">
                  <Bot size={13} className="text-emerald-400" />
                </div>
              )}
              <div className="max-w-[80%] min-w-0">
                <div className={`rounded-2xl px-4 py-3 text-sm leading-relaxed whitespace-pre-wrap break-words ${
                  msg.role === "user" ? "bg-emerald-600 text-white rounded-br-sm"
                  : msg.error ? "bg-red-950 border border-red-800 text-red-300 rounded-bl-sm"
                  : "bg-gray-800 text-gray-100 rounded-bl-sm"
                }`}>
                  {msg.loading
                    ? <span className="flex items-center gap-2 text-gray-400"><Loader2 size={13} className="animate-spin" />Thinking…</span>
                    : msg.content}
                </div>
                {msg.sources && msg.sources.length > 0 && (
                  <div className="mt-2 flex flex-wrap gap-1.5">
                    {msg.sources.map((s, i) => (
                      <span key={i} className="text-xs bg-gray-900 border border-gray-700 text-gray-400 px-2.5 py-1 rounded-full">
                        📄 {s.source} · p.{s.page}
                      </span>
                    ))}
                  </div>
                )}
              </div>
              {msg.role === "user" && (
                <div className="w-7 h-7 rounded-lg bg-gray-700 flex items-center justify-center shrink-0 mt-1">
                  <User size={13} className="text-gray-300" />
                </div>
              )}
            </div>
          ))}
        </div>
        <div ref={bottomRef} />
      </div>

      {/* Input — always enabled, no upload lock */}
      <div className="border-t border-gray-800 px-4 py-4 shrink-0">
        <div className="max-w-3xl mx-auto flex gap-3">
          <input ref={inputRef} value={input} onChange={e => setInput(e.target.value)}
            onKeyDown={e => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); sendMessage(); } }}
            placeholder={hasDocuments ? "Ask a question about your documents…" : "Upload a PDF or wait for documents to load…"}
            disabled={streaming}
            className="flex-1 min-w-0 bg-gray-800 border border-gray-700 rounded-xl px-4 py-3 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-emerald-500 disabled:opacity-40 transition-colors" />
          <button onClick={() => sendMessage()} disabled={streaming || !input.trim()}
            className="bg-emerald-600 hover:bg-emerald-500 disabled:opacity-40 disabled:cursor-not-allowed p-3 rounded-xl transition-colors shrink-0" aria-label="Send">
            {streaming ? <Loader2 size={18} className="animate-spin text-white" /> : <Send size={18} className="text-white" />}
          </button>
        </div>
        <p className="text-center text-xs text-gray-600 mt-2">
          Answers grounded in your documents · Groq Llama 3 · Gemini Flash · pgvector
        </p>
      </div>
    </div>
  );
}