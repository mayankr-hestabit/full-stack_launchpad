// Input — an "atom". Controlled component: value + onChange are passed in from the parent,
// this component never manages its own text state.

export default function Input({
  label,
  type = "text",
  placeholder = "",
  value,
  onChange,
  error = "",
  className = "",
}) {
  return (
    <div className={className}>
      {label && (
        <label className="mb-1 block text-sm font-medium text-slate-700">
          {label}
        </label>
      )}
      <input
        type={type}
        placeholder={placeholder}
        value={value}
        onChange={onChange}
        className={`w-full rounded-md border px-3 py-2 text-sm outline-none transition-colors
          focus:border-blue-500 focus:ring-1 focus:ring-blue-500
          ${error ? "border-red-500" : "border-slate-300"}`}
      />
      {error && <p className="mt-1 text-xs text-red-600">{error}</p>}
    </div>
  );
}
