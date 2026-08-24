import type { Product, ShoppingItem, Suggestion, VoiceCommandResult } from "../types";

const BASE_URL = import.meta.env.VITE_API_URL || "https://voice-shopping-assistant-backend.vercel.app";

/**
 * Thin fetch wrapper: every call goes through here so error handling,
 * base URL, and JSON parsing are consistent in exactly one place instead
 * of copy-pasted across every component that needs data.
 */
async function request<T>(path: string, options?: RequestInit): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${BASE_URL}${path}`, {
      headers: { "Content-Type": "application/json" },
      ...options,
    });
  } catch {
    throw new ApiError("Can't reach the server. Is the backend running?", 0);
  }

  if (!response.ok) {
    let detail = response.statusText;
    try {
      const body = await response.json();
      detail = body.detail || detail;
    } catch {
      // response wasn't JSON — keep statusText
    }
    throw new ApiError(detail, response.status);
  }

  if (response.status === 204) return undefined as T;
  return response.json();
}

export class ApiError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

export const api = {
  getList: () => request<ShoppingItem[]>("/api/list"),

  addItem: (name: string, quantity = 1, unit?: string) =>
    request<ShoppingItem>("/api/list", {
      method: "POST",
      body: JSON.stringify({ name, quantity, unit }),
    }),

  removeItem: (id: number) =>
    request<void>(`/api/list/${id}`, { method: "DELETE" }),

  sendVoiceCommand: (transcript: string, language: string) =>
    request<VoiceCommandResult>("/api/voice/command", {
      method: "POST",
      body: JSON.stringify({ transcript, language }),
    }),

  getSuggestions: () => request<Suggestion[]>("/api/suggestions"),

  searchProducts: (query: string) =>
    request<Product[]>(`/api/search?q=${encodeURIComponent(query)}`),

  health: () => request<{ status: string; app: string }>("/api/health"),
};
