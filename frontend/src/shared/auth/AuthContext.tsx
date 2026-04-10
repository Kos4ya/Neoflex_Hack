import { createContext, useCallback, useContext, useEffect, useState, type FC, type ReactNode } from 'react';
import {
  login as apiLogin,
  logout as apiLogout,
  restoreSession,
  getAccessToken,
  decodeJwt,
  clearTokens,
} from '../api/apiClient';
export type Role = 'user' | null;

export type User = {
  id: string;
  name: string;
  role: Role;
}

type AuthContextValue = {
  user: User | null;
  isInterviewer: boolean;
  isLoading: boolean;
  error: string | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

// ── Helpers ────────────────────────────────────────────────
function userFromToken(): User | null {
  const token = getAccessToken();
  if (!token) return null;
  const payload = decodeJwt(token);
  if (!payload) return null;
  return {
    id: payload.sub,
    name: (payload.name as string) ?? 'User',
    role: payload.role === 'user' ? 'user' : null,
  };
}

// ── Context ────────────────────────────────────────────────
const AuthContext = createContext<AuthContextValue | null>(null);

export const AuthProvider: FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Восстановление сессии при загрузке
  useEffect(() => {
    restoreSession()
      .then((restored) => {
        if (restored) {
          setUser(userFromToken());
        }
      })
      .catch(() => {
        clearTokens();
      })
      .finally(() => {
        setIsLoading(false);
      });
  }, []);

  const login = useCallback(async (email: string, password: string) => {
    setError(null);
    setIsLoading(true);
    try {
      await apiLogin({ email, password });
      setUser(userFromToken());
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Ошибка авторизации';
      setError(msg);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const logout = useCallback(() => {
    apiLogout();
    setUser(null);
    setError(null);
  }, []);

  return (
    <AuthContext.Provider
      value={{
        user,
        isInterviewer: user?.role === 'user',
        isLoading,
        error,
        login,
        logout,
      }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = (): AuthContextValue => {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
};