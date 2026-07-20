import Link from "next/link";
import PublicNav from "@/components/ui/PublicNav";
import Button from "@/components/ui/Button";

export default function LandingPage() {
  return (
    <div>
      <PublicNav />

      <main className="mx-auto max-w-3xl px-6 py-24 text-center">
        <h1 className="text-4xl font-bold text-slate-800">Week 3 Launchpad</h1>
        <p className="mt-4 text-slate-500">
          Next.js + TailwindCSS — internship frontend track. This page is publicly
          routed at <code className="rounded bg-slate-200 px-1.5 py-0.5 text-sm">/</code>.
        </p>

        <div className="mt-8 flex justify-center gap-3">
          <Link href="/dashboard">
            <Button variant="primary">Go to Dashboard</Button>
          </Link>
          <Link href="/about">
            <Button variant="secondary">About this project</Button>
          </Link>
        </div>
      </main>
    </div>
  );
}
