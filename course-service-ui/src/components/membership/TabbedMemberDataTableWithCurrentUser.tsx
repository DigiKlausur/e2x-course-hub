import { useCurrentUser } from "@/hooks/me";
import { TabbedMemberDataTable } from "./TabbedMemberDataTable";
import type { TabbedMemberDataTableProps } from "./TabbedMemberDataTable";

export function TabbedMemberDataTableWithCurrentUser(
  props: Omit<TabbedMemberDataTableProps, "currentUser">,
) {
  const { data: currentUser } = useCurrentUser();
  if (!currentUser) return null;
  return <TabbedMemberDataTable {...props} currentUser={currentUser} />;
}
