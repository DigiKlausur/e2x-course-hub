import type { TermCapabilities } from "@api/types";
import type { CapabilityTextMap } from "./types";

export const termCapabilityText = {
  viewTerm: {
    label: "View term",
    description: "Open the term and see its details.",
  },
  removeTerm: {
    label: "Delete Semester",
    description:
      "Permanently delete the semester and remove all of its members.",
  },
  selectEnvironment: {
    label: "Change term runtime",
    description:
      "Choose the notebook image and resources used for this semester.",
  },
} satisfies CapabilityTextMap<TermCapabilities>;
