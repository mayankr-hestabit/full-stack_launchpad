import DashboardShell from "@/components/ui/DashboardShell";

// This layout ONLY wraps routes inside /app/dashboard/**
// It nests INSIDE the root layout automatically — Next.js merges them
// based on folder position, no manual composition needed.

export default function DashboardLayout({ children }) {
  return <DashboardShell>{children}</DashboardShell>;
}
