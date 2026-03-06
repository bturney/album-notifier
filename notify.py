import sys
import re
import requests
import os


def get_env(name, *, validate=None):
    value = os.environ.get(name, "").strip()
    if not value:
        print(f"Error: Missing required environment variable: {name}. See README for setup instructions.")
        sys.exit(1)
    if validate and not validate(value):
        print(f"Error: Invalid value for {name}. See README for setup instructions.")
        sys.exit(1)
    return value


DISCORD_WEBHOOK_PATTERN = re.compile(r"https://discord(?:app)?\.com/api/webhooks/\d+/.+")

API_URL = get_env("API_URL", validate=lambda v: v.startswith("https://"))
DISCORD_WEBHOOK_URL = get_env("DISCORD_WEBHOOK_URL", validate=lambda v: bool(DISCORD_WEBHOOK_PATTERN.match(v)))


def build_album_embed(data):
    album = data["currentAlbum"]
    last = data["latestAlbum"]
    favorites = data.get("highestRatedAlbums", [])
    worsts = data.get("lowestRatedAlbums", [])
    favorite_genres = data.get("favoriteGenres", [])
    worst_genres = data.get("worstGenres", [])
    stats = {
        "albums": data.get("numberOfGeneratedAlbums", "?"),
        "votes": data.get("totalVotes", "?"),
        "avg": data.get("averageRating", "?")
    }

    # Group favorite (highest rated album)
    if favorites:
        fav = favorites[0]
        fav_str = f"*{fav['name']}* - {fav['artist']} ({fav['averageRating']:.1f}/5)"
    else:
        fav_str = "❓ No favorites yet"

    # Group least favorite album
    if worsts:
        worst = worsts[0]
        worst_str = f"*{worst['name']}* - {worst['artist']} ({worst['averageRating']:.1f}/5)"
    else:
        worst_str = "❓ No least favorites yet"

    # Group favorite genre
    if favorite_genres:
        fav_genre = favorite_genres[0]
        fav_genre_str = f"{fav_genre['genre'].replace('-', ' ').title()} ({fav_genre['rating']:.1f}/5 avg)"
    else:
        fav_genre_str = "❓ No favorite genre yet"

    # Group least favorite genre
    if worst_genres:
        worst_genre = worst_genres[0]
        worst_genre_str = f"{worst_genre['genre'].replace('-', ' ').title()} ({worst_genre['rating']:.1f}/5 avg)"
    else:
        worst_genre_str = "❓ No least favorite genre yet"

    # Streaming links
    links = [f"[Reviews]({album['globalReviewsUrl']})"]
    if album.get("wikipediaUrl"):
        links.append(f"[Wikipedia]({album['wikipediaUrl']})")
    if album.get("spotifyId"):
        links.append(f"[Spotify](https://open.spotify.com/album/{album['spotifyId']})")
    if album.get("appleMusicId"):
        links.append(f"[Apple Music](https://music.apple.com/album/{album['appleMusicId']})")

    links_str = " | ".join(links)

    # Format genres nicely
    genres = [genre.replace('-', ' ').title() for genre in album.get('genres', [])]
    genres_str = ', '.join(genres) if genres else 'Unknown'

    # Thumbnail: only include if images list is non-empty
    images = album.get('images') or []
    embed = {
        "title": f"🎵 **{album['name']}** – **{album['artist']}** ({album.get('releaseDate', '')})",
        "description": f"🎭 **Genre(s):** {genres_str}\n{links_str}",
        "fields": [
            {
                "name": "🏆 All-Time Favorite",
                "value": fav_str,
                "inline": False
            },
            {
                "name": "💀 Least Favorite",
                "value": worst_str,
                "inline": False
            },
            {
                "name": "🌟 Favorite Genre",
                "value": fav_genre_str,
                "inline": True
            },
            {
                "name": "👎 Worst Genre",
                "value": worst_genre_str,
                "inline": True
            }
        ],
        "color": 0x3498db,
        "footer": {
            "text": f"📊 {stats['albums']} albums rated, {stats['votes']} votes cast. Group average: {stats['avg']}/5"
        }
    }
    if images:
        embed["thumbnail"] = {"url": images[0]['url']}
    return embed


def fetch_album_data():
    try:
        response = requests.get(API_URL, timeout=15)
    except requests.exceptions.ConnectionError:
        print(f"Error: Could not connect to the API. Check your internet connection and API_URL.")
        sys.exit(1)
    except requests.exceptions.Timeout:
        print(f"Error: API request timed out after 15 seconds.")
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"Error: API request failed: {e}")
        sys.exit(1)

    if response.status_code != 200:
        print(f"Error: API returned status {response.status_code}. Check your API_URL.")
        sys.exit(1)

    try:
        data = response.json()
    except ValueError:
        print("Error: API returned malformed JSON.")
        sys.exit(1)

    if "currentAlbum" not in data:
        print("Error: API response missing 'currentAlbum'. Check your API_URL points to a valid group.")
        sys.exit(1)

    return data


def post_to_discord(embed):
    try:
        response = requests.post(
            DISCORD_WEBHOOK_URL,
            json={"content": "🎧 **Today's Album of the Day!** 🎵", "embeds": [embed]},
            timeout=15,
        )
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        status = e.response.status_code if e.response is not None else "unknown"
        if status in (401, 403):
            print(f"Error: Discord rejected the webhook (HTTP {status}). Check your DISCORD_WEBHOOK_URL is correct.")
        elif status == 404:
            print("Error: Discord webhook not found (HTTP 404). The webhook may have been deleted. Create a new one.")
        elif status == 429:
            print("Error: Discord rate limited (HTTP 429). Wait a few minutes and try again.")
        else:
            print(f"Error: Discord webhook request failed: {e}")
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"Error: Could not reach Discord: {e}")
        sys.exit(1)


def main():
    data = fetch_album_data()
    embed = build_album_embed(data)
    post_to_discord(embed)
    print(f"Posted: {embed['title']}")
    sys.exit(0)


if __name__ == "__main__":
    main()
