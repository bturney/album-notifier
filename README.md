# Discord Album Notifier

Automatically posts your [1001 Albums Generator](https://1001albumsgenerator.com) daily album to a Discord channel — with group stats, streaming links, and your all-time favorites.

> Listed as a third-party app on 1001albumsgenerator.com

---

## What it posts

Each day, your Discord channel gets a message like this:

<img width="568" height="326" alt="image" src="https://github.com/user-attachments/assets/e5f7e4d5-50a7-4def-9d54-bc3e6edaefb5" />


---

## Quick Start (5 minutes)

### 1. Create your copy

Click **"Use this template"** at the top of this page, then **"Create a new repository"**. Give it any name you like and make it private or public — your choice.

> If you don't see "Use this template", you may need to be logged into GitHub.

### 2. Find your API URL

1. Go to [1001albumsgenerator.com](https://1001albumsgenerator.com) and open your group's page
2. Your group URL looks like: `https://1001albumsgenerator.com/groups/your-group-slug`
3. Your API URL is: `https://1001albumsgenerator.com/api/v1/groups/your-group-slug`

(Just add `/api/v1` before `/groups` in the URL.)

### 3. Create a Discord webhook

1. Open your Discord server
2. Go to **Server Settings** → **Integrations** → **Webhooks**
3. Click **New Webhook**
4. Choose the channel where albums should be posted
5. Click **Copy Webhook URL** — save this for the next step

> **Keep this URL secret.** Anyone who has it can post messages to your channel. Don't paste it into code or share it publicly — that's exactly what the GitHub secret in the next step is for.

### 4. Add your secrets to GitHub

In your new repository, go to **Settings** → **Secrets and variables** → **Actions**, then click **New repository secret** for each:

| Name | Value |
|------|-------|
| `API_URL` | Your API URL from Step 2 |
| `DISCORD_WEBHOOK_URL` | Your webhook URL from Step 3 |

### 5. Test it

Go to the **Actions** tab in your repository, click **Album Notifier** in the left sidebar, then click **Run workflow** → **Run workflow**. Check your Discord channel — the album should appear within a minute.

---

## Customizing your schedule

The notifier runs **Monday–Friday at 8am US Eastern** by default. To change this, edit `.github/workflows/notify.yml` and update the `cron:` line.

Some common options are already in the file as comments:

```yaml
# Include weekends:       '0 12 * * *'
# 9am US Eastern:        '0 13 * * 1-5'
# 8am US Pacific:        '0 15 * * 1-5'
# 9am UK:                '0 9 * * 1-5'
```

GitHub Actions uses **UTC time**, so the examples above account for timezone offsets.

> **Note on Daylight Saving Time:** GitHub Actions cron doesn't automatically adjust for DST. When clocks change, your notification will shift by 1 hour. You can manually update the cron line twice a year, or simply accept the 1-hour drift.

---

## Keeping it running

GitHub automatically **disables scheduled workflows after 60 days of repository inactivity** (no commits). You'll receive an email warning before this happens.

To keep the notifier running without any code changes, you can either:
- **Re-enable it manually**: Go to Actions → Album Notifier → click the banner to re-enable
- **Push any small change**: Edit any file (e.g., add a space to the README) and commit it

---

## Running locally

You'll need [uv](https://docs.astral.sh/uv/getting-started/installation/) installed.

```bash
# Set your environment variables
export API_URL="https://1001albumsgenerator.com/api/v1/groups/your-group-slug"
export DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/..."

# Validate your setup (run this first)
uv run python validate.py

# Send today's album
uv run python notify.py
```

---

## Troubleshooting

**The workflow never runs**
Make sure both secrets (`API_URL` and `DISCORD_WEBHOOK_URL`) are set under Settings → Secrets and variables → Actions. The script exits immediately with an error if either is missing.

**I see an error in the Actions log**
Click the failed run in the Actions tab, then click the **notify** job to see the full output. The error message will tell you exactly what went wrong.

**Nothing posts to Discord**
Run `validate.py` locally (see above) — it checks both the API and your Discord webhook and tells you specifically what's failing.

**"Webhook not found" error**
The webhook URL was deleted in Discord. Go back to Server Settings → Integrations → Webhooks, create a new one, and update the `DISCORD_WEBHOOK_URL` secret in GitHub.

**Notifications stopped after ~2 months**
GitHub disabled the scheduled workflow due to inactivity. Go to the Actions tab and re-enable it, or push any commit to the repo.

**The notification time shifted by an hour**
Daylight Saving Time changed. Update the cron line in `.github/workflows/notify.yml` if you want to keep a consistent local time.

---

## License

MIT — see [LICENSE](LICENSE)
