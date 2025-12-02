"use client";

import { useCallback } from "react";

import { useAuth } from "@/contexts/AuthContext";

interface AuthFetchOptions extends RequestInit {
  skipAuth?: boolean;
}

/**
 * Hook for making authenticated API requests.
 *
 * Automatically adds the Authorization header with the current user's
 * access token from Supabase.
 *
 * @example
 * const { authFetch } = useAuthFetch();
 * const response = await authFetch("/api/agents");
 * const data = await response.json();
 */
export function useAuthFetch() {
  const { getAccessToken } = useAuth();

  const authFetch = useCallback(
    async (url: string, options: AuthFetchOptions = {}): Promise<Response> => {
      const { skipAuth, ...fetchOptions } = options;

      // Get the access token
      const token = skipAuth ? null : await getAccessToken();

      // Build headers
      const headers = new Headers(fetchOptions.headers);

      if (token) {
        headers.set("Authorization", `Bearer ${token}`);
      }

      // Set default content type for JSON if not already set and body is present
      if (
        fetchOptions.body &&
        typeof fetchOptions.body === "string" &&
        !headers.has("Content-Type")
      ) {
        headers.set("Content-Type", "application/json");
      }

      return fetch(url, {
        ...fetchOptions,
        headers,
      });
    },
    [getAccessToken]
  );

  return { authFetch };
}
