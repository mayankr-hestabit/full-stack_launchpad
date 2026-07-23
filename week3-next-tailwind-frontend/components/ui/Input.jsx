// Input — an "atom". Controlled component: value + onChange are passed in from the parent,
// this component never manages its own text state.
//
// Added `icon`: an optional lucide-react icon component rendered inside the field
// (left side) — used for things like the login page's username/lock icons.
// Added `variant="filled"`: a softer gray-filled style (matches Image 1 reference)
// as an alternative to the default bordered/white style.

export default function Input({
  label,
  type = "text",
  placeholder = "",
  value,
  onChange,
  error = "",
  icon: Icon,
  variant = "default",
  className = "",
}) {
  const filled = variant === "filled";

  return (
    <div className={className}>
      {label && (
        <label className="mb-1 block text-sm font-medium text-slate-700">
          {label}
        </label>
      )}

      <div className="relative">
        {Icon && (
          <Icon
            size={18}
            className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-slate-400"
          />
        )}
        <input
          type={type}
          placeholder={placeholder}
          value={value}
          onChange={onChange}
          className={`w-full rounded-md text-sm outline-none transition-colors
            ${Icon ? "pl-10 pr-3" : "px-3"} py-2.5
            ${filled
              ? "border border-slate-200 bg-slate-100 placeholder:text-slate-400 focus:border-slate-300"
              : "border focus:border-blue-500 focus:ring-1 focus:ring-blue-500"}
            ${!filled && (error ? "border-red-500" : "border-slate-300")}`}
        />
      </div>
      {error && <p className="mt-1 text-xs text-red-600">{error}</p>}
    </div>
  );
}
