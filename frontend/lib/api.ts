import axios from "axios";

export const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000",
});

type TokenProvider = () => Promise<string | null>;
type UserIdProvider = () => string | null;

let tokenProvider: TokenProvider | null = null;
let userIdProvider: UserIdProvider | null = null;

export function setAuthTokenProvider(provider: TokenProvider | null) {
  tokenProvider = provider;
}

export function setAuthUserIdProvider(provider: UserIdProvider | null) {
  userIdProvider = provider;
}

api.interceptors.request.use(async (config) => {
  config.headers = config.headers ?? {};

  if (!tokenProvider) {
    if (userIdProvider) {
      const userId = userIdProvider();
      if (userId) {
        config.headers["X-Test-User-Id"] = userId;
      }
    }
    return config;
  }

  const token = await tokenProvider();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
    return config;
  }

  if (userIdProvider) {
    const userId = userIdProvider();
    if (userId) {
      config.headers["X-Test-User-Id"] = userId;
    }
  }

  return config;
});
