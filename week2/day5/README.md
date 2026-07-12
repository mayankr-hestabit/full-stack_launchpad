# Day 5 — Capstone: E-Commerce Product Listing

## What I Built
A fully functional mini e-commerce product listing page with:
- Real product data fetched from dummyjson.com API
- Search, filter by category, sort by price/rating/discount
- Sliding cart drawer with add/remove/quantity controls
- Mobile responsive layout

## Pages
- `index.html` — Landing page with hero, features, CTA
- `products.html` — Product listing with cart

## Key Concepts Used

### Fetch API
```javascript
const response = await fetch('https://dummyjson.com/products?limit=100');
const data = await response.json();
```
Same API we hit with curl in Week 1 Day 4 — now consumed in JavaScript.

### Async/Await
Pauses function execution until Promise resolves.
Cleaner than .then() chaining for sequential async operations.

### Array Methods
- `map` — transform products array into HTML cards
- `filter` — search and category filtering
- `sort` — price/rating/discount sorting
- `reduce` — calculate cart totals
- `find` — locate specific product by ID

### DOM Manipulation
- `innerHTML` — inject product cards into grid
- `classList.add/remove` — open/close cart drawer
- `createElement` — build category dropdown options
- `dataset` — store product IDs in HTML attributes

### Event Listeners
- `input` — search with debounce
- `change` — category and sort dropdowns
- `click` — add to cart, qty controls, remove
- `keydown` — Escape to close cart

### Debounce
Search input debounced at 300ms —
waits until user stops typing before filtering.

### Cart Logic
- Checks if product already in cart → increases quantity
- `reduce` calculates total items, subtotal, discount, final total
- Quantity 0 → automatically removes item


## What I Learned
- `fetch` is Promise-based — always use async/await with try/catch
- `response.ok` checks HTTP status before parsing JSON
- `loading="lazy"` on images improves page load performance
- `Set` removes duplicates when building category list
- Cart state lives in a JS array — same pattern as Todo app
- `body.style.overflow = 'hidden'` prevents background scroll when drawer is open
- Responsive grid: 4 cols desktop → 3 cols tablet → 2 cols mobile → 1 col small