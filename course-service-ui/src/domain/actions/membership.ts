import type { MemberListActions } from "@api/types";
import { type MembershipRole, memberLabels } from "@domain/roles";
import type { MemberLabels } from "@domain/roles";
import type { ActionGroupText, ActionText } from "./types";

/**
 * Shared by every member list: LMS admins, course creators, course owners and
 * each semester role.
 */
export const memberListActionText = {
  list: ({ plural }: MemberLabels) => ({
    label: `View ${plural}`,
    description: `See who the ${plural.toLowerCase()} are.`,
  }),
  add: ({ plural }: MemberLabels) => ({
    label: `Add ${plural}`,
    description: `Give users the role of ${plural.toLowerCase()}.`,
  }),
  remove: ({ singular }: MemberLabels) => ({
    label: `Remove ${singular}`,
    description: `Take the role of ${singular.toLowerCase()} away from a user.`,
  }),
} satisfies Record<
  keyof MemberListActions,
  (members: MemberLabels) => ActionText
>;

/**
 * The texts of one member list, e.g. for the students of a semester. The short
 * labels make it show as one row of chips under the list's name.
 */
export function memberListText(
  role: MembershipRole,
): ActionGroupText<MemberListActions> {
  const labels = memberLabels[role];
  return {
    title: labels.plural,
    list: { ...memberListActionText.list(labels), short: "View" },
    add: { ...memberListActionText.add(labels), short: "Add" },
    remove: { ...memberListActionText.remove(labels), short: "Remove" },
  };
}
