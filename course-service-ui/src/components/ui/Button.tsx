import type { ButtonHTMLAttributes, ReactNode } from "react";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "danger";
  children: ReactNode;
}

const variantClasses: Record<NonNullable<ButtonProps["variant"]>, string> = {
  primary:
    "bg-hbrs-dark-blue text-white border border-hbrs-dark-blue hover:bg-hbrs-medium-blue hover:border-hbrs-medium-blue",
  secondary:
    "bg-white text-hbrs-dark-blue border border-hbrs-dark-blue hover:bg-hbrs-light-blue",
  danger: "bg-red-600 text-white border border-red-600 hover:bg-red-700",
};

export function Button({
  variant = "primary",
  children,
  className = "",
  ...props
}: ButtonProps) {
  return (
    <button
      {...props}
      className={`rounded-lg px-4 py-2.5 text-sm font-semibold transition-colors disabled:opacity-50 disabled:cursor-not-allowed ${variantClasses[variant]} ${className}`}
    >
      {children}
    </button>
  );
}
