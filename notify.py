import requests
import os

API_URL = "https://1001albumsgenerator.com/api/v1/groups/musicnerds"
DISCORD_WEBHOOK_URL = os.environ["DISCORD_WEBHOOK_URL"]

def fetch_current_album():
    r = requests.get(API_URL)
    r.raise_for_status()
    data = r.json()["currentAlbum"]
    return {
        "uuid": data["uuid"],
        "title": data["name"],
        "artist": data["artist"],
        "year": data["releaseDate"],
        "cover": data["images"][0]["url"] if data.get("images") else None,
        "genres": ", ".join(data.get("genres", [])),
        "reviews_url": data["globalReviewsUrl"],
        "wikipedia_url": data.get("wikipediaUrl"),
        "spotify_url": f"https://open.spotify.com/album/{data['spotifyId']}" if data.get("spotifyId") else None,
        "apple_music_url": f"https://music.apple.com/album/{data['appleMusicId']}" if data.get("appleMusicId") else None
    }

def send_to_discord(album):
    embed = {
        "title": f"***{album['title']}*** - **{album['artist']}**",
        "description": f"**Year:** {album['year']}\n"
                       + (f"**Genre(s):** {album['genres']}\n" if album['genres'] else "")
                       + f" • [Reviews]({album['reviews_url']})\n"
                       + (f" • [Wikipedia]({album['wikipedia_url']})\n" if album['wikipedia_url'] else "")
                       + (f" • [Spotify]({album['spotify_url']})\n" if album['spotify_url'] else "")
                       + (f" • [Apple Music]({album['apple_music_url']})" if album['apple_music_url'] else ""),
        "thumbnail": {"url": album['cover']} if album['cover'] else {},
        "color": 0x3498db,
    }

    requests.post(
        DISCORD_WEBHOOK_URL,
        json={"content": "🎧 **Today's Album:**", "embeds": [embed]},
        timeout=10
    )

if __name__ == "__main__":
    album = fetch_current_album()
    send_to_discord(album)
    print(f"Sent album: {album['title']} by {album['artist']}")

