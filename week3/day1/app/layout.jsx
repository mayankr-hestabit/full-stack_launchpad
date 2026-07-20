import "./globals.css";

export const metadata = {
  title: "Week 3 Launchpad",
  description: "Next.js + Tailwind — Week 3 project",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body className="bg-slate-100">{children}</body>
    </html>
  );
}
