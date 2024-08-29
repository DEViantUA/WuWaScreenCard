from PIL import Image
import numpy as np

slot_coords = [
    (35, 199, 200, 366),
    (53, 425, 181, 554),
    (53, 569, 181, 698), 
    (53, 713, 181, 842), 
    (53, 857, 181, 986)  
]


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
            self.additional_y_offset = int((self.aspect_diff // (1/9)) * 30)
            self.y_offset -= self.additional_y_offset
        else:
            self.additional_y_offset = 0

    def get_position(self, position):
        scaled_x = round(position[0] * self.x_ratio + self.x_offset)
        scaled_y = round(position[1] * self.y_ratio + self.y_offset)
        
        return (scaled_x, scaled_y)

    def get_position_frame(self, slot_coords):
        scaled_slots = []
        for i, slot in enumerate(slot_coords):
            
            x1, y1, x2, y2 = slot
            
            scaled_slot = (
                round(x1 * self.x_ratio + self.x_offset),
                round(y1 * self.y_ratio + self.y_offset),
                round(x2 * self.x_ratio + self.x_offset),
                round(y2 * self.y_ratio + self.y_offset),
            )
            scaled_slots.append(scaled_slot)
        
        return scaled_slots
    
    def get_size(self, size):
        scaled_x = round(size[0] * self.x_ratio)
        scaled_y = round(size[1] * self.y_ratio)
        if self.aspect_diff != 0:
            correction_factor = 229 / 254
            scaled_y = round(scaled_y * correction_factor)

        return (scaled_x, scaled_y)

class SlotChecker:
    def __init__(self, test_image_path: str, reference_image_path: Image.Image, monitor_size: tuple = (2560, 1440), threshold = 0.01):
        self.test_image = Image.open(test_image_path)
        self.reference_image = reference_image_path
        size = ImageScaler(monitor_size)
        self.slot_coords = size.get_position_frame(slot_coords)
                
        self.threshold = threshold
        self.empty_slots = []

        self.empty_colors = self.get_unique_colors(self.reference_image)

    def get_unique_colors(self, image):
        np_image = np.array(image.convert("RGB"))
        unique_colors = np.unique(np_image.reshape(-1, 3), axis=0)
        return unique_colors.shape[0]

    def count_unique_colors(self, image):
        np_image = np.array(image.convert("RGB"))
        unique_colors = np.unique(np_image.reshape(-1, 3), axis=0)
        return unique_colors.shape[0]

    def save_images(self, test_slot, reference_slot, coord, index):
        test_slot.save(f"test_slot_{index}.png")
        reference_slot.save(f"reference_slot_{index}.png")

    def check_slots(self):
        for i, coord in enumerate(self.slot_coords, start=1):
            try:
                test_slot = self.test_image.crop(coord)
                
                test_slot_colors = self.count_unique_colors(test_slot)
                
                color_diff_percentage = (test_slot_colors / self.empty_colors) * 100

                print(f"Slot {i}: Unique Colors: {test_slot_colors}, Empty Slot Colors: {self.empty_colors}, Color Diff Percentage: {color_diff_percentage:.2f}%")

                if color_diff_percentage > (self.threshold * 100):
                    print(f"Slot {i} is considered filled.")
                else:
                    self.empty_slots.append((i, coord))
                    print(f"Slot {i} is considered empty.")
            
            except Exception as e:
                print(f"Error processing slot {i}: {e}")

    def get_empty_slots(self):
        self.check_slots()
        return self.empty_slots