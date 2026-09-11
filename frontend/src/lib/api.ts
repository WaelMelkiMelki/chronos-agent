const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export type TokenPair = {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
};

const ACCESS_KEY = "chronos.access";
const REFRESH_KEY = "chronos.refresh";

export const auth = {
  save(tokens: TokenPair) {
    localStorage.setItem(ACCESS_KEY, tokens.access_token);
    localStorage.setItem(REFRESH_KEY, tokens.refresh_token);
  },
  clear() {
    localStorage.removeItem(ACCESS_KEY);
    localStorage.removeItem(REFRESH_KEY);
  },
  access(): string | null {
    return typeof window === "undefined" ? null : localStorage.getItem(ACCESS_KEY);
  },
  refresh(): string | null {
    return typeof window === "undefined" ? null : localStorage.getItem(REFRESH_KEY);
  },
  isAuthed(): boolean {
    return !!this.access();
  },
};

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const headers = new Headers(init.headers);
  headers.set("Content-Type", "application/json");
  const token = auth.access();
  if (token) headers.set("Authorization", "Bearer " + token);
  const res = await fetch(`${API_URL}${path}`, { ...init, headers });
  if (!res.ok) {
    const body = await res.text();
    throw new Error(`${res.status}: ${body}`);
  }
  if (res.status === 204) return undefined as T;
  return (await res.json()) as T;
}

export const api = {
  async register(email: string, password: string, full_name?: string): Promise<TokenPair> {
    return request<TokenPair>("/api/v1/auth/register", {
      method: "POST",
      body: JSON.stringify({ email, password, full_name }),
    });
  },
  async login(email: string, password: string): Promise<TokenPair> {
    return request<TokenPair>("/api/v1/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    });
  },
  async me() {
    return request<{ id: string; email: string; full_name: string | null }>("/api/v1/auth/me");
  },
  async googleLoginUrl(): Promise<{ auth_url: string }> {
    return request("/api/v1/auth/google/login");
  },
};

export const API_URL_BASE = API_URL;
