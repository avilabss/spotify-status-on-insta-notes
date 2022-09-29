import requests
import time

from instagrapi import Client
from defaults import config


class TokenError(Exception):
    pass

class ResponseError(Exception):
    pass

class InstaClient(Client):
    def create_note(self, note: str):
        uuid = self.uuid
        note = note.replace(" ", "+")

        data = "text={}&_uuid={}&audience=0".format(note, uuid)

        self.private_request("notes/create_note/", data, with_signature=False)


def get_currently_playing() -> dict:
    url = "https://api.spotify.com/v1/me/player/currently-playing?market=IN"

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {config.get('spotify', 'o-auth-token')}"
    }

    response = requests.get(url, headers=headers)

    if not response.ok:
        raise ResponseError(response.text)

    if response.status_code == 204:
        # Nothing is playing
        return {}

    if response.status_code == 401:
        raise TokenError

    return response.json()


def make_note(json_data: dict) -> str:
    default_text = "Playing nothing..."
    note_text = ""

    if not json_data:
        return default_text

    playing_status = json_data["is_playing"]
    song_name = json_data["item"]["name"]
    album_name = json_data["item"]["album"]["name"]
    artists_list = json_data["item"]["artists"]
    artist_names = []

    for artist in artists_list:
        artist_name = artist["name"]
        artist_names.append(artist_name) 

    if not playing_status:
        return default_text

    note_text += f"Listening to spotify\n\n"
    note_text += f"{song_name}\n"
    note_text += f"by {', '.join(artist_names)}\n"
    note_text += f"on {album_name}\n"
    note_text.strip()

    

    return note_text


def main_loop(client: InstaClient):
    while True:
        note = make_note(get_currently_playing())
        client.create_note(note)
        print("Note updated!")

        time.sleep(int(config.get("settings", "loop-delay")))
