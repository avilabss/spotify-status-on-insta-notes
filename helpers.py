import requests
import time

from instagrapi import Client
from defaults import config


class TokenError(Exception):
    pass

class ResponseError(Exception):
    pass

class InstaClient(Client):
    """
    Extending features of instagrapi client to support notes related endpoints.
    """

    def _get_my_note_id(self) -> int:
        """
        Fetch notes
        """
        notes = self.private_request("notes/get_notes/")
        items = notes["items"]

        if len(items) == 0:
            return None

        first_note_id = items[0]["id"]
        first_user_id = items[0]["user_id"]

        if first_user_id != self.user_id:
            return None

        return first_note_id

    def create_note(self, note: str) -> None:
        """
        Create or update note.
        :param note: Note text.
        """

        uuid = self.uuid
        note = note.replace(" ", "+")
        data = "text={}&_uuid={}&audience=0".format(note, uuid)
        self.private_request("notes/create_note/", data, with_signature=False)

    def delete_my_note(self) -> None:
        """
        Delete note
        """

        uuid = self.uuid
        note_id = self._get_my_note_id()

        if note_id:
            print(f"Deleting note id: {note_id}")
            data = "id={}&_uuid={}".format(note_id, uuid)
            self.private_request("notes/delete_note/", data, with_signature=False)


def get_currently_playing() -> dict:
    """
    Get what's currently playing on your spotify.
    """

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
    """
    Create a note by pasing spotify response.
    :param json_data: Spotify response data.
    :return: Note of usefull info.
    """

    note_text = ""

    if not json_data:
        return None

    playing_status = json_data["is_playing"]
    song_name = json_data["item"]["name"]
    album_name = json_data["item"]["album"]["name"]
    artists_list = json_data["item"]["artists"]
    artist_names = []

    for artist in artists_list:
        artist_name = artist["name"]
        artist_names.append(artist_name) 

    if not playing_status:
        return None

    note_text += f"Listening to spotify\n\n"
    note_text += f"{song_name}\n"
    note_text += f"by {', '.join(artist_names)}\n"
    note_text += f"on {album_name}\n"
    note_text.strip()

    note_text += "\n\n"
    note_text += "Live Spotify status feature by\n"
    note_text += "https://github.com/git-avilabs/spotify-status-on-insta-notes"

    return note_text


def main_loop(client: InstaClient) -> None:
    """
    Loop forever updating notes with what you are listning with a delay
    :param client: Modified client with extra features
    """

    while True:
        note = make_note(get_currently_playing())

        if note is None:
            print("Nothing is playing, so no notes to be added")
            client.delete_my_note()
            time.sleep(int(config.get("settings", "loop-delay")))
            continue

        client.create_note(note)
        print("Note updated!")

        time.sleep(int(config.get("settings", "loop-delay")))
