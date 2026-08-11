interface BadgeProps {
  variant?: "active" | "archived" | "default";
  children: string;
}

const variantClasses: Record<NonNullable<BadgeProps["variant"]>, string> = {
  active: "bg-green-100 text-green-800",
  archived: "bg-gray-100 text-gray-600",
  default: "bg-blue-100 text-blue-800",
};

export function Badge({ variant = "default", children }: BadgeProps) {
  return (
    <span
      className={`px-3 py-1 rounded-full text-xs font-semibold ${variantClasses[variant]}`}
    >
      {children}
    </span>
  );
}
