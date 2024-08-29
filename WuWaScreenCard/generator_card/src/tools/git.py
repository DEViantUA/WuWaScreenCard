# Copyright 2024 DEViantUa <t.me/deviant_ua>
# All rights reserved.

from PIL import Image
import os
import threading
from pathlib import Path
from io import BytesIO

from .http import AioSession
from .cache import Cache

lock = threading.Lock()

_caches = Cache.get_cache()

assets = Path(__file__).parent.parent / 'assets'

_BASE_URL = 'https://raw.githubusercontent.com/DEViantUA/StarRailCardData/main/asset/'


total_style = {
    "stats": "mask/stats.png",
    "weapon": "mask/weapon.png",
    "weapon_icon": "mask/weapon_icon.png",
    "const": "mask/const.png",
    "echo": "mask/echo.png",
    "echo_icon": "mask/echo_icon.png",
    "sets": "mask/sets.png",
    "skills": "mask/skills.png",
    "uid": "mask/uid.png",
    "background_mask": "background/maska.png",
}


card_style = {
    "background": "background/background.png",
    "light": "background/light.png",
    "pixel": "background/pixel.png",
    "none_weapon": "weapon/none_weapon.png",
    "constant_shadow": "constant/shadow.png",
    "skill_background": "skill/background.png",
    "echo_zero": "echo/zero.png",
    "background_echo": "echo/background.png",
    "zero_stat_icon": "echo/zero_stat_icon.png",
    "icon_0": "echo/icon_0.png",
    "icon_5": "echo/icon_5.png",
    "icon_10": "echo/icon_10.png",
    "icon_15": "echo/icon_15.png",
    "icon_20": "echo/icon_20.png",
    "icon_25": "echo/icon_25.png",
    
    
}


class ImageCache:
    
    _assets_download = False
    _mapping = {}
    _monitor_size = None
            
    @classmethod
    async def set_assets_download(cls, download = False):
        cls._assets_download = download
    
    @classmethod
    def set_mapping(cls,style):
        cls._mapping = card_style
        
    @classmethod
    async def _load_image(cls, name):
        
        try:
            image = _caches[name]
        except KeyError:
            try:
                _caches[name] = image = Image.open(assets / name)
                return _caches[name]
            except Exception as e:
                pass
        
        try:
            _caches[name] = image = Image.open(assets / name)
            return _caches[name]
        except Exception as e:
            pass
        
        url = _BASE_URL + name
        if url in _caches:
            return _caches[name]
        else:
            image_data = await AioSession.get(url, response_format= "bytes")
            image = Image.open(BytesIO(image_data))
            _caches[name] = image
        
        if cls._assets_download:
            file_path = assets / name
            file_path.parent.mkdir(parents=True, exist_ok=True)
            image.save(str(assets / name))
        
        return image

    async def __getattr__(cls, name):
        if name in cls._mapping:
            return await cls._load_image(cls._mapping[name])
        else:
            if name in total_style:
                return await cls._load_image(total_style[name]) 
            else:
                raise AttributeError(f"'{cls.__class__.__name__}' object has no attribute '{name}'")
        
    async def download_icon_stats(self, prop_id):
        if 'icon_stats' in self.mapping:
            url = self.mapping['icon_stats'].format(prop_id=prop_id)
            full_url = _BASE_URL + url
            if full_url in _caches:
                return _caches[full_url].copy()
            else:
                image_data = await self.download_image(full_url)
                image = Image.open(image_data)
                _caches[full_url] = image
                return image.copy()
        else:
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute 'icon_stats'")

    async def download_icon_constant(self, element, unlock, resizes = None):
        if 'icon_const_unlock' in self.mapping and "icon_const_lock" in self.mapping:
            if unlock:
                url = self.mapping['icon_const_unlock'].format(element=element.upper())
            else:
                url = self.mapping['icon_const_lock'].format(element=element.upper())
            full_url = _BASE_URL + url
            key = (full_url, resizes, unlock)
            if key in _caches:
                return _caches[key].copy()
            else:
                image_data = await self.download_image(full_url)
                image = Image.open(image_data)
                if not resizes is None:
                    image = image.resize(resizes)
                    
                _caches[full_url] = image
                return image.copy()
        else:
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute 'icon_stats'")