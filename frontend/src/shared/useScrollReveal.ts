import { useEffect, useRef } from 'react';

/**
 * Scroll-triggered reveal animation hook.
 *
 * Adds a `.visible` class to each observed element when it enters the viewport.
 * Fires once per element (unobserves after triggering) per the design spec:
 * "Scroll-triggered fade-up on section entry, ~300ms, fires once."
 *
 * Usage:
 *   const revealRef = useScrollReveal<HTMLElement>();
 *   <section ref={revealRef} className="scroll-reveal"> ... </section>
 *
 * For staggered children, apply `.scroll-reveal` with `--reveal-delay`
 * CSS custom properties on each child.
 */
export function useScrollReveal<T extends HTMLElement>(
  options?: IntersectionObserverInit,
) {
  const ref = useRef<T>(null);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add('visible');
            observer.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.12, rootMargin: '0px 0px -40px 0px', ...options },
    );

    // Observe the element itself
    if (el.classList.contains('scroll-reveal')) {
      observer.observe(el);
    }

    // Observe children with .scroll-reveal
    el.querySelectorAll('.scroll-reveal').forEach((child) => {
      observer.observe(child);
    });

    return () => observer.disconnect();
  }, []);

  return ref;
}
