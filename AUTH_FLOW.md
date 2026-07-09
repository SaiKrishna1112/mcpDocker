# Authentication Flow

## Overview

askoxy.ai MCP Server uses **OTP-only** authentication. No passwords are stored or transmitted.

Three auth paths are available:

| Path | Use Case |
|------|----------|
| OTP Login | Existing user, SMS or WhatsApp |
| OTP Register | New user registration |
| Token Login | Pre-authenticated client passes token directly |

---

## OTP Login Flow

```
Client                          MCP Server                    askoxy.ai API
  │                                  │                              │
  │── send_login_otp(mobile, +91) ──▶│                              │
  │                                  │── POST /user-service/... ───▶│
  │                                  │◀── { otpSession, salt } ─────│
  │◀── { otpSession, salt, time } ───│                              │
  │                                  │                              │
  │── verify_login_otp(otp_value) ──▶│                              │
  │                                  │── POST /user-service/... ───▶│
  │                                  │◀── { accessToken, userId } ──│
  │                                  │                              │
  │                                  │  create_session(userId, token)
  │                                  │  → UUID stored in SESSION_STORE
  │◀── { session_id } ───────────────│                              │
```

### Parameters for `send_login_otp`

| Field | Type | Example |
|-------|------|---------|
| `country_code` | str | `+91` |
| `mobile_or_whatsapp` | str | `9876543210` |
| `registration_type` | `sms` \| `whatsapp` | `sms` |

### Parameters for `verify_login_otp`

| Field | Type | Notes |
|-------|------|-------|
| `country_code` | str | Same as send step |
| `mobile_or_whatsapp` | str | Same number |
| `otp_session` | str | From send response |
| `otp_value` | str | OTP entered by user |
| `salt` | str | From send response |
| `expiry_time` | str | From send response |
| `registration_type` | `mobile` \| `whatsapp` | Note: different values from send step |

---

## OTP Registration Flow

```
Client                          MCP Server
  │                                  │
  │── send_register_otp(mobile) ────▶│── POST /user-service/... ──▶ API
  │◀── { otpSession, salt, time } ───│
  │                                  │
  │── verify_otp_and_authenticate ──▶│── POST /user-service/... ──▶ API
  │   (user_type="Register")         │◀── { accessToken, userStatus }
  │◀── { session_id, user_status } ──│
```

Optional: pass `referrer_id` in `send_register_otp` for referral tracking.

---

## Token Login (Direct)

For clients that have already authenticated via the askoxy.ai frontend:

```
Client                          MCP Server
  │                                  │
  │── set_user_session(user_id, token) ──▶│
  │◀── { session_id } ────────────────────│
```

No API call is made — the token is stored directly in the session store.

---

## Session Management

Sessions are managed in `auth/token_store.py`:

- Stored in memory (`SESSION_STORE` dict) and persisted to `~/.askoxy_sessions.json`
- Survive server restarts
- Structure:

```json
{
  "sessions": {
    "<uuid>": { "user_id": "<userId>" }
  },
  "tokens": {
    "<userId>": "<accessToken>"
  }
}
```

### Key functions

| Function | Description |
|----------|-------------|
| `create_session(user_id, token)` | Creates UUID session, persists to disk |
| `get_token_by_session(session_id)` | Resolves session → token |
| `get_user_id_by_session(session_id)` | Resolves session → user_id |
| `remove_session(session_id)` | Deletes session and token |

---

## Security Notes

- Only `primaryType == "CUSTOMER"` is accepted; all other roles raise `ValueError`.
- Tokens are never logged or returned to the client after session creation.
- `session_id` is the only credential the client needs to retain.
- Simple login (`simple_login`) bypasses OTP — use only in trusted/internal contexts.
