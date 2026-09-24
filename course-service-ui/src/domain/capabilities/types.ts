export interface CapabilityText {
  label: string;
  description: string;
}

/** The keys of `T` whose value is a flag, leaving out nested capability groups. */
export type BooleanKeys<T> = {
  [K in keyof T]-?: T[K] extends boolean ? K : never;
}[keyof T];

export type CapabilityTextMap<T> = Record<BooleanKeys<T>, CapabilityText>;
