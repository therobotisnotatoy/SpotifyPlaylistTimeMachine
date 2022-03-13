from datetime import datetime
import requests
import os
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import spotipy
import json
import ast
from spotipy.oauth2 import SpotifyOAuth
import sqlite3


def user_input():
    """Allows the user to select a date"""
    go_on = True
    while go_on:

        try:
            print("Enter 'exit' to abort")
            goal_date = input("Please enter date in YYYY-MM-DD format: ")

            """Checking user input"""
            if goal_date != "exit":
                g_year = int(goal_date[0:4])
                g_month = int(goal_date[5:7])
                g_day = int(goal_date[8:10])
                goal_date = str(datetime(g_year, g_month, g_day).date()) + "/"
                return goal_date

            go_on = False

        except:
            print("Input error. Try again.")


def get_top_list(target_date):
    """Database interaction. If target data is not in the database function will add one"""

    conn = sqlite3.connect("top_songs.db")
    cursor = conn.cursor()

    try:
        cursor.execute('''CREATE TABLE topsongs (date text PRIMARY KEY, songslist JSON)''')
        print("new database created")

    except:
        print("database exists")

    """Get info from database"""
    db_request = "SELECT songslist FROM topsongs WHERE date=?"
    cursor.execute(db_request, [target_date])
    answer = cursor.fetchall()

    """If database does not contains target date"""
    if len(answer) == 0:
        """Add data to database"""
        answer = get_top_list_from_web(target_date)
        db_request = "INSERT INTO topsongs VALUES (?,?)"
        cursor.execute(db_request, (target_date, json.dumps(answer)))
        conn.commit()

    else:
        answer = dict(ast.literal_eval(answer[0][0]))
        print("data from database")

    return answer


def get_top_list_from_web(target_date):
    """Get top song titles & authors list in given date"""

    """Loading web page"""
    URL = "https://www.billboard.com/charts/hot-100/"
    response = requests.get(URL+target_date)
    page_content = response.text

    """Web page class names"""
    first_title_tag_class = '''c-title a-no-trucate a-font-primary-bold-s u-letter-spacing-0021 u-font-size-23@tablet lrv-u-font-size-16 u-line-height-125 u-line-height-normal@mobile-max a-truncate-ellipsis u-max-width-245 u-max-width-230@tablet-only u-letter-spacing-0028@tablet'''
    first_author_tag_class = '''c-label a-no-trucate a-font-primary-s lrv-u-font-size-14@mobile-max u-line-height-normal@mobile-max u-letter-spacing-0021 lrv-u-display-block a-truncate-ellipsis-2line u-max-width-330 u-max-width-230@tablet-only u-font-size-20@tablet'''
    title_tags_class = "c-title a-no-trucate a-font-primary-bold-s u-letter-spacing-0021 lrv-u-font-size-18@tablet lrv-u-font-size-16 u-line-height-125 u-line-height-normal@mobile-max a-truncate-ellipsis u-max-width-330 u-max-width-230@tablet-only"
    author_tags_class = "c-label a-no-trucate a-font-primary-s lrv-u-font-size-14@mobile-max u-line-height-normal@mobile-max u-letter-spacing-0021 lrv-u-display-block a-truncate-ellipsis-2line u-max-width-330 u-max-width-230@tablet-only"

    """Parsing the web page"""
    soup = BeautifulSoup(page_content, "html.parser")
    first_title_tag = soup.find(name="h3", class_=first_title_tag_class)
    first_author_tag = soup.find(name="span", class_=first_author_tag_class)
    title_tags = soup.find_all(name="h3", class_=title_tags_class)
    author_tags = soup.find_all(name="span", class_=author_tags_class)

    """Extracting song titles & authors"""
    first_title = first_title_tag.getText().strip()
    first_author = first_author_tag.getText().strip()
    titles = [title.getText().strip() for title in title_tags]
    authors = [author.getText().strip() for author in author_tags]

    """Creating top list"""
    position = 1
    top_songs = {position: str(first_title) + "---" + str(first_author)}
    for title, author in zip(titles, authors):
        # print(title, "---", author)
        position += 1
        top_songs[position] = str(title) + "---" + str(author)

    return top_songs


def create_spotify_list(target_date, top_songs_list):

    """Creating spotify instance"""
    auth_manager = SpotifyOAuth(scope="playlist-modify-private",
                                redirect_uri="http://example.com",
                                client_id=spotify_client,
                                client_secret=spotify_secret,
                                show_dialog=True,
                                cache_path="token.txt"
                                )

    sp = spotipy.Spotify(auth_manager=auth_manager)

    """Creating song uris list for future use"""
    song_uris = []
    year = target_date.split("-")[0]

    for _, item in top_songs_list.items():
        song = item.split("---")

        try:
            result = sp.search(q=f"track:{song[0]} year:{year}", type="track")
            print(f'{song[0]} - {song[1]} /-/ {result["tracks"]["items"][0]["album"]["artists"][0]["external_urls"]["spotify"]}')
            uri = result["tracks"]["items"][0]["uri"]
            song_uris.append(uri)

        except IndexError:
            print(f"{song[0]} - {song[1]} /-/ Doesn't exist in Spotify. Skipped.")

    print("=" * 80)

    """Spotyfy playlist creation"""
    user_id = sp.current_user()["id"]
    if len(song_uris) != 0:
        playlist = sp.user_playlist_create(user=user_id,
                                           name=f"{target_date} Billboard 100",
                                           public=False,
                                           )

        sp.playlist_add_items(playlist_id=playlist["id"], items=song_uris)

        return playlist

    else:
        return False


def main():

    date = "2015-07-01"        # default
    # date = user_input()

    top_list = get_top_list(date)

    playlist = create_spotify_list(date, top_list)

    if playlist:
        print(f'Playlist created successfully: {playlist["external_urls"]["spotify"]}')
    else:
        print(f"Unfortunately, playlist can not be created")


if __name__ == "__main__":

    """Environment variables load"""
    load_dotenv()
    spotify_client = os.environ.get("export SPOTIPY_CLIENT_ID=", None)
    spotify_secret = os.environ.get("export SPOTIPY_CLIENT_SECRET=", None)

    """Running main code"""
    main()
