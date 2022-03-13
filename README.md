# SpotifyPlaylistTimeMachine
The program creates a Spotify playlist of the 100 most popular songs by user-entered date. The search is carried out on the website https://www.billboard.com/, using the Beautiful Soup library. Some of the songs on Spotify are not available, so the final playlist may contain less than 100 songs.

All queries are automatically saved in the database for faster work when the query is repeated. Because the history is not changed, only playlists are saved in the database. The Spotyfy playlist is generated over and over again as the platform can add / remove content


Used libraries:
bs4 (BeautifulSoup)
spotipy
SpotifyOAuth
sqlite3


!WARNING!
- You need a Spotify account to run the program. You can create a new one by following the link: http://spotify.com/signup/
- After logging in to the Spotyfy website, go to the developer dashboard and create a new Spotify App: https://developer.spotify.com/dashboard/
- create .env file in program directory
- Copy the Client ID and Client Secret into .env

Your .env file should look like:

export SPOTIPY_CLIENT_ID=your_id_here
export SPOTIPY_CLIENT_SECRET=your_secret_here

