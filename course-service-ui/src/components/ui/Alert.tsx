import type { ReactNode } from "react";

type AlertVariant = "error" | "warning" | "info";

const variantClasses: Record<AlertVariant, string> = {
  error: "bg-red-50 border-red-200 text-red-800",
  warning: "bg-amber-50 border-amber-200 text-amber-800",
  info: "bg-sky-50 border-sky-200 text-sky-900",
};

interface AlertProps {
  variant?: AlertVariant;
  title?: string;
  children: ReactNode;
  className?: string;
}

export function Alert({
  variant = "error",
  title,
  children,
  className = "",
}: AlertProps) {
  return (
    <div
      // role="alert" so a failure that appears after a button press is
      // announced, rather than silently changing the page for screen readers.
      role="alert"
      className={`rounded-lg border px-4 py-3 text-sm ${variantClasses[variant]} ${className}`}
    >
      {title && <p className="font-semibold mb-0.5">{title}</p>}
      <div>{children}</div>
    </div>
  );
}
