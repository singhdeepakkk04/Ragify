# Google Login Setup Guide

To enable "Sign in with Google", you need to obtain a Google Client ID.

## 1. Create a Google Cloud Project
1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project (e.g., "RAGify Dev").

## 2. Configure OAuth Consent Screen
1. Navigate to **APIs & Services > OAuth consent screen**.
2. Select **External** (for testing) or Internal.
3. Fill in required fields (App name, support email).
4. Add scopes: `userinfo.email`, `userinfo.profile`, `openid`.
5. Add test users (your email) if using External/Testing status.

## 3. Create OAuth Credentials
1. Navigate to **APIs & Services > Credentials**.
2. Click **Create Credentials** -> **OAuth client ID**.
3. Application type: **Web application**.
4. Name: "RAGify Frontend".
5. **Authorized JavaScript origins**:
   - `http://localhost:3000`
6. **Authorized redirect URIs**:
   - `http://localhost:3000` (optional for implicit, but good to have)
7. Click **Create**.

## 4. Copy Client ID
1. Copy the **Client ID** (e.g., `12345...apps.googleusercontent.com`).
2. You do NOT need the Client Secret for the frontend flow we implemented.

## 5. Update Environment Variables
1. Open `frontend/.env.local` (create if needed) or just use `.env`.
2. Add the variable:
   ```bash
   NEXT_PUBLIC_GOOGLE_CLIENT_ID=your-client-id-here
   ```
3. Restart the frontend server.

## Troubleshooting
- **Popup Closed by User**: Normal if user closes window.
- **Origin Mismatch**: Ensure `http://localhost:3000` is in Authorized Origins.
- **Cookies**: Ensure 3rd party cookies are not blocked if testing in Incognito.
