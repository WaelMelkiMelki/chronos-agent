"use client";

import { Suspense, useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";

function OAuthCallbackContent() {
  const router = useRouter();
  const params = useSearchParams();
  const status = params.get("status");

  useEffect(() => {
    const t = setTimeout(() => { router.push(status === "success" ? "/chat?google=connected" : "/chat?google=error"); }, 1200);
    return () => clearTimeout(t);
  }, [router, status]);

  return (
    <main className="flex h-screen items-center justify-center">
      <p className="text-lg">{status === "success" ? "✅ Google Calendar connecté" : "❌ Échec de la connexion Google"}</p>
    </main>
  );
}

export default function OAuthCallback() {
  return (
    <Suspense fallback={<main className="flex h-screen items-center justify-center"><p className="text-lg">Connexion en cours…</p></main>}>
      <OAuthCallbackContent />
    </Suspense>
  );
}