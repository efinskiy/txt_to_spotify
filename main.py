import math

import spotipy
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth, SpotifyClientCredentials
import os

SPOTIPY_CLIENT_ID = ''
SPOTIPY_CLIENT_SECRET = ''
SPOTIPY_REDIRECT_URI = 'http://localhost:9090'

os.environ['SPOTIPY_CLIENT_ID'] = SPOTIPY_CLIENT_ID
os.environ['SPOTIPY_CLIENT_SECRET'] = SPOTIPY_CLIENT_SECRET
os.environ['SPOTIPY_REDIRECT_URI'] = SPOTIPY_REDIRECT_URI


def txt_to_spotify(sp: Spotify):
    filename = input('Filename: ')

    parsed_songs = []
    f = open(filename, 'r', encoding='utf-8')
    while True:
        line = f.readline()

        if not line:
            break

        parsed_songs.append(line.replace('\n', ''))
    f.close()
    tracks_id = []
    failed_list = []
    cur_track_id = 0
    len_tracks = len(parsed_songs)
    for song in parsed_songs:
        p_song = sp.search(q=song, type='track', limit=1)
        cur_track_id += 1
        if not p_song['tracks']['items']:
            print(f'{cur_track_id}/{len_tracks} | {song} not found.')
            failed_list.append(song)
            continue
        print(f'{cur_track_id}/{len_tracks} | Searched: {song}, found: {p_song['tracks']['items'][0]['name']}')
        tracks_id.append(p_song['tracks']['items'][0])

    playlists = sp.current_user_playlists()['items']
    print('===============Ваши плейлисты===============')
    for p in playlists:
        print(f'{playlists.index(p)} -> {p['name']}')
    pl_index_correct = False
    while not pl_index_correct:
        print('Введите номер плейлиста: ')
        pl_index = input()
        if pl_index.isdigit():
            if int(pl_index) <= len(playlists):
                pl_index_correct = True

    print('Запуск импорта.')
    while tracks_id:
        uri_count = 0
        tracks = []
        while uri_count < 100 and tracks_id:
            tracks.append(tracks_id.pop())
            uri_count += 1
        uri_string = [t['uri'] for t in tracks]
        # print(uri_string)
        sp.playlist_add_items(playlist_id=playlists[int(pl_index)]['id'],
                              items=uri_string,
                              position=0)
        print(f'Импортировано {uri_count} треков.')

    print(f'Пропущенные треки: {len(failed_list)}')
    for failed in failed_list:
        print(failed)


def like_playlist_tracks(sp: Spotify):
    print('===============Ваши плейлисты===============')
    playlists = sp.current_user_playlists()['items']
    for p in playlists:
        print(f'{playlists.index(p)} -> {p['name']}')
    pl_index_correct = False
    while not pl_index_correct:
        print('Введите номер плейлиста: ')
        pl_index = input()
        if pl_index.isdigit():
            if int(pl_index) <= len(playlists):
                pl_index_correct = True
    playlist = playlists[int(pl_index)]
    total_tracks = playlist['tracks']['total']
    print('Total tracks: ', total_tracks)
    offset = 0
    aprox_iter = math.ceil(total_tracks / 50)
    print('Iters: ', aprox_iter)
    track_ids = []
    for i in range(0, aprox_iter):
        playlist_items = sp.playlist_items(playlist_id=playlist['id'],
                                           offset=offset,
                                           limit=50,
                                           fields='items(track(id))'
                                           )
        pl_i = playlist_items['items']
        tmp_tracks = [track['track']['id'] for track in pl_i]

        track_ids.append(tmp_tracks)
        offset += 50

    tmp_1 = []
    for b in track_ids:
        for t in b:
            tmp_1.append(t)
    print(len(tmp_1))

    total_added = 0
    for bulk in track_ids:
        sp.current_user_saved_tracks_add(bulk)
        print('Добавлено: ', len(bulk), ' треков.')
        total_added+=len(bulk)

    print('Всего добавлено: ', total_added)

if __name__ == '__main__':

    scope = ("playlist-read-private,playlist-read-collaborative,playlist-modify-private,playlist-modify-public,"
             "user-library-modify,user-library-read")
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

    print('0 -> Txt to Spotify')
    print('1 -> "Like" all tracks in playlist')
    flow = input('Выберите функцию: [0, 1]')

    flow_int = int(flow)
    if flow_int in [0, 1]:
        if flow_int == 0:
            txt_to_spotify(sp)
        if flow_int == 1:
            like_playlist_tracks(sp)
