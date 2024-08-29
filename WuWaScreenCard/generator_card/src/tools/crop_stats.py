from PIL import Image
import numpy as np
from .git import ImageCache

slot_coords = [
    (577, 260, 577 + 42, 260 + 39),
    (577, 303, 577 + 42, 303 + 39),
    (577, 346, 577 + 42, 346 + 39),
    (577, 389, 577 + 42, 389 + 39),
    (577, 432, 577 + 42, 432 + 39),
]

_of = ImageCache()
_of.set_mapping(1)



class SlotChecker:
    def __init__(self, image, zero, threshold=0.1):
        self.test_image = image
        self.reference_image = zero
        self.slot_coords = slot_coords
        self.threshold = threshold
        self.empty_slots = []

    def calculate_rmse(self, image1, image2):
        np_image1 = np.array(image1.convert("RGB"))
        np_image2 = np.array(image2.convert("RGB"))
        
        if np_image1.shape != np_image2.shape:
            raise ValueError("The images have different sizes.")
        
        rmse = np.sqrt(((np_image1 - np_image2) ** 2).mean())
        return rmse / 255

    def calculate_mean_color_difference(self, image1, image2):
        np_image1 = np.array(image1.convert("RGB"))
        np_image2 = np.array(image2.convert("RGB"))
        
        if np_image1.shape != np_image2.shape:
            raise ValueError("The images have different sizes.")
        
        mean_color1 = np.mean(np_image1, axis=(0, 1))
        mean_color2 = np.mean(np_image2, axis=(0, 1))
        
        diff = np.abs(mean_color1 - mean_color2)
        diff_percentage = np.mean(diff) / 255
        
        return diff_percentage

    def check_slots(self):
        for i, coord in enumerate(self.slot_coords, start=1):
            test_slot = self.test_image.crop(coord)
            rmse = self.calculate_rmse(test_slot, self.reference_image)
            color_diff = self.calculate_mean_color_difference(test_slot, self.reference_image)

            if rmse < self.threshold and color_diff < self.threshold:
                self.empty_slots.append((i, coord))

    def get_empty_slots(self):
        self.check_slots()
        return self.empty_slots

class ImageProcessor:
    def __init__(self, img_path):
        self.img = img_path
        

    def get_level(self):
        region = (80, 116, 80 + 69, 116 + 34)
        level_image = self.img.crop(region)
        level_image_rgb = level_image.convert("RGB")
        
        best_match = None
        best_diff = float('inf')
        
        for level, icon_image in self.icon_images.items():
            icon_rgb = icon_image.convert("RGB")
            diff = self.calculate_rmse(level_image_rgb, icon_rgb)
            
            if diff < 0.1 and diff < best_diff:
                best_diff = diff
                best_match = level
        
        return best_match

    def calculate_rmse(self, image1, image2):
        if image1.size != image2.size:
            image2 = image2.resize(image1.size)
        
        np_image1 = np.array(image1.convert("RGB"))
        np_image2 = np.array(image2.convert("RGB"))
        
        rmse = np.sqrt(((np_image1 - np_image2) ** 2).mean())
        return rmse / 255

    def crop_based_on_level(self, level):
        if level is None:
            return self.img 
        
        if 0 <= level < 5:
            crop_y = 252
        elif 5 <= level < 10:
            crop_y = 342
        elif 10 <= level < 15:
            crop_y = 300
        elif 15 <= level < 20:
            crop_y = 426
        elif level >= 20:
            crop_y = self.img.height 
        return self.img.crop((0, 0, self.img.width, crop_y))

    async def get_cropped_image(self):
        
        self.empty_icon_image = await _of.zero_stat_icon
        icon_images_paths = {
            0: _of.icon_0,
            5: _of.icon_5,
            10: _of.icon_10,
            15: _of.icon_15,
            20: _of.icon_20,
            25: _of.icon_25
        }
        
        self.icon_images = {level: await icon for level, icon in icon_images_paths.items()}
        
        
        checker = SlotChecker(self.img, self.empty_icon_image)
        empty_slots = checker.get_empty_slots()
        level = self.get_level()
        
        if empty_slots:
            first_empty_slot = empty_slots[0][1]
            crop_y = first_empty_slot[1]
            cropped_image = self.img.crop((0, 0, self.img.width, crop_y - 6))
        else:
            cropped_image = self.crop_based_on_level(level)
        
        return cropped_image