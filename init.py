import cv2
import time
import numpy as np

import param
import speedup


def circular_mask(img_h, img_w, center_x, center_y, radius):
    y, x = np.ogrid[:img_h, :img_w]
    dist_from_center = (x - center_x)**2 + (y - center_y)**2
    mask = dist_from_center <= radius**2
    return mask

def create_fan(angle):
	resolution_angle = (np.pi - 0.2) / param.RESOLUTION
	op_angle = angle + np.pi
	start = op_angle - (param.RESOLUTION / 2) * resolution_angle * 2

	starts = start + np.arange(param.RESOLUTION) * (resolution_angle * 2)
	ends = starts + resolution_angle * 2

	fan = np.empty((param.RESOLUTION, 6), dtype=np.float32)
	fan[:, 0] = np.cos(angle)
	fan[:, 1] = np.sin(angle)
	fan[:, 2] = np.cos(starts)
	fan[:, 3] = np.sin(starts)
	fan[:, 4] = np.cos(ends)
	fan[:, 5] = np.sin(ends)

	return fan

# counts all non-zero pixels in all triangles in all fans
def get_pixelatet_count_all(fans_triangles_int_shift_10):
	print("counting pixels")
	print("===============")
	img_temp = np.zeros([param.IMG_WIDTH, param.IMG_HEIGHT], dtype =  np.uint8)
	param.img_sum  = np.zeros([param.LASERCOUNT, param.IMG_WIDTH, param.IMG_HEIGHT], dtype =  np.uint16)
	circle_mask = circular_mask(param.IMG_HEIGHT, param.IMG_WIDTH, param.CENTER_X, param.CENTER_Y, param.RADIUS_VIEW_MASK)
	pixel_count = 0
	fan_index = 0
	h = param.IMG_HEIGHT
	for fan_triangles in fans_triangles_int_shift_10:
		for triangle in fan_triangles:
			img_temp.fill(0)
			points = triangle.reshape((-1, 1, 2))
			cv2.fillConvexPoly(img_temp, points = points, color= (255), shift=10, lineType = cv2.LINE_AA)
			img_temp[~circle_mask] = 0
			pixel_count += np.count_nonzero(img_temp)
			param.img_sum[fan_index] += img_temp
		print(	"{:>5} /".format(fan_index),
				"{:>5}".format(param.LASERCOUNT),
				"{:>12}".format(pixel_count),
				 flush = True)
		fan_index += 1
	param.img_sum_ravel			  = param.img_sum.ravel(order='C')
	print("Max: ",np.max(param.img_sum))
	return pixel_count
	
def create_files(fans_triangles_int_shift_10, total_pixels_count):
	print("calculating pixels")
	print("==================")
	param.pixel_positions 		= np.empty([total_pixels_count], dtype =  np.uint32)
	param.pixel_weights			= np.empty([total_pixels_count], dtype =  np.float32)
	param.triagle_start_positions = np.empty([param.RESOLUTION * param.LASERCOUNT], dtype = np.uint32)
	param.triangle_pixel_counts   = np.empty([param.RESOLUTION * param.LASERCOUNT], dtype = np.uint32)
	param.triangle_img_deck		= np.zeros([param.RESOLUTION, param.IMG_WIDTH, param.IMG_HEIGHT], dtype =  np.uint8)
	param.triangle_img_deck_ravel = param.triangle_img_deck.ravel(order='C')
	param.circle_mask = circular_mask(param.IMG_HEIGHT, param.IMG_WIDTH, param.CENTER_X, param.CENTER_Y, param.RADIUS_VIEW_MASK).flatten()
	
	total_pixels_index = 0
	triangle_index = 0
	fan_index = 0
	for fan_triangles in fans_triangles_int_shift_10:
		for triangle, img_temp in zip(fan_triangles, param.triangle_img_deck):
			points = triangle.reshape((-1, 1, 2))
			cv2.fillConvexPoly(img_temp, points = points, color = (255), shift=10, lineType = cv2.LINE_AA)
		param.fan_triangles_ravel    = fan_triangles.ravel(order='C')
		total_pixels_index, triangle_index = speedup.init_calc(total_pixels_index, triangle_index, fan_index, xlaser = points[0,0,0]/1024, ylaser = points[0,0,1]/1024)
		print(	"{:>5} /".format(fan_index + 1),
				"{:>5}".format(param.LASERCOUNT),
				"{:>12}".format(total_pixels_index),
				 flush = True)
		fan_index += 1
		
	print(" ")
	print("write to disk")
	print("=============")
	
	with open("pixel_positions",'wb') as f:
		np.save(f, param.pixel_positions)
	with open("pixel_weights",'wb') as f:
		np.save(f, param.pixel_weights)
	with open("triagle_start_positions",'wb') as f:
		np.save(f, param.triagle_start_positions)
	with open("triangle_pixel_counts",'wb') as f:
		np.save(f, param.triangle_pixel_counts)		
	return

start = time.time()

phi = np.linspace(0, 2 * np.pi, param.LASERCOUNT, endpoint=False, dtype=np.float32)	
fans_triangles  = np.empty([param.LASERCOUNT, param.RESOLUTION, 6], dtype=np.float32)
for i in range(param.LASERCOUNT):
	fans_triangles[i] = create_fan(phi[i])

fans_triangles  *= param.RADIUS_LASER_CIRCLE
fans_triangles[:,:,0] += param.CENTER_Y
fans_triangles[:,:,2] += param.CENTER_Y
fans_triangles[:,:,4] += param.CENTER_Y
fans_triangles[:,:,1] += param.CENTER_X
fans_triangles[:,:,3] += param.CENTER_X
fans_triangles[:,:,5] += param.CENTER_X
fans_triangles_int_shift_10 = np.round(fans_triangles * 1024).astype(np.int32)

total_pixels = get_pixelatet_count_all(fans_triangles_int_shift_10)
print(" ")
create_files(fans_triangles_int_shift_10, total_pixels)
print(" ")
print("time: {:>7.2f} sec".format(time.time() - start), flush = True)




