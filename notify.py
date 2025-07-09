import requests
import os

API_URL = "https://1001albumsgenerator.com/api/v1/groups/musicnerds"
DISCORD_WEBHOOK_URL = os.environ["DISCORD_WEBHOOK_URL"]

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
        "thumbnail": {"url": album['images'][0]['url']} if album.get('images') else {},
        "color": 0x3498db,
        "footer": {
            "text": f"📊 {stats['albums']} albums rated, {stats['votes']} votes cast. Group average: {stats['avg']}/5"
        }
    }
    return embed

def main():
    data = requests.get(API_URL).json()
    embed = build_album_embed(data)
    requests.post(
        DISCORD_WEBHOOK_URL,
        json={"content": "🎧 **Today's Album of the Day!** 🎵", "embeds": [embed]},
        timeout=10,
    )
    print(f"Posted: {embed['title']}")

if __name__ == "__main__":
    main()