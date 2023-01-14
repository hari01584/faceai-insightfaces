# from insightface.app import FaceAnalysis

# model_pack_name = 'antelopev2'
# app = FaceAnalysis(name=model_pack_name)
import json
import sys
import os
import time
import numpy as np
import cv2
import onnx
import onnxruntime
from onnx import numpy_helper

import insightface
import cv2

import cv2
import numpy as np
import insightface
from insightface.app import FaceAnalysis
from insightface.data import get_image as ins_get_image

app = FaceAnalysis(providers=['CUDAExecutionProvider', 'CPUExecutionProvider'])
app.prepare(ctx_id=0, det_size=(640, 640))
img = cv2.imread('./target.jpg')
# img = ins_get_image(')
faces = app.get(img)
print(faces)
rimg = app.draw_on(img, faces)
cv2.imwrite("./t1_output.jpg", rimg)


# detector = insightface.model_zoo.get_model('genderage.onnx', download=True)
# detector.prepare(0, nms_thresh=0.5, input_size=(640, 640))

# print(detector.input_name)

# session = detector.session

# img = cv2.imread("target.jpg")

# print(dir(session))
# # ret = detector.detect(img)
# # print(ret)

# # model = onnx.load('genderage.onnx')
# output_name = detector.output_names[0]
# input_name = detector.input_name
# result = session.run([output_name], {input_name: img})
# prediction=int(np.argmax(np.array(result).squeeze(), axis=0))
# print(prediction)
