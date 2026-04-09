const GATEWAY_URL = "/api/v1";
const REFRESH_TOKEN_KEY = 'ci_refresh_token';

type TokenState = {
  access: string | null;
  refresh: string | null;
}

const tokenState: TokenState = {
  access: null,
  refresh: localStorage.getItem(REFRESH_TOKEN_KEY),
};

export function getAccessToken(): string | null {
  return tokenState.access;
}

export function setTokens(access: string, refresh: string): void {
  tokenState.access = access;
  tokenState.refresh = refresh;
  localStorage.setItem(REFRESH_TOKEN_KEY, refresh);
}

export function clearTokens(): void {
  tokenState.access = null;
  tokenState.refresh = null;
  localStorage.removeItem(REFRESH_TOKEN_KEY);
}

export function hasRefreshToken(): boolean {
  return !!tokenState.refresh;
}

interface JwtPayload {
  sub: string;
  role: string;
  name: string;
  exp: number;
  iat: number;
  [key: string]: unknown;
}

export function decodeJwt(token: string): JwtPayload | null {
  try {
    const base64Url = token.split('.')[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const json = decodeURIComponent(
      atob(base64)
        .split('')
        .map((c) => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
        .join(''),
    );
    return JSON.parse(json);
  } catch {
    return null;
  }
}

export function isTokenExpired(token: string): boolean {
  const payload = decodeJwt(token);
  if (!payload?.exp) return true;
  return Date.now() >= (payload.exp - 30) * 1000;
}

let refreshPromise: Promise<boolean> | null = null;

async function refreshAccessToken(): Promise<boolean> {
  if (!tokenState.refresh) return false;

  if (refreshPromise) return refreshPromise;

  refreshPromise = (async () => {
    try {
      const res = await fetch('/api/v1/users/auth/refresh', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh_token: tokenState.refresh }),
      });

      if (!res.ok) {
        clearTokens();
        return false;
      }

      const data = await res.json();
      setTokens(data.access_token, data.refresh_token);
      return true;
    } catch {
      clearTokens();
      return false;
    } finally {
      refreshPromise = null;
    }
  })();

  return refreshPromise;
}

type RequestOptions = Omit<RequestInit, 'headers'> & {
  headers?: Record<string, string>;
  skipAuth?: boolean;
};

export class AuthError extends Error {
  constructor() {
    super('Authentication required');
    this.name = 'AuthError';
  }
}


export async function apiFetch<T = unknown>(
  endpoint: string,
  options: RequestOptions = {},
): Promise<T> {
  const { skipAuth = false, headers = {}, ...fetchOptions } = options;

  if (!skipAuth && tokenState.access && isTokenExpired(tokenState.access)) {
    const refreshed = await refreshAccessToken();
    if (!refreshed) throw new AuthError();
  }

  const makeRequest = (token: string | null) => {
    const reqHeaders: Record<string, string> = {
      'Content-Type': 'application/json',
      ...headers,
    };

    if (token && !skipAuth) {
      reqHeaders['Authorization'] = `Bearer ${token}`;
    }

    return fetch(`${GATEWAY_URL}${endpoint}`, {
      ...fetchOptions,
      headers: reqHeaders,
    });
  };

  let res = await makeRequest(tokenState.access);

  if (res.status === 401 && !skipAuth) {
    const refreshed = await refreshAccessToken();
    if (!refreshed) throw new AuthError();
    res = await makeRequest(tokenState.access);
  }

  if (res.status === 401) {
    clearTokens();
    throw new AuthError();
  }

  if (!res.ok) {
    const errorBody = await res.text().catch(() => '');
    throw new Error(`API Error ${res.status}: ${errorBody}`);
  }

  if (res.status === 204) return undefined as T;

  return res.json();
}

interface LoginRequest {
  email: string;
  password: string;
}

interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}


export async function login(credentials: LoginRequest): Promise<AuthTokens> {
  const res = await fetch('/api/v1/users/auth/login', {
     method: 'POST',
     headers: { 'Content-Type': 'application/json'},
     body: JSON.stringify(credentials),
    });
    
    if (!res.ok) {
    if (res.status === 401) {
      throw new Error('Неверный email или пароль');
    }
    const body = await res.text().catch(() => '');
    throw new Error(`Ошибка авторизации (${res.status}): ${body}`);
  }

  const data: AuthTokens = await res.json();
  setTokens(data.access_token, data.refresh_token);
  return data;
}


export async function restoreSession(): Promise<boolean> {
  if (!hasRefreshToken()) return false;
  
  return refreshAccessToken();
}

export function logout(): void {
  clearTokens();
}
