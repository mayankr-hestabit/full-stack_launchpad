// Badge — an "atom". Small colored label, commonly used inside tables/cards later (Day 5 user listing).

const badgeStyles = {
  primary: "bg-blue-100 text-blue-700",
  warning: "bg-amber-100 text-amber-700",
  success: "bg-emerald-100 text-emerald-700",
  danger: "bg-red-100 text-red-700",
  neutral: "bg-slate-100 text-slate-700",
};

export default function Badge({ children, variant = "neutral", className = "" }) {
  return (
    <span
      className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${badgeStyles[variant]} ${className}`}
    >
      {children}
    </span>
  );
}
