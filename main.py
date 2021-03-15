import tkinter as tk


class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.grid()
        self.create_widgets()

    def create_widgets(self):
        self.hi_widget = tk.Button(self)
        self.hi_widget["text"] = "Create new window"
        self.hi_widget["command"] = self.display_other_window
        self.hi_widget.pack(side="top")

    def display_other_window(self):
        newWindow = SecondWindow(self)
        newWindow.create_multi_buttons()

class SecondWindow(tk.Toplevel):
    def __init__(self, master=None, names=None):
        super().__init__(master)
        self.master = master
        self.attributes("-topmost",1)
        self.geometry('320x480')
        self.grid()
        self.create_menu_buttons(names)

    def create_menu_buttons(self, names):
        # content = tk.Frame(self, width=320, height=480, borderwidth=5, relief="sunken")
        # content.grid(column=0, row=0, sticky='NESW')
        i = 0
        for c in range(2):
            for r in range(3):
                print(c, r, i)
                newLabel = tk.Button(self)
                newLabel["text"] = names[i]
                i += 1
                newLabel["command"] = self.rename_buttons
                newLabel.grid(column=c, row=r, sticky="NSEW")
        self.rowconfigure((0,1,2), weight=1)
        self.columnconfigure((0,1), weight=1)

    def rename_buttons(self):
        for child in self.children:
            self.children[child]["text"] = "On"

menuItems = ["Lights", "Music", "Cameras", "Heat", "Locks", "Alarm"]

window = tk.Tk()

app = SecondWindow(master=window, names=menuItems)


app.mainloop()
