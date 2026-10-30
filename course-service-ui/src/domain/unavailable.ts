import type { UnavailableSelection } from "@api/types";
import { spawnRoleLabels } from "@domain/roles";

/** A sentence saying which selection is no longer in the catalog. */
export function describeUnavailable({
  kind,
  name,
  spawn_role,
}: UnavailableSelection): string {
  const role = spawn_role ? spawnRoleLabels[spawn_role] : "";
  switch (kind) {
    case "image_family":
      return `Notebook image '${name}' is no longer available.`;
    case "image_tag":
      return `Notebook image version '${name}' is no longer available.`;
    case "resource_tier":
      return `${role} Resources '${name}' are no longer available.`;
    case "profile":
      return `${role} profile '${name}' is no longer available. Please contact your administrator.`;
  }
}

/** Whether a user can choose a replacement; profiles cannot be chosen in the UI. */
export function isChangeableInUi({ kind }: UnavailableSelection): boolean {
  return kind !== "profile";
}
