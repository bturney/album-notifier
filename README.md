# Discord Album Notifier 🎵

A simple Python script that fetches the daily album from [1001albumsgenerator.com](https://1001albumsgenerator.com) and posts it to a Discord webhook with group statistics and favorites.

## Features

- 🎧 Posts daily album notifications to Discord
- 🏆 Shows group's all-time favorite album
- 💀 Shows group's least favorite album  
- 🌟 Displays favorite and least favorite genres
- 📊 Includes group statistics (albums rated, votes cast, average rating)
- 🔗 Provides streaming links (Spotify, Apple Music, etc.)

## Setup

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd album-notifier
   ```

2. **Install dependencies**
   ```bash
   pip install requests
   ```

3. **Set up Discord webhook**
   - Go to your Discord server settings
   - Navigate to Integrations → Webhooks
   - Create a new webhook and copy the URL

4. **Set environment variables**
   ```bash
   export DISCORD_WEBHOOK_URL="your-discord-webhook-url-here"
   export API_URL="https://1001albumsgenerator.com/api/v1/groups/your-group-slug"
   ```

## Usage

Run the script:
```bash
python notify.py
```

The script will:
1. Fetch the current album from your 1001albumsgenerator group
2. Build a rich Discord embed with album info and group statistics
3. Post it to your Discord channel

## Example Output

The script creates a Discord embed that looks like:

**Title:** 🎵 **Album Name** – **Artist** (Year)

**Description:**
- 🎭 **Genre(s):** Rock, Pop
- [Reviews] | [Wikipedia] | [Spotify] | [Apple Music]

**Fields:**
- 🏆 **All-Time Favorite:** *Album Name* - Artist (4.5/5)
- 💀 **Least Favorite:** *Album Name* - Artist (1.2/5)  
- 🌟 **Favorite Genre:** Rock (3.8/5 avg)
- 👎 **Worst Genre:** Funk (1.2/5 avg)

**Footer:** 📊 28 albums rated, 111 votes cast. Group average: 2.83/5

## Configuration

The script uses environment variables for configuration:

- `DISCORD_WEBHOOK_URL` (required): Your Discord webhook URL
- `API_URL` (required): Your 1001albumsgenerator group API URL

Both environment variables must be set for the script to work.

## Requirements

- Python 3.6+
- `requests` library
- Discord webhook URL
- 1001albumsgenerator group

## License

MIT License - feel free to use and modify!
