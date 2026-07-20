"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const links = [
  { href: "/", label: "Home" },
  { href: "/about", label: "About" },
  { href: "/dashboard", label: "Dashboard" },
];

export default function PublicNav() {
  const pathname = usePathname();

  return (
    <header className="flex h-14 items-center justify-between border-b border-slate-200 bg-white px-6">
      <span className="font-semibold text-slate-800">Week 3 Launchpad</span>
      <nav className="flex gap-6 text-sm">
        {links.map((link) => (
          <Link
            key={link.href}
            href={link.href}
            className={
              pathname === link.href
                ? "font-medium text-blue-600"
                : "text-slate-500 hover:text-slate-800"
            }
          >
            {link.label}
          </Link>
        ))}
      </nav>
    </header>
  );
}
