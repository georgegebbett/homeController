import tkinter as tk
import configparser

config = configparser.ConfigParser()
config.read('config.ini')

tapoUser = config['tapoCreds']['user']
tapoPass = config['tapoCreds']['pass']


LARGE_FONT = ("Verdana", 25)

from phue import Bridge

b = Bridge('192.168.1.252')
b.connect()

from PyP100 import PyP100



fairyLights = PyP100.P100("192.168.1.104", tapoUser, tapoPass)
fairyLights.handshake()
fairyLights.login()
lightGroups = b.get_group()

class HomeController(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        container = tk.Frame(self)
        self.attributes('-fullscreen', True)

        container.pack(side="top", fill="both", expand=True)

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        self.geometry('320x480')

        self.frames = {}

        for F in (StartPage, LightsPage, PresetsPage, LightsControlPage):
            frame = F(container, self)

            self.frames[F] = frame

            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(StartPage)

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

        button = tk.Button(self, text="Lights", font=LARGE_FONT,
                           command=lambda: controller.show_frame(LightsPage))
        button.grid(column=0, row=1, sticky="NSEW")

        button2 = tk.Button(self, text="Presets",
                            command=lambda: controller.show_frame(PresetsPage))
        button2.grid(column=0, row=2, sticky="NSEW")


class LightsPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)


        label = tk.Label(self, text="Lighting Control", font=LARGE_FONT)
        label.grid(column=0, row=0, sticky='EW', columnspan=2)

        i = 0
        print(lightGroups)
        for lightGroup in lightGroups:
            print(lightGroup)
            print(lightGroups[lightGroup]['name'])
            if 'Group for' in lightGroups[lightGroup]['name']:
                continue
            else:
                button = tk.Button(self, text=lightGroups[lightGroup]['name'],
                                   command=lambda: controller.show_frame(LightsControlPage))
                button.grid(column=i%2, row=int(i/2)+1, sticky="NSEW")
                self.grid_columnconfigure(i%2, weight=1)
                self.grid_rowconfigure(int(i/2)+1, weight=1)

                i += 1

        button2 = tk.Button(self, text="Home",
                            command=lambda: controller.show_frame(StartPage))
        button2.grid(column=0, row=i+1, sticky="NSEW", columnspan=2)
        self.grid_rowconfigure(i+1, weight=1)


class LightsControlPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(3, weight=1)

        label = tk.Label(self, text="Home Controller", font=LARGE_FONT)
        label.grid(column=0, row=0, sticky='EW', columnspan = 2)

        button = tk.Button(self, text="ON",
                           command=lambda: b.set_group(1,'on', True))
        button.grid(column=0, row=1, sticky="NSEW")

        button2 = tk.Button(self, text="OFF",
                            command=lambda: b.set_group(1,'on', False))
        button2.grid(column=1, row=1, sticky="NSEW")

        button3 = tk.Button(self, text="Flights On",
                            command=lambda: fairyLights.turnOn())
        button3.grid(column=0, row=2, sticky="NSEW")

        button4 = tk.Button(self, text="Flights Off",
                            command=lambda: fairyLights.turnOff())
        button4.grid(column=1, row=2, sticky="NSEW")

        button5 = tk.Button(self, text="Back",
                            command=lambda: controller.show_frame(LightsPage))
        button5.grid(column=0, row=3, sticky="NSEW", columnspan=2)


class PresetsPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)

        label = tk.Label(self, text="Heating control", font=LARGE_FONT)
        label.grid(column=0, row=0, sticky='EW')

        button = tk.Button(self, text="Heating on",
                           command=lambda: controller.show_frame(StartPage))
        button.grid(column=0, row=1, sticky="NSEW")

        button2 = tk.Button(self, text="Home",
                            command=lambda: controller.show_frame(StartPage))
        button2.grid(column=0, row=2, sticky="NSEW")




app = HomeController()
app.mainloop()
