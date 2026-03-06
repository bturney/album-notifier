"""
Setup validation script — run once after configuring your secrets.
Usage: uv run python validate.py
"""
import os
import sys
import re

try:
    import requests
except ImportError:
    print("[FAIL] 'requests' package not installed. Run: uv sync")
    sys.exit(1)

DISCORD_WEBHOOK_PATTERN = re.compile(r"https://discord(?:app)?\.com/api/webhooks/\d+/.+")

passed = 0
failed = 0


def check(label, ok, fix):
    global passed, failed
    if ok:
        print(f"[PASS] {label}")
        passed += 1
    else:
        print(f"[FAIL] {label}")
        print(f"       Fix: {fix}")
        failed += 1
    return ok


# 1. Check API_URL env var
api_url = os.environ.get("API_URL", "").strip()
api_url_ok = check(
    "API_URL is set",
    bool(api_url),
    "Set API_URL to your group's API URL, e.g. https://1001albumsgenerator.com/api/v1/groups/your-group-slug"
)
if api_url_ok:
    check(
        "API_URL starts with https://",
        api_url.startswith("https://"),
        "API_URL must start with https://"
    )

# 2. Check DISCORD_WEBHOOK_URL env var
webhook_url = os.environ.get("DISCORD_WEBHOOK_URL", "").strip()
webhook_ok = check(
    "DISCORD_WEBHOOK_URL is set",
    bool(webhook_url),
    "Set DISCORD_WEBHOOK_URL to your Discord webhook URL. See README: Setup > Discord Webhook."
)
if webhook_ok:
    check(
        "DISCORD_WEBHOOK_URL format looks valid",
        bool(DISCORD_WEBHOOK_PATTERN.match(webhook_url)),
        "URL should match: https://discord.com/api/webhooks/<id>/<token>"
    )

# 3. GET API_URL — verify 200 + JSON with currentAlbum
if api_url_ok and api_url.startswith("https://"):
    try:
        resp = requests.get(api_url, timeout=15)
        if resp.status_code == 200:
            try:
                data = resp.json()
                check(
                    "API returns valid data with currentAlbum",
                    "currentAlbum" in data,
                    "API responded but 'currentAlbum' key is missing. Double-check your group slug in API_URL."
                )
            except ValueError:
                check("API returns valid JSON", False, "API returned non-JSON response. Check your API_URL.")
        else:
            check(
                f"API returns HTTP 200",
                False,
                f"API returned HTTP {resp.status_code}. Check your API_URL and that your group slug is correct."
            )
    except requests.exceptions.ConnectionError:
        check("API is reachable", False, "Could not connect. Check your internet connection and API_URL.")
    except requests.exceptions.Timeout:
        check("API is reachable", False, "API request timed out. Check your internet connection.")
    except requests.exceptions.RequestException as e:
        check("API is reachable", False, f"Request error: {e}")

# 4. POST test message to Discord webhook
if webhook_ok and DISCORD_WEBHOOK_PATTERN.match(webhook_url):
    try:
        resp = requests.post(
            webhook_url,
            json={"content": "✅ Album Notifier setup check — if you see this, your webhook is working!"},
            timeout=15,
        )
        if resp.status_code in (200, 204):
            check("Discord webhook accepts test message", True, "")
        elif resp.status_code in (401, 403):
            check(
                "Discord webhook accepts test message",
                False,
                f"HTTP {resp.status_code}: Webhook token is invalid. Regenerate the webhook in Discord server settings."
            )
        elif resp.status_code == 404:
            check(
                "Discord webhook accepts test message",
                False,
                "HTTP 404: Webhook not found. It may have been deleted. Create a new webhook and update DISCORD_WEBHOOK_URL."
            )
        elif resp.status_code == 429:
            check(
                "Discord webhook accepts test message",
                False,
                "HTTP 429: Rate limited by Discord. Wait a few minutes and try again."
            )
        else:
            check(
                "Discord webhook accepts test message",
                False,
                f"HTTP {resp.status_code}: Unexpected response from Discord."
            )
    except requests.exceptions.RequestException as e:
        check("Discord webhook is reachable", False, f"Request error: {e}")

print()
print(f"Results: {passed} passed, {failed} failed")
if failed == 0:
    print("All checks passed! Run 'uv run python notify.py' to send today's album.")
    sys.exit(0)
else:
    print("Fix the issues above, then re-run this script.")
    sys.exit(1)
