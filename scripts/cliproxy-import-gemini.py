#!/usr/bin/env python3
"""Import Gemini CLI credentials into CLIProxyAPI.

Both tools use the same OAuth client ID,
so the refresh token is directly compatible. This converts Gemini CLI's oauth_creds.json
into CLIProxyAPI's GeminiTokenStorage format.

Useful when `cliproxyapi -login` fails (e.g., 1000+ GCP projects in picker)
and you already have a working Gemini CLI installation.

Usage:
    uv run cliproxy-import-gemini.py                     # default paths
    uv run cliproxy-import-gemini.py --source /path.json # custom source
"""

import argparse
import base64
import datetime
import json
import os
import stat
import sys
from pathlib import Path

CLIENT_ID = os.environ.get("GEMINI_OAUTH_CLIENT_ID", "")
CLIENT_SECRET = os.environ.get("GEMINI_OAUTH_CLIENT_SECRET", "")
SCOPES = [
    "https://www.googleapis.com/auth/cloud-platform",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
]


def decode_jwt_payload(token: str) -> dict:
    payload = token.split(".")[1]
    payload += "=" * (4 - len(payload) % 4)
    return json.loads(base64.urlsafe_b64decode(payload))


def main() -> None:
    parser = argparse.ArgumentParser(description="Import Gemini CLI creds into CLIProxyAPI")
    parser.add_argument(
        "--source",
        type=Path,
        default=Path.home() / ".gemini" / "oauth_creds.json",
        help="Gemini CLI credentials file (default: ~/.gemini/oauth_creds.json)",
    )
    parser.add_argument(
        "--auth-dir",
        type=Path,
        default=Path.home() / ".cli-proxy-api",
        help="CLIProxyAPI auth directory (default: ~/.cli-proxy-api)",
    )
    args = parser.parse_args()

    if not args.source.exists():
        print(f"Error: {args.source} not found", file=sys.stderr)
        print("Login with Gemini CLI first: gemini auth login", file=sys.stderr)
        sys.exit(1)

    src = json.loads(args.source.read_text())

    # Extract email from JWT id_token
    claims = decode_jwt_payload(src["id_token"])
    email = claims["email"]

    # Convert expiry
    expiry_ms = src.get("expiry_date", 0)
    if expiry_ms:
        dt = datetime.datetime.fromtimestamp(expiry_ms / 1000, tz=datetime.timezone.utc)
        expiry = dt.strftime("%Y-%m-%dT%H:%M:%S.000Z")
    else:
        expiry = "1970-01-01T00:00:00.000Z"

    # CLIProxyAPI GeminiTokenStorage format
    auth = {
        "token": {
            "access_token": src["access_token"],
            "token_type": "Bearer",
            "refresh_token": src["refresh_token"],
            "expiry": expiry,
            "token_uri": "https://oauth2.googleapis.com/token",
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "scopes": SCOPES,
            "universe_domain": "googleapis.com",
        },
        "project_id": "",
        "email": email,
        "auto": False,
        "checked": False,
        "type": "gemini",
    }

    # Filename: {email}-{project_id}.json (empty project → auto-detected on load)
    args.auth_dir.mkdir(parents=True, exist_ok=True)
    outfile = args.auth_dir / f"{email}-.json"
    outfile.write_text(json.dumps(auth, indent=2))
    outfile.chmod(stat.S_IRUSR | stat.S_IWUSR)  # 600

    print(f"Imported Gemini credentials for {email}")
    print(f"  Source: {args.source}")
    print(f"  Target: {outfile}")
    print()
    print("Restart the proxy: cliproxy.sh --stop && cliproxy.sh")


if __name__ == "__main__":
    main()
