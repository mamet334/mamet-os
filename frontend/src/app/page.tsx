"use client";

import React, { useState } from "react";

function ChatColumn({
  columnId,
  label,
  icon,
}: {
  columnId: string;
  label: string;
  icon: string;
}) {
  const [messages, setMessages] = useState<{ role: string; content: string }[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);

  const handleSend = async () => {
    if (!input.trim() || loading) return;
    const userMsg = { role: "user", content: input };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);
    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_id: "test@email.com",
          column: columnId,
          message: input,
        }),
      });
      const data = await res.json();
      setMessages((prev) => [...prev, { role: "system", content: data.response }]);
    } catch {
      setMessages((prev) => [...prev, { role: "system", content: "❌ Gagal" }]);
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch("/api/upload", {
        method: "POST",
        body: formData,
      });
      const data = await res.json();
      if (data.status === "success") {
        const sysMsg = {
          role: "system",
          content: `✅ Dokumen "${file.name}" berhasil diunggah. (${data.chunks} chunk, ${data.char_count} karakter)`,
        };
        setMessages((prev) => [...prev, sysMsg]);
      } else {
        setMessages((prev) => [...prev, { role: "system", content: `❌ ${data.message || "Gagal mengunggah"}` }]);
      }
    } catch {
      setMessages((prev) => [...prev, { role: "system", content: "❌ Gagal mengunggah dokumen" }]);
    } finally {
      setUploading(false);
      e.target.value = '';
    }
  };

  return (
    <div className="flex flex-col h-full bg-[#0d0d0d]">
      <div className="px-4 py-3 border-b border-[#222] bg-[#111] flex items-center justify-between">
        <h2 className="text-sm font-semibold text-gray-200">
          {icon} {label}
        </h2>
        {columnId === "kolom1" && (
          <label className={`cursor-pointer text-xs px-2 py-1 rounded text-white ${uploading ? 'bg-gray-500' : 'bg-blue-600 hover:bg-blue-700'}`}>
            {uploading ? "⏳ Upload..." : "📎 Upload"}
            <input
              type="file"
              className="hidden"
              accept=".txt,.md,.pdf,.docx,.csv,.json"
              onChange={handleFileUpload}
              disabled={uploading}
            />
          </label>
        )}
      </div>
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {messages.length === 0 && (
          <p className="text-gray-500 text-sm text-center mt-8">
            Mulai percakapan di {label}
          </p>
        )}
        {messages.map((msg, i) => (
          <div
            key={i}
            className={`p-3 rounded text-sm ${
              msg.role === "user"
                ? "bg-blue-900/40 ml-8 text-blue-100"
                : "bg-[#1a1a1a] mr-8 border border-[#333] text-gray-200"
            }`}
          >
            {msg.content}
          </div>
        ))}
        {loading && <p className="text-gray-400 text-sm">Memproses...</p>}
      </div>
      <div className="p-3 border-t border-[#222] bg-[#111]">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSend()}
            placeholder={`Ketik di ${label}...`}
            className="flex-1 bg-[#2a2a2a] border border-[#555] rounded px-3 py-2 text-sm text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
          />
          <button
            onClick={handleSend}
            disabled={loading || !input.trim()}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-700 disabled:text-gray-400 rounded text-sm font-medium text-white transition"
          >
            Kirim
          </button>
        </div>
      </div>
    </div>
  );
}

export default function Home() {
  const [activeColumn, setActiveColumn] = useState("kolom2");

  const columns = [
    { id: "kolom1", label: "Pencarian Cepat", icon: "🔍" },
    { id: "kolom2", label: "Asisten Pribadi", icon: "🤖" },
    { id: "kolom3", label: "Engineer", icon: "🔧" },
  ];

  return (
    <div className="h-screen flex flex-col bg-[#0a0a0a]">
      <header className="bg-[#111] border-b border-[#222] px-4 py-3 flex items-center justify-between shrink-0">
        <h1 className="text-lg font-bold text-gray-100">MAMET OS</h1>
        <span className="text-xs text-gray-500">v0.1.0</span>
      </header>

      <nav className="md:hidden flex border-b border-[#222] shrink-0">
        {columns.map((col) => (
          <button
            key={col.id}
            onClick={() => setActiveColumn(col.id)}
            className={`flex-1 py-3 text-center text-sm ${
              activeColumn === col.id
                ? "border-b-2 border-blue-500 text-blue-400 bg-[#111]"
                : "text-gray-500"
            }`}
          >
            <span className="block text-lg">{col.icon}</span>
            <span className="text-xs">{col.label}</span>
          </button>
        ))}
      </nav>

      <main className="flex-1 flex overflow-hidden">
        <div className="hidden md:flex flex-1 divide-x divide-[#222]">
          {columns.map((col) => (
            <ChatColumn
              key={col.id}
              columnId={col.id}
              label={col.label}
              icon={col.icon}
            />
          ))}
        </div>
        <div className="md:hidden flex-1">
          {columns
            .filter((col) => col.id === activeColumn)
            .map((col) => (
              <ChatColumn
                key={col.id}
                columnId={col.id}
                label={col.label}
                icon={col.icon}
              />
            ))}
        </div>
      </main>
    </div>
  );
}