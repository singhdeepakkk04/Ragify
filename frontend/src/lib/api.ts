import axios from 'axios';
import { createClient } from './supabase';

function getApiV1BaseUrl(): string {
    const raw = (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000').replace(/\/+$/, '');
    return raw.endsWith('/api/v1') ? raw : `${raw}/api/v1`;
}

const api = axios.create({
    baseURL: getApiV1BaseUrl(),
    headers: {
        'Content-Type': 'application/json',
    },
    timeout: 15000, // 15s — fail fast instead of hanging forever
});

// ── Token cache — avoids calling getSession() on every request ──────────────
let _cachedToken: string | null = null;
let _tokenExpiresAt: number = 0;
let _supabase: ReturnType<typeof createClient> | null = null;
let _authListenerSet = false;

function getSupabaseClient() {
    // Only create in browser context — never during SSR (breaks Google OAuth cookies)
    if (typeof window === 'undefined') return null;
    if (!_supabase) {
        _supabase = createClient();
        // Listen for auth state changes to immediately update the token cache
        if (!_authListenerSet) {
            _supabase.auth.onAuthStateChange((_event, session) => {
                _cachedToken = session?.access_token ?? null;
                _tokenExpiresAt = session?.expires_at ?? 0;
            });
            _authListenerSet = true;
        }
    }
    return _supabase;
}

export async function getToken(): Promise<string | null> {
    const client = getSupabaseClient();
    if (!client) return null;

    const now = Math.floor(Date.now() / 1000);
    // Refresh only if missing or expiring within 60 seconds
    if (!_cachedToken || now >= _tokenExpiresAt - 60) {
        const { data: { session } } = await client.auth.getSession();
        _cachedToken = session?.access_token ?? null;
        _tokenExpiresAt = session?.expires_at ?? 0;
    }
    return _cachedToken;
}

api.interceptors.request.use(async (config) => {

    const token = await getToken();
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

api.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 401) {
            _cachedToken = null;
            _tokenExpiresAt = 0;
            window.location.href = '/login';
        }
        return Promise.reject(error);
    }
);

export default api;
