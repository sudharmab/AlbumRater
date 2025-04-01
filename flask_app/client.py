import requests
import time


class Album(object):
    def __init__(self, spotify_json, spotify_client):
        self.id = spotify_json.get("id", "Unknown ID")
        self.name = spotify_json.get("name", "Unknown Name")
        self.release_date = spotify_json.get("release_date", "Unknown Date")
        self.artists = [
            artist["name"]
            for artist in spotify_json.get("artists", [])
            if "name" in artist
        ]

        images = spotify_json.get("images", [])
        self.image = images[1]["url"] if len(images) > 1 else None

        artist_id = (
            spotify_json["artists"][0]["id"] if spotify_json.get("artists") else None
        )
        self.genres = []
        if artist_id:
            artist_data = spotify_client.get_artist_by_id(artist_id)
            self.genres = artist_data.get("genres", [])


class SpotifyClient(object):
    def __init__(self):
        self.sess = requests.Session()
        self.auth_url = "https://accounts.spotify.com/api/token"
        self.auth_data = {
            "grant_type": "client_credentials",
            "client_id": "d2e304cbc8904703bc9ced052fdb6fc9",
            "client_secret": "0d4e8bcd7da44d7b80362db9007184ed",
        }

        try:
            self.auth_response = requests.post(self.auth_url, data=self.auth_data)
            self.auth_response.raise_for_status()
            self.access_token = self.auth_response.json().get("access_token")
            if not self.access_token:
                raise Exception("Failed to retrieve access token.")
        except requests.RequestException as e:
            print(f"Error fetching access token: {e}")
            self.access_token = None
        except ValueError:
            print("Error: Failed to decode Spotify authentication response.")
            self.access_token = None

    def search(self, search_string):
        search_url = "https://api.spotify.com/v1/search"
        headers = {"Authorization": f"Bearer {self.access_token}"}
        params = {"q": search_string, "type": "album", "limit": 10}
        response = requests.get(search_url, headers=headers, params=params)
        data = response.json()

        results = []
        for album_json in data["albums"]["items"]:
            # Pass the current instance (self) to the Album class
            results.append(Album(album_json, self))

        return results

    def get_album_by_id(self, id):
        if not self.access_token:
            print("No access token available. Cannot fetch album.")
            return None

        album_url = f"https://api.spotify.com/v1/albums/{id}"
        headers = {"Authorization": f"Bearer {self.access_token}"}
        try:
            response = self.sess.get(album_url, headers=headers)
            response.raise_for_status()
            data = response.json()
            return Album(data, self)
        except requests.RequestException as e:
            print(f"Error fetching album with ID {id}: {e}")
        except ValueError:
            print("Error decoding JSON response for album details.")
        return None

    def get_artist_by_id(self, artist_id):
        artist_url = f"https://api.spotify.com/v1/artists/{artist_id}"
        headers = {"Authorization": f"Bearer {self.access_token}"}
        response = self.sess.get(artist_url, headers=headers)
        data = response.json()
        return data

    def make_request_with_retries(url, headers, max_retries=3):
        retries = 0
        while retries < max_retries:
            try:
                response = requests.get(url, headers=headers)
                response.raise_for_status()
                return response
            except requests.RequestException as e:
                retries += 1
                print(f"Request failed: {e}. Retrying {retries}/{max_retries}...")
                time.sleep(2**retries)
        return None
