import { useEffect } from "react";

/**
 * Stops the page behind a modal from scrolling while `active` is true.
 * Restores the previous value on release, so stacked modals keep the page
 * locked until the last one closes.
 */
export function useBodyScrollLock(active: boolean) {
  useEffect(() => {
    if (!active) return;
    const previous = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    return () => {
      document.body.style.overflow = previous;
    };
  }, [active]);
}
