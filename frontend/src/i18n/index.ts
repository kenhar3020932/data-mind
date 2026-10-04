/**
 * i18n Internationalization module for DataMind-King
 * Supports English (EN) and Urdu (UR) with RTL support
 */
export const locales = ["en", "ur"] as const;
export type Locale = (typeof locales)[number];

export const rtlLocales: Set<Locale> = new Set(["ur"]);

export interface Translations {
  [key: string]: {
    [key: string]: string;
  };
}

export const translations: Translations = {
  en: {
    // Navigation
    "nav.home": "Home",
    "nav.datasets": "Datasets",
    "nav.sql": "SQL Studio",
    "nav.charts": "Charts",
    "nav.dashboards": "Dashboards",
    "nav.settings": "Settings",

    // Common
    "common.save": "Save",
    "common.cancel": "Cancel",
    "common.delete": "Delete",
    "common.confirm": "Confirm",
    "common.loading": "Loading...",
    "common.error": "Error",
    "common.success": "Success",
    "common.search": "Search...",
    "common.close": "Close",
    "common.open": "Open",
    "common.refresh": "Refresh",
    "common.export": "Export",
    "common.import": "Import",

    // Auth
    "auth.login": "Sign In",
    "auth.register": "Register",
    "auth.logout": "Sign Out",
    "auth.email": "Email",
    "auth.password": "Password",
    "auth.username": "Username",
    "auth.forgot_password": "Forgot Password?",

    // Dashboard
    "dashboard.title": "Dashboard",
    "dashboard.add_widget": "Add Widget",
    "dashboard.edit": "Edit Widget",
    "dashboard.delete": "Delete Widget",
    "dashboard.drag_to_move": "Drag to move",

    // SQL Studio
    "sql.execute": "Execute",
    "sql.clear": "Clear",
    "sql.results": "Results",
    "sql.rows": "rows",
    "sql.execution_time": "Execution Time",
    "sql.sql_gate": "SQL Gate",

    // Brain Theater
    "brain.task": "Task",
    "brain.execute": "Execute",
    "brain.agents": "Agents",
    "brain.confidence": "Confidence",
    "brain.cost": "Cost",
    "brain.duration": "Duration",

    // Charts
    "charts.line": "Line Chart",
    "charts.bar": "Bar Chart",
    "charts.pie": "Pie Chart",
    "charts.scatter": "Scatter Plot",
    "charts.area": "Area Chart",
    "charts.heatmap": "Heatmap",

    // Messages
    "msg.welcome": "Welcome to DataMind-King",
    "msg.save_success": "Saved successfully",
    "msg.delete_success": "Deleted successfully",
    "msg.error_occurred": "An error occurred",
    "msg.loading_data": "Loading data...",
    "msg.no_results": "No results found",
    "msg.unsaved_changes": "You have unsaved changes",
  },
  ur: {
    // Navigation
    "nav.home": "ہوم",
    "nav.datasets": "ڈیٹا سیٹ",
    "nav.sql": "ایس کیو ال اسٹوڈیو",
    "nav.charts": "چارٹس",
    "nav.dashboards": "ڈیش بورڈ",
    "nav.settings": "ترتیبات",

    // Common
    "common.save": "محفوظ کریں",
    "common.cancel": "منسوخ",
    "common.delete": "حذف",
    "common.confirm": "تصدیق",
    "common.loading": "لوڈ ہو رہا ہے...",
    "common.error": "خرابی",
    "common.success": "کامیابی",
    "common.search": "تلاش...",
    "common.close": "بند کریں",
    "common.open": "کھولیں",
    "common.refresh": "ریفریش",
    "common.export": "ایکسپورٹ",
    "common.import": "ایمپورٹ",

    // Auth
    "auth.login": "سائن ان",
    "auth.register": "رجسٹر",
    "auth.logout": "سائن آؤٹ",
    "auth.email": "ای میل",
    "auth.password": "پاس ورڈ",
    "auth.username": "صارف نام",
    "auth.forgot_password": "پاس ورڈ بھول گئے؟",

    // Dashboard
    "dashboard.title": "ڈیش بورڈ",
    "dashboard.add_widget": "وڈجٹ شامل کریں",
    "dashboard.edit": "وڈجٹ ایڈٹ",
    "dashboard.delete": "وڈجٹ حذف",
    "dashboard.drag_to_move": "منتقل کرنے کے لیے گھسیٹیں",

    // SQL Studio
    "sql.execute": "چلائیں",
    "sql.clear": "صاف",
    "sql.results": "نتائج",
    "sql.rows": "قطاریں",
    "sql.execution_time": "اجرا وقت",
    "sql.sql_gate": "ایس کیو ال گیٹ",

    // Brain Theater
    "brain.task": "کلپ",
    "brain.execute": "اجرا",
    "brain.agents": "ایجینٹس",
    "brain.confidence": "اعتماد",
    "brain.cost": "لاگت",
    "brain.duration": "مدت",

    // Charts
    "charts.line": "لائن چارٹ",
    "charts.bar": "بار چارٹ",
    "charts.pie": "پائی چارٹ",
    "charts.scatter": "اسکیٹر پلاٹ",
    "charts.area": "ایریا چارٹ",
    "charts.heatmap": "ہیٹ میپ",

    // Messages
    "msg.welcome": "ڈیٹا مائڈ کنگ میں خوش آمدید",
    "msg.save_success": "کامیابی سے محفوظ ہوا",
    "msg.delete_success": "کامیابی سے حذف ہوا",
    "msg.error_occurred": "خرابی پیش آئی",
    "msg.loading_data": "ڈیٹا لوڈ ہو رہا ہے...",
    "msg.no_results": "کوئی نتیجہ نہیں ملا",
    "msg.unsaved_changes": "آپ کے غیر محفوظ تبدیلیاں ہیں",
  },
};

let currentLocale: Locale = "en";

export function setLocale(locale: Locale): void {
  currentLocale = locale;
  document.documentElement.dir = rtlLocales.has(locale) ? "rtl" : "ltr";
  document.documentElement.lang = locale;
  localStorage.setItem("locale", locale);
}

export function getLocale(): Locale {
  return currentLocale;
}

export function t(key: string, params?: Record<string, string>): string {
  const translation = translations[currentLocale]?.[key] ?? translations["en"]?.[key] ?? key;
  if (!params) return translation;
  return Object.entries(params).reduce(
    (str, [param, value]) => str.replace(new RegExp(`\\{${param}\\}`, "g"), value),
    translation,
  );
}

export function initLocale(): Locale {
  const stored = localStorage.getItem("locale") as Locale | null;
  if (stored && locales.includes(stored)) {
    currentLocale = stored;
  } else {
    const browserLang = navigator.language.toLowerCase();
    if (browserLang.startsWith("ur")) {
      currentLocale = "ur";
    }
  }
  document.documentElement.dir = rtlLocales.has(currentLocale) ? "rtl" : "ltr";
  document.documentElement.lang = currentLocale;
  return currentLocale;
}