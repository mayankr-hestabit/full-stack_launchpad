import "./globals.css";
import DashboardShell from "@/components/ui/DashboardShell";

export const metadata = {
  title: "Dashboard | Week 3 Launchpad",
  description: "Next.js + Tailwind dashboard skeleton",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body className="bg-slate-100">
        <DashboardShell>{children}</DashboardShell>
      </body>
    </html>
  );
}