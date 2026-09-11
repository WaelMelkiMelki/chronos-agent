"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { API_URL_BASE, api, auth } from "@/lib/api";

type Msg = { role: "user" | "assistant"; content: string };
type PendingAction = { tool: string; preview: string };

export default function ChatPage() {
  const router = useRouter();
  const [messages, setMessages] = useState<Msg[]>([]);
  const [input, setInput] = useState("");
  const [threadId, setThreadId] = useState<string | null>(null);
  const [pending, setPending] = useState<PendingAction[] | null>(null);
  const [busy, setBusy] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => { if (!auth.isAuthed()) router.push("/login"); }, [router]);
  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: "smooth" }); }, [messages]);

  async function connectGoogle() {
    try { const { auth_url } = await api.googleLoginUrl(); window.location.href = auth_url; } catch (e) { alert("Erreur: " + (e as Error).message); }
  }

  async function streamResponse(path: string, body: unknown) {
    const token = auth.access();
    const res = await fetch(`${API_URL_BASE}${path}`, { method: "POST", headers: { "Content-Type": "application/json", ...(token ? { Authorization: "Bearer " + token } : {}) }, body: JSON.stringify(body) });
    if (!res.body) return;
    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";
    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      const parts = buffer.split("\n\n");
      buffer = parts.pop() ?? "";
      for (const chunk of parts) {
        const line = chunk.split("\n").find((l) => l.startsWith("data: "));
        if (!line) continue;
        const payload = JSON.parse(line.slice(6));
        handleEvent(payload);
      }
    }
  }

  function handleEvent(ev: { type?: string; thread_id?: string; response?: string; planned_actions?: PendingAction[]; status?: string }) {
    if (ev.type === "thread" && ev.thread_id) setThreadId(ev.thread_id);
    if (ev.type === "final") {
      if (typeof ev.response === "string") {
        const response = ev.response;
        setMessages((m) => [...m, { role: "assistant", content: response }]);
      }
      if (ev.planned_actions && ev.planned_actions.length > 0 && ev.status === "awaiting_confirmation") { setPending(ev.planned_actions); } else { setPending(null); }
    }
  }

  async function send(e: React.FormEvent) {
    e.preventDefault();
    if (!input.trim() || busy) return;
    const userMsg = input;
    setInput("");
    setMessages((m) => [...m, { role: "user", content: userMsg }]);
    setBusy(true);
    try { await streamResponse("/api/v1/chat", { message: userMsg, thread_id: threadId }); } catch (err) { setMessages((m) => [...m, { role: "assistant", content: "Erreur: " + (err as Error).message }]); }
    finally { setBusy(false); }
  }

  async function confirm(approved: boolean) {
    if (!threadId) return;
    setBusy(true);
    setPending(null);
    try { await streamResponse("/api/v1/chat/confirm", { thread_id: threadId, approved }); } finally { setBusy(false); }
  }

  return (
    <main className="mx-auto flex h-screen max-w-3xl flex-col p-6">
      <header className="flex items-center justify-between border-b border-neutral-200 pb-4">
        <h1 className="text-lg font-semibold">chronos-agent</h1>
        <div className="flex gap-2">
          <button onClick={connectGoogle} className="rounded-md border border-neutral-300 px-3 py-1 text-sm hover:bg-neutral-100">Connecter Google</button>
          <button onClick={() => { auth.clear(); router.push("/login"); }} className="rounded-md border border-neutral-300 px-3 py-1 text-sm hover:bg-neutral-100">Déconnexion</button>
        </div>
      </header>
      <div className="flex-1 space-y-4 overflow-y-auto py-6">
        {messages.length === 0 && <p className="text-sm text-neutral-500">Essayez : « Ajoute une réunion demain à 15h »</p>}
        {messages.map((m, i) => (
          <div key={i} className={m.role === "user" ? "ml-auto max-w-[80%] rounded-2xl bg-black px-4 py-2 text-white" : "mr-auto max-w-[80%] rounded-2xl bg-white px-4 py-2 shadow-sm whitespace-pre-wrap"}>
            {m.content}
          </div>
        ))}
        {pending && (
          <div className="mr-auto max-w-[80%] rounded-2xl border border-amber-300 bg-amber-50 px-4 py-3">
            <p className="mb-2 text-sm font-medium">Confirmer ?</p>
            <ul className="mb-3 list-disc pl-5 text-sm">{pending.map((a, i) => <li key={i}>{a.preview}</li>)}</ul>
            <div className="flex gap-2">
              <button onClick={() => confirm(true)} className="rounded-md bg-black px-3 py-1 text-sm text-white">Confirmer</button>
              <button onClick={() => confirm(false)} className="rounded-md border border-neutral-300 px-3 py-1 text-sm">Annuler</button>
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>
      <form onSubmit={send} className="flex gap-2 border-t border-neutral-200 pt-4">
        <input className="flex-1 rounded-lg border border-neutral-300 px-3 py-2" placeholder="Écrivez votre demande…" value={input} onChange={(e) => setInput(e.target.value)} disabled={busy} />
        <button type="submit" disabled={busy || !input.trim()} className="rounded-lg bg-black px-4 py-2 text-white disabled:opacity-50">Envoyer</button>
      </form>
    </main>
  );
}
