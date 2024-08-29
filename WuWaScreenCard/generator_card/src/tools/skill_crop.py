from PIL import Image,ImageDraw

positions = {
    "colonka_one": {
        "level": (0, 1039, 246, 1083),
        "icon_stats_main": (58, 904, 183, 1029),
        "icon_two": (58, 564, 183, 689),
        "icon_three": (58, 269, 183, 394),
    },
    "colonka_two": {
        "level": (302, 855, 558, 900),
        "icon_stats_main": (368, 719, 493, 844),
        "icon_two": (368, 378, 493, 503),
        "icon_three": (368, 83, 493, 208),
    },
    "colonka_three": {
        "level": (666, 771, 922, 816),
        "icon_stats_main": (731, 635, 856, 760),
        "icon_two": (731, 295, 856, 420),
        "icon_three": (731, 0, 856, 125),
        "icon_four": (731, 958, 856, 1083),
    },
    "colonka_four": {
        "level": (1030, 857, 1286, 902),
        "icon_stats_main": (1098, 721, 1223, 846),
        "icon_two": (1098, 380, 1223, 505),
        "icon_three": (1098, 85, 1223, 210),
    },
    "colonka_five": {
        "level": (1346, 1039, 1598, 1083),
        "icon_stats_main": (1404, 904, 1529, 1029),
        "icon_two": (1404, 564, 1529, 689),
        "icon_three": (1404, 269, 1529, 394),
    },
}

def extract_icon(image: Image.Image, coordinates):
    if len(coordinates) == 4:
        left, upper, right, lower = coordinates
        left = max(left, 0)
        upper = max(upper, 0)
        right = min(right, image.width)
        lower = min(lower, image.height)
        return image.crop((left, upper, right, lower))
    else:
        raise ValueError("Coordinates must be a tuple of 4 elements: (left, upper, right, lower)")

def find_white_areas(mask: Image.Image, threshold=200):
    mask = mask.convert('L')
    binary_mask = mask.point(lambda p: 255 if p > threshold else 0)

    white_areas = []
    visited = set()

    def expand_area(start_x, start_y):
        left = right = start_x
        upper = lower = start_y

        while right < binary_mask.width and binary_mask.getpixel((right, start_y)) == 0:
            right += 1

        while lower < binary_mask.height and binary_mask.getpixel((start_x, lower)) == 0:
            lower += 1

        return (left, upper, right, lower)

    for x in range(binary_mask.width):
        for y in range(binary_mask.height):
            if (x, y) not in visited and binary_mask.getpixel((x, y)) == 0:
                white_area = expand_area(x, y)
                white_areas.append(white_area)
                for i in range(white_area[0], white_area[2]):
                    for j in range(white_area[1], white_area[3]):
                        visited.add((i, j))

    return white_areas

def get_skill_iconV(img: Image.Image, mask: Image.Image) -> dict:
    icons_dict = {}
    img.save("image.png")
    mask.save("obj.png")
    white_areas = find_white_areas(mask)
    
    for i, white_area in enumerate(white_areas):
        mask_for_area = Image.new('L', img.size, 255)
        area_mask = Image.new('L', (white_area[2] - white_area[0], white_area[3] - white_area[1]), 0)
        area_mask.paste(0, (0, 0, area_mask.width, area_mask.height))
        mask_for_area.paste(area_mask, (white_area[0], white_area[1]))

        extracted_icon = Image.composite(img, Image.new('RGB', img.size), mask_for_area)
        extracted_icon = extracted_icon.crop(white_area)
        icons_dict[f"icon_{i}"] = extracted_icon
        extracted_icon.show()
                
    return icons_dict

index = [
    "icon_three", #3
    "icon_three", #2
    "icon_three", #4
    "icon_three", #1
    "icon_three", #5
    
    "icon_two", #3
    "icon_two", #2
    "icon_two", #4
    "icon_two", #1
    "icon_two", #5
    
    "icon_stats_main", #3
    "icon_stats_main", #2
    "icon_stats_main", #4
    "level", #3
    "level", #2
    
    "level", #4
    "icon_stats_main", #1
    "icon_stats_main", #5
    "icon_four", #3
    "level", #1
    "level", #5
    
]




colonka = [
    "colonka_three",
    "colonka_two",
    "colonka_four",
    "colonka_one",
    "colonka_five",
    
    "colonka_three",
    "colonka_two",
    "colonka_four",
    "colonka_one",
    "colonka_five",
    
    "colonka_three",
    "colonka_two",
    "colonka_four",
    "colonka_three",
    "colonka_two",
    
    "colonka_four",
    "colonka_one",
    "colonka_five",
    "colonka_three",
    "colonka_one",
    "colonka_five",
]

def get_skill_icon(img: Image.Image, mask: Image.Image):
    if mask.mode != "L":
        mask = mask.convert("L")
    
    mask = mask.point(lambda p: p > 128 and 255)
    
    cut_images = {}
    width, height = mask.size
    visited = set()
    
    def flood_fill(x, y):
        stack = [(x, y)]
        area = []
        
        min_x, min_y = x, y
        max_x, max_y = x, y
        
        while stack:
            cx, cy = stack.pop()
            if (cx, cy) in visited or cx < 0 or cy < 0 or cx >= width or cy >= height:
                continue
            
            visited.add((cx, cy))
            
            if mask.getpixel((cx, cy)) == 255:
                area.append((cx, cy))
                min_x = min(min_x, cx)
                min_y = min(min_y, cy)
                max_x = max(max_x, cx)
                max_y = max(max_y, cy)
                stack.extend([(cx-1, cy), (cx+1, cy), (cx, cy-1), (cx, cy+1)])
        
        return area, min_x, min_y, max_x, max_y
    
    i = 0
    
    for y in range(height):
        for x in range(width):
            if mask.getpixel((x, y)) == 255 and (x, y) not in visited:
                white_area, min_x, min_y, max_x, max_y = flood_fill(x, y)
                
                if white_area:
                    temp_mask = Image.new("L", img.size, 0)
                    draw = ImageDraw.Draw(temp_mask)
                    draw.point(white_area, fill=255)
                    
                    masked_image = Image.composite(img, Image.new("RGBA", img.size, (0, 0, 0, 0)), temp_mask)
                    
                    pos = (min_x, min_y, max_x + 1, max_y + 1)
                    cropped_image = masked_image.crop(pos)
                    if not colonka[i] in cut_images:
                        cut_images[colonka[i]] = {}
                    cut_images[colonka[i]][index[i]] = cropped_image
                    
                    i += 1
                    
    return cut_images 
