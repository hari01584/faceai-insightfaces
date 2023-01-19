#!/usr/bin/python3
import pathlib
import pygubu
from tkinter import PhotoImage, filedialog as fd
from PIL import ImageTk, Image, ImageOps
import os
from tkinter import messagebox
from face_ai import resource_path
from ratelimit import limits, RateLimitException, sleep_and_retry
from face_ai import SFaceAI
from sklearn.metrics.pairwise import pairwise_distances

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

        self.label_subj_photo = builder.get_object("label_subj_photo")
        self.label_targ_photo = builder.get_object("label_targ_photo")

        self.label_results = builder.get_object("label_results")

        self.sface_api = SFaceAI()

        builder.connect_callbacks(self)

    def run(self):
        self.mainwindow.title('FaceAI')
        self.mainwindow.tk.call("source", resource_path("azure.tcl"))
        self.mainwindow.tk.call("set_theme", "light")

        self.isfoldercb.state(['!alternate'])
        self.isfoldercb.state(['!selected']) # Default mark checked

        # Init var to None for later
        self.target_file_cache = None
        self.subject_file_cache = None
        
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
    @limits(calls=1, period=2, raise_on_limit=False)
    def btn_subj_conf(self, event=None):
        if(not event): return
        if(not self.subject_file_cache): return
        w = event.width
        h = event.height
        print("Call")
        # Set picture
        resized_image = resizeOps(self.subject_file_cache, min(w, h))

        self.subject_photo=ImageTk.PhotoImage(resized_image)
        self.click_select_img.config(image=self.subject_photo)


    @limits(calls=1, period=2, raise_on_limit=False)
    def btn_target_conf(self, event=None):
        if(not event): return
        if(not self.target_file_cache): return
        if(self.isfoldercb.instate(['selected'])): return

        w = event.width
        h = event.height
        print("Call")
        # Set picture
        resized_image = resizeOps(self.target_file_cache, min(w, h))

        self.target_photo=ImageTk.PhotoImage(resized_image)
        self.target_select_img.config(image=self.target_photo)


    def callcheckchange(self):
        self.target_select_img.config(text='Click to select', image='')


    def calc_param_subject(self):
        data = self.sface_api.write_preview(self.target_file, "subject_cache.jpg")
        self.subject_file_cache = "subject_cache.jpg"
        # newimg = self.sface_api.preview(self.)
        if(not data): return

        face = data[0]
        det_score = face.det_score
        gender = face.gender
        age = face.age
        #  'det_score': 0.86529696, 'gender': 1, 'age': 25,
        # txt = det_score*100 + "\n" + "M" if gender == 1 else "F" + "\n" + age
        txt = "%0.2f%% (%s)\nAge: %d" % (det_score*100, "M" if gender == 1 else "F", age)
        print(txt)
        self.label_subj_photo.config(text=txt)


    def calc_param_target(self):
        data = self.sface_api.write_preview(self.source_file, "target_cache.jpg")
        self.target_file_cache = "target_cache.jpg"
        # newimg = self.sface_api.preview(self.)
        if(not data): return

        face = data[0]
        det_score = face.det_score
        gender = face.gender
        age = face.age
        #  'det_score': 0.86529696, 'gender': 1, 'age': 25,
        # txt = det_score*100 + "\n" + "M" if gender == 1 else "F" + "\n" + age
        txt = "%0.2f%% (%s)\nAge: %d" % (det_score*100, "M" if gender == 1 else "F", age)
        print(txt)
        self.label_targ_photo.config(text=txt)

    def btn_click_subject(self):
        self.target_file = fd.askopenfilename()
        if(not self.target_file): return

        self.subject_file_cache = None
        # Calculate and find params
        self.calc_param_subject()

        # Set picture
        w = self.click_select_img.winfo_width()
        h = self.click_select_img.winfo_height()
        # resized_image= img.resize((w,h), Image.ANTIALIAS)
        resized_image = resizeOps(self.subject_file_cache, min(w, h))

        self.subject_photo=ImageTk.PhotoImage(resized_image)

        # self.click_img = ImageTk.PhotoImage(Image.open(self.target_file))
        self.click_select_img.config(text="\n\n\n\nSelected: "+os.path.basename(self.target_file)+"\n\n\n\n", image=self.subject_photo)
        

    def btn_click_target(self):
        self.target_file_cache = None

        if(self.isfoldercb.instate(['selected'])):
            self.source_folder = fd.askdirectory()
            if(not self.source_folder): return
            self.source_file = None
            self.target_select_img.config(text="\n\n\n\nSelected: "+os.path.basename(self.source_folder)+"\n\n\n\n", image=None)
            self.is_source_folder = True
        else:
            self.source_file = fd.askopenfilename()
            if(not self.source_file): return
            self.source_folder = None

            # Calculate
            self.calc_param_target()

            # Image
            w = self.target_select_img.winfo_width()
            h = self.target_select_img.winfo_height()
            # resized_image= img.resize((w,h), Image.ANTIALIAS)
            resized_image = resizeOps(self.target_file_cache, min(w, h))

            self.target_photo=ImageTk.PhotoImage(resized_image)

            self.target_select_img.config(text="\n\n\n\nSelected: "+os.path.basename(self.source_file)+"\n\n\n\n", image=self.target_photo)
            self.is_source_folder = False

    def btn_click_compare(self):
        self.is_source_folder = self.isfoldercb.instate(['selected'])
        if(not self.target_file or (self.is_source_folder and not self.source_folder) or (not self.is_source_folder and not self.source_file)):
            messagebox.showwarning("Input Missing", "Please choose both source and target images!")
            return
        
        if(self.isfoldercb.instate(['selected'])):
            from result_widget import RevampUiResultApp
            widget = RevampUiResultApp(self.mainwindow)

            widget.startProcessing(self.source_file if self.source_file else self.source_folder,self.target_file)
        else:
            # Open accordingly
            # self.label_results
            data = self.sface_api.func(self.source_file, self.target_file)

            tex = self.sface_api.summary(data)
            self.label_results.config(text=tex)


if __name__ == "__main__":
    app = RevampUiMainApp()
    app.run()
