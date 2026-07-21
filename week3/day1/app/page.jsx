import Image from "next/image";
import Link from "next/link";
import PublicNav from "@/components/ui/PublicNav";
import Button from "@/components/ui/Button";
import Card from "@/components/ui/Card";
import { Zap, ShieldCheck, LayoutGrid, Rocket } from "lucide-react";

// Per-page metadata — overrides/extends the root layout's metadata for this route.
// This is what controls search engine snippets and social share previews.
export const metadata = {
  title: "Week 3 Launchpad — Ship dashboards faster",
  description:
    "A reusable Next.js + Tailwind component system for building dashboards fast.",
  openGraph: {
    title: "Week 3 Launchpad",
    description: "A reusable Next.js + Tailwind component system for building dashboards fast.",
    images: ["/hero.png"],
  },
};

const features = [
  {
    icon: Zap,
    title: "Fast by default",
    description: "Server Components mean less JS shipped to the browser out of the box.",
  },
  {
    icon: LayoutGrid,
    title: "Reusable components",
    description: "A shared UI library — Button, Card, Badge, Modal — built once, used everywhere.",
  },
  {
    icon: ShieldCheck,
    title: "Type-safe routing",
    description: "File-based routing with nested layouts keeps navigation predictable.",
  },
  {
    icon: Rocket,
    title: "Production-ready",
    description: "Image and font optimization built in, no extra configuration required.",
  },
];

const testimonials = [
  {
    name: "Sara Ahmed",
    role: "Frontend Intern",
    avatar: "/avatar1.png",
    quote: "Went from zero to a working dashboard shell in a single afternoon.",
  },
  {
    name: "Ravi Kumar",
    role: "Frontend Intern",
    avatar: "/avatar2.png",
    quote: "The component library made every later page faster to build.",
  },
  {
    name: "Maya Joseph",
    role: "Mentor",
    avatar: "/avatar3.png",
    quote: "Clean separation between layout, components, and pages — solid structure.",
  },
];

export default function LandingPage() {
  return (
    <div>
      <PublicNav />

      {/* HERO — responsive: stacked on mobile, side-by-side from md breakpoint up */}
      <section className="mx-auto flex max-w-6xl flex-col items-center gap-10 px-6 py-16 md:flex-row md:py-24">
        <div className="text-center md:w-1/2 md:text-left">
          <h1 className="text-3xl font-bold leading-tight text-slate-800 sm:text-4xl md:text-5xl">
            Ship dashboards faster with a reusable component system
          </h1>
          <p className="mt-4 text-slate-500">
            Built with Next.js App Router and TailwindCSS — Week 3 Advance Frontend
            internship project.
          </p>
          <div className="mt-8 flex flex-col justify-center gap-3 sm:flex-row md:justify-start">
            <Link href="/dashboard">
              <Button variant="primary" size="lg" className="w-full sm:w-auto">
                Go to Dashboard
              </Button>
            </Link>
            <Link href="/about">
              <Button variant="secondary" size="lg" className="w-full sm:w-auto">
                Learn more
              </Button>
            </Link>
          </div>
        </div>

        <div className="md:w-1/2">
          {/* next/image: width/height reserve layout space (prevents shift),
              priority = load immediately since it's above the fold */}
          <Image
            src="/hero.png"
            alt="Abstract illustration representing a dashboard UI"
            width={1200}
            height={900}
            priority
            className="w-full rounded-2xl"
          />
        </div>
      </section>

      {/* FEATURES — 1 col mobile, 2 col sm, 4 col lg */}
      <section className="bg-white py-16">
        <div className="mx-auto max-w-6xl px-6">
          <h2 className="text-center text-2xl font-bold text-slate-800">Features</h2>
          <div className="mt-10 grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
            {features.map(({ icon: Icon, title, description }) => (
              <Card key={title}>
                <Icon size={22} className="text-blue-600" />
                <h3 className="mt-3 font-semibold text-slate-800">{title}</h3>
                <p className="mt-1 text-sm text-slate-500">{description}</p>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* TESTIMONIALS — 1 col mobile, 3 col md */}
      <section className="py-16">
        <div className="mx-auto max-w-6xl px-6">
          <h2 className="text-center text-2xl font-bold text-slate-800">
            What people are saying
          </h2>
          <div className="mt-10 grid grid-cols-1 gap-6 md:grid-cols-3">
            {testimonials.map((t) => (
              <Card key={t.name}>
                <p className="text-sm text-slate-600">&ldquo;{t.quote}&rdquo;</p>
                <div className="mt-4 flex items-center gap-3">
                  <Image
                    src={t.avatar}
                    alt={`${t.name} avatar`}
                    width={40}
                    height={40}
                    className="rounded-full"
                  />
                  <div>
                    <p className="text-sm font-medium text-slate-800">{t.name}</p>
                    <p className="text-xs text-slate-500">{t.role}</p>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* FOOTER */}
      <footer className="border-t border-slate-200 bg-white py-8">
        <div className="mx-auto flex max-w-6xl flex-col items-center justify-between gap-4 px-6 text-sm text-slate-500 sm:flex-row">
          <span>© 2026 Week 3 Launchpad. Internship project.</span>
          <div className="flex gap-4">
            <Link href="/" className="hover:text-slate-800">Home</Link>
            <Link href="/about" className="hover:text-slate-800">About</Link>
            <Link href="/dashboard" className="hover:text-slate-800">Dashboard</Link>
          </div>
        </div>
      </footer>
    </div>
  );
}
