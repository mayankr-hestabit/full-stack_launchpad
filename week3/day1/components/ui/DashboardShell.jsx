"use client";
 
import { useState } from "react";
import Navbar from "./Navbar";
import Sidebar from "./Sidebar";
 
export default function DashboardShell({ children }) {
  const [sidebarOpen, setSidebarOpen] = useState(true);
 
  return (
    <>
      <Navbar onToggleSidebar={() => setSidebarOpen(!sidebarOpen)} />
      <Sidebar open={sidebarOpen} />
 
      {/* main content shifts left when sidebar closes */}
      <main
        className={`mt-14 min-h-[calc(100vh-3.5rem)] p-6 transition-all
          ${sidebarOpen ? "ml-56" : "ml-0"}`}
      >
        {children}
      </main>
    </>
  );
}
 