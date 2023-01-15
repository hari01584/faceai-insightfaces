from arcface_onnx import ArcFaceONNX
import os
import os.path as osp
import cv2
import numpy as np
from scrfd import SCRFD
import sys
import json
from pathlib import Path
from insightface.app import FaceAnalysis
import insightface

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class SFaceAI:
    def __init__(self):
        self.app = FaceAnalysis(allowed_modules=['detection', 'recognition', 'genderage'],providers=['CUDAExecutionProvider', 'CPUExecutionProvider'])
        self.app.prepare(ctx_id=0, det_size=(640, 640))

    def __get_from_img(self, img):
        return self.app.get(img)

    def get(self, imgpath):
        img = cv2.imread(imgpath)
        # img = ins_get_image(')
        
        return self.__get_from_img(img)

    def preview(self, imgpath):
        img = cv2.imread(imgpath)
        faces = self.__get_from_img(img)
        new_img = self.app.draw_on(img, faces)
        return new_img, faces


    def write_preview(self, imgpath, name):
        new_img, faces = self.preview(imgpath)
        cv2.imwrite(name, new_img)
        return faces

class FaceAI:
    def __init__(self):
        # assets_dir = osp.expanduser('~/.insightface/models/buffalo_l')

        assets_dir = 'models'
        self.detector = SCRFD(resource_path(os.path.join(assets_dir, 'det_10g.onnx')))
        self.detector.prepare(0)
        model_path = resource_path(os.path.join(assets_dir, 'w600k_r50.onnx'))
        self.rec = ArcFaceONNX(model_path)
        self.rec.prepare(0)

    def deduce(self, folpath, filepath):
        from os import listdir
        from os.path import isfile, join
        onlyfiles = [f for f in listdir(folpath) if isfile(join(folpath, f))]
        # Run matching with each files
        target_file = filepath
        for file in onlyfiles:
            match = self.func(target_file, file)


    def func(self, img1, img2):
        data = {}

        print("Checking ", img1, "and", img2)
        image1 = cv2.imread(img1)
        image2 = cv2.imread(img2)
        bboxes1, kpss1 = self.detector.autodetect(image1, max_num=1)
        if bboxes1.shape[0]==0:
            return -1.0, "Face not found in Image-1", "-", json.dumps(data)
        bboxes2, kpss2 = self.detector.autodetect(image2, max_num=1)
        if bboxes2.shape[0]==0:
            return -1.0, "Face not found in Image-2", "-", json.dumps(data)
        kps1 = kpss1[0]
        kps2 = kpss2[0]
        feat1 = self.rec.get(image1, kps1)
        feat2 = self.rec.get(image2, kps2)
        # Dump data for technical details
        data["person1"] = {
            "name": Path(img2).stem,
            "box": bboxes2.tolist()
        }
        data["person2"] = {
            "name": Path(img1).stem,
            "box": bboxes1.tolist()
        }
        print(json.dumps(data))
        sim = self.rec.compute_sim(feat1, feat2)
        if sim<0.2:
            conclu = 'They are NOT the same person'
        elif sim>=0.2 and sim<0.28:
            conclu = 'They are LIKELY TO be the same person'
        else:
            conclu = 'They ARE the same person'

        match = "-"
        if(sim < 0.7):
            match = '-'
        elif(sim < 0.8):
            match = 'Low match'
        elif(sim < 0.9):
            match = 'High match'
        elif(sim <= 1):
            match = 'Highest match'

        return sim, conclu, match, json.dumps(data, indent=4)
