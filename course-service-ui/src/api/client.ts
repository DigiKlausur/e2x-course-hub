import { getCookie } from "./http";

export interface ApiError extends Error {
  response?: {
    status: number;
    type?: string;
    title?: string;
    detail?: string;
    extra?: Record<string, unknown>;
  };
}

const baseSettings: RequestInit = {
  credentials: "same-origin" as RequestCredentials,
  headers: {
    "X-CSRFToken": getCookie("_xsrf") || "",
  },
};

const handleResponse = async (response: Response): Promise<unknown> => {
  let data: Record<string, unknown>;
  try {
    data = await response.json();
  } catch {
    // Non-JSON response fallback
    if (!response.ok) {
      const error = new Error(`HTTP ${response.status}`) as ApiError;
      error.response = { status: response.status };
      throw error;
    }
    return null;
  }

  if (!response.ok) {
    // Prefer RFC 9457 fields
    const errorMessage =
      (data.detail as string) ||
      (data.title as string) ||
      `HTTP ${response.status}`;
    const error = new Error(errorMessage) as ApiError;

    // Attach the whole problem details object for programmatic use
    error.response = {
      status: response.status,
      type: data.type as string,
      title: data.title as string,
      detail: data.detail as string,
      extra: { ...data }, // all other fields like course_id, term_id, etc.
    };

    throw error;
  }

  return data;
};

/**
 * Thin fetch wrappers.
 *
 * Each method is generic in its response type so call sites can name the
 * schema-derived type directly instead of asserting one onto `unknown`. The
 * response is still not validated at runtime — the guarantee comes from the
 * types in `types.ts` being generated from the service's OpenAPI document, so
 * a backend shape change turns into a compile error at the call site.
 *
 * Endpoints that answer 204 have no body; type those as `void`.
 */
export const requests = {
  get: async <T>(
    url: string,
    params: Record<string, string> | undefined = undefined,
  ): Promise<T> => {
    const settings: RequestInit = {
      ...baseSettings,
      method: "GET",
    };
    if (params !== undefined) {
      url += "?" + new URLSearchParams(params).toString();
    }
    const response = await fetch(url, settings);
    return handleResponse(response) as Promise<T>;
  },
  post: async <T>(url: string, data: unknown): Promise<T> => {
    const settings: RequestInit = {
      ...baseSettings,
      method: "POST",
      headers: {
        ...baseSettings.headers,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    };
    const response = await fetch(url, settings);
    return handleResponse(response) as Promise<T>;
  },
  put: async <T>(url: string, data: unknown): Promise<T> => {
    const settings: RequestInit = {
      ...baseSettings,
      method: "PUT",
      headers: {
        ...baseSettings.headers,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    };
    const response = await fetch(url, settings);
    return handleResponse(response) as Promise<T>;
  },
  patch: async <T>(url: string, data: unknown): Promise<T> => {
    const settings: RequestInit = {
      ...baseSettings,
      method: "PATCH",
      headers: {
        ...baseSettings.headers,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    };
    const response = await fetch(url, settings);
    return handleResponse(response) as Promise<T>;
  },
  delete: async <T = void>(url: string): Promise<T> => {
    const settings: RequestInit = {
      ...baseSettings,
      method: "DELETE",
    };
    const response = await fetch(url, settings);
    return handleResponse(response) as Promise<T>;
  },
};
