/** An accepted username format, with a hint telling users how to enter it. */
export interface UsernameFormat {
  pattern: string;
  hint: string;
}

// Global config injected by the server
export interface AppConfig {
  baseUrl: string;
  apiUrl: string;
  /** Without formats, every username is accepted. */
  usernameFormats: UsernameFormat[];
}

declare global {
  interface Window {
    __APP_CONFIG__?: AppConfig;
  }
}

// Get config with fallback for development
export function getConfig(): AppConfig {
  if (window.__APP_CONFIG__) {
    return window.__APP_CONFIG__;
  }

  // Fallback for local development
  console.warn("Using development config fallback");
  return {
    baseUrl: import.meta.env.VITE_BASE_URL || "",
    apiUrl: import.meta.env.VITE_API_URL || "/api",
    usernameFormats: [],
  };
}

export const config = getConfig();
