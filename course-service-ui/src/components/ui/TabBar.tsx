import { NavLink } from "react-router-dom";

interface Tab {
  label: string;
  to: string;
}

interface TabBarProps {
  tabs: Tab[];
}

export function TabBar({ tabs }: TabBarProps) {
  return (
    <nav className="bg-white border-b border-gray-200 flex gap-7 px-10">
      {tabs.map((tab) => (
        <NavLink
          key={tab.to}
          to={tab.to}
          end
          className={({ isActive }) =>
            `py-[18px] text-sm cursor-pointer border-b-[3px] transition-colors ${
              isActive
                ? "border-hbrs-dark-blue text-hbrs-dark-blue font-semibold"
                : "border-transparent text-gray-500 hover:text-gray-800"
            }`
          }
        >
          {tab.label}
        </NavLink>
      ))}
    </nav>
  );
}
