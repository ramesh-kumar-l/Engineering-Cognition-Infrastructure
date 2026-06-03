import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import type { ReactNode } from "react";
import { setAuthToken, setUnauthorizedHandler } from "./api-client";

interface AuthState {
  /** Bearer token; null in dev-bypass mode (ECI_IDENTITY_AUTH_DISABLED=true). */
  token: string | null;
  /** Whether the backend rejected us with 401 and a real token is required. */
  needsAuth: boolean;
  setToken: (token: string | null) => void;
}

const AuthContext = createContext<AuthState | null>(null);
const STORAGE_KEY = "eci.token";

/**
 * Auth/tenant layer. Starts in dev-bypass mode (no token needed); structured so the
 * OIDC login flow (/auth/login + /auth/callback) can populate a real token later.
 */
export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setTokenState] = useState<string | null>(() =>
    localStorage.getItem(STORAGE_KEY),
  );
  const [needsAuth, setNeedsAuth] = useState(false);

  const setToken = useCallback((next: string | null) => {
    setTokenState(next);
    if (next) localStorage.setItem(STORAGE_KEY, next);
    else localStorage.removeItem(STORAGE_KEY);
    if (next) setNeedsAuth(false);
  }, []);

  useEffect(() => {
    setAuthToken(token);
  }, [token]);

  useEffect(() => {
    setUnauthorizedHandler(() => setNeedsAuth(true));
    return () => setUnauthorizedHandler(null);
  }, []);

  const value = useMemo<AuthState>(
    () => ({ token, needsAuth, setToken }),
    [token, needsAuth, setToken],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthState {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
