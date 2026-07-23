# Week 3 — Advance Frontend (Next.js + TailwindCSS)

**Internship project — Week 3 track**
A single, evolving Next.js + TailwindCSS project built day-by-day across a 5-day internship sprint. This README documents the full build — objectives, what was implemented, the concepts behind each decision, and lessons learned — intended to be readable on its own by a reviewer who wasn't present for the build.

Progress is tracked via git tags (`day1` → `day5`) rather than duplicated folders, since this is one repo that evolved incrementally.

---

## Table of Contents

1. [Tech Stack](#tech-stack)
2. [Getting Started](#getting-started)
3. [Project Structure](#project-structure)
4. [Routes](#routes)
5. [Day 1 — Dashboard Layout Skeleton](#day-1--dashboard-layout-skeleton)
6. [Day 2 — Reusable Component Library](#day-2--reusable-component-library)
7. [Day 3 — Routing + Nested Layouts](#day-3--routing--nested-layouts)
8. [Day 4 — Responsive Landing Page + Optimization](#day-4--responsive-landing-page--optimization)
9. [Day 5 — Capstone](#day-5--capstone)
10. [Component Library Reference](#component-library-reference)
11. [Core Concepts Glossary](#core-concepts-glossary)
12. [Known Issues / Fixed Bugs](#known-issues--fixed-bugs)
13. [Lessons Learned](#lessons-learned)
14. [Screenshots](#screenshots)
15. [Submission Checklist](#submission-checklist)

---

## Tech Stack

| Tool | Purpose |
|---|---|
| **Next.js 15** (App Router) | React framework — file-based routing, layouts, Server/Client Components, image & font optimization |
| **TailwindCSS v4** | Utility-first CSS — all styling in this project is done via utility classes, no separate CSS files per component |
| **lucide-react** | Icon set — used throughout Navbar, Sidebar, feature cards, and buttons |

No backend, no database, no real authentication — this is a **frontend-only** project. Login and data tables use static/mocked data by design.

---

## Getting Started

```bash
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

To view a specific day's state in git history:
```bash
git checkout day1   # or day2, day3, day4, day5
git checkout main   # return to latest
```

---

## Project Structure

```
app/
├── layout.jsx                  # Root layout — <html>/<body>, next/font (Inter), base metadata
├── globals.css                  # Tailwind import + @theme font config
├── page.jsx                      # "/" — public landing page
├── about/
│   └── page.jsx                   # "/about" — public about page
├── login/
│   └── page.jsx                    # "/login" — static login form
└── dashboard/
    ├── layout.jsx                   # NESTED layout — adds Navbar + Sidebar, applies only within /dashboard/**
    ├── page.jsx                      # "/dashboard" — colored stat cards
    ├── users/
    │   └── page.jsx                    # "/dashboard/users" — mocked data table
    ├── profile/
    │   └── page.jsx                     # "/dashboard/profile" — profile view + edit modal
    ├── charts/
    │   └── page.jsx                      # "/dashboard/charts" — placeholder route
    └── tables/
        └── page.jsx                       # "/dashboard/tables" — placeholder route

components/
└── ui/
    ├── Button.jsx           # Atom — variant + size driven button
    ├── Input.jsx              # Atom — controlled text input, label + error state
    ├── Badge.jsx                # Atom — small colored status label
    ├── Card.jsx                   # Molecule — plain/colored container, optional footer
    ├── Modal.jsx                    # Molecule — controlled dialog overlay
    ├── DashboardShell.jsx             # Organism — owns sidebar open/close state, mobile-responsive
    ├── Navbar.jsx                      # Organism — dashboard top bar
    ├── Sidebar.jsx                       # Organism — dashboard left nav, routed + active-state aware
    └── PublicNav.jsx                       # Organism — nav for public (non-dashboard) pages

public/
├── hero.png                # Landing page hero illustration
├── avatar1.png              # Testimonial avatar
├── avatar2.png                # Testimonial avatar
└── avatar3.png                  # Testimonial avatar

UI-COMPONENT-DOCS.md    # Standalone usage reference for every component (also embedded below)
README.md                 # This file
```

**Why this structure?** It follows atomic design: `Button`/`Input`/`Badge` are atoms (can't be broken down further), `Card`/`Modal` are molecules (combine atoms + layout), `Sidebar`/`Navbar`/`DashboardShell` are organisms (assemble molecules into a functional section), and each `page.jsx` composes organisms + molecules into a full page.

---

## Routes

| Route | Layout chain | Description |
|---|---|---|
| `/` | Root only | Public landing page — hero, features, testimonials, footer |
| `/about` | Root only | Public about page |
| `/login` | Root only | Static login form (no real auth) |
| `/dashboard` | Root → Dashboard | Colored stat cards |
| `/dashboard/users` | Root → Dashboard | Mocked users table |
| `/dashboard/profile` | Root → Dashboard | Profile view + edit modal |
| `/dashboard/charts` | Root → Dashboard | Placeholder |
| `/dashboard/tables` | Root → Dashboard | Placeholder |

Routes under `/dashboard/**` all render inside the dark Navbar/Sidebar shell. `/`, `/about`, and `/login` do not — they only inherit the root layout.

---

## Day 1 — Dashboard Layout Skeleton

**Objective:** Build a dashboard header + sidebar skeleton matching the SB Admin reference design.

**Topics covered:** File-based routing, `app/` directory structure, layouts, static vs client components, Tailwind installation and utility classes.

**What was built:**
- `Navbar.jsx` — fixed top bar: hamburger menu button, brand name, search input, user profile dropdown
- `Sidebar.jsx` — fixed left nav: grouped sections (Core / Interface / Addons), collapsible sub-menus for "Layouts" and "Pages"
- `DashboardShell.jsx` — a Client Component wrapper that owns the sidebar's open/closed state and connects the Navbar's hamburger button to the Sidebar's visibility

**Concepts applied:**
- **App Router file conventions** — `layout.jsx` persists across navigation and does not re-render when the route changes underneath it; this is what makes a shared sidebar/navbar not "flicker" between page loads.
- **Server vs Client Components** — every component in `/app` is a Server Component by default (renders to HTML on the server, ships no JS for that component). `"use client"` is added only where a component needs `useState`, event handlers, or browser APIs — here, that's `Navbar`, `Sidebar`, and `DashboardShell`, since they need interactivity (dropdown, toggle).
- **Lifting state up** — Navbar and Sidebar are sibling components with no direct way to communicate. The shared `sidebarOpen` state was moved up to their nearest common parent (`DashboardShell`), which passes it down as a **value** (`open`, to Sidebar) and a **function** (`onToggleSidebar`, to Navbar).

---

## Day 2 — Reusable Component Library

**Objective:** Build a `Button`, `Input`, `Card`, `Badge`, `Modal` component library and use it to build the dashboard's stat cards.

**Topics covered:** Flexbox vs Grid, atomic design/component mindset, reusable components with props.

**What was built:**
- Five components, each driven by a `variant` (or `color`) prop rather than being duplicated per color/state
- Four colored stat cards (Primary/Warning/Success/Danger) built with `Card`, laid out with CSS **Grid**
- `UI-COMPONENT-DOCS.md` — a standalone usage reference for the library

**Concepts applied:**
- **Flexbox vs Grid** — Flexbox is one-dimensional (a single row or column); Grid is two-dimensional (rows and columns together). The stat-card row uses `grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4` (2D, responsive), while each card's internal footer row uses `flex justify-between` (1D).
- **Variant props over duplicated components** — one `Button` handles five color states via a `variant` prop, instead of `PrimaryButton`, `WarningButton`, etc. This is the core mechanism that makes the library "reusable" rather than just a folder of similar-looking components.
- **Controlled components** — `Input` and `Modal` never manage their own internal state (text value, open/closed); the parent always owns and passes it down via props. This keeps data flow predictable (unidirectional), and is a pattern React encourages broadly.

---

## Day 3 — Routing + Nested Layouts

**Objective:** Multi-page structure (`/`, `/about`, `/dashboard`, `/dashboard/profile`) with shared navigation.

**Topics covered:** Next.js routing conventions, nested layouts, shared navigation, Client vs Server Components (revisited in a routing context).

**What was built:**
- Split the app into **public routes** (`/`, `/about` — no dashboard chrome) and **dashboard routes** (`/dashboard/**` — Navbar + Sidebar applied via a nested layout)
- `app/dashboard/layout.jsx` — a nested layout that wraps `DashboardShell` around every route inside `app/dashboard/`
- `Sidebar.jsx` rebuilt to use real `next/link` navigation (previously static buttons) with `usePathname()`-driven active-state highlighting
- `/dashboard/profile` — introduced `useRouter()` for a "Go Back" button

**Concepts applied:**
- **Nested layouts** — a `layout.jsx` file applies to everything in its folder and below. Next.js composes layouts automatically based on folder position — root layout wraps the whole app, `dashboard/layout.jsx` wraps only `/dashboard` and its sub-routes. No manual composition/wiring required; it's purely structural.
- **`Link` vs `useRouter`** — `<Link href="...">` is for anything a user directly clicks: it renders a real `<a>` tag (correct for SEO and accessibility, supports right-click → open in new tab). `useRouter()` (`router.push()`, `router.back()`) is for **programmatic** navigation triggered by logic rather than a click on a link — e.g. redirecting after a form submits, or a "Back" button with no fixed destination.
- **`usePathname()`** — a hook that reads the current URL client-side. Used to compare against each Sidebar link's `href` and apply an active/highlighted style dynamically, replacing the hardcoded `active` prop from Day 2.

---

## Day 4 — Responsive Landing Page + Optimization

**Objective:** Build a responsive SaaS-style landing page (hero, features grid, testimonials, footer) with image and font optimization and SEO metadata.

**Topics covered:** `next/image`, responsive images, typography and SEO, `next/font`.

**What was built:**
- Full landing page at `/`: hero section with CTA buttons, a 4-item features grid, a 3-item testimonials grid, and a footer
- Fully responsive: stacked/single-column on mobile, multi-column from `sm`/`md`/`lg` breakpoints up
- `next/image` used for the hero illustration and testimonial avatars
- `next/font/google` (Inter) wired into the root layout and hooked into Tailwind via `@theme { --font-sans: var(--font-inter); }`
- Expanded `metadata` export on the landing page, including Open Graph fields

**Concepts applied:**
- **Why `next/image` over `<img>`** — it auto-generates responsive image sizes, lazy-loads by default (opt out with `priority` for above-the-fold images), automatically serves modern formats (WebP/AVIF) where supported, and reserves layout space via `width`/`height` to prevent layout shift while loading.
- **Why `next/font` over a `<link>` to Google Fonts** — a standard Google Fonts `<link>` tag means a render-blocking network request to Google's servers at page-load time. `next/font` downloads the font file at **build time** and self-hosts it alongside the app — zero runtime request to an external domain, and no "flash of unstyled text" from font-swapping.
- **Per-page metadata** — `page.jsx` files can export their own `metadata` object that overrides/extends the root layout's metadata for that specific route. This is what controls the browser tab title, search engine snippet, and social-media share preview per page.
- **Responsive breakpoints in Tailwind** — `sm:`, `md:`, `lg:` prefixes apply a utility class only from that screen width upward (mobile-first). E.g. `flex-col md:flex-row` stacks on small screens, goes side-by-side from 768px up.

---

## Day 5 — Capstone

**Objective:** Full multi-page UI — `/login`, `/dashboard`, `/dashboard/users`, `/dashboard/profile` — using only the reusable component library, with clean routing and mobile responsiveness.

**What was built:**
- `/login` — static form using `Input` + `Button`; submits with basic validation and redirects to `/dashboard` (no real backend/auth)
- `/dashboard/users` — a mocked data table (`name`, `email`, `role`, `status`) using `Card` + `Badge`, wrapped in `overflow-x-auto` so it scrolls horizontally on narrow screens instead of squashing columns
- `/dashboard/profile` — rebuilt to combine **all five** library components: `Card` for the layout, `Badge` for status, `Button` for actions, and a `Modal` + `Input` pair for an "Edit Profile" flow
- **Mobile responsiveness audit and fix** (see [Known Issues](#known-issues--fixed-bugs) below) — this was the most significant fix of the whole project

**Concepts applied:**
- **Composing a full feature from existing atoms** — no new base components were created on Day 5; every UI element on every page (login, table, profile) was built purely by combining `Button`/`Input`/`Badge`/`Card`/`Modal`. This is the actual payoff of investing in a component library on Day 2 — later days get faster and more consistent because of it.
- **Static/mocked data patterns** — the users table uses a hardcoded array rather than a fetch call, since there's no backend in this project. In a real app, this array would be replaced by data from an API route or database call, without needing to change the table's rendering logic.
- **Responsive tables** — tables don't reflow well with Flexbox/Grid the way cards do; the standard pattern is a horizontally scrollable container (`overflow-x-auto` + a `min-w` on the table itself) rather than trying to force columns to shrink illegibly.

---

## Component Library Reference

### Button

```jsx
import Button from "@/components/ui/Button";

<Button variant="primary" size="md" onClick={() => console.log("clicked")}>
  Save
</Button>
```

| Prop | Type | Default | Options |
|---|---|---|---|
| `variant` | string | `"primary"` | `primary`, `warning`, `success`, `danger`, `secondary` |
| `size` | string | `"md"` | `sm`, `md`, `lg` |
| `disabled` | boolean | `false` | — |
| `type` | string | `"button"` | `button`, `submit` |

### Input

```jsx
import Input from "@/components/ui/Input";

<Input
  label="Email"
  type="email"
  value={email}
  onChange={(e) => setEmail(e.target.value)}
  error={!email ? "Email is required" : ""}
/>
```

| Prop | Type | Required |
|---|---|---|
| `label` | string | No |
| `type` | string | No (default `"text"`) |
| `value` | string | Yes |
| `onChange` | function | Yes |
| `error` | string | No |

### Badge

```jsx
import Badge from "@/components/ui/Badge";

<Badge variant="success">Active</Badge>
```

| Prop | Type | Default | Options |
|---|---|---|---|
| `variant` | string | `"neutral"` | `primary`, `warning`, `success`, `danger`, `neutral` |
| `className` | string | `""` | any additional Tailwind classes |

### Card

```jsx
import Card from "@/components/ui/Card";
import { ChevronRight } from "lucide-react";

// Plain card
<Card><p>Any content</p></Card>

// Colored stat card with footer
<Card
  color="primary"
  footer={<div className="flex w-full items-center justify-between"><span>View Details</span><ChevronRight size={14} /></div>}
>
  <p className="text-lg font-semibold">Primary Card</p>
</Card>

// Table wrapper with no inner padding
<Card bodyClassName="p-0"><table>...</table></Card>
```

| Prop | Type | Default | Options |
|---|---|---|---|
| `color` | string | `"none"` | `primary`, `warning`, `success`, `danger`, `none` |
| `footer` | ReactNode | — | any JSX, rendered in a separate footer strip |
| `bodyClassName` | string | `"p-4"` | override inner padding (e.g. `"p-0"` for tables) |

### Modal

```jsx
import Modal from "@/components/ui/Modal";
import { useState } from "react";

const [open, setOpen] = useState(false);

<Modal open={open} onClose={() => setOpen(false)} title="Confirm Action">
  <p>Are you sure?</p>
</Modal>
```

| Prop | Type | Required |
|---|---|---|
| `open` | boolean | Yes |
| `onClose` | function | Yes |
| `title` | string | No |
| `children` | ReactNode | Yes |

**Design principles used across the library:**
- **Controlled components** — `Input` and `Modal` never manage their own open/value state; the parent always owns it. Keeps data flow predictable.
- **Variant props over separate components** — one component per concept, styled via props, instead of a component per visual state.
- **Composition via `children`** — `Card` and `Modal` accept arbitrary JSX rather than fixed fields, so they stay reusable across very different content.

---

## Core Concepts Glossary

Quick reference for concepts referenced above — written as answers to how they might be asked in review:

| Concept | Explanation |
|---|---|
| **Server Component** | Default in `/app`. Renders to HTML on the server, ships no JS to the browser for that component. Cannot use `useState`/`useEffect`/event handlers. |
| **Client Component** | Opted into via `"use client"` at the top of the file. Needed for interactivity — state, event handlers, browser-only APIs. |
| **Lifting state up** | Moving shared state to the nearest common parent of two components that need to coordinate, so it can be passed down to both. |
| **Layout (App Router)** | A `layout.jsx` file that wraps every `page.jsx` in its folder and below; persists across navigation within that scope. |
| **Nested layout** | A layout defined in a subfolder — applies only to routes inside that subfolder, composed automatically with parent layouts. |
| **Controlled component** | A component whose state (value, open/closed) is owned entirely by its parent via props, not managed internally. |
| **`next/image`** | Next.js's optimized image component — responsive sizing, lazy loading, automatic modern-format serving, layout-shift prevention. |
| **`next/font`** | Build-time font self-hosting — avoids runtime requests to external font providers. |
| **Flexbox vs Grid** | Flex = one-dimensional layout (single row/column). Grid = two-dimensional layout (rows + columns together). |
| **Atomic design** | Atoms (Button, Input, Badge) → Molecules (Card, Modal) → Organisms (Sidebar, Navbar) → Pages. |

---

## Known Issues / Fixed Bugs

### Fixed: Sidebar broke mobile layout (found + fixed Day 5)

**The bug:** `DashboardShell` defaulted `sidebarOpen` to `true` unconditionally, and `main` applied `ml-56` whenever the sidebar was open — with no distinction between screen sizes. On a ~375px-wide phone screen, this left under 150px of usable content width.

**The fix:** Sidebar now defaults to **closed** on load, and opens automatically only on `lg+` screens (1024px+) via a `useEffect` checking `window.innerWidth`. On mobile/tablet, the sidebar overlays the content (with a dismissible dark backdrop) instead of pushing it, and `main` only gets `lg:ml-56` — never on smaller screens.

**Why it wasn't caught earlier:** Days 1–4 were primarily tested at desktop width during development; the mobile-responsiveness requirement wasn't explicitly exercised until Day 5's checklist called for it directly.

### Not implemented (explicitly out of scope)
- Real authentication on `/login` — static UI only, per the curriculum's "no backend" instruction
- Area/bar charts and the full DataTable seen in the original SB Admin reference — never listed as a required deliverable in the written exercises; `/dashboard/charts` and `/dashboard/tables` exist as placeholder routes only

---

## Lessons Learned

- **Server vs Client Components isn't a stylistic choice — it's a boundary you design around.** Deciding early which pieces genuinely need interactivity (and keeping everything else server-rendered) shaped the whole component structure from Day 1 onward, not just individual file headers.
- **A component library only proves its value once something reuses it under different pressure.** `Button`/`Card`/`Badge` didn't feel obviously "worth it" until Day 5, when the same five components assembled a login form, a data table, and a profile editor — three UIs that don't look alike, built from the same primitives.
- **Nested layouts remove a whole category of repetition bugs.** Manually re-importing a sidebar/navbar into every dashboard page would mean repeating the same code in five files — and forgetting it in a sixth. One `dashboard/layout.jsx` guarantees consistency structurally, not by discipline.
- **"Responsive" has to be checked per component, not assumed at the end.** The dashboard shell looked correct on desktop for four straight days. The mobile-breaking bug (content squeezed under 150px) wasn't caught until Day 5's explicit mobile-responsiveness requirement forced a real check at narrow widths — a reminder to test breakpoints continuously, not just once at the end.
- **Controlled components keep state predictable as an app grows.** Every form field and dialog in this project is driven by state owned in a parent component. By Day 5, with multiple interactive pieces per page (edit modal + form + table), this made it straightforward to reason about what triggers what, instead of tracking hidden internal state scattered across components.
- **Git tags per milestone are more useful than folder duplication.** Tagging `day1` through `day5` made it possible to show "what did Day 2 look like" on demand without maintaining five separate, drifting copies of the project.

---

## Screenshots

> Add before submitting:
> - `screenshots/dashboard.png` — desktop dashboard view
> - `screenshots/login.png` — login form
> - `screenshots/users.png` — users table
> - `screenshots/profile.png` — profile page with edit modal open
> - `screenshots/mobile.png` — mobile view showing the sidebar overlay behavior

---

## Submission Checklist

- [ ] `npm run dev` runs cleanly with no console errors
- [ ] All routes in the [Routes](#routes) table load correctly
- [ ] Sidebar navigation highlights the active route
- [ ] Login form validates empty fields and redirects to `/dashboard` on submit
- [ ] Users table scrolls horizontally on narrow viewports instead of breaking
- [ ] Profile edit modal opens, accepts input, and closes correctly
- [ ] Sidebar overlays (not pushes) content below 1024px width
- [ ] Screenshots added to `screenshots/` and linked above
- [ ] Project folder renamed to `week3-next-tailwind-frontend` (if not already)
- [ ] All 5 days committed and tagged in git (`git tag` should list `day1`–`day5`)