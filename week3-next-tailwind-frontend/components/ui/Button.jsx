// Button — an "atom": the smallest reusable UI piece, can't be broken down further.

const variantStyles = {
  primary: "bg-blue-600 text-white hover:bg-blue-700",
  warning: "bg-amber-500 text-white hover:bg-amber-600",
  success: "bg-emerald-600 text-white hover:bg-emerald-700",
  danger: "bg-red-600 text-white hover:bg-red-700",
  secondary: "bg-slate-200 text-slate-800 hover:bg-slate-300",
};

const sizeStyles = {
  sm: "px-3 py-1.5 text-sm",
  md: "px-4 py-2 text-sm",
  lg: "px-5 py-2.5 text-base",
};

export default function Button({
  children,
  variant = "primary",
  size = "md",
  onClick,
  type = "button",
  className = "",
  disabled = false,
}) {
  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled}
      className={`rounded-md font-medium transition-colors disabled:cursor-not-allowed disabled:opacity-50
        ${variantStyles[variant]} ${sizeStyles[size]} ${className}`}
    >
      {children}
    </button>
  );
}
