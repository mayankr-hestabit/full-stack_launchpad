"use client";

import Link from "next/link";

import { Menu, Search, UserCircle, ChevronDown } from "lucide-react";
import { useState } from "react";

export default function Navbar({ onToggleSidebar }) {
  const [menuOpen, setMenuOpen] = useState(false);

  return (
    <header className="fixed top-0 left-0 right-0 z-50 flex h-14 items-center justify-between bg-slate-900 px-4">
      {/* Left side: hamburger + brand */}
      <div className="flex items-center gap-3">
        <button
          onClick={onToggleSidebar}
          className="text-slate-300 hover:text-white"
          aria-label="Toggle sidebar"
        >
          <Menu size={20} />
        </button>
        <span className="text-lg font-semibold text-white">Start Bootstrap</span>
      </div>

      {/* Right side: search + user menu */}
      <div className="flex items-center gap-4">
        <div className="hidden items-center overflow-hidden rounded-md sm:flex">
          <input
            type="text"
            placeholder="Search for..."
            className="h-9 w-56 bg-slate-100 px-3 text-sm text-slate-800 outline-none placeholder:text-slate-400"
          />
          <button className="flex h-9 w-10 items-center justify-center bg-blue-600 text-white hover:bg-blue-700">
            <Search size={16} />
          </button>
        </div>

        <div className="relative">
          <button
            onClick={() => setMenuOpen(!menuOpen)}
            className="flex items-center gap-1 text-slate-300 hover:text-white"
          >
            <UserCircle size={22} />
            <ChevronDown size={14} />
          </button>

          {menuOpen && (
            <div className="absolute right-0 mt-2 w-40 rounded-md bg-white py-1 text-sm text-slate-700 shadow-lg">
              <Link href="/dashboard/profile" className="block px-4 py-2 hover:bg-slate-100">Profile</Link>
              <Link href="/#" className="block px-4 py-2 hover:bg-slate-100">Settings</Link>
              <Link href="/login" className="block px-4 py-2 hover:bg-slate-100">Logout</Link>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
