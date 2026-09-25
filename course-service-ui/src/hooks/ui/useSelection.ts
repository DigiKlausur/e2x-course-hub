import { useCallback, useState } from "react";

export interface Selection {
  selected: Set<string>;
  /** Selects the id if it is not selected, and deselects it otherwise. */
  toggle: (id: string) => void;
  /** Selects or deselects all given ids at once, e.g. for select-all. */
  toggleRows: (select: boolean, ids: string[]) => void;
  remove: (id: string) => void;
  clear: () => void;
}

/**
 * A set of selected row ids, e.g. usernames in a member table. The returned
 * functions are stable, so they can be passed straight to mutation callbacks.
 */
export function useSelection(): Selection {
  const [selected, setSelected] = useState<Set<string>>(() => new Set());

  const toggle = useCallback((id: string) => {
    setSelected((prev) => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
      return next;
    });
  }, []);

  const toggleRows = useCallback((select: boolean, ids: string[]) => {
    setSelected((prev) => {
      const next = new Set(prev);
      if (select) {
        ids.forEach((id) => next.add(id));
      } else {
        ids.forEach((id) => next.delete(id));
      }
      return next;
    });
  }, []);

  const remove = useCallback((id: string) => {
    setSelected((prev) => {
      if (!prev.has(id)) return prev;
      const next = new Set(prev);
      next.delete(id);
      return next;
    });
  }, []);

  const clear = useCallback(() => setSelected(new Set()), []);

  return { selected, toggle, toggleRows, remove, clear };
}
