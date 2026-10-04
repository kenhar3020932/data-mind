/**
 * Design system theme configuration for DataMind-King
 * Neural glass aesthetic with CSS custom properties
 */

export const theme = {
  // Colors
  colors: {
    primary: {
      DEFAULT: "#6366f1",
      light: "#818cf8",
      dark: "#4f46e5",
      50: "#eef2ff",
      100: "#e0e7ff",
      200: "#c7d2fe",
      300: "#a5b4fc",
      400: "#818cf8",
      500: "#6366f1",
      600: "#4f46e5",
      700: "#4338ca",
      800: "#3730a3",
      900: "#312e81",
    },
    secondary: {
      DEFAULT: "#8b5cf6",
      light: "#a78bfa",
      dark: "#7c3aed",
    },
    accent: {
      DEFAULT: "#06b6d4",
      light: "#22d3ee",
      dark: "#0891b2",
    },
    success: "#10b981",
    warning: "#f59e0b",
    error: "#ef4444",
    info: "#3b82f6",

    // Neutrals
    background: "#0a0a0f",
    surface: "#12121a",
    card: "#1a1a2e",
    border: "#2a2a3e",
    foreground: "#f8fafc",
    muted: "#94a3b8",
  },

  // Typography
  typography: {
    fontFamily: {
      sans: ["Inter", "system-ui", "sans-serif"],
      mono: ["JetBrains Mono", "Fira Code", "monospace"],
    },
    fontSize: {
      xs: "0.75rem",
      sm: "0.875rem",
      base: "1rem",
      lg: "1.125rem",
      xl: "1.25rem",
      "2xl": "1.5rem",
      "3xl": "1.875rem",
      "4xl": "2.25rem",
    },
    fontWeight: {
      normal: "400",
      medium: "500",
      semibold: "600",
      bold: "700",
    },
  },

  // Spacing
  spacing: {
    xs: "0.25rem",
    sm: "0.5rem",
    md: "1rem",
    lg: "1.5rem",
    xl: "2rem",
    "2xl": "3rem",
    "3xl": "4rem",
  },

  // Borders
  borderRadius: {
    none: "0",
    sm: "0.125rem",
    default: "0.25rem",
    md: "0.375rem",
    lg: "0.5rem",
    xl: "0.75rem",
    full: "9999px",
  },

  // Shadows
  shadows: {
    sm: "0 1px 2px 0 rgb(0 0 0 / 0.3)",
    default: "0 1px 3px 0 rgb(0 0 0 / 0.3), 0 1px 2px -1px rgb(0 0 0 / 0.3)",
    md: "0 4px 6px -1px rgb(0 0 0 / 0.3), 0 2px 4px -2px rgb(0 0 0 / 0.3)",
    lg: "0 10px 15px -3px rgb(0 0 0 / 0.3), 0 4px 6px -4px rgb(0 0 0 / 0.3)",
    xl: "0 20px 25px -5px rgb(0 0 0 / 0.3), 0 8px 10px -6px rgb(0 0 0 / 0.3)",
    glow: "0 0 20px rgb(99 102 241 / 0.3)",
    glowLg: "0 0 40px rgb(99 102 241 / 0.4)",
  },

  // Transitions
  transitions: {
    fast: "150ms",
    normal: "200ms",
    slow: "300ms",
  },

  // Z-index
  zIndex: {
    dropdown: 100,
    sticky: 200,
    modal: 300,
    popover: 400,
    overlay: 500,
    skipLink: 600,
  },
} as const;

export type Theme = typeof theme;

// Export CSS variables for runtime usage
export function applyThemeToDOM(): void {
  const root = document.documentElement;
  const c = theme.colors;

  // Primary
  root.style.setProperty("--color-primary", c.primary.DEFAULT);
  root.style.setProperty("--color-primary-light", c.primary.light);
  root.style.setProperty("--color-primary-dark", c.primary.dark);

  // Surface
  root.style.setProperty("--color-background", c.background);
  root.style.setProperty("--color-surface", c.surface);
  root.style.setProperty("--color-card", c.card);
  root.style.setProperty("--color-border", c.border);
  root.style.setProperty("--color-foreground", c.foreground);
  root.style.setProperty("--color-muted", c.muted);

  // Semantic
  root.style.setProperty("--color-success", c.success);
  root.style.setProperty("--color-warning", c.warning);
  root.style.setProperty("--color-error", c.error);
  root.style.setProperty("--color-info", c.info);

  // Shadows
  root.style.setProperty("--shadow-glow", theme.shadows.glow);
  root.style.setProperty("--shadow-glow-lg", theme.shadows.glowLg);
}