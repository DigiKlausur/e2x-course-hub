export interface ActionText {
  label: string;
  description: string;
  /**
   * A short label for a compact display, e.g. "Add" within the group
   * "Students". A group whose actions all have one is shown as a row of chips.
   */
  short?: string;
}

/** A text for every action of `T`, in the same shape as the tree. */
export type ActionTextMap<T> = {
  [K in keyof T]-?: T[K] extends boolean ? ActionText : ActionGroupText<T[K]>;
};

/** The texts of a group of actions, with the title the group is shown under. */
export type ActionGroupText<T> = ActionTextMap<T> & { title: string };
