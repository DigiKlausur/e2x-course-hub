import type { MembershipCapabilities } from "@api/types";
import type { CapabilityText } from "./types";

/** A member list's labels as shown in the UI, e.g. "Teaching Assistant(s)". */
export interface MemberLabels {
  singular: string;
  plural: string;
}

/** Shared by every member list: course owners and each term role. */
export const membershipCapabilityText = {
  view: ({ plural }: MemberLabels) => ({
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
  keyof MembershipCapabilities,
  (members: MemberLabels) => CapabilityText
>;
