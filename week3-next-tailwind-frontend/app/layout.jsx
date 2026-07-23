import "./globals.css";
import { Inter } from "next/font/google";

// next/font downloads this at BUILD TIME and self-hosts it — no runtime
// request to Google's servers, no layout shift from font-swapping.
const inter = Inter({
  subsets: ["latin"],
  display: "swap",
  variable: "--font-inter",
});

export const metadata = {
  title: "Week 3 Launchpad",
  description: "Next.js + Tailwind — Week 3 internship project",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en" className={inter.variable}>
      <body className="bg-slate-100 font-sans">{children}</body>
    </html>
  );
}
