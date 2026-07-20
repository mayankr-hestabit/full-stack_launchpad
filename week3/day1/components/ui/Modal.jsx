"use client";

import { X } from "lucide-react";

// Modal — a "molecule". Controlled component: `open` and `onClose` are owned by the PARENT,
// same "lifting state up" pattern as the Sidebar toggle from Day 1.

export default function Modal({ open, onClose, title, children }) {
  if (!open) return null;

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/50 p-4">
      {/* backdrop click closes the modal */}
      <div className="absolute inset-0" onClick={onClose} />

      <div className="relative w-full max-w-md rounded-lg bg-white shadow-xl">
        <div className="flex items-center justify-between border-b border-slate-100 px-5 py-3">
          <h2 className="text-base font-semibold text-slate-800">{title}</h2>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-700">
            <X size={18} />
          </button>
        </div>
        <div className="p-5">{children}</div>
      </div>
    </div>
  );
}