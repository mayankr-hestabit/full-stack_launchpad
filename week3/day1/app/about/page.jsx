import PublicNav from "@/components/ui/PublicNav";

export default function AboutPage() {
  return (
    <div>
      <PublicNav />

      <main className="mx-auto max-w-2xl px-6 py-16">
        <h1 className="text-2xl font-bold text-slate-800">About</h1>
        <p className="mt-4 text-sm leading-relaxed text-slate-600">
          This project is the Week 3 deliverable for the Advance Frontend track —
          built with Next.js App Router and TailwindCSS. It demonstrates file-based
          routing, nested layouts, a reusable component library, and responsive
          dashboard UI patterns.
        </p>
        <p className="mt-4 text-sm leading-relaxed text-slate-600">
          Routes: <code className="rounded bg-slate-200 px-1.5 py-0.5">/</code>,{" "}
          <code className="rounded bg-slate-200 px-1.5 py-0.5">/about</code>,{" "}
          <code className="rounded bg-slate-200 px-1.5 py-0.5">/dashboard</code>,{" "}
          <code className="rounded bg-slate-200 px-1.5 py-0.5">/dashboard/profile</code>
        </p>
      </main>
    </div>
  );
}
