# askoxy.ai MCP Server

A FastMCP server exposing the askoxy.ai e-commerce API to MCP-compatible clients (e.g. Amazon Q).

---

## Architecture

```
mcpDocker/
├── mcpserver/
│   ├── server.py          # FastMCP entry point – registers all tools
│   ├── start.py           # Flexible launcher (web | mcp | both)
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── .env.example
│   ├── auth/              # OTP login, registration, token store
│   ├── products/          # Search, public listing, images, combos
│   ├── user/              # Profile, addresses
│   ├── cart/              # Add, view, decrement, remove
│   ├── orders/            # Validation, management, checkout
│   └── utils/             # HTTP helpers (httpx)
└── simple_server.py       # Minimal standalone test server
```

---

## Authentication Flow

askoxy.ai uses **OTP-only** authentication (no password).

```
1. send_login_otp(mobile, country_code, registration_type)
        │
        ▼
   Returns: { otpSession, salt, otpGeneratedTime }
        │
2. verify_login_otp(otp_session, otp_value, salt, ...)
        │
        ▼
   Returns: { session_id }   ← store this for all subsequent calls
```

- `session_id` is a UUID stored in `~/.askoxy_sessions.json` (persisted across restarts).
- All authenticated tools require `session_id` as a parameter.
- Only `CUSTOMER` user type is permitted.

### Registration Flow

```
1. send_register_otp(mobile, country_code, registration_type)
2. verify_otp_and_authenticate(..., user_type="Register")
   → Returns: { session_id, user_status }
```

---

## Tool Reference

### Public (no auth)
| Tool | Description |
|------|-------------|
| `hello_world` | Health check |
| `get_trending_products` | Browse trending products |

### Auth
| Tool | Description |
|------|-------------|
| `send_login_otp` | Send OTP via SMS or WhatsApp |
| `verify_login_otp` | Verify OTP → get session_id |
| `send_register_otp` | Send OTP for new user |
| `verify_otp_and_authenticate` | Verify OTP for login or register |

### Products (auth required)
| Tool | Description |
|------|-------------|
| `dynamic_product_search` | Keyword search |
| `get_product_suggestions` | AI-powered recommendations |
| `get_product_images` | Images by itemId |
| `get_combo_item_details` | Combo offer details |

### User
| Tool | Description |
|------|-------------|
| `get_customer_profile` | Fetch profile |
| `update_customer_profile` | Create/update profile |
| `view_address_list` | List saved addresses |
| `add_address` | Add delivery address |

### Cart
| Tool | Description |
|------|-------------|
| `add_to_cart` | Add / increment item |
| `view_user_cart` | View cart with totals |
| `decrement_cart_item` | Reduce quantity by 1 |
| `remove_cart_item` | Remove item entirely |

### Orders
| Tool | Description |
|------|-------------|
| `check_order_conditions` | Validate cart constraints |
| `check_delivery_availability` | Check pincode serviceability |
| `place_order` | Place order after payment |
| `get_order_history` | Past orders |
| `track_order` | Current order status |
| `cancel_order` | Cancel eligible order |

### Checkout (sequential)
`fetch_cart_summary` → `get_user_addresses` → `validate_pincode_serviceability` → `calculate_delivery_charges` → `get_available_coupons` → `apply_wallet_amount` → `fetch_delivery_slots` → `initiate_payment` → `confirm_payment` → `validate_checkout`

---

## Quick Start

### 1. Local (MCP mode)

```bash
cd mcpserver
cp .env.example .env
pip install -r requirements.txt
SERVER_MODE=mcp python start.py
# SSE endpoint: http://localhost:8001/sse
```

### 2. Docker

```bash
cd mcpserver
docker build -t askoxy-mcp .
docker run -p 8001:8001 -e SERVER_MODE=mcp askoxy-mcp
```

### 3. Both (MCP + Web)

```bash
docker run -p 8001:8001 -e SERVER_MODE=both askoxy-mcp
# Web:  http://localhost:8001/
# MCP:  http://localhost:8001/mcp/sse
```

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SERVER_MODE` | `web` | `web` \| `mcp` \| `both` |
| `PORT` | `8001` | Server port |
| `MCP_PORT` | `8001` | MCP SSE port |
| `DEBUG` | `false` | Enable debug logging |

---

## Deployment

### Render

```bash
# render.yaml is pre-configured
# Set SERVER_MODE=both in Render environment variables
```

### Amazon Q / MCP Client Config

```json
{
  "mcpServers": {
    "askoxy": {
      "serverUrl": "https://<your-render-url>/mcp/sse",
      "transport": "sse"
    }
  }
}
```

---

## Security

- No secrets in code — use `.env` or environment variables only.
- Sessions stored locally in `~/.askoxy_sessions.json`.
- Only `CUSTOMER` role permitted; all other roles are rejected.
- All HTTP calls use 30s timeout via `httpx`.
