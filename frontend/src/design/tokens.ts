/**
 * Design tokens for DataMind-King frontend
 * Exported as TypeScript constants for build-time usage
 */

export const colors = {
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
  background: "#0a0a0f",
  surface: "#12121a",
  card: "#1a1a2e",
  border: "#2a2a3e",
  foreground: "#f8fafc",
  muted: "#94a3b8",
} as const;

export const spacing = {
  xs: "0.25rem",
  sm: "0.5rem",
  md: "1rem",
  lg: "1.5rem",
  xl: "2rem",
  "2xl": "3rem",
  "3xl": "4rem",
} as const;

export const borderRadius = {
  none: "0",
  sm: "0.125rem",
  default: "0.25rem",
  md: "0.375rem",
  lg: "0.5rem",
  xl: "0.75rem",
  full: "9999px",
} as const;

export const shadows = {
  sm: "0 1px 2px 0 rgb(0 0 0 / 0.3)",
  default: "0 1px 3px 0 rgb(0 0 0 / 0.3), 0 1px 2px -1px rgb(0 0 0 / 0.3)",
  md: "0 4px 6px -1px rgb(0 0 0 / 0.3), 0 2px 4px -2px rgb(0 0 0 / 0.3)",
  lg: "0 10px 15px -3px rgb(0 0 0 / 0.3), 0 4px 6px -4px rgb(0 0 0 / 0.3)",
  xl: "0 20px 25px -5px rgb(0 0 0 / 0.3), 0 8px 10px -6px rgb(0 0 0 / 0.3)",
  glow: "0 0 20px rgb(99 102 241 / 0.3)",
  glowLg: "0 0 40px rgb(99 102 241 / 0.4)",
} as const;

export const typography = {
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
} as const;

export const transitions = {
  fast: "150ms",
  normal: "200ms",
  slow: "300ms",
} as const;

export const zIndex = {
  dropdown: 100,
  sticky: 200,
  modal: 300,
  popover: 400,
  overlay: 500,
} as const;

// CSS variable names for runtime usage
export const cssVariables = {
  colorPrimary: "--color-primary",
  colorPrimaryLight: "--color-primary-light",
  colorPrimaryDark: "--color-primary-dark",
  colorSuccess: "--color-success",
  colorWarning: "--color-warning",
  colorError: "--color-error",
  colorInfo: "--color-info",
  colorBackground: "--color-background",
  colorSurface: "--color-surface",
  colorCard: "--color-card",
  colorBorder: "--color-border",
  colorForeground: "--color-foreground",
  colorMuted: "--color-muted",
  shadowGlow: "--shadow-glow",
  shadowGlowLg: "--shadow-glow-lg",
} as const;