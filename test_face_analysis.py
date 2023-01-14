import cv2
import numpy as np
import insightface
from insightface.app import FaceAnalysis
from insightface.data import get_image as ins_get_image

app = FaceAnalysis(allowed_modules=['detection', 'recognition', 'genderage'],providers=['CUDAExecutionProvider', 'CPUExecutionProvider'])
app.prepare(ctx_id=0, det_size=(640, 640))
img = cv2.imread('target.jpg')
faces = app.get(img)
print(faces)
rimg = app.draw_on(img, faces)
cv2.imwrite("./t1_output.jpg", rimg)
