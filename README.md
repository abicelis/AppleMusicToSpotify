# Installation

- Clone this project
- Create a python env `python3 -m venv env`
- Activate the env `source env/bin/activate`
- Install requirements with PIP `pip install -r requirements.txt`

# Usage

```
Usage: python script.py <Spotify user ID> <Spotify OAuth Token> <Apple Playlist URL>
   - Spotify user ID: This is your normal Username (Get it here: https://www.spotify.com/us/account/overview/)
   - Spotify OAuth Token: Get this token from https://developer.spotify.com/console/post-playlist-tracks/ (Make sure to add 'playlist-modify-public' and 'playlist-modify-private' scopes)
   - Apple Playlist URL: Should start with 'https://music.apple.com/us/playlist/ ...'
```