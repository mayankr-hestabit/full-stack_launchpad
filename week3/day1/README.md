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

# Week 3 — Day 2: Adding Buttons, Badges and Cards to the Dashboard

# UI Component Docs

Usage reference for the reusable component library in `/components/ui/`.

---

## Button

Variant + size driven button.

```jsx
import Button from "@/components/ui/Button";

<Button variant="primary" size="md" onClick={() => console.log("clicked")}>
  Save
</Button>
```

**Props**
| Prop | Type | Default | Options |
|---|---|---|---|
| `variant` | string | `"primary"` | `primary`, `warning`, `success`, `danger`, `secondary` |
| `size` | string | `"md"` | `sm`, `md`, `lg` |
| `disabled` | boolean | `false` | — |
| `type` | string | `"button"` | `button`, `submit` |

---

## Input

Controlled text input — value/onChange must be supplied by the parent.

```jsx
import Input from "@/components/ui/Input";
import { useState } from "react";

const [email, setEmail] = useState("");


## Badge

Small colored status label.

```jsx
import Badge from "@/components/ui/Badge";

<Badge variant="success">Active</Badge>
```

**Props**
| Prop | Type | Default | Options |
|---|---|---|---|
| `variant` | string | `"neutral"` | `primary`, `warning`, `success`, `danger`, `neutral` |

---

## Card

Flexible container. Plain mode or colored "stat card" mode with a footer slot.

```jsx
import Card from "@/components/ui/Card";
import { ChevronRight } from "lucide-react";

// Plain card
<Card>
  <p>Any content here</p>
</Card>

// Colored stat card with footer
<Card
  color="primary"
  footer={
    <div className="flex w-full items-center justify-between">
      <span>View Details</span>
      <ChevronRight size={14} />
    </div>
  }
>
  <p className="text-lg font-semibold">Primary Card</p>
</Card>
```

**Props**
| Prop | Type | Default | Options |
|---|---|---|---|
| `color` | string | `"none"` | `primary`, `warning`, `success`, `danger`, `none` |
| `footer` | ReactNode | — | any JSX, rendered in a separate footer strip |

---

## Modal

Controlled dialog. Parent owns the `open` boolean.

```jsx
import Modal from "@/components/ui/Modal";
import { useState } from "react";

const [open, setOpen] = useState(false);

<>
  <Button onClick={() => setOpen(true)}>Open Modal</Button>

  <Modal open={open} onClose={() => setOpen(false)} title="Confirm Action">
    <p>Are you sure?</p>
  </Modal>
</>
```

**Props**
| Prop | Type | Required |
|---|---|---|
| `open` | boolean | Yes |
| `onClose` | function | Yes |
| `title` | string | No |
| `children` | ReactNode | Yes (modal body content) |

---

## Design Principles Used

- **Controlled components** — Input and Modal never manage their own open/value state internally; the parent always owns it and passes it down. Keeps data flow predictable (unidirectional).
- **Variant props over separate components** — one `Button`/`Badge`/`Card` component handles all color states via a `variant`/`color` prop, instead of `PrimaryButton`, `WarningButton`, etc.
- **Composition via `children`** — Card and Modal accept arbitrary JSX as children rather than fixed fields, so they stay reusable across very different content.