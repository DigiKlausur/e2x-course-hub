/** Whether any action in an action tree is allowed. */
export function hasAny(tree: object): boolean {
  return Object.values(tree).some((value) =>
    typeof value === "boolean" ? value : hasAny(value),
  );
}
