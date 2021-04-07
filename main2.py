import tkinter as tk
import configparser
import json
import spotipy
import os
from spotipy.oauth2 import SpotifyOAuth
from ast import literal_eval
from phue import Bridge
from PyP100 import PyP100


# open and read the config file
config = configparser.ConfigParser()
config.read('config.ini')

# set Tapo variables
tapoUser = config['tapo']['user']
tapoPass = config['tapo']['pass']
tapoDevices = literal_eval(config['tapo']['devices'])

# set Spotify variables
spotifyClientId = config['spotify']['clientId']
spotifyClientSecret = config['spotify']['clientSecret']
spotifyRedirectUri = config['spotify']['redirectUri']
spotifyScope = config['spotify']['scope']
spotifyUsername = config['spotify']['username']

# set Hue variables
hueBridgeIp = config['hue']['bridgeIp']

# set other misc variables
runFullscreen = config.getboolean('general', 'fullscreen')
rooms = literal_eval(config['general']['rooms'])
LARGE_FONT = ("Verdana", 25)
roomToBeControlled = 0

# create Spotify client
spotifyAuthManager = SpotifyOAuth(client_id=spotifyClientId, client_secret=spotifyClientSecret,
                                  redirect_uri=spotifyRedirectUri, scope=spotifyScope,
                                  open_browser=False, username=spotifyUsername)
spotify = spotipy.Spotify(auth_manager=spotifyAuthManager)

# create and connect to Hue bridge object
b = Bridge(hueBridgeIp)
b.connect()
lightGroups = b.get_group()

# make sure we have the full list of rooms ready to go
print('Rooms:')
for room in rooms:
    print(room['id'], room['name'], room['hueGroup'], room['spotifyDevice'])

# gather up Tapo devices and connect to each one
tapoDeviceObjects = []

for device in tapoDevices:
    devObject = PyP100.P100(device['ip'], tapoUser, tapoPass)
    setattr(devObject, 'room', device['room'])
    setattr(devObject, 'name', device['name'])
    tapoDeviceObjects.append(devObject)

print('Tapo devices:')

for device in tapoDeviceObjects:
    print(device,
          getattr(device, 'name'),
          getattr(device, 'room'),
          getattr(device, 'ipAddress'))
    device.handshake()
    device.login()

class HomeController(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        container = tk.Frame(self)

        if runFullscreen:
            self.attributes('-fullscreen', True)
            self.config(cursor="none")

        container.pack(side="top", fill="both", expand=True)

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        self.geometry('320x480')

        self.frames = {}

        for F in (
                StartPage, RoomsPage, UtilitiesPage, RoomControlPage, TapoControlPage, MusicControlPage, MusicTransferPage,
                PlaylistPage, SceneControlPage):
            frame = F(container, self)
            self.frames[F] = frame

            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(StartPage)
        print(self.frames)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()


class StartPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)

        label = tk.Label(self, text="Home Controller", font=LARGE_FONT)
        label.grid(column=0, row=0, sticky='EW')

        button = tk.Button(self, text="Rooms", font=LARGE_FONT,
                           command=lambda: controller.show_frame(RoomsPage))
        button.grid(column=0, row=1, sticky="NSEW")

        button2 = tk.Button(self, text="Utilities", font=LARGE_FONT,
                            command=lambda: controller.show_frame(UtilitiesPage))
        button2.grid(column=0, row=2, sticky="NSEW")


class RoomsPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        label = tk.Label(self, text="Rooms", font=LARGE_FONT)
        label.grid(column=0, row=0, sticky='EW', columnspan=2)

        i = 0
        for room in rooms:
            button = tk.Button(self, text=room['name'], font=LARGE_FONT, wraplength='140',
                               command=lambda roomId=room['id']: openRoomControlPage(roomId, controller))
            setattr(button, 'id', room['id'])
            button.grid(column=i % 2, row=int(i / 2) + 1, sticky="NSEW")
            self.grid_columnconfigure(i % 2, weight=1)
            self.grid_rowconfigure(int(i / 2) + 1, weight=1)

            i += 1

        button2 = tk.Button(self, text="Home", font=LARGE_FONT,
                            command=lambda: controller.show_frame(StartPage))
        button2.grid(column=0, row=i + 1, sticky="NSEW", columnspan=2)
        self.grid_rowconfigure(i + 1, weight=1)


class RoomControlPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(3, weight=1)
        self.roomToBeControlledName = tk.StringVar()
        self.lightButtonText = tk.StringVar()
        print(self)

        label = tk.Label(self, textvariable=self.roomToBeControlledName, font=LARGE_FONT)
        label.grid(column=0, row=0, sticky='EW', columnspan=2)

        button = tk.Button(self, textvariable=self.lightButtonText, wraplength='140', font=LARGE_FONT,
                           command=lambda: lightStateChange())
        button.grid(column=0, row=1, sticky="NSEW")

        button2 = tk.Button(self, text="Scenes", font=LARGE_FONT, wraplength='140',
                            command=lambda: openSceneControlPage(controller))
        button2.grid(column=1, row=1, sticky="NSEW")

        button3 = tk.Button(self, text="Smart Plugs", font=LARGE_FONT, wraplength='140',
                            command=lambda: openTapoControlPage(controller))
        button3.grid(column=0, row=2, sticky="NSEW")

        button4 = tk.Button(self, text="Music", font=LARGE_FONT, wraplength='140',
                            command=lambda: openMusicControlPage(controller))
        button4.grid(column=1, row=2, sticky="NSEW")

        button5 = tk.Button(self, text="Back", font=LARGE_FONT, wraplength='140',
                            command=lambda: controller.show_frame(RoomsPage))
        button5.grid(column=0, row=3, sticky="NSEW", columnspan=2)

    def updateName(self, roomID):
        self.roomToBeControlledName.set(rooms[roomID]['name'])

    def getLightState(self, roomID):
        for room in rooms:
            if room['id'] == roomID:
                if b.get_group(room['hueGroup'], 'on'):
                    print('lights on')
                    self.lightButtonText.set("Lights Off")
                else:
                    print('lights off')
                    self.lightButtonText.set("Lights On")


class TapoControlPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.roomToBeControlledName = tk.StringVar()
        self.lightButtonText = tk.StringVar()
        print(self)

        label = tk.Label(self, textvariable=self.roomToBeControlledName, font=LARGE_FONT)
        label.grid(column=0, row=0, sticky='EW', columnspan=2)

    def drawButtons(self, tapoList, controller):

        for widget in self.grid_slaves():
            if isinstance(widget, tk.Button):
                widget.grid_forget()

        if tapoList:
            i = 0
            for tapo in tapoList:
                button = tk.Button(self, text=getattr(tapo, 'name'), font=LARGE_FONT, wraplength='140',
                                   command=lambda tapoDevice=tapo: changeTapoState(tapoDevice))
                setattr(button, 'id', room['id'])
                button.grid(column=i % 2, row=int(i / 2) + 1, sticky="NSEW")
                self.grid_columnconfigure(i % 2, weight=1)
                self.grid_rowconfigure(int(i / 2) + 1, weight=1)

                i += 1

            button5 = tk.Button(self, text="Back", font=LARGE_FONT, wraplength='140',
                                command=lambda: controller.show_frame(RoomControlPage))
            self.grid_rowconfigure(i + 1, weight=1)
            button5.grid(column=0, row=i + 1, sticky="NSEW", columnspan=2)

        else:
            button5 = tk.Button(self, text="Back", font=LARGE_FONT, wraplength='140',
                                command=lambda: controller.show_frame(RoomControlPage))
            button5.grid(column=0, row=1, sticky="NSEW", columnspan=2)
            self.grid_rowconfigure(0, weight=1)
            self.grid_rowconfigure(1, weight=5)
            self.grid_columnconfigure(0, weight=1)
            self.grid_columnconfigure(1, weight=1)

    def updateName(self, roomID):
        self.roomToBeControlledName.set(rooms[roomID]['name'])

    def getLightState(self, roomID):
        for room in rooms:
            if room['id'] == roomID:
                if b.get_group(room['hueGroup'], 'on'):
                    print('lights on')
                    self.lightButtonText.set("Lights Off")
                else:
                    print('lights off')
                    self.lightButtonText.set("Lights On")


class MusicControlPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(3, weight=1)
        self.trackName = tk.StringVar()
        self.playButtonText = tk.StringVar()
        print(self)

        label = tk.Label(self, textvariable=self.trackName, font=LARGE_FONT)
        label.grid(column=0, row=0, sticky='EW', columnspan=2)

        button = tk.Button(self, textvariable=self.playButtonText, wraplength='140', font=LARGE_FONT,
                           command=lambda: musicStateChange())
        button.grid(column=0, row=1, sticky="NSEW")

        button2 = tk.Button(self, text="Next Song", font=LARGE_FONT, wraplength='140',
                            command=lambda: nextSong())
        button2.grid(column=1, row=1, sticky="NSEW")

        button3 = tk.Button(self, text="Transfer", font=LARGE_FONT, wraplength='140',
                            command=lambda: openMusicTransferPage(controller))
        button3.grid(column=0, row=2, sticky="NSEW")

        button4 = tk.Button(self, text="Playlists", font=LARGE_FONT, wraplength='140',
                            command=lambda: openPlaylistPage(controller))
        button4.grid(column=1, row=2, sticky="NSEW")

        button5 = tk.Button(self, text="Back", font=LARGE_FONT, wraplength='140',
                            command=lambda: controller.show_frame(RoomControlPage))
        button5.grid(column=0, row=3, sticky="NSEW", columnspan=2)

    def updateName(self, roomID):
        print('updating name')
        for room in rooms:
            if room['id'] == roomID:
                spotDev = room['spotifyDevice']
                print('device is', spotDev)
                print(spotify.current_playback())
                if spotify.current_playback():
                    if spotify.current_playback()['device']['id'] == spotDev:
                        self.trackName.set(spotify.current_playback()['item']['name'])
                    else:
                        self.trackName.set("Nothing playing")
                else:
                    self.trackName.set("Nothing playing")

    def getMusicState(self, spotDev):
        if spotify.current_playback():
            if spotify.current_playback()['device']['id'] == spotDev:
                if spotify.current_playback()['is_playing']:
                    print(spotify.current_playback()['item']['name'])
                    self.playButtonText.set("Pause")
                else:
                    self.playButtonText.set("Play")
        else:
            self.playButtonText.set("Play")


class MusicTransferPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.roomToBeControlledName = tk.StringVar()
        self.lightButtonText = tk.StringVar()
        print(self)

        label = tk.Label(self, text='Transfer to:', font=LARGE_FONT)
        label.grid(column=0, row=0, sticky='EW', columnspan=2)

    def drawButtons(self, controller):

        for widget in self.grid_slaves():
            if isinstance(widget, tk.Button):
                widget.grid_forget()

        if rooms:
            i = 0
            for room in rooms:
                if room['spotifyDevice']:
                    button = tk.Button(self, text=room['name'], font=LARGE_FONT, wraplength='140',
                                       command=lambda transferTo=room['spotifyDevice']: transferMusic(transferTo,
                                                                                                      controller))
                    button.grid(column=i % 2, row=int(i / 2) + 1, sticky="NSEW")
                    self.grid_columnconfigure(i % 2, weight=1)
                    self.grid_rowconfigure(int(i / 2) + 1, weight=1)

                    i += 1

            button5 = tk.Button(self, text="Back", font=LARGE_FONT, wraplength='140',
                                command=lambda: controller.show_frame(MusicControlPage))
            self.grid_rowconfigure(i + 1, weight=1)
            button5.grid(column=0, row=i + 1, sticky="NSEW", columnspan=2)

        else:
            button5 = tk.Button(self, text="Back", font=LARGE_FONT, wraplength='140',
                                command=lambda: controller.show_frame(MusicControlPage))
            button5.grid(column=0, row=3, sticky="SEW", columnspan=2)


class PlaylistPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.roomToBeControlledName = tk.StringVar()
        self.lightButtonText = tk.StringVar()
        print(self)

        self.grid_columnconfigure(0, weight=2)
        self.grid_columnconfigure(1, weight=2)
        self.grid_columnconfigure(2, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=4)
        self.grid_rowconfigure(2, weight=4)
        self.grid_rowconfigure(3, weight=2)

    def drawButtons(self, controller):

        for widget in self.grid_slaves():
            widget.grid_forget()
        label = tk.Label(self, text='Playlists', font=LARGE_FONT)
        label.grid(column=0, row=0, sticky='EW', columnspan=3)
        listBox = tk.Listbox(self, font=LARGE_FONT)

        i = 1

        for playlist in spotify.current_user_playlists(limit=50)['items']:
            print(playlist['name'])
            listBox.insert(i, playlist['name'])
            i += 1
        listBox.grid(column=0, row=1, columnspan=2, rowspan=2, sticky='NSEW')

        button1 = tk.Button(self, text="Back", font=LARGE_FONT, wraplength='140',
                            command=lambda: controller.show_frame(MusicControlPage))
        button1.grid(column=0, row=3, sticky="NSEW")

        button2 = tk.Button(self, text="Play", font=LARGE_FONT, wraplength='140',
                            command=lambda lb=listBox, c=controller: self.playSong(lb, c))
        button2.grid(column=1, row=3, sticky="NSEW")

        button3 = tk.Button(self, text="▲", font=LARGE_FONT, wraplength='140',
                            command=lambda lb=listBox: self.scrollBox(lb, True))
        button3.grid(column=2, row=1, sticky="NSEW")

        button4 = tk.Button(self, text="▼", font=LARGE_FONT, wraplength='140',
                            command=lambda lb=listBox: self.scrollBox(lb, False))
        button4.grid(column=2, row=2, sticky="NSEW")

    def playSong(self, listB, controller):
        playName = (listB.get(listB.curselection()[0]))

        for playlist in spotify.current_user_playlists(limit=50)['items']:
            if playlist['name'] == playName:
                for room in rooms:
                    if room['id'] == roomToBeControlled:
                        spotDev = room['spotifyDevice']
                        spotify.start_playback(device_id=spotDev, context_uri=playlist['uri'])
                        openMusicControlPage(controller)

    def scrollBox(self, listB, directionUp):
        if directionUp:
            listB.yview_scroll(-5, 'units')
        else:
            listB.yview_scroll(5, 'units')


class SceneControlPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.roomToBeControlledName = tk.StringVar()
        self.lightButtonText = tk.StringVar()
        print(self)

        label = tk.Label(self, textvariable=self.roomToBeControlledName, font=LARGE_FONT)
        label.grid(column=0, row=0, sticky='EW', columnspan=2)

    def drawButtons(self, sceneList, controller, firstScene):

        for widget in self.grid_slaves():
            if isinstance(widget, tk.Button):
                widget.grid_forget()
        if sceneList:
            if len(sceneList) > 6:
                sceneList2 = sceneList[firstScene:firstScene+5]
            i = 0
            for room in rooms:
                if room['id'] == roomToBeControlled:
                    hueRoom = room['hueGroup']
            for scene in sceneList2:
                button = tk.Button(self, text=scene['name'], font=LARGE_FONT, wraplength='140',
                                   command=lambda rId=hueRoom, sId=scene['id']: b.activate_scene(group_id=rId,
                                                                                                 scene_id=sId))
                setattr(button, 'id', room['id'])
                button.grid(column=i % 2, row=int(i / 2) + 1, sticky="NSEW")
                self.grid_columnconfigure(i % 2, weight=1)
                self.grid_rowconfigure(int(i / 2) + 1, weight=1)

                i += 1

            button5 = tk.Button(self, text="Back", font=LARGE_FONT, wraplength='140',
                                command=lambda: controller.show_frame(RoomControlPage))
            button6 = tk.Button(self, text="Next", font=LARGE_FONT, wraplength='140',
                                command=lambda: self.drawButtons(sceneList, controller, firstScene+6))
            self.grid_rowconfigure(i + 1, weight=1)
            button5.grid(column=0, row=i + 1, sticky="NSEW", columnspan=2)
            button6.grid(column=1, row=i, sticky="NSEW")

        else:
            button5 = tk.Button(self, text="Back", font=LARGE_FONT, wraplength='140',
                                command=lambda: controller.show_frame(RoomControlPage))
            button5.grid(column=0, row=1, sticky="NSEW", columnspan=2)
            self.grid_rowconfigure(0, weight=1)
            self.grid_rowconfigure(1, weight=5)
            self.grid_columnconfigure(0, weight=1)
            self.grid_columnconfigure(1, weight=1)

    def updateName(self, roomID):
        self.roomToBeControlledName.set(rooms[roomID]['name'])

    def getLightState(self, roomID):
        for room in rooms:
            if room['id'] == roomID:
                if b.get_group(room['hueGroup'], 'on'):
                    print('lights on')
                    self.lightButtonText.set("Lights Off")
                else:
                    print('lights off')
                    self.lightButtonText.set("Lights On")


class UtilitiesPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)

        label = tk.Label(self, text="Utilities", font=LARGE_FONT)
        label.grid(column=0, row=0, columnspan=2, sticky='EW')

        button = tk.Button(self, text="Set up \nSpotify", font=LARGE_FONT,
                           command=lambda: print(spotify.current_playback()))
        button.grid(column=0, row=1, sticky="NSEW")

        button4 = tk.Button(self, text="Update", font=LARGE_FONT,
                           command=lambda: os.system("./update.sh"))
        button4.grid(column=1, row=1, sticky="NSEW")

        button2 = tk.Button(self, text="Home", font=LARGE_FONT,
                            command=lambda: controller.show_frame(StartPage))
        button2.grid(column=0, row=2, sticky="NSEW")

        button3 = tk.Button(self, text="Quit", font=LARGE_FONT,
                            command=lambda: app.destroy())
        button3.grid(column=1, row=2, sticky="NSEW")


def openRoomControlPage(room, controller):
    global roomToBeControlled
    roomToBeControlled = room
    print('room controls for', room)
    app.frames[RoomControlPage].updateName(roomToBeControlled)
    app.frames[RoomControlPage].getLightState(roomToBeControlled)
    controller.show_frame(RoomControlPage)


def openTapoControlPage(controller):
    print('tapo controls for', roomToBeControlled)
    app.frames[TapoControlPage].updateName(roomToBeControlled)
    print("tapo devices in this room:")
    roomTapos = []
    for device in tapoDeviceObjects:
        if getattr(device, 'room') == roomToBeControlled:
            print(getattr(device, 'name'))
            roomTapos.append(device)
    controller.show_frame(TapoControlPage)
    app.frames[TapoControlPage].drawButtons(roomTapos, controller)


def openSceneControlPage(controller):
    print('scene controls for', roomToBeControlled)
    app.frames[SceneControlPage].updateName(roomToBeControlled)
    print("scenes in this room:")
    roomSceneList = []
    for room in rooms:
        if room['id'] == roomToBeControlled:
            hueRoom = room['hueGroup']
            print('hue room', hueRoom)
            scenes = b.get_scene()
            # print(scenes)
            for scene in scenes.keys():
                # print(scenes[scene])
                if 'group' in scenes[scene].keys():
                    # print(scenes[scene]['group'])
                    if scenes[scene]['group'] == str(hueRoom):
                        # print(scenes[scene]['name'])
                        roomSceneList.append({'name': scenes[scene]['name'], 'id': scene})
    print(roomSceneList)
    controller.show_frame(SceneControlPage)
    app.frames[SceneControlPage].drawButtons(roomSceneList, controller, 0)


def openMusicControlPage(controller):
    print('music controls for', roomToBeControlled)
    app.frames[MusicControlPage].updateName(roomToBeControlled)
    print("spotify device in this room:")
    for room in rooms:
        if room['id'] == roomToBeControlled:
            print(room['spotifyDevice'])
            thisSpotDev = room['spotifyDevice']
            app.frames[MusicControlPage].getMusicState(thisSpotDev)
            controller.show_frame(MusicControlPage)


def openMusicTransferPage(controller):
    print('music transfer for', roomToBeControlled)
    app.frames[MusicTransferPage].drawButtons(controller)
    controller.show_frame(MusicTransferPage)


def openPlaylistPage(controller):
    print('playlists')
    app.frames[PlaylistPage].drawButtons(controller)
    controller.show_frame(PlaylistPage)


def changeTapoState(tapoObj):
    # print(literal_eval(tapoObj.getDeviceInfo())['result']['device_on'])
    if json.loads(tapoObj.getDeviceInfo())['result']['device_on']:
        tapoObj.turnOff()
    else:
        tapoObj.turnOn()


def lightStateChange():
    for room in rooms:
        if room['id'] == roomToBeControlled:
            if b.get_group(room['hueGroup'], 'on'):
                b.set_group(room['hueGroup'], 'on', False)
            else:
                b.set_group(room['hueGroup'], 'on', True)
    app.frames[RoomControlPage].getLightState(roomToBeControlled)


def musicStateChange():
    for room in rooms:
        if room['id'] == roomToBeControlled:
            if spotify.current_playback():
                if spotify.current_playback()['device']['id'] == room['spotifyDevice']:
                    if spotify.current_playback()['is_playing']:
                        print('pausing')
                        spotify.pause_playback(room['spotifyDevice'])
                    else:
                        print('playing')
                        spotify.start_playback(device_id=room['spotifyDevice'])
            else:
                print('playing')
                spotify.start_playback(device_id=room['spotifyDevice'])

            app.frames[MusicControlPage].getMusicState(room['spotifyDevice'])
            app.frames[MusicControlPage].updateName(roomToBeControlled)


def nextSong():
    for room in rooms:
        if room['id'] == roomToBeControlled:
            if spotify.current_playback()['device']['id'] == room['spotifyDevice']:
                if spotify.current_playback()['is_playing']:
                    print('next song')
                    spotify.next_track(room['spotifyDevice'])
                else:
                    print('nothing playing')
                app.frames[MusicControlPage].getMusicState(room['spotifyDevice'])
                app.frames[MusicControlPage].updateName(roomToBeControlled)


def transferMusic(deviceToTransferTo, controller):
    spotify.transfer_playback(deviceToTransferTo)
    controller.show_frame(RoomsPage)


app = HomeController()
app.mainloop()
