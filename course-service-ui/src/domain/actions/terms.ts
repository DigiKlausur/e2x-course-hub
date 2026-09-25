import type { TermActions } from "@api/types";
import type { ActionTextMap } from "./types";

export const termActionText = {
  view: {
    label: "View term",
    description: "Open the term and see its details.",
  },
  remove: {
    label: "Delete Semester",
    description:
      "Permanently delete the semester and remove all of its members.",
  },
  environment: {
    select: {
      label: "Change term runtime",
      description:
        "Choose the notebook image and resources used for this semester.",
    },
  },
} satisfies ActionTextMap<TermActions>;
