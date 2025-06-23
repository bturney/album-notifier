import requests
import os

API_URL = "https://1001albumsgenerator.com/api/v1/groups/musicnerds"
DISCORD_WEBHOOK_URL = os.environ["DISCORD_WEBHOOK_URL"]

def build_album_embed(data):
    album = data["currentAlbum"]
    last = data["latestAlbum"]
    favorites = data.get("highestRatedAlbums", [])
    worsts = data.get("worstGenres", [])
    stats = {
        "albums": data.get("numberOfGeneratedAlbums", "?"),
        "votes": data.get("totalVotes", "?"),
        "avg": data.get("averageRating", "?")
    }

    # Group favorite (highest rated album)
    if favorites:
        fav = favorites[0]
        fav_str = f"*{fav['name']}* - {fav['averageRating']:.2f}/5"
    else:
        fav_str = "?"

    # Group least favorite genre
    if worsts:
        worst = worsts[0]
        worst_str = f"{worst['genre'].capitalize()} ({worst['rating']:.2f}/5 avg)"
    else:
        worst_str = "?"

    # Streaming links
    links = [f"[Reviews]({album['globalReviewsUrl']})"]
    if album.get("wikipediaUrl"):
        links.append(f"[Wikipedia]({album['wikipediaUrl']})")
    if album.get("spotifyId"):
        links.append(f"[Spotify](https://open.spotify.com/album/{album['spotifyId']})")
    if album.get("appleMusicId"):
        links.append(f"[Apple Music](https://music.apple.com/album/{album['appleMusicId']})")

    links_str = " | ".join(links)

    embed = {
        "title": f"***{album['name']}*** – **{album['artist']}** ({album.get('releaseDate', '')})",
        "description":
            f"**Genre(s):** {', '.join(album.get('genres', [])) or '?'}\n"
            f"{links_str}\n\n"
            f"**All-time group favorite:**\n{fav_str}\n\n"
            f"**Genre we hate:**\n{worst_str}\n\n"
            f"*{stats['albums']} albums rated, {stats['votes']} votes cast. Group average: {stats['avg']}/5*",
        "thumbnail": {"url": album['images'][0]['url']} if album.get('images') else {},
        "color": 0x3498db,
    }
    return embed

def main():
    data = requests.get(API_URL).json()
    embed = build_album_embed(data)
    requests.post(
        DISCORD_WEBHOOK_URL,
        json={"content": "🎧 **Today's Album!**", "embeds": [embed]},
        timeout=10,
    )
    print(f"Posted: {embed['title']}")

if __name__ == "__main__":
    main()