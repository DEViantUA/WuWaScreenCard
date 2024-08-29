import os
import sys
from PIL import Image
from .src.tools import pill
from .src.tools import cache, http, git, weapon_icon, params, slot_zero, crop_stats, skill_crop
from pathlib import Path

_of = git.ImageCache()
_of.set_mapping(1)


path_os = Path(__file__).parent.parent



async def create_menu_skill(icons):
    
    background = await _of.skill_background
    background = background.convert("RGBA").copy()
    
    for key in icons:
        icon:Image.Image = icons[key].convert("RGBA")
        if key == "level":
            background.alpha_composite(icon.resize((98,16)), (5,130))
        elif key == "icon_stats_main":
            background.alpha_composite(icon.resize((70,69)), (20,59))
        elif key == "icon_two":
            background.alpha_composite(icon.resize((52,52)), (1,15))
        elif key == "icon_three":
            background.alpha_composite(icon.resize((52,52)), (54,15))

    return background


async def create_menu_skill_four(icons):
    
    background = await _of.skill_background
    background = background.convert("RGBA").copy()
    
    for key in icons:
        icon:Image.Image = icons[key].convert("RGBA")
        if key == "level":
            background.alpha_composite(icon.resize((98,16)), (5,109))
        elif key == "icon_stats_main":
            background.alpha_composite(icon.resize((66,65)), (21,40))
        elif key == "icon_two":
            background.alpha_composite(icon.resize((55,54)), (0,0))
        elif key == "icon_three":
            background.alpha_composite(icon.resize((55,54)), (53,0))
        elif key == "icon_four":
            background.alpha_composite(icon.resize((41,41)), (33,125))
            
    return background

class ImageOverlay:
    def __init__(self, monitor_size):
        self.monitor_size = monitor_size

    def calculate_target_size(self):
        target_width = self.monitor_size[0]
        target_height = int(target_width / 16 * 9)

        if target_height > self.monitor_size[1]:
            target_height = self.monitor_size[1]
            target_width = int(target_height / 9 * 16)
        
        return target_width, target_height

    def overlay_image(self, img1: Image.Image):
        target_size = self.calculate_target_size()
        
        img2 = Image.new("RGBA", self.monitor_size, (0, 0, 0, 255))
        img1_resized = img1.resize(target_size)
        
        x_pos = int((self.monitor_size[0] - target_size[0]) / 2)
        y_pos = int((self.monitor_size[1] - target_size[1]) / 2)
        
        img2.alpha_composite(img1_resized.convert("RGBA"), (x_pos, y_pos))
        
        return img2

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
        if position[1] != 0:
            scaled_y = round(position[1] * self.y_ratio + self.y_offset)
        else:
            scaled_y = 0
        return (scaled_x, scaled_y)

    
    def get_size(self, size):
        scaled_x = round(size[0] * self.x_ratio)
        scaled_y = round(size[1] * self.y_ratio)

        if self.original_aspect_ratio != self.current_aspect_ratio:
            if self.original_aspect_ratio > self.current_aspect_ratio:
                scaled_y = round(size[1] * self.x_ratio)
            else:
                scaled_x = round(size[0] * self.y_ratio)

        return (scaled_x, scaled_y)
    
    def overlay_image(self,img1: Image.Image):
        img2 = Image.new("RGBA", (self.monitor_size), (0,0,0,255))
        img1_resized = img1.resize(self.monitor_size)
        
        x_pos = 0
        y_pos = int((img2.height - img1_resized.height) / 2)
        
        img2.alpha_composite(img1_resized.convert("RGBA"),(x_pos, y_pos))
        
        return img2       
    
class WuWaCard:
    
    def __init__(self, uid: int, path_screen: str, monitor_size: tuple) -> None:
        self.uid = uid
        if hasattr(sys, '_MEIPASS'):
            base_path = sys._MEIPASS
        else:
            base_path = os.getcwd()

        self.resize = ImageScaler(monitor_size)
        self.monitor_size = monitor_size
        
        self.path = os.path.join(base_path, path_screen)
        
        self.cache = {"maxsize": 150, "ttl": 300}
    
    async def __aenter__(self):
        cache.Cache.get_cache(maxsize = self.cache.get("maxsize", 150), ttl = self.cache.get("ttl", 300))
        await http.AioSession.enter(None)
        
        return self
    
    async def __aexit__(self, exc_type, exc, tb):
        await http.AioSession.exit(exc_type, exc, tb)
        
    async def open_image(self, path):
        image = Image.open(fr"{path}")
        return image.convert("RGBA")
    
    async def start(self):
        
        self.echo = []
        slot_echo = slot_zero.SlotChecker(f"{self.path}/echo_two.png", await _of.echo_zero, self.monitor_size, threshold=0.01).get_empty_slots()       
        echo_index = 6 - len(slot_echo)
        for key in params.screen_name:
            if params.screen_name.get(key) == "charter":
                image = await self.open_image(str(f"{self.path}/charter.png"))
                self.background = await self.create_background(image)
                self.stats = await self.create_stats(image)
                
            elif params.screen_name.get(key) == "weapon_info":
                image = await self.open_image(str(f"{self.path}/weapon_info.png"))
                self.weapon = await self.create_weapon(image)
            elif params.screen_name.get(key) == "const":
                image = await self.open_image(str(f"{self.path}/const.png"))
                self.const = await self.create_constant(image)
            elif "echo_" in params.screen_name.get(key):
                echo_index -= 1
                if echo_index <= 0:
                    continue
                image = await self.open_image(str(f"{self.path}/{params.screen_name.get(key)}.png"))
                echo = await self.create_echo(image)
                self.echo.append(echo)
            elif params.screen_name.get(key) == "echo2":
                image = await self.open_image(str(f"{self.path}/echo2.png")) #
                self.sets = await self.create_sets(image)
            elif params.screen_name.get(key) == "skills":
                image = await self.open_image(str(f"{self.path}/skills.png"))
                self.skills = await self.create_skills(image)
                
        await self.build()
        
        return self.background
    
    
    async def create_background(self, screenshot: Image.Image) -> Image.Image:
        background = Image.new("RGBA", (1920,782), (0,0,0,0))
        background_two = background.copy()
        background_default = await _of.background
        background_default = background_default.copy()
        
        mask = await _of.background_mask
        screenshot = await pill.get_center_size((2184,1229), screenshot)
        background.alpha_composite(screenshot,(-163,-175))
        background_two.paste(background,(0,0), mask.convert("L"))
        background_default.alpha_composite(background_two)
        
        return background_default
    
    async def create_stats(self, screenshot):
        object_coords = self.resize.get_position((232, 142))
        object_size = self.resize.get_size((560, 757))
        stats_size = (560,757)
        background = Image.new("RGBA", stats_size, (0,0,0,0))
        
        stats = pill.crop_object_from_image(screenshot, object_coords, object_size)
        mask = await _of.stats
        
        background.paste(stats.resize(stats_size),(0,0), mask.convert("L"))
        
        return background
      
    async def create_weapon(self, screenshot: Image.Image) -> Image.Image:
        object_coords = self.resize.get_position((1874, 162))
        object_size = self.resize.get_size((576, 305))
        stats_size = (576, 305)
        
        background = Image.new("RGBA", (627,335), (0,0,0,0))
        
        background_stats = Image.new("RGBA",stats_size, (0,0,0,0))
        stats = pill.crop_object_from_image(screenshot, object_coords, object_size)
        maska = await _of.weapon
        background_stats.paste(stats.resize(stats_size),(0,0), maska.convert("L"))
        
        maska = await _of.weapon_icon
        background_icon = Image.new("RGBA", (176,208), (0,0,0,0))
        icon, status = await weapon_icon.WeaponIconFinder(screenshot, monitor_size= self.monitor_size).save_cropped_icon()
        if status:
            background_icon.paste(icon.resize((176,208)),(0,0),maska.convert("L"))
        else:
            background_icon = icon
            
        background.alpha_composite(background_stats, (0,30))
        background.alpha_composite(background_icon, (451,0))
                
        return background
      
    async def create_constant(self, screenshot: Image.Image) -> Image.Image:
        object_coords = self.resize.get_position((676,0))
        object_size =  self.resize.get_size((1441,1441))
        object_size = list(object_size)
        const_size = (1441,1441)
        
        if object_size[1] < screenshot.height:
            object_size = (object_size[0], screenshot.height)

        background = Image.new("RGBA", const_size, (0,0,0,0))
        image = pill.crop_object_from_image(screenshot, object_coords, object_size)
        maska = await _of.const
        shadow = await _of.constant_shadow

        background.paste(image.resize(const_size),(0,0), maska.convert("L"))
        
        background.alpha_composite(shadow.resize(const_size))
        
        return background
        
    async def create_echo(self, screenshot):
        object_coords = self.resize.get_position((1814, 162))
        object_size = self.resize.get_size((636, 481))
        echo_size = (326,215)
        
        background = Image.new("RGBA", echo_size, (0,0,0,0))
               
        background_stats = Image.new("RGBA", object_size, (0,0,0,0))
        background_stats_def = await _of.background_echo
        background_stats_def = background_stats_def.convert("RGBA").copy()
        stats = pill.crop_object_from_image(screenshot, object_coords, object_size)
        stats = await crop_stats.ImageProcessor(stats).get_cropped_image()
        
        background_stats_def.alpha_composite(stats.convert("RGBA"))

        maska = await _of.echo
        
        background_stats.paste(background_stats_def,(0,0), maska.convert("L"))
        
        maska = await _of.echo_icon
        background_icon = Image.new("RGBA", (158,191), (0,0,0,0))
        icon, status = await weapon_icon.WeaponIconFinder(screenshot, 158, 191,  monitor_size= self.monitor_size, echo= True).save_cropped_icon()
        if status:
            background_icon.paste(icon.resize((158,191)),(0,0),maska.convert("L"))
        else:
            background_icon = icon
        
        background.alpha_composite(background_stats.resize((273,207)), (53,8))
        background.alpha_composite(background_icon.resize((87,105)), (0,0))
                
        return background
     
    async def create_sets(self,screenshot):
        object_coords = self.resize.get_position((249, 829))
        object_size = self.resize.get_size((574, 314))
        
        sets_size = (574, 314)
        
        background = Image.new("RGBA", sets_size, (0,0,0,0))
               
        stats = pill.crop_object_from_image(screenshot, object_coords, object_size)
        maska = await _of.sets
                
        background.paste(stats.resize(sets_size), (0,0), maska.convert("L"))
         
        return background
    
    async def create_skills(self,screenshot):
        skills = []
        icons_skills = Image.new("RGBA", self.monitor_size, (0,0,0,0))
        mask = await _of.skills
        
        mask = ImageOverlay(self.monitor_size).overlay_image(mask)
        
        icons_skills.paste(screenshot,(0,0), mask.convert("L"))
        
        icons_skills = skill_crop.get_skill_icon(icons_skills, mask)
        
        for key in icons_skills:
            if key == "colonka_three":
                skills.append(await create_menu_skill_four(icons_skills[key]))
            else:
                skills.append(await create_menu_skill(icons_skills[key]))
                
        return skills
    
    async def build(self):
        
        light = await _of.light
        pixel = await _of.pixel
        self.background.alpha_composite(light, (0,0))
        self.background.alpha_composite(pixel, (0,0))
        self.background.alpha_composite(self.stats.resize((347,469)),(39,31))
        self.background.alpha_composite(self.weapon.resize((312,167)),(442,31))
        self.background.alpha_composite(self.const.resize((282,281)),(444,218))
        self.background.alpha_composite(self.sets.resize((299,164)),(1604,534))
        
        position = [
            (305,523),
            (38,559),
            (158,559),
            (452,559),
            (599,559),
        ]
        
        for i, key in enumerate(self.skills):
            self.background.alpha_composite(key, position[i])
        
        position_x = 1223
        position_y = 29
        
        for i, key in enumerate(self.echo):
            self.background.alpha_composite(key, (position_x, position_y))
            
            position_x += 364
            if i in [1,3]:
                position_x = 1223
                position_y += 235
                
        