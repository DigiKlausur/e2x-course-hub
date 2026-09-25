export interface ActionText {
  label: string;
  description: string;
}

/** Texts for (some of) the actions of `T`, in the same shape as the tree. */
export type ActionTextMap<T> = {
  [K in keyof T]?: T[K] extends boolean ? ActionText : ActionTextMap<T[K]>;
};
