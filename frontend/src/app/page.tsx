import Link from "next/link";

export default function Home() {
  return (
    <main className="mx-auto max-w-3xl px-6 py-24 text-center">
      <h1 className="text-5xl font-bold tracking-tight">chronos-agent</h1>
      <p className="mt-4 text-lg text-neutral-600">
        Votre assistant IA local qui gère votre calendrier en langage naturel.
      </p>
      <div className="mt-10 flex justify-center gap-4">
        <Link href="/login" className="rounded-lg bg-black px-6 py-3 text-white hover:bg-neutral-800">Se connecter</Link>
        <Link href="/chat" className="rounded-lg border border-neutral-300 px-6 py-3 hover:bg-neutral-100">Ouvrir le chat</Link>
      </div>
    </main>
  );
}