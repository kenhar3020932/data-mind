/**
 * Animation definitions for DataMind-King
 * Uses CSS custom properties for performance
 */

export const animations = {
  // Duration tokens
  duration: {
    instant: "75ms",
    fast: "150ms",
    normal: "200ms",
    slow: "300ms",
    slower: "500ms",
  } as const,

  // Timing functions
  easing: {
    ease: "cubic-bezier(0.4, 0, 0.2, 1)",
    easeIn: "cubic-bezier(0.4, 0, 1, 1)",
    easeOut: "cubic-bezier(0, 0, 0.2, 1)",
    easeInOut: "cubic-bezier(0.4, 0, 0.2, 1)",
    spring: "cubic-bezier(0.34, 1.56, 0.64, 1)",
    linear: "linear",
  } as const,

  // Keyframe animations
  keyframes: {
    fadeIn: `
      from { opacity: 0; transform: translateY(8px); }
      to { opacity: 1; transform: translateY(0); }
    `,
    fadeOut: `
      from { opacity: 1; transform: translateY(0); }
      to { opacity: 0; transform: translateY(8px); }
    `,
    slideInRight: `
      from { transform: translateX(100%); }
      to { transform: translateX(0); }
    `,
    slideInLeft: `
      from { transform: translateX(-100%); }
      to { transform: translateX(0); }
    `,
    slideInUp: `
      from { transform: translateY(100%); }
      to { transform: translateY(0); }
    `,
    scaleIn: `
      from { opacity: 0; transform: scale(0.95); }
      to { opacity: 1; transform: scale(1); }
    `,
    pulse: `
      0%, 100% { opacity: 1; }
      50% { opacity: 0.5; }
    `,
    shimmer: `
      from { background-position: -200% 0; }
      to { background-position: 200% 0; }
    `,
    spin: `
      from { transform: rotate(0deg); }
      to { transform: rotate(360deg); }
    `,
    float: `
      0%, 100% { transform: translateY(0); }
      50% { transform: translateY(-10px); }
    `,
    glow: `
      0%, 100% { box-shadow: 0 0 20px rgb(99 102 241 / 0.3); }
      50% { box-shadow: 0 0 40px rgb(99 102 241 / 0.6); }
    `,
  } as const,
} as const;

export type AnimationName = keyof typeof animations.keyframes;
export type Duration = keyof typeof animations.duration;
export type Easing = keyof typeof animations.easing;

/** Generate CSS animation class */
export function createAnimationClass(
  name: AnimationName,
  duration: Duration = "normal",
  easing: Easing = "ease",
  fillMode: "both" | "forwards" | " backwards" | "none" = "both",
): string {
  const uniqueId = `anim-${name}-${Date.now()}`;
  const keyframe = animations.keyframes[name];
  const dur = animations.duration[duration];
  const ease = animations.easing[easing];

  const style = document.createElement("style");
  style.textContent = `
    @keyframes ${uniqueId} {
      ${keyframe.trim()}
    }
    .${uniqueId} {
      animation: ${uniqueId} ${dur} ${ease} ${fillMode};
    }
  `;
  document.head.appendChild(style);

  return uniqueId;
}

/** Cleanup animation styles */
export function cleanupAnimations(): void {
  const styles = document.querySelectorAll('style[data-anim]');
  styles.forEach((s) => s.remove());
}

/** Animate element with intersection observer */
export function observeAnimations(
  selector: string,
  options?: IntersectionObserverInit,
): () => void {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add("animate-fade-in");
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.1, ...options });

  document.querySelectorAll(selector).forEach((el) => observer.observe(el));

  return () => observer.disconnect();
}