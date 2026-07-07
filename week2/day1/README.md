# Day 1 — Semantic HTML5

## What I Built
A fully structured blog page using only semantic HTML — no CSS, no divs.
Covers semantic layout, forms with validation, media elements, and accessibility.

## Structure
day1/
|__blog.html

## Semantic Tags Used

| Tag | Purpose |
|-----|---------|
| `<header>` | Page and article headers |
| `<nav>` | Navigation menus (main + footer) |
| `<main>` | Primary page content wrapper |
| `<section>` | Thematic content groups |
| `<article>` | Self-contained blog posts |
| `<aside>` | Sidebar (search, about, categories, tags) |
| `<footer>` | Page and article footers |
| `<figure>` | Images with captions |
| `<figcaption>` | Caption for figure elements |
| `<time>` | Machine-readable dates |
| `<address>` | Author contact information |

## Forms & Validation
- `type="email"` — browser validates email format automatically
- `type="search"` — semantic search input
- `required` — browser blocks submit if empty
- `minlength="2"` — minimum character validation
- `aria-required="true"` — tells screen readers field is required
- `<select>` — dropdown with options
- `<textarea>` — multiline text input

## Media Elements
- `<video controls>` — embedded video with playback controls
- `<audio controls>` — embedded audio with playback controls
- `<source>` — specifies media file and type
- Fallback text for unsupported browsers

## Accessibility
| Feature | What it does |
|---------|--------------|
| `alt` text | Describes images for screen readers |
| `aria-label` | Gives elements a spoken name |
| `aria-labelledby` | Links sections to their headings by ID |
| `aria-required` | Marks required form fields for screen readers |
| `tabindex="0"` | Makes elements focusable via keyboard Tab |
| `role="banner"` | Identifies header landmark |
| `role="main"` | Identifies main content landmark |
| `role="contentinfo"` | Identifies footer landmark |
| `role="search"` | Identifies search form |

## Key Learnings
- Semantic tags describe meaning, not appearance — same visual result as divs but better for SEO and accessibility
- `<article>` = self-contained content (can be taken out of context and still make sense)
- `<section>` = thematic grouping (needs surrounding context to make sense)
- `<aside>` = related but not essential content (sidebar)
- Screen readers use landmark roles (`banner`, `main`, `contentinfo`) to let users jump between page regions
- Forms need `<label for="id">` paired with input `id` — clicking the label focuses the input
- `tabindex="0"` follows natural DOM order — never use positive tabindex values as they override natural order and confuse keyboard users
- Always provide fallback content inside `<video>` and `<audio>` for unsupported browsers

## What's Next
Day 2 — CSS Layout Mastery: adding Flexbox and Grid to make this blog page visually match the reference design.
