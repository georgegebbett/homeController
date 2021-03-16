import tkinter as tk
import configparser
from ast import literal_eval

config = configparser.ConfigParser()
config.read('config.ini')

tapoUser = config['tapo']['user']
tapoPass = config['tapo']['pass']

rooms = literal_eval(config['general']['rooms'])

hueBridgeIp = config['hue']['bridgeIp']

tapoDevices = literal_eval(config['tapo']['devices'])

print('Rooms:')
for room in rooms:
    print(room['id'], room['name'], room['hueGroup'])

LARGE_FONT = ("Verdana", 25)

from phue import Bridge

b = Bridge(hueBridgeIp)
b.connect()

from PyP100 import PyP100

tapoDeviceObjects = []

for device in tapoDevices:
    devObject = PyP100.P100(device['ip'], tapoUser, tapoPass)
    setattr(devObject, 'room', device['room'])
    setattr(devObject, 'name', device['name'])
    tapoDeviceObjects.append(devObject)

print('Tapo devices:')

for device in tapoDeviceObjects:
    print(getattr(device, 'name'),
          getattr(device, 'room'),
          getattr(device, 'ipAddress'))

fairyLights = PyP100.P100("192.168.1.104", tapoUser, tapoPass)
fairyLights.handshake()
fairyLights.login()
lightGroups = b.get_group()

roomToBeControlled = 0


class HomeController(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        container = tk.Frame(self)
        # self.attributes('-fullscreen', True)
        # self.config(cursor="none")

        container.pack(side="top", fill="both", expand=True)

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        self.geometry('320x480')

        self.frames = {}

        for F in (StartPage, RoomsPage, PresetsPage, RoomControlPage):
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

        button2 = tk.Button(self, text="Presets", font=LARGE_FONT,
                            command=lambda: controller.show_frame(PresetsPage))
        button2.grid(column=0, row=2, sticky="NSEW")


class RoomsPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        label = tk.Label(self, text="Rooms", font=LARGE_FONT)
        label.grid(column=0, row=0, sticky='EW', columnspan=2)

        i = 0
        for room in rooms:
            button = tk.Button(self, text=room['name'], font=LARGE_FONT, wraplength='140',
                               command=lambda roomId=room['id']: openLightControlPage(roomId, controller))
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
        print(self)

        label = tk.Label(self, textvariable=self.roomToBeControlledName, font=LARGE_FONT)
        label.grid(column=0, row=0, sticky='EW', columnspan=2)

        button = tk.Button(self, text="Lights ON", font=LARGE_FONT,
                           command=lambda: lightStateChange(True))
        button.grid(column=0, row=1, sticky="NSEW")

        button2 = tk.Button(self, text="Lights OFF", font=LARGE_FONT,
                            command=lambda: lightStateChange(False))
        button2.grid(column=1, row=1, sticky="NSEW")

        button3 = tk.Button(self, text="Flights On", font=LARGE_FONT,
                            command=lambda: fairyLights.turnOn())
        button3.grid(column=0, row=2, sticky="NSEW")

        button4 = tk.Button(self, text="Flights Off", font=LARGE_FONT,
                            command=lambda: fairyLights.turnOff())
        button4.grid(column=1, row=2, sticky="NSEW")

        button5 = tk.Button(self, text="Back", font=LARGE_FONT,
                            command=lambda: controller.show_frame(RoomsPage))
        button5.grid(column=0, row=3, sticky="NSEW", columnspan=2)

    def updateName(self, roomID):
        self.roomToBeControlledName.set(rooms[roomID]['name'])



class PresetsPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)

        label = tk.Label(self, text="Heating control", font=LARGE_FONT)
        label.grid(column=0, row=0, sticky='EW')

        button = tk.Button(self, text="Heating on", font=LARGE_FONT,
                           command=lambda: controller.show_frame(StartPage))
        button.grid(column=0, row=1, sticky="NSEW")

        button2 = tk.Button(self, text="Home", font=LARGE_FONT,
                            command=lambda: controller.show_frame(StartPage))
        button2.grid(column=0, row=2, sticky="NSEW")


def openLightControlPage(room, controller):
    global roomToBeControlled
    roomToBeControlled = room
    print('light controls for', room)
    app.frames[RoomControlPage].updateName(roomToBeControlled)
    controller.show_frame(RoomControlPage)


def lightStateChange(onBool):
    for room in rooms:
        if room['id'] == roomToBeControlled:
            if onBool:
                b.set_group(room['hueGroup'], 'on', True)
            else:
                b.set_group(room['hueGroup'], 'on', False)


app = HomeController()
app.mainloop()
