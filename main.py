#!/usr/bin/python3
import pathlib
import pygubu
from tkinter import filedialog as fd
from PIL import ImageTk, Image
import os
from tkinter import messagebox
from face_ai import resource_path

PROJECT_PATH = pathlib.Path(__file__).parent
PROJECT_UI = PROJECT_PATH / "revamp_ui_main.ui"


class RevampUiMainApp:
    def __init__(self, master=None):
        self.builder = builder = pygubu.Builder()
        builder.add_resource_path(PROJECT_PATH)
        builder.add_from_file(PROJECT_UI)
        # Main widget
        self.mainwindow = builder.get_object("toplevel1", master)
        self.isfoldercb = builder.get_object("isfoldercheckbutton")
        self.click_select_img = builder.get_object("button1")
        self.target_select_img = builder.get_object("button2")

        builder.connect_callbacks(self)

    def run(self):
        self.mainwindow.title('FaceAI')
        self.mainwindow.tk.call("source", resource_path("azure.tcl"))
        self.mainwindow.tk.call("set_theme", "light")

        self.isfoldercb.state(['!alternate'])
        self.isfoldercb.state(['!selected']) # Default mark checked

        # Init var to None for later
        self.target_file = None
        self.source_folder = None
        self.source_file = None
        self.is_source_folder = None

        self.mainwindow.mainloop()

    def btn_click_switchtheme(self):
        if self.mainwindow.tk.call("ttk::style", "theme", "use") == "azure-dark":
            # Set light theme
            self.mainwindow.tk.call("set_theme", "light")
        else:
            # Set dark theme
            self.mainwindow.tk.call("set_theme", "dark")


    def btn_click_subject(self):
        self.target_file = fd.askopenfilename()
        if(not self.target_file): return

        # self.click_img = ImageTk.PhotoImage(Image.open(self.target_file))
        self.click_select_img.config(text="\n\n\n\nSelected: "+os.path.basename(self.target_file)+"\n\n\n\n")
        

    def btn_click_target(self):
        if(self.isfoldercb.instate(['selected'])):
            self.source_folder = fd.askdirectory()
            if(not self.source_folder): return
            self.source_file = None
            self.target_select_img.config(text="\n\n\n\nSelected: "+os.path.basename(self.source_folder)+"\n\n\n\n")
            self.is_source_folder = True
        else:
            self.source_file = fd.askopenfilename()
            if(not self.source_file): return
            self.source_folder = None
            self.target_select_img.config(text="\n\n\n\nSelected: "+os.path.basename(self.source_file)+"\n\n\n\n")
            self.is_source_folder = False

    def btn_click_compare(self):
        self.is_source_folder = self.isfoldercb.instate(['selected'])
        if(not self.target_file or (self.is_source_folder and not self.source_folder) or (not self.is_source_folder and not self.source_file)):
            messagebox.showwarning("Input Missing", "Please choose both source and target images!")

        from result_widget import RevampUiResultApp
        widget = RevampUiResultApp(self.mainwindow)

        widget.startProcessing(self.source_file if self.source_file else self.source_folder,self.target_file)





if __name__ == "__main__":
    app = RevampUiMainApp()
    app.run()
