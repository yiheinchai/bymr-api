from dataclasses import dataclass
from enum import Enum
from typing import Optional
from functools import partial
from typing import Callable, Optional, cast


class TowerType(Enum):
    CATAPULT = 51
    SIMPLE_SIGN = 52
    RADIO = 113
    MONSTER_CAGE = 114
    MONSTER_LAB = 116
    HEAVY_TRAP = 117
    CHAMPION_CHAMBER = 119
    BIG_GULP = 120
    WMI_TOTEM = 121
    INFERNO_ENTRANCE = 127
    QUAKE_TOWER = 129
    MAGMA_TOWER = 132
    SIEGE_FACTORY = 133
    SIEGE_WORKS = 134
    DAVE_TROPHY = 135
    SPURTZ_CANNON = 136
    BLACK_SPURTZ_CANNON = 137
    STRONGHOLD = 138
    RESOURCE_OUTPOST = 139
    OUTPOST_DEFENDER = 140
    MONSTER_ACADEMY = 26
    BOOBYTRAP = 24
    TROJAN_HORSE = 27
    TWIGSNAPPER = 1
    PEBBLESHINER = 2
    PUTTYSQUISHER = 3
    GOOFACTORY = 4
    RAILGUN_TOWER = 118
    FLAK_TOWER = 115
    LASER_TOWER = 23
    TESLA_TOWER = 25
    SNIPER_TOWER = 21
    OUTPOST_HALL = 112
    TOWN_HALL = 14
    MAPROOM = 11
    GENERAL_STORE = 12


MAX_LEVELS_BASE = {
    TowerType.TWIGSNAPPER: 10,
    TowerType.PEBBLESHINER: 10,
    TowerType.PUTTYSQUISHER: 10,
    TowerType.GOOFACTORY: 10,
    TowerType.RAILGUN_TOWER: 8,
    TowerType.LASER_TOWER: 8,
    TowerType.FLAK_TOWER: 8,
    TowerType.SNIPER_TOWER: 8,
    TowerType.TESLA_TOWER: 8,
}

MAX_LEVELS_FORTS = {
    TowerType.TWIGSNAPPER: 10,
    TowerType.PEBBLESHINER: 10,
    TowerType.PUTTYSQUISHER: 10,
    TowerType.GOOFACTORY: 10,
    TowerType.RAILGUN_TOWER: 6,
    TowerType.LASER_TOWER: 6,
    TowerType.FLAK_TOWER: 6,
    TowerType.SNIPER_TOWER: 8,
    TowerType.TESLA_TOWER: 6,
}


class Tower:
    tower_type: TowerType
    level: Optional[int]
    fort: Optional[int]

    def __init__(self, tower_type: TowerType, level: int, fort: int = None):
        self.tower_type = tower_type
        self.level = level
        self.fort = fort


class TwigSnapper(Tower):
    def __init__(self, level: int = None):
        super().__init__(TowerType.TWIGSNAPPER, level)


class PebbleShiner(Tower):
    def __init__(self, level: int = None):
        super().__init__(TowerType.PEBBLESHINER, level)


class PuttySquisher(Tower):
    def __init__(self, level: int = None):
        super().__init__(TowerType.PUTTYSQUISHER, level)


class GooFactory(Tower):
    def __init__(self, level: int = None):
        super().__init__(TowerType.GOOFACTORY, level)


class RailgunTower(Tower):
    def __init__(self, level: int = None, fort: int = 4):
        super().__init__(TowerType.RAILGUN_TOWER, level, fort)


class LaserTower(Tower):
    def __init__(self, level: int = None, fort: int = 4):
        super().__init__(TowerType.LASER_TOWER, level, fort)


class FlakTower(Tower):
    def __init__(self, level: int = None, fort: int = 4):
        super().__init__(TowerType.FLAK_TOWER, level, fort)


class SniperTower(Tower):
    def __init__(self, level: int = None, fort: int = 4):
        super().__init__(TowerType.SNIPER_TOWER, level, fort)


class TeslaTower(Tower):
    def __init__(self, level: int = None, fort: int = 4):
        super().__init__(TowerType.TESLA_TOWER, level, fort)


class TowerSltr:
    LaserTower = LaserTower
    RailgunTower = RailgunTower
    GooFactory = GooFactory
    PuttySquisher = PuttySquisher
    PebbleShiner = PebbleShiner
    TwigSnapper = TwigSnapper
    FlakTower = FlakTower
    SniperTower = SniperTower
    TeslaTower = TeslaTower


class TemplateMode(Enum):
    BASE = "Base"
    FORT = "Fort"


class Template:
    template: dict
    twr = TowerType
    towers = TowerSltr
    mode = TemplateMode.BASE.value

    def set_mode(self, mode: TemplateMode):
        self.mode = mode
        return self

    def set_tower_level(self, tower_type: TowerType, level: int):
        for key in self.template:
            if self.template[key].get("t") == tower_type.value:
                self.template[key]["l"] = level
        return self

    def set_fort_lvl(self, lvl):
        for key in self.template:
            if "fort" in self.template[key]:
                self.template[key]["fort"] = lvl
        return self

    def add_tower(self, x: int, y: int, tower: Tower):
        last_idx = max(map(lambda k: int(k), self.template.keys()))
        self.template[str(last_idx + 1)] = {
            "X": x,
            "l": tower.level,
            "Y": y,
            "fort": tower.fort,
            "t": tower.tower_type.value,
            "id": last_idx + 1,
        }
        return self

    def add_tesla(self, x, y):
        # reference of adding 1 tesla tower
        # "177": {"X": -500, "l": 8, "Y": 330, "fort": 4, "t": 25, "id": 177},

        last_idx = max(map(lambda k: int(k), self.template.keys()))
        self.template[str(last_idx + 1)] = {
            "X": x,
            "l": 8,
            "Y": y,
            "fort": 4,
            "t": 25,
            "id": last_idx + 1,
        }
        return self

    def to_dict(self):
        return self.template


class UltraTemplate(Template):

    def __init__(self):
        super().__init__()

        self.template = {
            "0": {"X": 0, "fort": 4, "t": 112, "Y": -50, "id": 0},
            "2": {"l": 5, "X": 130, "t": 17, "Y": 60, "id": 2},
            "3": {"l": 5, "X": 130, "t": 17, "Y": 40, "id": 3},
            "4": {"l": 5, "X": 130, "t": 17, "Y": 20, "id": 4},
            "5": {"l": 5, "X": 130, "t": 17, "Y": 0, "id": 5},
            "6": {"l": 5, "X": 130, "t": 17, "Y": -20, "id": 6},
            "7": {"l": 5, "X": 150, "t": 17, "Y": 60, "id": 7},
            "8": {"l": 5, "X": 170, "t": 17, "Y": 60, "id": 8},
            "9": {"l": 5, "X": 190, "t": 17, "Y": 60, "id": 9},
            "10": {"X": 150, "fort": 3, "l": 5, "Y": 80, "t": 115, "id": 10},
            "12": {"l": 5, "X": 130, "t": 17, "Y": 100, "id": 12},
            "13": {"l": 5, "X": 130, "t": 17, "Y": 120, "id": 13},
            "14": {"l": 5, "X": 210, "t": 17, "Y": 60, "id": 14},
            "15": {"l": 5, "X": 130, "t": 17, "Y": 140, "id": 15},
            "16": {"l": 5, "X": 230, "t": 17, "Y": 60, "id": 16},
            "17": {"l": 5, "X": 230, "t": 17, "Y": 80, "id": 17},
            "18": {"l": 5, "X": 230, "t": 17, "Y": 100, "id": 18},
            "19": {"l": 5, "X": 230, "t": 17, "Y": 120, "id": 19},
            "20": {"l": 5, "X": 230, "t": 17, "Y": 140, "id": 20},
            "21": {"l": 5, "X": 290, "t": 17, "Y": 60, "id": 21},
            "22": {"l": 5, "X": 210, "t": 17, "Y": 150, "id": 22},
            "23": {"l": 5, "X": 190, "t": 17, "Y": 150, "id": 23},
            "24": {"l": 5, "X": 170, "t": 17, "Y": 150, "id": 24},
            "25": {"l": 5, "X": 150, "t": 17, "Y": 150, "id": 25},
            "26": {"l": 5, "X": 310, "t": 17, "Y": 50, "id": 26},
            "27": {"l": 5, "X": -20, "t": 17, "Y": -50, "id": 27},
            "28": {"l": 5, "X": -20, "t": 17, "Y": -30, "id": 28},
            "29": {"l": 5, "X": -20, "t": 17, "Y": -10, "id": 29},
            "30": {"l": 5, "X": -20, "t": 17, "Y": 10, "id": 30},
            "31": {"l": 5, "X": -20, "t": 17, "Y": 30, "id": 31},
            "32": {"l": 5, "X": -40, "t": 17, "Y": -50, "id": 32},
            "33": {"l": 5, "X": -60, "t": 17, "Y": -50, "id": 33},
            "34": {"l": 5, "X": -80, "t": 17, "Y": -50, "id": 34},
            "35": {"l": 5, "X": -100, "t": 17, "Y": -50, "id": 35},
            "36": {"l": 5, "X": -120, "t": 17, "Y": -50, "id": 36},
            "37": {"l": 5, "X": -120, "t": 17, "Y": -70, "id": 37},
            "38": {"l": 5, "X": -120, "t": 17, "Y": -90, "id": 38},
            "39": {"l": 5, "X": -120, "t": 17, "Y": -110, "id": 39},
            "40": {"l": 5, "X": -120, "t": 17, "Y": -130, "id": 40},
            "41": {"X": -100, "fort": 3, "l": 5, "Y": -120, "t": 115, "id": 41},
            "42": {"l": 5, "X": -200, "t": 17, "Y": -20, "id": 42},
            "43": {"l": 5, "X": -100, "t": 17, "Y": -140, "id": 43},
            "44": {"l": 5, "X": -80, "t": 17, "Y": -140, "id": 44},
            "45": {"l": 5, "X": -60, "t": 17, "Y": -140, "id": 45},
            "46": {"l": 5, "X": -40, "t": 17, "Y": -140, "id": 46},
            "47": {"l": 5, "X": -200, "t": 17, "Y": 0, "id": 47},
            "48": {"l": 5, "X": -20, "t": 17, "Y": -130, "id": 48},
            "49": {"l": 5, "X": -20, "t": 17, "Y": -110, "id": 49},
            "50": {"l": 5, "X": -20, "t": 17, "Y": -90, "id": 50},
            "51": {"X": -20, "t": 117, "Y": -70, "id": 51},
            "52": {"X": 60, "fort": 2, "l": 3, "Y": 80, "t": 23, "id": 52},
            "53": {"X": 0, "fort": 2, "l": 3, "Y": -120, "t": 118, "id": 53},
            "54": {"l": 5, "X": 40, "t": 17, "Y": 100, "id": 54},
            "55": {"X": 40, "t": 24, "Y": 80, "id": 55},
            "56": {"X": 70, "t": 24, "Y": -70, "id": 56},
            "57": {"X": 20, "t": 117, "Y": 80, "id": 57},
            "58": {"X": 90, "t": 117, "Y": -70, "id": 58},
            "59": {"l": 6, "X": -430, "t": 15, "Y": 60, "id": 59},
            "60": {"l": 3, "X": 130, "t": 22, "Y": -130, "id": 60},
            "61": {"l": 3, "X": -90, "t": 22, "Y": 70, "id": 61},
            "62": {"X": -90, "fort": 2, "l": 3, "Y": -30, "t": 25, "id": 62},
            "63": {"X": -20, "t": 117, "Y": 50, "id": 63},
            "64": {"X": -40, "t": 24, "Y": 40, "id": 64},
            "65": {"X": -60, "t": 24, "Y": 40, "id": 65},
            "66": {"X": 130, "t": 24, "Y": -40, "id": 66},
            "67": {"X": 150, "t": 24, "Y": -30, "id": 67},
            "69": {"X": 170, "t": 24, "Y": -30, "id": 69},
            "70": {"l": 5, "X": 70, "t": 17, "Y": -90, "id": 70},
            "71": {"l": 5, "X": 70, "t": 17, "Y": -110, "id": 71},
            "72": {"l": 5, "X": 70, "t": 17, "Y": -130, "id": 72},
            "73": {"l": 5, "X": 70, "t": 17, "Y": -150, "id": 73},
            "74": {"l": 5, "X": 50, "t": 17, "Y": -140, "id": 74},
            "75": {"l": 5, "X": 30, "t": 17, "Y": -140, "id": 75},
            "76": {"l": 5, "X": 70, "t": 17, "Y": -170, "id": 76},
            "77": {"l": 5, "X": 70, "t": 17, "Y": -190, "id": 77},
            "78": {"l": 5, "X": 70, "t": 17, "Y": -210, "id": 78},
            "79": {"X": 110, "fort": 1, "l": 8, "Y": -220, "t": 21, "id": 79},
            "80": {"l": 5, "X": 110, "t": 17, "Y": -150, "id": 80},
            "81": {"l": 5, "X": 130, "t": 17, "Y": -150, "id": 81},
            "82": {"l": 5, "X": 150, "t": 17, "Y": -150, "id": 82},
            "83": {"l": 5, "X": 110, "t": 17, "Y": -130, "id": 83},
            "84": {"l": 5, "X": 40, "t": 17, "Y": 120, "id": 84},
            "85": {"l": 5, "X": 40, "t": 17, "Y": 140, "id": 85},
            "86": {"l": 5, "X": 60, "t": 17, "Y": 150, "id": 86},
            "87": {"l": 5, "X": 80, "t": 17, "Y": 150, "id": 87},
            "88": {"l": 5, "X": 40, "t": 17, "Y": 160, "id": 88},
            "89": {"l": 5, "X": 40, "t": 17, "Y": 180, "id": 89},
            "90": {"l": 5, "X": 40, "t": 17, "Y": 200, "id": 90},
            "91": {"l": 5, "X": 40, "t": 17, "Y": 220, "id": 91},
            "92": {"X": 0, "fort": 1, "l": 8, "Y": -210, "t": 20, "id": 92},
            "93": {"X": 60, "fort": 1, "l": 8, "Y": 170, "t": 20, "id": 93},
            "94": {"l": 5, "X": 250, "t": 17, "Y": 60, "id": 94},
            "95": {"l": 5, "X": 270, "t": 17, "Y": 60, "id": 95},
            "96": {"l": 5, "X": 220, "t": 17, "Y": 20, "id": 96},
            "97": {"X": 220, "t": 24, "Y": 40, "id": 97},
            "98": {"l": 5, "X": -140, "t": 17, "Y": -50, "id": 98},
            "99": {"l": 5, "X": -160, "t": 17, "Y": -50, "id": 99},
            "100": {"l": 5, "X": -110, "t": 17, "Y": -10, "id": 100},
            "101": {"X": -110, "t": 24, "Y": -30, "id": 101},
            "102": {"l": 5, "X": 220, "t": 17, "Y": 0, "id": 102},
            "103": {"l": 5, "X": 220, "t": 17, "Y": -20, "id": 103},
            "104": {"l": 5, "X": 220, "t": 17, "Y": -40, "id": 104},
            "105": {"X": 220, "fort": 1, "l": 8, "Y": -110, "t": 21, "id": 105},
            "106": {"X": -160, "fort": 1, "l": 8, "Y": 70, "t": 21, "id": 106},
            "107": {"l": 5, "X": -110, "t": 17, "Y": 10, "id": 107},
            "108": {"l": 5, "X": -110, "t": 17, "Y": 30, "id": 108},
            "109": {"l": 5, "X": -110, "t": 17, "Y": 50, "id": 109},
            "110": {"l": 5, "X": -130, "t": 17, "Y": 50, "id": 110},
            "111": {"l": 5, "X": -150, "t": 17, "Y": 50, "id": 111},
            "112": {"l": 5, "X": -170, "t": 17, "Y": 50, "id": 112},
            "113": {"X": -180, "fort": 2, "l": 3, "Y": -20, "t": 23, "id": 113},
            "114": {"l": 5, "X": 240, "t": 17, "Y": -40, "id": 114},
            "115": {"l": 5, "X": 260, "t": 17, "Y": -40, "id": 115},
            "116": {"l": 5, "X": 280, "t": 17, "Y": -40, "id": 116},
            "117": {"l": 5, "X": 0, "t": 17, "Y": 140, "id": 117},
            "118": {"l": 5, "X": 0, "t": 17, "Y": 160, "id": 118},
            "119": {"l": 5, "X": -20, "t": 17, "Y": 160, "id": 119},
            "120": {"l": 5, "X": -40, "t": 17, "Y": 160, "id": 120},
            "121": {"X": -190, "fort": 1, "l": 8, "Y": -120, "t": 20, "id": 121},
            "122": {"X": 0, "t": 24, "Y": -140, "id": 122},
            "123": {"X": -20, "t": 24, "Y": -150, "id": 123},
            "124": {"X": 240, "fort": 1, "l": 8, "Y": -20, "t": 20, "id": 124},
            "125": {"X": -30, "fort": 1, "l": 8, "Y": 180, "t": 21, "id": 125},
            "126": {"l": 5, "X": 300, "t": 17, "Y": -40, "id": 126},
            "127": {"l": 5, "X": 290, "t": 17, "Y": -60, "id": 127},
            "128": {"l": 5, "X": 290, "t": 17, "Y": -80, "id": 128},
            "129": {"l": 5, "X": -180, "t": 17, "Y": 70, "id": 129},
            "130": {"l": 5, "X": -190, "t": 17, "Y": 50, "id": 130},
            "131": {"X": 20, "t": 24, "Y": 160, "id": 131},
            "132": {"X": 20, "t": 24, "Y": 140, "id": 132},
            "133": {"X": 90, "t": 24, "Y": -150, "id": 133},
            "134": {"X": 90, "t": 24, "Y": -130, "id": 134},
            "135": {"l": 5, "X": 310, "t": 17, "Y": 10, "id": 135},
            "136": {"l": 5, "X": 310, "t": 17, "Y": 30, "id": 136},
            "137": {"l": 5, "X": -180, "t": 17, "Y": -50, "id": 137},
            "138": {"l": 5, "X": -180, "t": 17, "Y": 90, "id": 138},
            "139": {"l": 5, "X": -200, "t": 17, "Y": -40, "id": 139},
            "140": {"X": -200, "t": 24, "Y": 20, "id": 140},
            "143": {"X": -110, "t": 24, "Y": 140, "id": 143},
            "144": {"X": 190, "t": 24, "Y": -150, "id": 144},
            "145": {"X": 220, "t": 24, "Y": -130, "id": 145},
            "146": {"X": 0, "t": 24, "Y": 80, "id": 146},
            "147": {"X": 0, "t": 24, "Y": 100, "id": 147},
            "148": {"X": 110, "t": 24, "Y": -70, "id": 148},
            "149": {"X": 190, "t": 24, "Y": -30, "id": 149},
            "150": {"X": 100, "t": 24, "Y": 150, "id": 150},
            "151": {"X": -90, "t": 24, "Y": 160, "id": 151},
            "152": {"X": 150, "fort": 2, "l": 3, "Y": -10, "t": 25, "id": 152},
            "153": {"X": -110, "t": 9, "Y": -360, "id": 153},
            "154": {"l": 3, "X": 30, "t": 13, "Y": -370, "id": 154},
            "155": {"rCP": 1, "X": 250, "l": 8, "Y": -180, "t": 1, "id": 155},
            "156": {"rCP": 7, "X": 180, "l": 8, "Y": -220, "t": 2, "id": 156},
            "157": {"rCP": 11, "X": 225, "l": 8, "Y": -335, "t": 3, "id": 157},
            "158": {"rCP": 7, "X": 365, "l": 8, "Y": 35, "t": 4, "id": 158},
            "159": {"l": 3, "X": 55, "t": 13, "Y": 290, "id": 159},
            "160": {"l": 4, "X": 230, "t": 5, "Y": 270, "id": 160},
            "161": {"rCP": 3, "X": -250, "l": 8, "Y": 80, "t": 1, "id": 161},
            "162": {"rCP": 4, "X": -180, "l": 8, "Y": 140, "t": 2, "id": 162},
            "163": {"rCP": 7, "X": -90, "l": 8, "Y": 300, "t": 3, "id": 163},
            "164": {"rCP": 2, "X": -225, "l": 8, "Y": 255, "t": 4, "id": 164},
            "165": {"X": 355, "t": 16, "Y": -125, "id": 165},
            "167": {"X": -400, "t": 10, "Y": -110, "id": 167},
            "168": {"rCP": 11, "X": -260, "l": 8, "Y": -150, "t": 1, "id": 168},
            "169": {"rCP": 6, "X": -190, "l": 8, "Y": -190, "t": 2, "id": 169},
            "170": {"rCP": 2, "X": -350, "l": 8, "Y": -260, "t": 3, "id": 170},
            "171": {"rCP": 3, "X": -240, "l": 8, "Y": -340, "t": 4, "id": 171},
            "172": {"rCP": 16, "X": 180, "l": 8, "Y": 170, "t": 2, "id": 172},
            "173": {"rCP": 16, "X": 250, "l": 8, "Y": 110, "t": 1, "id": 173},
            "174": {"rCP": 16, "X": 350, "l": 8, "Y": 155, "t": 3, "id": 174},
            "175": {"rCP": 5, "X": 345, "l": 8, "Y": -255, "t": 4, "id": 175},
            "176": {"X": 130, "t": 117, "Y": 80, "id": 176},
        }


class CheckersTemplate(Template):
    def __init__(self):
        super().__init__()

        self.template = {
            "0": {"X": 0, "fort": 4, "t": 112, "Y": -50, "id": 0},
            "1": {"l": 5, "X": 130, "t": 17, "Y": 60, "id": 1},
            "2": {"l": 5, "X": 130, "t": 17, "Y": 40, "id": 2},
            "3": {"l": 5, "X": 130, "t": 17, "Y": 20, "id": 3},
            "4": {"l": 5, "X": 130, "t": 17, "Y": 0, "id": 4},
            "5": {"l": 5, "X": 130, "t": 17, "Y": -20, "id": 5},
            "6": {"l": 5, "X": 150, "t": 17, "Y": 60, "id": 6},
            "7": {"l": 5, "X": 170, "t": 17, "Y": 60, "id": 7},
            "8": {"l": 5, "X": 190, "t": 17, "Y": 60, "id": 8},
            "9": {"X": 150, "l": 5, "Y": 80, "fort": 3, "t": 115, "id": 9},
            "10": {"l": 5, "X": 130, "t": 17, "Y": 100, "id": 10},
            "11": {"l": 5, "X": 130, "t": 17, "Y": 120, "id": 11},
            "12": {"l": 5, "X": 210, "t": 17, "Y": 60, "id": 12},
            "13": {"l": 5, "X": 130, "t": 17, "Y": 140, "id": 13},
            "14": {"l": 5, "X": 230, "t": 17, "Y": 60, "id": 14},
            "15": {"l": 5, "X": 230, "t": 17, "Y": 80, "id": 15},
            "16": {"l": 5, "X": 230, "t": 17, "Y": 100, "id": 16},
            "17": {"l": 5, "X": 230, "t": 17, "Y": 120, "id": 17},
            "18": {"l": 5, "X": 230, "t": 17, "Y": 140, "id": 18},
            "19": {"l": 5, "X": 290, "t": 17, "Y": 60, "id": 19},
            "20": {"l": 5, "X": 210, "t": 17, "Y": 150, "id": 20},
            "21": {"l": 5, "X": 190, "t": 17, "Y": 150, "id": 21},
            "22": {"l": 5, "X": 170, "t": 17, "Y": 150, "id": 22},
            "23": {"l": 5, "X": 150, "t": 17, "Y": 150, "id": 23},
            "24": {"l": 5, "X": 310, "t": 17, "Y": 50, "id": 24},
            "25": {"l": 5, "X": -20, "t": 17, "Y": -50, "id": 25},
            "26": {"l": 5, "X": -20, "t": 17, "Y": -30, "id": 26},
            "27": {"l": 5, "X": -20, "t": 17, "Y": -10, "id": 27},
            "28": {"l": 5, "X": -20, "t": 17, "Y": 10, "id": 28},
            "29": {"l": 5, "X": -20, "t": 17, "Y": 30, "id": 29},
            "30": {"l": 5, "X": -40, "t": 17, "Y": -50, "id": 30},
            "31": {"l": 5, "X": -60, "t": 17, "Y": -50, "id": 31},
            "32": {"l": 5, "X": -80, "t": 17, "Y": -50, "id": 32},
            "33": {"l": 5, "X": -100, "t": 17, "Y": -50, "id": 33},
            "34": {"l": 5, "X": -120, "t": 17, "Y": -50, "id": 34},
            "35": {"l": 5, "X": -120, "t": 17, "Y": -70, "id": 35},
            "36": {"l": 5, "X": -120, "t": 17, "Y": -90, "id": 36},
            "37": {"l": 5, "X": -120, "t": 17, "Y": -110, "id": 37},
            "38": {"l": 5, "X": 150, "t": 17, "Y": -5, "id": 38},
            "39": {"X": -100, "l": 5, "Y": -120, "fort": 3, "t": 115, "id": 39},
            "40": {"l": 5, "X": -200, "t": 17, "Y": -20, "id": 40},
            "41": {"l": 5, "X": 170, "t": 17, "Y": 40, "id": 41},
            "42": {"l": 5, "X": 150, "t": 17, "Y": 35, "id": 42},
            "43": {"l": 5, "X": 150, "t": 17, "Y": 15, "id": 43},
            "44": {"l": 5, "X": 170, "t": 17, "Y": -5, "id": 44},
            "45": {"l": 5, "X": -200, "t": 17, "Y": 0, "id": 45},
            "46": {"l": 5, "X": -20, "t": 17, "Y": -130, "id": 46},
            "47": {"l": 5, "X": -20, "t": 17, "Y": -110, "id": 47},
            "48": {"l": 5, "X": -20, "t": 17, "Y": -90, "id": 48},
            "49": {"X": -20, "t": 117, "Y": -70, "id": 49},
            "50": {"X": 60, "l": 3, "Y": 80, "fort": 2, "t": 23, "id": 50},
            "51": {"X": 0, "l": 3, "Y": -120, "fort": 2, "t": 118, "id": 51},
            "52": {"l": 5, "X": 40, "t": 17, "Y": 100, "id": 52},
            "53": {"X": 40, "t": 24, "Y": 80, "id": 53},
            "54": {"X": 70, "t": 24, "Y": -70, "id": 54},
            "55": {"X": 20, "t": 117, "Y": 80, "id": 55},
            "56": {"X": 90, "t": 117, "Y": -70, "id": 56},
            "57": {"l": 6, "X": 250, "t": 15, "Y": 80, "id": 57},
            "58": {"l": 3, "X": 130, "t": 22, "Y": -130, "id": 58},
            "59": {"l": 3, "X": -90, "t": 22, "Y": 70, "id": 59},
            "60": {"X": -90, "l": 3, "Y": -30, "fort": 2, "t": 25, "id": 60},
            "61": {"X": -20, "t": 117, "Y": 50, "id": 61},
            "62": {"X": -40, "t": 24, "Y": 40, "id": 62},
            "63": {"X": -60, "t": 24, "Y": 40, "id": 63},
            "64": {"X": 130, "t": 24, "Y": -40, "id": 64},
            "65": {"X": 150, "t": 24, "Y": -30, "id": 65},
            "66": {"X": 170, "t": 24, "Y": -30, "id": 66},
            "67": {"l": 5, "X": 70, "t": 17, "Y": -90, "id": 67},
            "68": {"l": 5, "X": 70, "t": 17, "Y": -110, "id": 68},
            "69": {"l": 5, "X": 70, "t": 17, "Y": -130, "id": 69},
            "70": {"l": 5, "X": 70, "t": 17, "Y": -150, "id": 70},
            "71": {"l": 5, "X": 50, "t": 17, "Y": -140, "id": 71},
            "72": {"l": 5, "X": 30, "t": 17, "Y": -140, "id": 72},
            "73": {"l": 5, "X": 70, "t": 17, "Y": -170, "id": 73},
            "74": {"l": 5, "X": 70, "t": 17, "Y": -190, "id": 74},
            "75": {"l": 5, "X": 70, "t": 17, "Y": -210, "id": 75},
            "76": {"X": 110, "l": 8, "Y": -220, "fort": 1, "t": 21, "id": 76},
            "77": {"l": 5, "X": 110, "t": 17, "Y": -150, "id": 77},
            "78": {"l": 5, "X": 130, "t": 17, "Y": -150, "id": 78},
            "79": {"l": 5, "X": 150, "t": 17, "Y": -150, "id": 79},
            "80": {"l": 5, "X": 110, "t": 17, "Y": -130, "id": 80},
            "81": {"l": 5, "X": 40, "t": 17, "Y": 120, "id": 81},
            "82": {"l": 5, "X": 40, "t": 17, "Y": 140, "id": 82},
            "83": {"l": 5, "X": 60, "t": 17, "Y": 150, "id": 83},
            "84": {"l": 5, "X": 80, "t": 17, "Y": 150, "id": 84},
            "85": {"l": 5, "X": 40, "t": 17, "Y": 160, "id": 85},
            "86": {"l": 5, "X": 40, "t": 17, "Y": 180, "id": 86},
            "87": {"l": 5, "X": 40, "t": 17, "Y": 200, "id": 87},
            "88": {"l": 5, "X": 40, "t": 17, "Y": 220, "id": 88},
            "89": {"X": 0, "l": 8, "Y": -210, "fort": 1, "t": 20, "id": 89},
            "90": {"X": 60, "l": 8, "Y": 170, "fort": 1, "t": 20, "id": 90},
            "91": {"l": 5, "X": 250, "t": 17, "Y": 60, "id": 91},
            "92": {"l": 5, "X": 270, "t": 17, "Y": 60, "id": 92},
            "93": {"l": 5, "X": 220, "t": 17, "Y": 20, "id": 93},
            "94": {"X": 220, "t": 24, "Y": 40, "id": 94},
            "95": {"l": 5, "X": -140, "t": 17, "Y": -50, "id": 95},
            "96": {"l": 5, "X": -160, "t": 17, "Y": -50, "id": 96},
            "97": {"l": 5, "X": -110, "t": 17, "Y": -10, "id": 97},
            "98": {"X": -110, "t": 24, "Y": -30, "id": 98},
            "99": {"l": 5, "X": 220, "t": 17, "Y": 0, "id": 99},
            "100": {"l": 5, "X": 220, "t": 17, "Y": -20, "id": 100},
            "101": {"l": 5, "X": 220, "t": 17, "Y": -40, "id": 101},
            "102": {"X": 220, "l": 8, "Y": -110, "fort": 1, "t": 21, "id": 102},
            "103": {"X": -160, "l": 8, "Y": 70, "fort": 1, "t": 21, "id": 103},
            "104": {"l": 5, "X": -110, "t": 17, "Y": 10, "id": 104},
            "105": {"l": 5, "X": -110, "t": 17, "Y": 30, "id": 105},
            "106": {"l": 5, "X": -110, "t": 17, "Y": 50, "id": 106},
            "107": {"l": 5, "X": -130, "t": 17, "Y": 50, "id": 107},
            "108": {"l": 5, "X": -150, "t": 17, "Y": 50, "id": 108},
            "109": {"l": 5, "X": -170, "t": 17, "Y": 50, "id": 109},
            "110": {"X": -180, "l": 3, "Y": -20, "fort": 2, "t": 23, "id": 110},
            "111": {"l": 5, "X": 240, "t": 17, "Y": -40, "id": 111},
            "112": {"l": 5, "X": 260, "t": 17, "Y": -40, "id": 112},
            "113": {"l": 5, "X": 280, "t": 17, "Y": -40, "id": 113},
            "114": {"l": 5, "X": 0, "t": 17, "Y": 140, "id": 114},
            "115": {"l": 5, "X": 0, "t": 17, "Y": 160, "id": 115},
            "116": {"l": 5, "X": -20, "t": 17, "Y": 160, "id": 116},
            "117": {"l": 5, "X": -40, "t": 17, "Y": 160, "id": 117},
            "118": {"X": -190, "l": 8, "Y": -120, "fort": 1, "t": 20, "id": 118},
            "119": {"X": 0, "t": 24, "Y": -140, "id": 119},
            "120": {"X": -20, "t": 24, "Y": -150, "id": 120},
            "121": {"X": 240, "l": 8, "Y": -20, "fort": 1, "t": 20, "id": 121},
            "122": {"X": -30, "l": 8, "Y": 180, "fort": 1, "t": 21, "id": 122},
            "123": {"l": 5, "X": 300, "t": 17, "Y": -40, "id": 123},
            "124": {"l": 5, "X": 290, "t": 17, "Y": -60, "id": 124},
            "125": {"l": 5, "X": 290, "t": 17, "Y": -80, "id": 125},
            "126": {"l": 5, "X": -180, "t": 17, "Y": 70, "id": 126},
            "127": {"l": 5, "X": -190, "t": 17, "Y": 50, "id": 127},
            "128": {"X": 20, "t": 24, "Y": 160, "id": 128},
            "129": {"X": 20, "t": 24, "Y": 140, "id": 129},
            "130": {"X": 90, "t": 24, "Y": -150, "id": 130},
            "131": {"X": 90, "t": 24, "Y": -130, "id": 131},
            "132": {"l": 5, "X": 310, "t": 17, "Y": 10, "id": 132},
            "133": {"l": 5, "X": 310, "t": 17, "Y": 30, "id": 133},
            "134": {"l": 5, "X": -180, "t": 17, "Y": -50, "id": 134},
            "135": {"l": 5, "X": -180, "t": 17, "Y": 90, "id": 135},
            "136": {"l": 5, "X": -200, "t": 17, "Y": -40, "id": 136},
            "137": {"X": -200, "t": 24, "Y": 20, "id": 137},
            "138": {"X": -110, "t": 24, "Y": 140, "id": 138},
            "139": {"X": 190, "t": 24, "Y": -150, "id": 139},
            "140": {"X": 170, "t": 24, "Y": -150, "id": 140},
            "141": {"X": 0, "t": 24, "Y": 80, "id": 141},
            "142": {"X": 0, "t": 24, "Y": 100, "id": 142},
            "143": {"X": 110, "t": 24, "Y": -70, "id": 143},
            "144": {"X": 190, "t": 24, "Y": -30, "id": 144},
            "145": {"X": 100, "t": 24, "Y": 150, "id": 145},
            "146": {"X": -90, "t": 24, "Y": 160, "id": 146},
            "147": {"X": 330, "t": 9, "Y": 0, "id": 147},
            "148": {"l": 3, "X": -220, "t": 13, "Y": -225, "id": 148},
            "149": {"l": 3, "X": -120, "t": 13, "Y": -225, "id": 150},
            "150": {"l": 4, "X": -220, "t": 5, "Y": 140, "id": 151},
            "151": {"X": 320, "t": 16, "Y": -105, "id": 152},
            "152": {"X": 220, "t": 10, "Y": -210, "id": 153},
            "153": {"X": 130, "t": 117, "Y": 80, "id": 154},
        }

        # self.add_unbounded_checkers()

    def add_checkers(self):
        # "170": {"X": -500, "l": 3, "Y": 330, "fort": 4, "t": 25, "id": 170},
        # "171": {"X": -500, "l": 3, "Y": 260, "fort": 4, "t": 25, "id": 171},
        # --- CONFIGURATION ---
        tesla_size = 70
        last_idx = max(map(lambda k: int(k), self.template.keys()))

        towers = [
            TowerType.TESLA_TOWER.value,
            TowerType.FLAK_TOWER.value,
            TowerType.RAILGUN_TOWER.value,
        ]

        y_max = 400
        y_bottom_limit = -400  # The absolute bottom line of the map
        x_min = -500
        x_right_wall = 410

        y_grid = list(range(y_max, y_bottom_limit, -tesla_size))

        x_left_block_end = x_min + (4 * tesla_size)

        for i in range(4):
            x = x_min + (i * tesla_size)
            for y in y_grid[1:]:  # Skip first row (top)
                last_idx += 1
                self.template[str(last_idx)] = {
                    "X": x,
                    "l": 3,
                    "Y": y,
                    "fort": 4,
                    "t": towers[(last_idx) % len(towers)],
                    "id": last_idx,
                }

        top_rows = [y_grid[1], y_grid[2]]  # Shifted down by 70px (330, 260)
        bottom_rows = [y_grid[-1], y_grid[-2]]  # The bottom two (-370, -300)

        for x in range(x_left_block_end, x_right_wall, tesla_size):

            for y in top_rows:
                last_idx += 1
                self.template[str(last_idx)] = {
                    "X": x,
                    "l": 3,
                    "Y": y,
                    "fort": 4,
                    "t": towers[(last_idx) % len(towers)],
                    "id": last_idx,
                }

            for y in bottom_rows:
                last_idx += 1
                self.template[str(last_idx)] = {
                    "X": x,
                    "l": 3,
                    "Y": y,
                    "fort": 4,
                    "t": towers[(last_idx) % len(towers)],
                    "id": last_idx,
                }

        for y in y_grid[1:]:  # Skip first row (top)
            last_idx += 1
            self.template[str(last_idx)] = {
                "X": x_right_wall,
                "l": 3,
                "Y": y,
                "fort": 4,
                "t": towers[(last_idx) % len(towers)],
                "id": last_idx,
            }
        return self

    def add_patch(self, towers: list[Tower], bounds=tuple[int, int, int, int]):
        patch_size = 70
        last_idx = max(map(lambda k: int(k), self.template.keys()))

        x_start, x_end = bounds[0], bounds[1]
        y_start, y_end = bounds[2], bounds[3]

        for x in range(x_start, x_end, patch_size):
            for y in range(y_start, y_end, patch_size):
                last_idx += 1

                tower = towers[(last_idx) % len(towers)]

                tower_dict = {
                    "X": x,
                    "Y": y,
                    "t": tower.tower_type.value,
                    "id": last_idx,
                }

                if tower.level is not None:
                    tower_dict["l"] = tower.level
                else:
                    # get the max level
                    if self.mode == TemplateMode.BASE:
                        tower_dict["l"] = MAX_LEVELS_BASE.get(tower.tower_type, 1)
                    else:
                        tower_dict["l"] = MAX_LEVELS_FORTS.get(tower.tower_type, 1)

                if tower.fort is not None:
                    tower_dict["fort"] = tower.fort
                self.template[str(last_idx)] = tower_dict
        return self

    def add_farming_patch(self, level: int = 3, bounds: tuple = (-1500, -1000, -1500, -1000)):
        patch_size = 70
        last_idx = max(map(lambda k: int(k), self.template.keys()))
        towers = [
            TowerType.PEBBLESHINER.value,
            TowerType.TWIGSNAPPER.value,
            TowerType.GOOFACTORY.value,
            TowerType.PUTTYSQUISHER.value,
        ]

        x_start, x_end = bounds[0], bounds[1]
        y_start, y_end = bounds[2], bounds[3]

        for x in range(x_start, x_end, patch_size):
            for y in range(y_start, y_end, patch_size):
                last_idx += 1

                self.template[str(last_idx)] = {
                    "X": x,
                    "l": level,
                    "Y": y,
                    "t": towers[(last_idx) % len(towers)],
                    "id": last_idx,
                }
        return self

    def add_unbounded_checkers(self):

        tesla_size = 70
        last_idx = max(map(lambda k: int(k), self.template.keys()))
        towers = [
            TowerType.TESLA_TOWER.value,
            TowerType.FLAK_TOWER.value,
            TowerType.RAILGUN_TOWER.value,
        ]

        x_min, x_max, y_min, y_max = -1000, -500, -400, 1000
        for x in range(x_min, -150 - tesla_size, tesla_size):
            for y in range(y_max - tesla_size, y_min + 1, -tesla_size):
                last_idx += 1

                self.template[str(last_idx)] = {
                    "X": x,
                    "l": 3,
                    "Y": y,
                    "fort": 4,
                    "t": towers[(last_idx) % len(towers)],
                    "id": last_idx,
                }
        return self

    def toggle_town_hall(self):
        for key in self.template:
            if self.template[key]["t"] == self.twr.OUTPOST_HALL.value:  # Town Hall type
                self.template[key]["t"] = self.twr.TOWN_HALL.value
                self.template[key]["fort"] = 4
                self.template[key]["l"] = 10

        self.add_tower(-600, -600, self.twr.MAPROOM.value)
        self.add_tower(-700, -600, self.twr.GENERAL_STORE.value)

        return self


class NoobTemplate(Template):
    def __init__(self):
        super().__init__()

        self.template = {
            "0": {"X": -70, "Y": 0, "t": 14, "id": 0},
            "1": {"X": 60, "Y": 0, "t": 1, "cP": 5, "id": 1, "pr": 1, "st": 0, "rCP": 5},
            "2": {"X": 60, "Y": 70, "t": 2, "cP": 5, "id": 2, "pr": 1, "st": 0, "rCP": 5},
            "3": {"X": 60, "Y": -70, "t": 12, "id": 3},
            "25": {"X": -10, "Y": -70, "t": 21, "id": 25},
            "26": {"X": -170, "Y": -170, "t": 15, "id": 26},
            "27": {"X": -35, "Y": 135, "t": 5, "id": 27},
            "28": {"X": 60, "Y": 140, "t": 11, "id": 28},
            "29": {"X": -5, "Y": -195, "t": 13, "id": 29},
            "30": {"X": 140, "Y": 60, "t": 4, "cP": 10, "id": 30, "pr": 1, "st": 2, "rCP": 10},
        }
