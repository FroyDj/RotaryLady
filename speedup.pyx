# cython: language_level=3
import os
os.environ['NUMPY_EXPERIMENTAL_ARRAY_FUNCTION'] = '0'
import math
cimport cython

import param

@cython.boundscheck(False)
@cython.wraparound(False)
@cython.nonecheck(False)
@cython.cdivision(True)
@cython.initializedcheck(False)
@cython.binding(False)

def pixelcount(int ppv_count, int triangle_count, int fancount):
	cdef unsigned char[::1]			triangle_img_deck_ravel_view	= param.triangle_img_deck_ravel
	cdef unsigned char[::1]			circle_mask			= param.circle_mask
	cdef short unsigned int[::1]		img_sum_ravel_view		= param.img_sum_ravel
	cdef Py_ssize_t				i, j
	cdef unsigned int	pixel_total = param.IMG_WIDTH * param.IMG_HEIGHT
	cdef unsigned short	w = param.IMG_WIDTH
	cdef unsigned int	start, length, mi, o
	cdef int		ppv_count_last, r
	cdef unsigned char	h
		
	start = 0
	r = param.RESOLUTION
	o = fancount * pixel_total
	start = 0
	length = pixel_total
	for i in range(r): 
		mi = 0
		for j in range(start, length):
			if triangle_img_deck_ravel_view[j] != 0:
				h = triangle_img_deck_ravel_view[j]
				triangle_img_deck_ravel_view[j] = 0
				if circle_mask[mi] != 0:
					img_sum_ravel_view[mi + o] += h
					ppv_count += 1
			mi += 1
		start += pixel_total
		length += pixel_total
		triangle_count += 1
		
	return ppv_count, triangle_count

def init_calc(int ppv_count, int triangle_count, int fan_index, float xlaser, float ylaser):
	cdef unsigned char[::1]			triangle_img_deck_ravel_view	= param.triangle_img_deck_ravel
	cdef unsigned char[::1]			circle_mask			= param.circle_mask
	cdef unsigned int[::1]			pixel_positions_view		= param.pixel_positions
	cdef float[::1]				pixel_weights_view		= param.pixel_weights
	cdef short unsigned int[::1]		img_sum_ravel_view		= param.img_sum_ravel
	cdef int[::1]				fan_triangles_ravel_view	= param.fan_triangles_ravel
	cdef unsigned int[::1]			triagle_start_positions_view	= param.triagle_start_positions
	cdef unsigned int[::1]			triangle_pixel_counts_view	= param.triangle_pixel_counts
	cdef Py_ssize_t				i, j
	cdef unsigned int			pixel_total			= param.IMG_WIDTH * param.IMG_HEIGHT
	cdef unsigned short			w = param.IMG_WIDTH
	cdef unsigned int			start, length, mi, hh
	cdef float				distance, x, y
	cdef int				ppv_count_last
	cdef unsigned char			h
	
	hh = fan_index * pixel_total
	start = 0
	r = param.RESOLUTION
	ppv_count_last = ppv_count
	for i in range(r):
		mi = 0
		triagle_start_positions_view[triangle_count] = ppv_count
		for j in range(start, start + pixel_total):
			if triangle_img_deck_ravel_view[j] != 0:
				h = triangle_img_deck_ravel_view[j]
				triangle_img_deck_ravel_view[j] = 0
				if circle_mask[mi] != 0:
					pixel_positions_view[ppv_count] = mi
					dx = -xlaser + mi % w
					dy = -ylaser + mi // w
					distance = math.sqrt(dx*dx + dy*dy)
					pixel_weights_view[ppv_count] = h / (img_sum_ravel_view[hh + mi] * distance)
					ppv_count += 1
				
			mi += 1
		triangle_pixel_counts_view[triangle_count] = ppv_count - ppv_count_last
		ppv_count_last = ppv_count
		triangle_count += 1
		start += pixel_total
	return ppv_count, triangle_count

def match_opti(double th, int c):
	cdef unsigned char[::1]			img_to_view
	cdef unsigned char[::1]			img_to_view_r			= param.img_to_r
	cdef unsigned char[::1]			img_to_view_g			= param.img_to_g
	cdef unsigned char[::1]			img_to_view_b			= param.img_to_b
	
	cdef float[::1]				img_is_view
	cdef float[::1]				img_is_view_r			= param.img_is_r
	cdef float[::1]				img_is_view_g			= param.img_is_g
	cdef float[::1]				img_is_view_b			= param.img_is_b
	
	cdef float[::1]				multiplyer_view
	cdef float[::1]				multiplyer_view_r		= param.multiplier_r
	cdef float[::1]				multiplyer_view_g		= param.multiplier_g
	cdef float[::1]				multiplyer_view_b		= param.multiplier_b
	
	cdef unsigned int[::1]			pixel_positions_view		= param.pixel_positions
	cdef float[::1]				pixel_weights_view		= param.pixel_weights
	cdef unsigned int[::1]			triagle_start_positions_view	= param.triagle_start_positions
	cdef unsigned int[::1]			triangle_pixel_counts_view	= param.triangle_pixel_counts
	
	cdef unsigned int		start, length, pix_pos
	cdef double			current_dist, current_dist_last, pot_fut_dist, diff, improv
	cdef Py_ssize_t			i, j, count = 0
	cdef float			as_is, to_be, multiplyer, pwv
	cdef str 			col_str 
	
	
	if c == 0:
		img_to_view		= img_to_view_b
		img_is_view		= img_is_view_b
		multiplyer_view	= multiplyer_view_b
		col_str = 'blue '
	
	if c == 1:
		img_to_view		= img_to_view_g
		img_is_view		= img_is_view_g
		multiplyer_view	= multiplyer_view_g
		col_str = 'green'
		
	if c == 2:
		img_to_view		= img_to_view_r
		img_is_view		= img_is_view_r
		multiplyer_view	= multiplyer_view_r
		col_str = 'red  '

	for i in range(param.RESOLUTION * param.LASERCOUNT):
		start  = triagle_start_positions_view[i]
		length = triangle_pixel_counts_view[i]
		multiplyer = multiplyer_view[i]
		length += start
		for j in range(start, length):
			pix_pos = pixel_positions_view[j]
			pwv = pixel_weights_view[j]
			img_is_view[pix_pos] += pwv * multiplyer
	
	#distance
	current_dist_last = 0.0
	for i in range(param.IMG_WIDTH * param.IMG_HEIGHT):
		to_be = img_to_view[i]
		if to_be != 0:
			as_is = img_is_view[i]
			as_is -= to_be
			current_dist_last += as_is*as_is
	current_dist_last = math.sqrt(current_dist_last)
	
	while True:
		for i in range(param.RESOLUTION * param.LASERCOUNT):
			start  = triagle_start_positions_view[i]
			length = triangle_pixel_counts_view[i]
			multiplyer = multiplyer_view[i]
			current_dist = 0.0
			pot_fut_dist = 0.0
			length += start
			for j in range(start, length):
				pix_pos = pixel_positions_view[j]
				pwv = pixel_weights_view[j]
				to_be = img_to_view[pix_pos]
				as_is = img_is_view[pix_pos] - multiplyer * pwv
				to_be -= as_is
				current_dist += to_be * pwv
				pot_fut_dist += pwv*pwv
			if pot_fut_dist != 0.0:
				diff = current_dist / pot_fut_dist
			else:
				diff = 0.0
			if diff < 0.0:
				diff = 0.0
			for j in range(start, length):
				pix_pos = pixel_positions_view[j]
				pwv = pixel_weights_view[j]
				pwv *= (diff - multiplyer)
				img_is_view[pix_pos] += pwv
			multiplyer_view[i] = diff
		count += 1
		
		#distance
		current_dist = 0.0
		for i in range(param.IMG_WIDTH * param.IMG_HEIGHT):
			to_be = img_to_view[i]
			if to_be != 0.0:
				as_is  = img_is_view[i]
				as_is -= to_be
				current_dist += as_is*as_is
		current_dist = math.sqrt(current_dist)
		
		improv = current_dist_last - current_dist
		print(	col_str,
				"| round: {:>5}".format(count),
				"| RMSE: {:>13.1f}".format(current_dist),
				"| RMSE improve: {:>12.1f}".format(improv),
				"/ {:>4.1f}".format(th),
				flush = True)
		current_dist_last = current_dist
		if improv < th:
			break
	
	for i in range(param.IMG_WIDTH * param.IMG_HEIGHT):
		img_is_view[i] = 0.0
	
	for i in range(param.RESOLUTION * param.LASERCOUNT):
		start  = triagle_start_positions_view[i]
		length = triangle_pixel_counts_view[i]
		multiplyer = multiplyer_view[i]
		length += start
		for j in range(start, length):
			pix_pos = pixel_positions_view[j]
			pwv = pixel_weights_view[j]
			img_is_view[pix_pos] += pwv * multiplyer
	
	return	
			
			
			
			
			
			
			
			
			
			
			
			
			
