// Global config injected by the server
export interface AppConfig {
  baseUrl: string;
  apiUrl: string;
  user: {
    name: string;
    admin: boolean;
  };
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
    user: {
      name: "dev-user",
      admin: true,
    },
  };
}

export const config = getConfig();
