import { useCurrentUser } from "@hooks/me";
import type { MemberDataTableProps } from "./MemberDataTable";
import { MemberDataTable } from "./MemberDataTable";

// MemberDataTableWithCurrentUser.tsx
export function MemberDataTableWithCurrentUser(
  props: Omit<MemberDataTableProps, "currentUser">,
) {
  const { data: currentUser } = useCurrentUser();
  if (!currentUser) return null;
  return <MemberDataTable {...props} currentUser={currentUser} />;
}
