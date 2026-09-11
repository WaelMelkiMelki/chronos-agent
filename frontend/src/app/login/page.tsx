"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { api, auth } from "@/lib/api";

export default function LoginPage() {
  const router = useRouter();
  const [mode, setMode] = useState<"login" | "register">("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const tokens = mode === "login" ? await api.login(email, password) : await api.register(email, password, fullName);
      auth.save(tokens);
      router.push("/chat");
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="mx-auto mt-24 max-w-md rounded-2xl border border-neutral-200 bg-white p-8 shadow-sm">
      <h1 className="text-2xl font-semibold">{mode === "login" ? "Connexion" : "Créer un compte"}</h1>
      <form onSubmit={submit} className="mt-6 space-y-4">
        {mode === "register" && <input className="w-full rounded-lg border border-neutral-300 px-3 py-2" placeholder="Nom complet" value={fullName} onChange={(e) => setFullName(e.target.value)} />}
        <input className="w-full rounded-lg border border-neutral-300 px-3 py-2" type="email" placeholder="Email" required value={email} onChange={(e) => setEmail(e.target.value)} />
        <input className="w-full rounded-lg border border-neutral-300 px-3 py-2" type="password" placeholder="Mot de passe (8+ caractères)" required value={password} onChange={(e) => setPassword(e.target.value)} />
        {error && <p className="text-sm text-red-600">{error}</p>}
        <button type="submit" disabled={loading} className="w-full rounded-lg bg-black px-4 py-2 text-white hover:bg-neutral-800 disabled:opacity-50">{loading ? "…" : mode === "login" ? "Se connecter" : "Créer"}</button>
      </form>
      <button onClick={() => setMode(mode === "login" ? "register" : "login")} className="mt-4 text-sm text-neutral-500 underline">
        {mode === "login" ? "Pas de compte ? S'inscrire" : "Déjà un compte ? Se connecter"}
      </button>
    </main>
  );
}