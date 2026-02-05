"""
Solution: Multi-Role JWT Auth Demo

Implements:
- In‑memory user "database"
- Signup with bcrypt password hashing
- Login with JWT issuance
- Token validation
- Role-based authorization for fake endpoints
"""

import time
import bcrypt
import jwt

# =========================================================
# CONFIG
# =========================================================

SECRET_KEY = "supersecretkey"  # in real apps: ENV variable
ALGO = "HS256"
TOKEN_TTL_SECONDS = 60

# In‑memory "users table"
# username -> {"password_hash": bytes, "role": str}
users: dict[str, dict] = {}


# =========================================================
# SIGNUP
# =========================================================

def signup(username: str, password: str, role: str) -> None:
    """
    Register a new user:
    - hash password
    - store hash + role in users dict
    """
    if username in users:
        print(f"[signup] User '{username}' already exists")
        return

    password_bytes = password.encode("utf-8")
    pwd_hash = bcrypt.hashpw(password_bytes, bcrypt.gensalt())

    users[username] = {
        "password_hash": pwd_hash,
        "role": role,
    }

    print(f"[signup] Created user '{username}' with role '{role}'")
    print(f"[signup] Stored hash for {username}: {pwd_hash!r}")


# =========================================================
# LOGIN + TOKEN ISSUANCE
# =========================================================

def login(username: str, password: str) -> str | None:
    """
    Authenticate user and return a signed JWT if successful.
    """
    user = users.get(username)
    if not user:
        print(f"[login] User '{username}' not found")
        return None

    password_bytes = password.encode("utf-8")
    if not bcrypt.checkpw(password_bytes, user["password_hash"]):
        print(f"[login] Invalid password for '{username}'")
        return None

    payload = {
        "sub": username,
        "role": user["role"],
        "exp": int(time.time()) + TOKEN_TTL_SECONDS,
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGO)
    print(f"[login] Login successful for '{username}'")
    print(f"[login] Issued token: {token}")
    return token


# =========================================================
# TOKEN DECODING / VALIDATION
# =========================================================

def decode_token(token: str) -> dict | None:
    """
    Decode and validate a JWT.
    Returns payload dict if valid, else None.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGO])
        print("[decode_token] Token is valid")
        print(f"[decode_token] Payload: {payload}")
        return payload
    except jwt.ExpiredSignatureError:
        print("[decode_token] Token expired ")
    except jwt.InvalidTokenError:
        print("[decode_token] Invalid token ")

    return None


# =========================================================
# AUTHORIZATION HELPER
# =========================================================

def require_role(token: str, allowed_roles: list[str]) -> dict | None:
    """
    Check that token is valid and user role is in allowed_roles.
    Returns payload if access granted, else None.
    """
    payload = decode_token(token)
    if not payload:
        print("[require_role] Authentication failed")
        return None

    role = payload.get("role")
    if role in allowed_roles:
        print(f"[require_role] Access granted (role={role}) ")
        return payload

    print(f"[require_role] Access denied (role={role}) ")
    return None


# =========================================================
# FAKE PROTECTED ENDPOINTS
# =========================================================

def delete_user(token: str, username_to_delete: str) -> None:
    """
    Only 'admin' can delete users.
    """
    print(f"\n[endpoint] delete_user called by token holder for '{username_to_delete}'")
    payload = require_role(token, ["admin"])
    if not payload:
        print("[delete_user] Forbidden")
        return

    # Just simulate delete
    print(f"[delete_user] User '{username_to_delete}' deleted (simulated)")


def view_profile(token: str) -> None:
    """
    'admin' and 'user' can view their own profile.
    """
    print("\n[endpoint] view_profile called")
    payload = require_role(token, ["admin", "user"])
    if not payload:
        print("[view_profile] Forbidden")
        return

    username = payload.get("sub")
    print(f"[view_profile] Showing profile for '{username}'")


# =========================================================
# DEMO / TEST FLOW
# =========================================================

if __name__ == "__main__":
    # Signup two users
    signup("alice", "alice123", role="admin")
    signup("bob", "bob123", role="user")

    print("\n========== LOGIN AND TOKEN GENERATION ==========\n")

    # Login both users
    alice_token = login("alice", "alice123")
    bob_token = login("bob", "bob123")

    print("\n========== ACCESS TESTS (VALID TOKEN) ==========\n")

    # Alice (admin) can delete and view
    if alice_token:
        view_profile(alice_token)
        delete_user(alice_token, "bob")

    # Bob (user) can view, but should not delete
    if bob_token:
        view_profile(bob_token)
        delete_user(bob_token, "alice")

    print("\n========== EXPIRY TEST ==========\n")
    print("Waiting for token expiry (sleeping a bit more than TTL)...")
    time.sleep(TOKEN_TTL_SECONDS + 2)

    # Try to use expired token
    if alice_token:
        view_profile(alice_token)
