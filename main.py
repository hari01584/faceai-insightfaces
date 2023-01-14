#!/usr/bin/python3
import pathlib
import pygubu
from tkinter import PhotoImage, filedialog as fd
from PIL import ImageTk, Image, ImageOps
import os
from tkinter import messagebox
from face_ai import resource_path
from ratelimit import limits, RateLimitException, sleep_and_retry

PROJECT_PATH = pathlib.Path(__file__).parent
PROJECT_UI = PROJECT_PATH / "revamp_ui_main.ui"

def resizeOps(path, size):
    desired_size = size
    im_pth = path

    im = Image.open(im_pth)
    old_size = im.size  # old_size[0] is in (width, height) format

    ratio = float(desired_size)/max(old_size)
    new_size = tuple([int(x*ratio) for x in old_size])
    # use thumbnail() or resize() method to resize the input image

    # thumbnail is a in-place operation

    # im.thumbnail(new_size, Image.ANTIALIAS)

    im = im.resize(new_size, Image.ANTIALIAS)
    # create a new image and paste the resized on it

    new_im = Image.new("RGB", (desired_size, desired_size))
    new_im.paste(im, ((desired_size-new_size[0])//2,
                        (desired_size-new_size[1])//2))

    return new_im


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

    # @on_exception(expo, RateLimitException, max_tries=8)
    @limits(calls=1, period=0.5, raise_on_limit=False)
    def btn_subj_conf(self, event=None):
        if(not event): return
        if(not self.target_file): return
        w = event.width
        h = event.height
        print("Call")
        # Set picture
        resized_image = resizeOps(self.target_file, min(w, h))

        self.subject_photo=ImageTk.PhotoImage(resized_image)
        self.click_select_img.config(image=self.subject_photo)


    @limits(calls=1, period=0.5, raise_on_limit=False)
    def btn_target_conf(self, event=None):
        if(not event): return
        if(not self.source_file): return
        if(self.isfoldercb.instate(['selected'])): return

        w = event.width
        h = event.height
        print("Call")
        # Set picture
        resized_image = resizeOps(self.source_file, min(w, h))

        self.target_photo=ImageTk.PhotoImage(resized_image)
        self.target_select_img.config(image=self.target_photo)



    def btn_click_subject(self):
        self.target_file = fd.askopenfilename()
        if(not self.target_file): return

        # Set picture
        w = self.click_select_img.winfo_width()
        h = self.click_select_img.winfo_height()
        # resized_image= img.resize((w,h), Image.ANTIALIAS)
        resized_image = resizeOps(self.target_file, min(w, h))

        self.subject_photo=ImageTk.PhotoImage(resized_image)

        # self.click_img = ImageTk.PhotoImage(Image.open(self.target_file))
        self.click_select_img.config(text="\n\n\n\nSelected: "+os.path.basename(self.target_file)+"\n\n\n\n", image=self.subject_photo)
        

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

            # Image
            w = self.target_select_img.winfo_width()
            h = self.target_select_img.winfo_height()
            # resized_image= img.resize((w,h), Image.ANTIALIAS)
            resized_image = resizeOps(self.source_file, min(w, h))

            self.target_photo=ImageTk.PhotoImage(resized_image)

            self.target_select_img.config(text="\n\n\n\nSelected: "+os.path.basename(self.source_file)+"\n\n\n\n", image=self.target_photo)
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
