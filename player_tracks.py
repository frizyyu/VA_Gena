import random
import threading
import time

import vlc


class Player:
    def __init__(self):
        self.is_flow = False
        self.Instance = vlc.Instance("--no-xlib")
        self.player = self.Instance.media_player_new()
        self.playlist = []
        self.name_t = ""
        # self.track_url = ""
        self.web_url = ""
        self.current_track = None
        self.for_favorite = ["новые треки", "старое", "лучшее", "первый трек", "последний трек", "слушать", "похожее"]
        self.player.event_manager().event_attach(vlc.EventType.MediaPlayerEndReached, self.end_track_callback)

    def add_to_playlist(self, track, name, web_url):
        self.playlist.append(track)
        self.name_t = " ".join(name)
        # self.track_url = track
        self.web_url = web_url

    def cur_track(self):
        return self.name_t, self.web_url

    def stop(self):
        self.player.stop()

    def play(self):
        if not self.playlist:
            print("Playlist is empty")
            return
        if self.current_track is None:
            self.current_track = 0
        self.media = self.Instance.media_new(self.playlist[self.current_track])
        self.player.set_media(self.media)
        self.player.play()

    def pause(self):
        self.player.pause()

    def resume(self):
        self.player.play()

    def end_track_callback(self, event):
        if self.is_flow:
            import random
            import json
            with open("playlists.json", encoding="UTF8") as myf:
                pl_d = json.load(myf)
                myf.close()
            name = f'{random.choice(pl_d["favorite"])} {random.choice(self.for_favorite)}'
            print(name)
            name_dur = get_track(name)
            self.add_to_playlist(name_dur[0], name, name_dur[2])
        if self.current_track is None:
            print("Playlist is empty")
            return
        self.current_track += 1
        print(self.playlist)
        if self.current_track >= len(self.playlist):
            self.current_track = 0
        print("!")

        def nne():
            self.media = self.Instance.media_new(self.playlist[self.current_track])
            self.player.set_media(self.media)
            self.player.play()

        thread = threading.Thread(target=nne)
        thread.start()
        '''self.media = self.Instance.media_new(self.playlist[self.current_track])
        print("2")
        self.player.set_media(self.media)
        print("3")
        self.player.play()
        self.player.audio_set_volume(100)'''

    def next_track(self):
        print("Q")
        if self.is_flow:
            import random
            import json
            with open("playlists.json", encoding="UTF8") as myf:
                pl_d = json.load(myf)
                myf.close()
            name = f'{random.choice(pl_d["favorite"])} {random.choice(self.for_favorite)} слушать'
            print(name)
            name_dur = get_track(name)
            self.add_to_playlist(name_dur[0], name, name_dur[2])
        print(len(self.playlist), "QQQQQQQQQQQQQQQQQQQQQQQ")
        if len(self.playlist) == 1:
            self.stop()
        if self.current_track is None:
            print("Playlist is empty")
            return
        self.current_track += 1
        if self.current_track >= len(self.playlist):
            self.current_track = 0
        self.media = self.Instance.media_new(self.playlist[self.current_track])
        self.player.set_media(self.media)
        self.player.play()

    def previous_track(self):
        if self.current_track is None:
            print("Playlist is empty")
            return
        self.current_track -= 1
        if self.current_track < 0:
            self.current_track = len(self.playlist) - 1
        self.media = self.Instance.media_new(self.playlist[self.current_track])
        self.player.set_media(self.media)
        self.player.play()

    def volume(self, num):
        self.player.audio_set_volume(num)

    def shuffle(self):
        if not self.playlist:
            print("Playlist is empty")
            return
        self.current_track = random.randint(0, len(self.playlist) - 1)
        self.media = self.Instance.media_new(self.playlist[self.current_track])
        self.player.set_media(self.media)
        self.player.play()


from yt_dlp import YoutubeDL


def get_track(arg):
    try:
        YDL_OPTIONS = {'format': 'worstaudio/best', 'noplaylist': 'False', 'simulate': 'True',
                       'preferredquality': '192', 'preferredcodec': 'mp3', 'key': 'FFmpegExtractAudio'}
        with YoutubeDL(YDL_OPTIONS) as ydl:
            result = ydl.extract_info(f"ytsearch:{arg}", download=False)

        if 'entries' in result:
            # Can be a playlist or a list of videos
            video = result['entries'][0]
        else:
            # Just a video
            video = result

        to_play = video["url"]
        dur = video["duration"]
        web_url = video["webpage_url"]
        return to_play, dur, web_url
    except Exception as e:
        with open("LOGS.txt", "w") as f:
            import traceback
            f.write(f"ASDASD {traceback.format_exc()}")
        import pygame
        pygame.init()
        pygame.mixer.music.load("gena_error.mp3")
        pygame.mixer.music.play()
        #get_track(arg) #протестить
        print(e, "ASDASD")


def download_audio(arg, name, pl_name, name_url):
    import yt_dlp
    import json
    try:
        ydl_opts = {
            'outtmpl': '/music/' + f"{name}_{pl_name}" + '.%(ext)s',
            'format': 'bestaudio[ext=m4a]/best[ext=mp4]/best',
        }
        # print("asyegfuygervuyenirver", arg.__class__.__name__)
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([f"{arg}"])
        with open("playlists.json", encoding="UTF8") as myf:
            pl_d = json.load(myf)
            myf.close()
        name_url = list(name_url)
        name_url[0] = f"{name_url[0]}_{pl_name}"
        if pl_name in pl_d.keys():
            pl_d[pl_name].append(list(name_url))
        else:
            pl_d[pl_name] = []
            pl_d[pl_name].append(list(name_url))
        with open("playlists.json", "w", encoding="UTF8") as f:
            print(pl_d)
            json.dump(pl_d, f)
            f.close()
    except Exception as e:
        import pygame
        pygame.init()
        pygame.mixer.music.load("gena_error.mp3")
        pygame.mixer.music.play()
        #через пайгейм проигрывать звук ошибки
        print(e, "ASDASD")
'''l = ["КТО ОНА sexbimba3131", "Уу-хуу Пошлая Молли", "аризона бошки remix", "mana break zxcursed", "STFU минин", "Тесно Aarne, BUSHIDO ZHO", "#HABIBATI пошлая молли"]
for x in l:
    name1 = x
    n = get_track(name1)
    print(n)
    download_audio(n[-1], name1, "негры", (name1, n[-1]))'''



# пауза+, воспроизведение+, стоп+,
# следующий, предыдущий, громкость, плейлисты, реки по любимым исполнителям и жанрам
# авто скачивание при добавлении в плейлист
#погода
