"use client";

import { useState, useEffect } from "react";
import Navbar from "./Navbar";
import Sidebar from "./Sidebar";

export default function DashboardShell({ children }) {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  // On first load: open by default on desktop (lg breakpoint, 1024px+),
  // closed by default on mobile/tablet. window is only available client-side,
  // hence this runs in useEffect rather than during render.
  useEffect(() => {
    if (window.innerWidth >= 1024) {
      setSidebarOpen(true);
    }
  }, []);

  return (
    <>
      <Navbar onToggleSidebar={() => setSidebarOpen(!sidebarOpen)} />
      <Sidebar open={sidebarOpen} />

      {/* Backdrop — only rendered on mobile/tablet while sidebar is open.
          Clicking it closes the sidebar. Hidden entirely on lg+ screens,
          where the sidebar pushes content instead of overlaying it. */}
      {sidebarOpen && (
        <div
          onClick={() => setSidebarOpen(false)}
          className="fixed inset-0 top-14 z-30 bg-black/40 lg:hidden"
        />
      )}

      {/* main only shifts right on lg+ screens (ml-56); on mobile the sidebar
          overlays on top instead, so content always stays full-width there */}
      <main
        className={`mt-14 min-h-[calc(100vh-3.5rem)] p-4 transition-all sm:p-6
          ${sidebarOpen ? "lg:ml-56" : "ml-0"}`}
      >
        {children}
      </main>
    </>
  );
}
