RESOLUTION  		=  400
LASERCOUNT  		=  300						# actully it's the lasercount per color
IMG_WIDTH			=  1000
IMG_HEIGHT    		= IMG_WIDTH
CENTER_X			= IMG_HEIGHT // 2
CENTER_Y			= IMG_WIDTH  // 2
RADIUS_LASER_CIRCLE = CENTER_X	- 1				# should be smaller then IMG_WIDTH / 2
RADIUS_VIEW_MASK 	= RADIUS_LASER_CIRCLE - 10	# should be smaller then RADIUS_VIEW_MASK


IMAGE				= "example.jpg"
THRESHOLD			= 1.0						# improvement per optimizing-cycle is measured in delta RMSE over all pixels of each
												# channel red, green and blue. the algorithem stops, when iprovement per cycle drops
												# below this value. floatingpoint errors accumulate, if this is chosen too low.

img_to_r = None
img_to_g = None
img_to_b = None

img_is_r = None
img_is_g = None
img_is_b = None

circle_mask = None

multiplier_r = None
multiplier_g = None
multiplier_b = None

pixel_positions			= None
pixel_weights			= None
triagle_start_positions	= None
triangle_pixel_counts	= None

img_sum = None
img_sum_ravel = None

fan_triangles = None
fan_triangles_ravel = None
triangle_img_deck = None
triangle_img_deck_ravel = None