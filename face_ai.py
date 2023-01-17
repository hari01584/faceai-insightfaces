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
import face_align

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
        # model_pack_name = 'antelopev2'
        assets_dir = resource_path('')
        self.app = FaceAnalysis(allowed_modules=['detection', 'recognition', 'genderage'],root=assets_dir, providers=['CUDAExecutionProvider', 'CPUExecutionProvider'])
        self.app.prepare(ctx_id=0, det_size=(640, 640))

    def __get_from_img(self, img):
        return self.app.get(img)

    def get(self, imgpath):
        img = cv2.imread(imgpath)
        # img = ins_get_image(')
        
        return self.__get_from_img(img)

    def get_cropped(self, img, kps):
        aimg = face_align.norm_crop(img, landmark=kps, image_size=self.input_size[0])
        embedding = self.get_feat(aimg).flatten()
        return embedding


    def preview(self, imgpath):
        img = cv2.imread(imgpath)
        faces = self.__get_from_img(img)
        new_img = self.app.draw_on(img, faces)
        return new_img, faces


    def write_preview(self, imgpath, name):
        new_img, faces = self.preview(imgpath)
        cv2.imwrite(name, new_img)
        return faces

    def getfeat(self, img):
        faces = self.app.get(img)
        if(len(faces) == 0):
            return None
        return faces[0]
    # def compare(self, img1, img2):

    def compute_sim(self, feat1, feat2):
        from numpy.linalg import norm
        feat1 = feat1.ravel()
        feat2 = feat2.ravel()
        sim = np.dot(feat1, feat2) / (norm(feat1) * norm(feat2))
        return sim


    def func(self, img1, img2):
        pimg1 = img1
        pimg2 = img2
        img1 = cv2.imread(img1)
        img2 = cv2.imread(img2)

        feat1 = self.getfeat(img1)
        feat2 = self.getfeat(img2)

        data = {}

        if(not feat1 or not feat2):
            # sim, gage, match, json.dumps(data, indent=4), feat2
            return -1, '-', 'Invalid, No face', json.dumps(data, indent=4), None

        # print(feat1)
        bbox1 = feat1.bbox
        kps1 = feat1.kps
        detect1 = feat1.det_score
        gender1 = feat1.gender
        age1 = feat1.age
        embedding1 = feat1.embedding

        # Store data to json
        data["person1"] = {
            "name": Path(pimg1).stem,
            "box": bbox1.tolist(),
            "detect_score": str(detect1),
            "gender": str(gender1),
            "age": str(age1)
        }

        bbox2 = feat2.bbox
        kps2 = feat2.kps
        detect2 = feat2.det_score
        gender2 = feat2.gender
        age2 = feat2.age
        embedding2 = feat2.embedding

        data["person2"] = {
            "name": Path(pimg2).stem,
            "box": bbox2.tolist(),
            "detect_score": str(detect2),
            "gender": str(gender2),
            "age": str(age2)
        }

        # Similiarly get detection scores for P2

        # Calculate matching/recognition, arcosine loss
        sim = self.compute_sim(feat1.embedding, feat2.embedding)

        # More stats
        match = "-"
        if(sim < 0.7):
            match = '-'
        elif(sim < 0.8):
            match = 'Low match'
        elif(sim < 0.9):
            match = 'High match'
        elif(sim <= 1.1):
            match = 'Highest match'
        
        gage = ('M' if gender2 == 1 else 'F') +" "+str(age2)
        return sim, gage, match, json.dumps(data, indent=4), feat2


    def summary(self, data):
        return "%d%%\n%s\n%s"%(data[0]*100, data[1], data[2])