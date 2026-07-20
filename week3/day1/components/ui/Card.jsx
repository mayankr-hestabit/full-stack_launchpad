// Card — a "molecule": combines layout + optional colored variant + footer slot.
// Two ways to use it:
//   1. Plain wrapper: <Card><p>any content</p></Card>
//   2. Colored stat card (like the dashboard reference): pass `color` + `footer`

const colorStyles = {
  primary: "bg-blue-600 text-white",
  warning: "bg-amber-500 text-white",
  success: "bg-emerald-600 text-white",
  danger: "bg-red-600 text-white",
  none: "bg-white text-slate-800 border border-slate-200",
};

export default function Card({ children, color = "none", footer, className = "" }) {
  return (
    <div className={`overflow-hidden rounded-lg shadow-sm ${colorStyles[color]} ${className}`}>
      <div className="p-4">{children}</div>

      {footer && (
        <div
          className={`flex items-center justify-between px-4 py-2 text-xs font-medium
            ${color === "none" ? "border-t border-slate-100 text-slate-500" : "bg-black/10"}`}
        >
          {footer}
        </div>
      )}
    </div>
  );
}