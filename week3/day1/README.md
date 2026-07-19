# Week 3 — Day 1: Dashboard Layout Skeleton

Next.js (App Router) + TailwindCSS — dashboard header and sidebar skeleton, built as part of the Week 3 Advance Frontend track.

## Objective

Build a Dashboard Layout skeleton (header + sidebar) matching the SB Admin reference design, using Next.js fundamentals and Tailwind utility-first styling.

## Tech Stack

- **Next.js 15** (App Router)
- **TailwindCSS**
- **lucide-react** — icon set

## Folder Structure

```
app/
├── layout.jsx          # Root layout — wraps every page in DashboardShell
├── page.jsx             # Home/dashboard page content
└── globals.css          # Tailwind base styles

components/
└── ui/
    ├── DashboardShell.jsx   # Client wrapper — holds sidebar open/close state
    ├── Navbar.jsx            # Top navigation bar (hamburger, brand, search, user menu)
    └── Sidebar.jsx           # Left navigation (Core / Interface / Addons sections)
```

## Components Built

| Component | Type | Responsibility |
|---|---|---|
| `DashboardShell` | Client Component | Owns `sidebarOpen` state; connects Navbar's toggle button to Sidebar's visibility |
| `Navbar` | Client Component | Top bar — hamburger menu, brand name, search input, user dropdown |
| `Sidebar` | Client Component | Left nav — grouped links (Core, Interface, Addons) with collapsible sub-items |

`layout.jsx` and `page.jsx` remain **Server Components** — no client-side interactivity is needed at that level, so no `"use client"` directive is used there. Only components requiring `useState` (dropdown, toggle) are marked as Client Components.

## Features Implemented

- Fixed top navbar with hamburger menu, brand, search bar, and user profile dropdown
- Fixed left sidebar with grouped, labeled navigation sections
- Collapsible sub-menus within sidebar links (e.g. "Layouts", "Pages")
- **Working sidebar toggle** — clicking the hamburger slides the sidebar in/out and reflows the main content, using React state lifted into a shared parent (`DashboardShell`)
- Responsive base layout using Tailwind's fixed positioning + spacing utilities

## Key Concepts Applied

- **App Router file conventions** — `layout.jsx` persists across navigation, doesn't re-render on route change
- **Server vs Client Components** — components default to Server; `"use client"` opted in only where interactivity (state, event handlers) is required
- **Lifting state up** — shared state (`sidebarOpen`) moved to the nearest common parent of Navbar and Sidebar, passed down as a value (`open`) and a function (`onToggleSidebar`)
- **Component composition** — small reusable sub-components (`SidebarSectionLabel`, `SidebarLink`) instead of repeated JSX
- **Tailwind utility-first styling** — spacing (`p-`, `m-`, `gap-`), color scale (`slate-900`, `slate-100`), fixed positioning offsets

## Setup & Run

```bash
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

## Notes / Next Steps

- Day 2 will introduce the reusable component library (`Button`, `Input`, `Card`, `Badge`, `Modal`) and stat cards inside the dashboard content area.
- Dev-mode "N" indicator (bottom-left) disabled via `devIndicators: false` in `next.config.js` — dev-only Next.js tooling, not part of the shipped app.