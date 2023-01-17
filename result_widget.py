#!/usr/bin/python3
import pathlib
import pygubu
from tkinter import CENTER, END, PhotoImage, ttk
from PIL import ImageTk, Image
from pathlib import Path
from face_ai import SFaceAI
import cv2

PROJECT_PATH = pathlib.Path(__file__).parent
PROJECT_UI = PROJECT_PATH / "revamp_ui_result.ui"


class RevampUiResultApp:
    def __init__(self, master=None):
        self.builder = builder = pygubu.Builder()
        builder.add_resource_path(PROJECT_PATH)
        builder.add_from_file(PROJECT_UI)
        # Main widget
        self.mainwindow = builder.get_object("toplevel1", master)
        self.progress_bar = builder.get_object("progress_scan")
        self.treeview = builder.get_object("treeview")
        self.scrollbar_tv = builder.get_object("scrollbar_tv")
        self.technicaldata = builder.get_object("technicaldata")
        
        builder.connect_callbacks(self)

        self.sface_api = SFaceAI()

    def run(self):
        self.mainwindow.title('FaceAI')
        self.mainwindow.tk.call("source", "azure.tcl")
        self.mainwindow.tk.call("set_theme", "light")
        self.mainwindow.mainloop()

    def btn_click_switchtheme(self):
        if self.mainwindow.tk.call("ttk::style", "theme", "use") == "azure-dark":
            # Set light theme
            self.mainwindow.tk.call("set_theme", "light")
        else:
            # Set dark theme
            self.mainwindow.tk.call("set_theme", "dark")

        s = ttk.Style()
        s.configure("Treeview", rowheight=100)


    def startProcessing(self, source, targetFile):
        self.mainwindow.after(100, self._startProcessing, source, targetFile)

    def _startProcessing(self, source, targetFile):
        self.mainwindow.update_idletasks()
        from face_ai import SFaceAI
        fapi = SFaceAI()

        from tkinter import messagebox
        from os import listdir, path, walk
        from os.path import isfile, join, abspath
        
        if(path.isdir(source)):
            onlyfiles = []
            for dirpath,_,filenames in walk(source):
                for f in filenames:
                    onlyfiles.append(abspath(join(dirpath, f)))
        else:
            onlyfiles = [source]
        # Set progress bar to 0
        totalCnt = len(onlyfiles)
        self.progress_bar["maximum"] = totalCnt

        # Run matching with each files
        target_file = targetFile
        self.data = []
        for file in onlyfiles:
            try:
                # fullpath = join(source, file)
                fullpath = file # New change

                # print(fullpath, "and", target_file)
                match = fapi.func(target_file, fullpath)
                add = [fullpath, *match]
                self.data.append(add)
            except Exception as e:
                messagebox.showerror("Err", e)
            finally:
                self.progress_bar["value"] += 1
                self.mainwindow.update_idletasks()

        self.populatetree()

    def set_input(self, value):
        self.technicaldata.delete(1.0, END)
        self.technicaldata.insert(END, value)

    def treeitem_select(self, event=None):
        if(not event): return
        selection = self.treeview.selection()[0]
        indx = int(selection)
        row = self.data[indx]
        # print("Selected")
        self.set_input(row[4])

    def populatetree(self):
        s = ttk.Style()
        s.configure("Treeview", rowheight=100)

        # Configure scrollbar!
        self.scrollbar_tv.config(command = self.treeview.yview)
        self.treeview.configure(yscrollcommand=self.scrollbar_tv.set)

        # print(self.treeview["columns"])
        for column in self.treeview["columns"]:
            self.treeview.column(column, anchor=CENTER) # This will center text in rows
            # self.treeview.heading(column, text=column)

        index = iid = 0
        self.image_cache = [None] * len(self.data)
        self.data.sort(key=lambda x: x[1], reverse=True)
        for row in self.data:
            print(row)
            # _img = Image.open(row[0])
            # _img, face_data = self.sface_api.preview(row[0])
            _face = row[5]
            _img = cv2.imread(row[0])
            if(_face):
                # print("Here face")
                print(_face)
                _img = self.sface_api.app.draw_on(_img, [_face])
            # TODO : Use face_data
            # new_height = 100
            # new_width  = (int)(new_height * float(_img.size[0]) / float(_img.size[1]))
            # new_width = 100
            # new_height = 100
            # _img = _img.resize((new_width, new_height), Image.ANTIALIAS)
            _img = cv2.resize(_img, (100,100))
            b,g,r = cv2.split(_img)
            _img = cv2.merge((r,g,b))

            im = Image.fromarray(_img)

            self.image_cache[iid] = ImageTk.PhotoImage(image=im)

            row[0] = Path(row[0]).stem
            row[1] = str(round(row[1]*100, 2))  # Convert to %
            self.treeview.insert("", index, iid, values=row, image=self.image_cache[iid])
            index = iid = index + 1



if __name__ == "__main__":
    app = RevampUiResultApp()
    app.startProcessing("/home/hsk/Desktop/Freelance/insightface/photo", "/home/hsk/Desktop/Freelance/insightface/target.jpg")
    app.run()
