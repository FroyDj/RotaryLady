import cv2
import time
import numpy as np
from multiprocessing import Pool
import multiprocessing.sharedctypes

import speedup
import param

param.pixel_positions			= np.load("pixel_positions" )
param.pixel_weights				= np.load("pixel_weights")
param.triagle_start_positions	= np.load("triagle_start_positions") 
param.triangle_pixel_counts		= np.load("triangle_pixel_counts")

img			= cv2.imread(param.IMAGE)

param.img_is_r  = multiprocessing.sharedctypes.RawArray('f', size_or_initializer = param.IMG_WIDTH * param.IMG_HEIGHT)
param.img_is_g  = multiprocessing.sharedctypes.RawArray('f', size_or_initializer = param.IMG_WIDTH * param.IMG_HEIGHT)
param.img_is_b  = multiprocessing.sharedctypes.RawArray('f', size_or_initializer = param.IMG_WIDTH * param.IMG_HEIGHT)

param.img_to_r     = img[:,:,2].flatten().astype(np.uint8)
param.img_to_g     = img[:,:,1].flatten().astype(np.uint8)
param.img_to_b     = img[:,:,0].flatten().astype(np.uint8)

param.multiplier_r = np.ones((param.RESOLUTION * param.LASERCOUNT), dtype=np.float32) * 70.0
param.multiplier_g = np.ones((param.RESOLUTION * param.LASERCOUNT), dtype=np.float32) * 70.0
param.multiplier_b = np.ones((param.RESOLUTION * param.LASERCOUNT), dtype=np.float32) * 70.0

th = [param.THRESHOLD, param.THRESHOLD, param.THRESHOLD]
color = [0, 1, 2]

p = Pool(3)
start = time.time()
p.starmap(speedup.match_opti, zip(th, color))

img_r = np.frombuffer(param.img_is_r, dtype = np.float32, count=param.IMG_WIDTH * param.IMG_HEIGHT).reshape(param.IMG_WIDTH, param.IMG_HEIGHT)
img_r = np.clip(img_r, 0, 255).astype(np.uint8)

img_g = np.frombuffer(param.img_is_g, dtype = np.float32, count=param.IMG_WIDTH * param.IMG_HEIGHT).reshape(param.IMG_WIDTH, param.IMG_HEIGHT)
img_g = np.clip(img_g, 0, 255).astype(np.uint8)

img_b = np.frombuffer(param.img_is_b, dtype = np.float32, count=param.IMG_WIDTH * param.IMG_HEIGHT).reshape(param.IMG_WIDTH, param.IMG_HEIGHT)
img_b = np.clip(img_b, 0, 255).astype(np.uint8)

img = cv2.merge((img_b, img_g, img_r))

cv2.imwrite("out.jpg" , img, [int(cv2.IMWRITE_JPEG_QUALITY), 100])

print("time: {:>7.2f} sec".format(time.time() - start), flush = True)




