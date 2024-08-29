from PIL import  ImageOps
from .git import ImageCache

_of = ImageCache()
_of.set_mapping(1)



class ImageScaler:
    def __init__(self, monitor_size, original_size=(2560, 1440), x_offset=0, y_offset=0):
        self.monitor_size = monitor_size
        self.original_size = original_size
        self.x_offset = x_offset
        self.y_offset = y_offset

        self.x_ratio = self.monitor_size[0] / self.original_size[0]
        self.y_ratio = self.monitor_size[1] / self.original_size[1]

        self.original_aspect_ratio = self.original_size[0] / self.original_size[1]
        self.current_aspect_ratio = self.monitor_size[0] / self.monitor_size[1]

        self.aspect_diff = abs(self.original_aspect_ratio - self.current_aspect_ratio)

        if self.aspect_diff != 0:
            self.additional_y_offset = int((self.aspect_diff // (1/9)) * 20)
            self.y_offset -= self.additional_y_offset
        else:
            self.additional_y_offset = 0

    def get_position(self, position):
        scaled_x = round(position[0] * self.x_ratio + self.x_offset)
        scaled_y = round(position[1] * self.y_ratio + self.y_offset)
        
        return (scaled_x, scaled_y)

    def get_size(self, size):
        scaled_x = round(size[0] * self.x_ratio)
        scaled_y = round(size[1] * self.y_ratio)
        if self.aspect_diff != 0:
            correction_factor = 229 / 254
            scaled_y = round(scaled_y * correction_factor)

        return (scaled_x, scaled_y)

    
    

class WeaponIconFinder:
    def __init__(self, image, block_width=176, block_height=208, monitor_size = (2560,1440), echo = False):
        
        
        resize = ImageScaler(monitor_size)
        
        size = resize.get_size((block_width,block_height))
        self.block_width = size[0]
        self.block_height = size[1]
                
        if echo:
            self.positions = [
                (243, 230), (415, 230), (587, 230),
                (243, 435), (415, 435), (587, 435),
                (243, 640), (415, 640), (587, 640),
                (243, 845), (415, 845), (587, 845)
            ]
        else:
            self.positions = [
                (108, 237), (284, 237), (460, 237),
                (108, 454), (284, 454), (460, 454),
                (108, 672), (284, 672), (460, 672),
                (108, 892), (284, 892), (460, 892)
            ]
            
        self.positions = [resize.get_position(key) for key in self.positions]
                
        self.image = image
        self.gray_image = ImageOps.grayscale(self.image)
        

    def find_selected_icon(self):
        max_white_pixels = 0
        selected_block = None

        for (x0, y0) in self.positions:
            white_pixel_count = 0

            for y in range(y0, y0 + self.block_height):
                for x in range(x0, x0 + self.block_width):
                    if self.gray_image.getpixel((x, y)) == 255:
                        white_pixel_count += 1

            if white_pixel_count > max_white_pixels:
                max_white_pixels = white_pixel_count
                selected_block = (x0, y0, x0 + self.block_width, y0 + self.block_height)

        if selected_block:
            cropped_icon = self.image.crop(selected_block)
            return cropped_icon
        return None

    async def save_cropped_icon(self):
        cropped_icon = self.find_selected_icon()
        if cropped_icon:
            return cropped_icon, True
        else:
            return await _of.none_weapon, False
