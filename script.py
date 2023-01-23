import sys
import requests
import json
import re
import urllib.request
from bs4 import BeautifulSoup

# Constants
newSpotifyPlaylistName = "New Playlist"
spotifySearhEndpoint = "https://api.spotify.com/v1/search"
spotifyCreatePlaylistEndpoint = "https://api.spotify.com/v1/users/[user_id]/playlists"
spotifyAddItemsToPlaylistEndpoint = "https://api.spotify.com/v1/playlists/[playlist_id]/tracks"


def hr():
	print("----------------------------------------------------\n")

def getSpotifyHeader():
	spotifyHeaders = {
		'Authorization': f"Bearer {spotifyToken}",
		'Accept': "application/json",
		'Content-Type': "application/json",
	}
	return spotifyHeaders

def cleanup(string):
	string = re.sub(r'\(.*\)+', '', string)					# Remove stuff in parenthesis
	# print(string)
	string = re.sub(r'\[.*\]+', '', string)					# Remove stuff in brackets
	# print(string)
	string = re.sub(r'[^\.\,a-zA-Z0-9_\- &]+', '', string) 	# Remove strange characters
	# print(string)
	string = string.replace('  ', '')						# Remove double spaces.
	# print(string)
	string = string.strip()									# Remove starting/trailing blank spaces.
	# print(string)

	return string


def extractSongsFromApplePlaylist(appleMusicPlaylistUrl):
	with urllib.request.urlopen(appleMusicPlaylistUrl) as response:
		html = response.read()

	songs = []
	page = BeautifulSoup(html, features="html.parser")		
	rows = page.body.findAll('div', attrs={'class' : 'songs-list-row--playlist'})
	for row in rows:
		track = cleanup(row.find('div', attrs={'class' : 'songs-list-row__song-name'}).text)
		artist = cleanup(row.find('div', attrs={'class' : 'songs-list__song-link-wrapper'}).text)
		# print(f"'{track}' - '{artist}'")

		songs.append((track, artist))
	return songs


def retrieveSongURI(track, artist): 
	q = requests.utils.quote(f"track:{track} artist:{artist}")
	url = f"{spotifySearhEndpoint}?q={q}&type=track&limit=1"
	r = requests.get(url, headers=getSpotifyHeader())

	# print(r.text)

	if r.status_code == 200:
		try:
			spotifyTrack = r.json()['tracks']['items'][0]['name']
			spotifyArtist = r.json()['tracks']['items'][0]['artists'][0]['name']
			uri = r.json()['tracks']['items'][0]['uri']

			print(f"Found '{spotifyTrack}' by '{spotifyArtist}'. URI = {uri}")
			return uri
		except:
			print(f"ERROR: Could not find '{track}' by '{artist}'")
			return ""
	else:
		print(f"ERROR: '{r.json()}'")
		return ""


def createSpotifyPlaylist(playlistName):
	data = {
		'name': playlistName,
		'public': False,
		'collaborative': False,
	}

	url = spotifyCreatePlaylistEndpoint.replace("[user_id]", spotifyUserId)
	r = requests.post(url, data=json.dumps(data), headers=getSpotifyHeader())


	if r.status_code == 201:
		return r.json()["id"]

	print(f"ERROR: Could not create Playlist ({r.text})")
	return ""


def addSongsToSpotifyPlaylist(playlistId, songs):
	compositeSongs = [songs[x:x+100] for x in range(0, len(songs),100)]

	for l in compositeSongs:
		data = {
			'uris': l
		}

		url = spotifyAddItemsToPlaylistEndpoint.replace("[playlist_id]", playlistId)
		r = requests.post(url, data=json.dumps(data), headers=getSpotifyHeader())


		if r.status_code != 201:
			print(r.text)

if(len(sys.argv)) != 4:
	print(f"Usage: python {sys.argv[0]} <Spotify Username> <Spotify OAuth Token> <Apple Playlist URL>")

	print("   - Spotify Username: This is your normal username (Get it here: https://www.spotify.com/us/account/overview/)")
	print("   - Spotify OAuth Token: Get this token from https://developer.spotify.com/console/post-playlist-tracks/ (Make sure to add 'playlist-modify-public' and 'playlist-modify-private' scopes)")
	print("   - Apple Playlist URL: Should start with 'https://music.apple.com/us/playlist/ ...'")
	print(f"\n EXAMPLE: python {sys.argv[0]} username token https://music.apple.com/us/playlist/.....")
	sys.exit(0)

# Grab arguments
spotifyUserId = sys.argv[1]
spotifyToken = sys.argv[2]
appleMusicPlaylistUrl = sys.argv[3]


hr()
print(f"Will extract song names from {appleMusicPlaylistUrl}:")
input("Press Enter to continue...")
trackArtistTupleList = extractSongsFromApplePlaylist(appleMusicPlaylistUrl)
print("Done. Extracted " + str(len(trackArtistTupleList)) + " songs from Apple Music.")
hr()


print("Will try to retrieve Spotify URIs for each of the songs.")
input("Press Enter to continue...")
spotifySongUris = []
for trackArtistTuple in trackArtistTupleList:
	uri = retrieveSongURI(trackArtistTuple[0], trackArtistTuple[1])
	if uri != "":
		spotifySongUris.append(uri)
print(f"Done. Found {str(len(spotifySongUris))} songs.")
hr()


print("Will try to create a new Spotify playlist.")
input("Press Enter to continue...")
playlistId = createSpotifyPlaylist(newSpotifyPlaylistName)
if playlistId == "":
	sys.exit(0)
print(f"Done. Playlist ID is {playlistId}.")
hr()


print("Will try to add songs to Playlist.")
input("Press Enter to continue...")
addSongsToSpotifyPlaylist(playlistId, spotifySongUris)
print(f"Done.")