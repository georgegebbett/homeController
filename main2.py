import tkinter as tk

LARGE_FONT = ("Verdana", 12)


class HomeController(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        container = tk.Frame(self)

        container.pack(side="top", fill="both", expand=True)

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        self.geometry('320x480')

        self.frames = {}

        for F in (StartPage, LightsPage, HeatPage):
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

        button = tk.Button(self, text="Lights",
                           command=lambda: controller.show_frame(LightsPage))
        button.grid(column=0, row=1, sticky="NSEW")

        button2 = tk.Button(self, text="Heat",
                            command=lambda: controller.show_frame(HeatPage))
        button2.grid(column=0, row=2, sticky="NSEW")


class LightsPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)

        label = tk.Label(self, text="Lighting Control", font=LARGE_FONT)
        label.grid(column=0, row=0, sticky='EW')

        button = tk.Button(self, text="Living Room",
                           command=lambda: controller.show_frame(StartPage))
        button.grid(column=0, row=1, sticky="NSEW")

        button2 = tk.Button(self, text="Home",
                            command=lambda: controller.show_frame(StartPage))
        button2.grid(column=0, row=2, sticky="NSEW")


class HeatPage(tk.Frame):

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
