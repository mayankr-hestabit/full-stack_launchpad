# Day 2 — CSS Layout Mastery

## What I Built
Styled blog layout using Flexbox and CSS Grid.

## CSS Concepts Used

### Flexbox
- Navbar: logo left, links right using `justify-content: space-between`
- Hero: centered content using `align-items: center`
- Sidebar: vertical stack using `flex-direction: column`
- Tags: horizontal wrap using `flex-wrap: wrap`

### CSS Grid
- Page layout: `grid-template-columns: 2fr 1fr` (content + sidebar)
- Article cards: `grid-template-columns: repeat(2, 1fr)` (2 column grid)
- Footer: `grid-template-columns: repeat(3, 1fr)` (3 column grid)

### CSS Variables
- Defined colors, spacing, font sizes in `:root`
- Reused everywhere with `var(--variable-name)`

### Box Model
- `box-sizing: border-box` on everything via `*` selector
- Consistent padding and margin using spacing variables

### Responsive Design
- `@media (max-width: 768px)` collapses grid to single column
- `@media (max-width: 480px)` wraps nav links on very small screens
- Mobile-first approach

### Transitions & Hover Effects
- Cards lift on hover: `transform: translateY(-4px)`
- Nav links change color on hover
- Tags change background on hover

## Key Learnings
- Flexbox for one-dimensional layouts (row or column)
- Grid for two-dimensional layouts (rows AND columns)
- CSS variables make design changes instant across entire stylesheet
- `position: sticky` keeps navbar visible while scrolling
- `object-fit: cover` prevents images from stretching
- Always reset margin/padding with `* { margin: 0; padding: 0 }`
