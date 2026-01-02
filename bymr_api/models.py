"""Data models for the BYMR API SDK."""

from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any, Union
from enum import Enum


class BuildingType(Enum):
    """Building types in the game."""

    TOWN_HALL = 1
    RESOURCE_GENERATOR = 2
    DEFENSE = 3
    STORAGE = 4


# Add more as needed
@dataclass
class Building:
    """Represents a building in the game."""

    id: int
    t: int  # type
    X: int  # X coordinate
    Y: int  # Y coordinate
    l: Optional[int] = None  # level
    st: Optional[int] = None  # status/state
    cP: Optional[int] = None  # current production
    rCP: Optional[int] = None  # resource current production
    pr: Optional[int] = None  # production rate
    cU: Optional[int] = None  # current upgrade
    rPS: Optional[int] = None  # resource production something
    mq: Optional[List] = None  # message queue?
    rIP: Optional[str] = None  # resource input?
    upl: Optional[int] = None  # upgrade level? (adjusted to int based on data)
    upg: Optional[str] = None  # resource input?
    cB: Optional[str] = None
    fz: Optional[str] = None
    fort: Optional[int] = None  # fortification level

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format expected by API."""
        result = {
            "id": self.id,
            "t": self.t,
            "X": self.X,
            "Y": self.Y,
        }
        if self.l is not None:
            result["l"] = self.l
        if self.st is not None:
            result["st"] = self.st
        if self.cP is not None:
            result["cP"] = self.cP
        if self.rCP is not None:
            result["rCP"] = self.rCP
        if self.pr is not None:
            result["pr"] = self.pr
        if self.cU is not None:
            result["cU"] = self.cU
        if self.rPS is not None:
            result["rPS"] = self.rPS
        if self.mq is not None:
            result["mq"] = self.mq
        if self.rIP is not None:
            result["rIP"] = self.rIP
        if self.upl is not None:
            result["upl"] = self.upl
        if self.upg is not None:
            result["upg"] = self.upg
        if self.cB is not None:
            result["cB"] = self.cB
        if self.fz is not None:
            result["fz"] = self.fz

        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Building":
        """Create from dictionary."""
        return cls(
            id=data["id"],
            t=data["t"],
            X=data["X"],
            Y=data["Y"],
            l=data.get("l"),
            st=data.get("st"),
            cP=data.get("cP"),
            rCP=data.get("rCP"),
            pr=data.get("pr"),
            cU=data.get("cU"),
            rPS=data.get("rPS"),
            mq=data.get("mq"),
            rIP=data.get("rIP"),
            upl=data.get("upl"),
            upg=data.get("upg"),
            cB=data.get("cB"),
            fz=data.get("fz"),
        )


@dataclass
class BuildingData:
    """Collection of buildings."""

    buildings: Dict[str, Building] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Dict[str, Any]]:
        """Convert to dictionary format expected by API."""
        return {str(k): v.to_dict() for k, v in self.buildings.items()}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BuildingData":
        """Create from API response dictionary."""
        buildings = {}
        for key, building_data in data.items():
            buildings[key] = Building(**building_data)
        return cls(buildings=buildings)


@dataclass
class Resources:
    """Game resources."""

    r1: int = 0  # Resource type 1
    r2: int = 0  # Resource type 2
    r3: int = 0  # Resource type 3
    r4: int = 0  # Resource type 4
    r1max: int = 10000
    r2max: int = 10000
    r3max: int = 10000
    r4max: int = 10000

    def to_dict(self) -> Dict[str, int]:
        """Convert to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Resources":
        """Create from dictionary."""
        return cls(
            r1=data.get("r1", 0),
            r2=data.get("r2", 0),
            r3=data.get("r3", 0),
            r4=data.get("r4", 0),
            r1max=data.get("r1max", 10000),
            r2max=data.get("r2max", 10000),
            r3max=data.get("r3max", 10000),
            r4max=data.get("r4max", 10000),
        )


@dataclass
class AIAttacks:
    """AI attack data."""

    nextAttack: float
    sessionsSinceLastAttack: int
    lastattack: float
    attackPreference: int

    def to_dict(self) -> Dict[str, Union[float, int]]:
        """Convert to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AIAttacks":
        """Create from dictionary."""
        return cls(
            nextAttack=data.get("nextAttack", 0),
            sessionsSinceLastAttack=data.get("sessionsSinceLastAttack", 0),
            lastattack=data.get("lastattack", 0),
            attackPreference=data.get("attackPreference", 0),
        )


@dataclass
class BuildingResources:
    """Building resources data."""

    t: int  # timestamp

    def to_dict(self) -> Dict[str, int]:
        """Convert to dictionary."""
        return {"t": self.t}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BuildingResources":
        """Create from dictionary."""
        return cls(t=data.get("t", 0))


@dataclass
class Reward:
    """Reward data."""

    id: str

    def to_dict(self) -> Dict[str, str]:
        """Convert to dictionary."""
        return {"id": self.id}


@dataclass
class Achievement:
    """Achievement data."""

    completed: Dict[str, int] = field(default_factory=dict)  # c in API
    stats: Dict[str, Any] = field(default_factory=dict)  # s in API

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {"c": self.completed, "s": self.stats}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Achievement":
        """Create from dictionary."""
        return cls(
            completed=data.get("c", {}),
            stats=data.get("s", {}),
        )


@dataclass
class PopupData:
    """Popup data."""

    popupStates: Dict[str, Any] = field(default_factory=dict)
    lastDialog: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PopupData":
        """Create from dictionary."""
        return cls(
            popupStates=data.get("popupStates", {}),
            lastDialog=data.get("lastDialog", 0),
        )


@dataclass
class Stats:
    """Player statistics."""

    moga: int = 0
    mg: int = 0
    updateid_mr3: int = 0
    mob: int = 0
    updateid: int = 0
    inferno: int = 0
    updateid_mr2: int = 2
    mobg: int = 0
    mp: int = 0
    popupdata: PopupData = field(default_factory=PopupData)
    achievements: Achievement = field(default_factory=Achievement)
    other: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        result = asdict(self)
        result["popupdata"] = self.popupdata.to_dict()
        result["achievements"] = self.achievements.to_dict()
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Stats":
        """Create from dictionary."""
        return cls(
            moga=data.get("moga", 0),
            mg=data.get("mg", 0),
            updateid_mr3=data.get("updateid_mr3", 0),
            mob=data.get("mob", 0),
            updateid=data.get("updateid", 0),
            inferno=data.get("inferno", 0),
            updateid_mr2=data.get("updateid_mr2", 2),
            mobg=data.get("mobg", 0),
            mp=data.get("mp", 0),
            popupdata=PopupData.from_dict(data.get("popupdata", {})),
            achievements=Achievement.from_dict(data.get("achievements", {})),
            other=data.get("other", {}),
        )


@dataclass
class Locker:
    """Locker data."""

    t: int  # type

    def to_dict(self) -> Dict[str, int]:
        """Convert to dictionary."""
        return {"t": self.t}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Locker":
        """Create from dictionary."""
        return cls(t=data.get("t", 0))


@dataclass
class Academy:
    """Academy creature data."""

    level: int

    def to_dict(self) -> Dict[str, int]:
        """Convert to dictionary."""
        return {"level": self.level}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Academy":
        """Create from dictionary."""
        return cls(level=data.get("level", 1))


@dataclass
class Event:
    """Event data."""

    startDate: int = 0
    reward: Optional[Any] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {"startDate": self.startDate, "reward": self.reward}


@dataclass
class MonsterBaiter:
    """Monster baiter data."""

    musk: int = 0
    queue: Dict[str, Any] = field(default_factory=dict)
    attackDir: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MonsterBaiter":
        """Create from dictionary."""
        return cls(
            musk=data.get("musk", 0),
            queue=data.get("queue", {}),
            attackDir=data.get("attackDir", 0),
        )


@dataclass
class Mushroom:
    """Mushroom spawn data."""

    s: int  # spawn time
    l: List[List[int]] = field(default_factory=list)  # locations

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {"s": self.s, "l": self.l}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Mushroom":
        """Create from dictionary."""

        return cls(
            s=data.get("s", 0),
            l=data.get("l", []),
        )


@dataclass
class Monster:
    """Monster/creature data."""

    type: str
    level: int = 1

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {"type": self.type, "level": self.level}


@dataclass
class MonsterData:
    """Collection of monster data."""

    h: List[Any] = field(default_factory=list)  # housed monsters
    hcc: List[Any] = field(default_factory=list)  # housed creature count
    overdrivetime: int = 0
    space: int = 200
    saved: int = 0
    housed: Dict[str, int] = field(default_factory=dict)
    hstage: List[Any] = field(default_factory=list)
    hid: List[Any] = field(default_factory=list)
    finishtime: int = 0
    overdrivepower: int = 0
    hcount: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MonsterData":
        """Create from dictionary."""
        return cls(
            h=data.get("h", []),
            hcc=data.get("hcc", []),
            overdrivetime=data.get("overdrivetime", 0),
            space=data.get("space", 200),
            saved=data.get("saved", 0),
            housed=data.get("housed", {}),
            hstage=data.get("hstage", []),
            hid=data.get("hid", []),
            finishtime=data.get("finishtime", 0),
            overdrivepower=data.get("overdrivepower", 0),
            hcount=data.get("hcount", 0),
        )


@dataclass
class Quest:
    """Quest data."""

    quest_id: str
    status: int  # 1=active, 2=completed

    def to_dict(self) -> Dict[str, int]:
        """Convert to dictionary."""
        return {self.quest_id: self.status}


@dataclass
class UserData:
    version: int
    baseid: int
    type: str
    lastupdate: int

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format expected by API."""
        return {
            "version": self.version,
            "baseid": self.baseid,
            "type": self.type,
            "lastupdate": self.lastupdate,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> UserData:
        return cls(**data)


@dataclass
class BaseData:
    """Complete base save data."""

    version: int
    baseid: int
    basesaveid: int
    basename: str
    lastupdate: int = 0

    # Building and resources
    buildingdata: BuildingData = field(default_factory=BuildingData)
    buildinghealthdata: Dict[str, Any] = field(default_factory=dict)
    buildingresources: BuildingResources = field(default_factory=lambda: BuildingResources(t=0))
    resources: Resources = field(default_factory=Resources)

    # Combat and defense
    damage: int = 0
    flinger: int = 1
    catapult: int = 0
    aiattacks: AIAttacks = field(
        default_factory=lambda: AIAttacks(
            nextAttack=0, sessionsSinceLastAttack=0, lastattack=0, attackPreference=0
        )
    )
    siege: Optional[Any] = None
    attackersiege: Optional[Any] = None
    effects: List[List[Union[int, str]]] = field(default_factory=list)

    # Progress and stats
    tutorialstage: int = 0
    timeplayed: int = 0
    basevalue: int = 0
    empirevalue: int = 0
    points: int = 0
    baseseed: int = 0
    clienttime: int = 0

    # Research and rewards
    researchdata: Dict[str, int] = field(default_factory=dict)
    rewards: Dict[str, Dict[str, str]] = field(default_factory=dict)
    achieved: List[Any] = field(default_factory=list)

    # Stats and inventory
    stats: Stats = field(default_factory=Stats)
    inventory: Dict[str, Any] = field(default_factory=dict)
    lockerdata: Dict[str, Locker] = field(default_factory=dict)
    academy: Dict[str, Academy] = field(default_factory=dict)

    # Quests and events
    quests: Dict[str, int] = field(default_factory=dict)
    events: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    frontpage: Dict[str, Dict[str, str]] = field(default_factory=dict)

    # Monsters
    monsters: MonsterData = field(default_factory=MonsterData)
    monsterupdate: List[Any] = field(default_factory=list)
    monsterbaiter: MonsterBaiter = field(default_factory=MonsterBaiter)
    champion: List[Dict[str, Any]] = field(default_factory=list)

    # Environment
    mushrooms: Mushroom = field(default_factory=lambda: Mushroom(s=0, l=[]))

    # Additional fields from full save data
    empiredestroyed: int = 0
    worldid: str = ""
    event_score: int = 0
    chatenabled: int = 0
    relationship: int = 0
    healtime: int = 0
    over: int = 0
    protect: int = 0
    purchasecomplete: int = 0
    seed: int = 0
    bookmarked: int = 0
    fan: int = 0
    emailshared: int = 0
    unreadmessages: int = 0
    giftsentcount: int = 0
    canattack: bool = False
    fortifycellid: int = 0
    name: str = ""
    level: int = 1
    destroyed: int = 0
    locked: int = 0
    usemap: int = 1
    credits: int = 0
    iresources: Resources = field(default_factory=Resources)
    storedata: Dict[str, Any] = field(default_factory=dict)
    coords: Dict[str, Any] = field(default_factory=dict)
    player: Dict[str, Any] = field(default_factory=dict)
    krallen: Dict[str, Any] = field(default_factory=dict)
    loot: Dict[str, Any] = field(default_factory=dict)
    homebase: List[int] = field(default_factory=list)
    outposts: List[List[Any]] = field(default_factory=list)
    wmstatus: List[Any] = field(default_factory=list)
    chatservers: List[str] = field(default_factory=list)
    gifts: List[Any] = field(default_factory=list)
    sentinvites: List[Any] = field(default_factory=list)
    sentgifts: List[Any] = field(default_factory=list)
    fbpromos: List[Any] = field(default_factory=list)
    powerups: List[Any] = field(default_factory=list)
    attpowerups: List[Any] = field(default_factory=list)
    fbid: Optional[str] = None
    cantmovetill: Optional[int] = None
    attackreport: Optional[Any] = None
    buildingkeydata: Dict[str, Any] = field(default_factory=dict)
    attacks: List[Any] = field(default_factory=list)
    lootreport: Dict[str, Any] = field(default_factory=dict)
    attackloot: Dict[str, Any] = field(default_factory=dict)
    savetemplate: List[Any] = field(default_factory=list)
    updates: List[Any] = field(default_factory=list)
    createtime: int = 0
    savetime: int = 0
    id: int = 0
    baseid_inferno: int = 0
    wmid: int = 0
    type: str = "main"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format expected by API."""
        return {
            "version": self.version,
            "baseid": self.baseid,
            "basesaveid": self.basesaveid,
            "basename": self.basename,
            "lastupdate": self.lastupdate,
            "buildingdata": self.buildingdata.to_dict(),
            "buildinghealthdata": self.buildinghealthdata,
            "buildingresources": self.buildingresources.to_dict(),
            "resources": self.resources.to_dict(),
            "damage": self.damage,
            "flinger": self.flinger,
            "catapult": self.catapult,
            "aiattacks": self.aiattacks.to_dict(),
            "siege": self.siege,
            "attackersiege": self.attackersiege,
            "effects": self.effects,
            "tutorialstage": self.tutorialstage,
            "timeplayed": self.timeplayed,
            "basevalue": self.basevalue,
            "empirevalue": self.empirevalue,
            "points": self.points,
            "baseseed": self.baseseed,
            "clienttime": self.clienttime,
            "researchdata": self.researchdata,
            "rewards": self.rewards,
            "achieved": self.achieved,
            "stats": self.stats.to_dict(),
            "inventory": self.inventory,
            "lockerdata": {k: v.to_dict() for k, v in self.lockerdata.items()},
            "academy": {k: v.to_dict() for k, v in self.academy.items()},
            "quests": self.quests,
            "events": self.events,
            "frontpage": self.frontpage,
            "monsters": self.monsters.to_dict(),
            "monsterupdate": self.monsterupdate,
            "monsterbaiter": self.monsterbaiter.to_dict(),
            "champion": self.champion,
            "mushrooms": self.mushrooms.to_dict(),
            "empiredestroyed": self.empiredestroyed,
            "worldid": self.worldid,
            "event_score": self.event_score,
            "chatenabled": self.chatenabled,
            "relationship": self.relationship,
            "healtime": self.healtime,
            "over": self.over,
            "protect": self.protect,
            "purchasecomplete": self.purchasecomplete,
            "seed": self.seed,
            "bookmarked": self.bookmarked,
            "fan": self.fan,
            "emailshared": self.emailshared,
            "unreadmessages": self.unreadmessages,
            "giftsentcount": self.giftsentcount,
            "canattack": self.canattack,
            "fortifycellid": self.fortifycellid,
            "name": self.name,
            "level": self.level,
            "destroyed": self.destroyed,
            "locked": self.locked,
            "usemap": self.usemap,
            "credits": self.credits,
            "iresources": self.iresources.to_dict(),
            "storedata": self.storedata,
            "coords": self.coords,
            "player": self.player,
            "krallen": self.krallen,
            "loot": self.loot,
            "homebase": self.homebase,
            "outposts": self.outposts,
            "wmstatus": self.wmstatus,
            "chatservers": self.chatservers,
            "gifts": self.gifts,
            "sentinvites": self.sentinvites,
            "sentgifts": self.sentgifts,
            "fbpromos": self.fbpromos,
            "powerups": self.powerups,
            "attpowerups": self.attpowerups,
            "fbid": self.fbid,
            "cantmovetill": self.cantmovetill,
            "attackreport": self.attackreport,
            "buildingkeydata": self.buildingkeydata,
            "attacks": self.attacks,
            "lootreport": self.lootreport,
            "attackloot": self.attackloot,
            "savetemplate": self.savetemplate,
            "updates": self.updates,
            "createtime": self.createtime,
            "savetime": self.savetime,
            "id": self.id,
            "baseid_inferno": self.baseid_inferno,
            "wmid": self.wmid,
            "type": self.type,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BaseData":
        """Create BaseData instance from dictionary."""
        instance = cls(
            version=data.get("version", 128),
            baseid=data.get("baseid", 0),
            basesaveid=data.get("basesaveid", 0),
            basename=data.get("basename", ""),
        )
        instance.update_from_dict(data)
        return instance

    def update_from_dict(self, data: Dict[str, Any]) -> None:
        """Update this BaseData instance from a dictionary (e.g., API response)."""
        # Simple fields
        self.version = data.get("version", self.version)
        self.baseid = data.get("baseid", self.baseid)
        self.basesaveid = data.get("basesaveid", self.basesaveid)
        self.basename = data.get("basename", self.basename)
        self.lastupdate = data.get("lastupdate", self.lastupdate)

        # Complex nested objects
        self.buildingdata = BuildingData.from_dict(data.get("buildingdata", {}))
        self.buildinghealthdata = data.get("buildinghealthdata", self.buildinghealthdata)
        self.buildingresources = BuildingResources.from_dict(
            data.get("buildingresources", {"t": self.buildingresources.t})
        )
        self.resources = Resources.from_dict(data.get("resources", {}))

        # Combat
        self.damage = data.get("damage", self.damage)
        self.flinger = data.get("flinger", self.flinger)
        self.catapult = data.get("catapult", self.catapult)
        self.aiattacks = AIAttacks.from_dict(data.get("aiattacks", {}))
        self.siege = data.get("siege", self.siege)
        self.attackersiege = data.get("attackersiege", self.attackersiege)
        self.effects = data.get("effects", self.effects)

        # Progress
        self.tutorialstage = data.get("tutorialstage", self.tutorialstage)
        self.timeplayed = data.get("timeplayed", self.timeplayed)
        self.basevalue = data.get("basevalue", self.basevalue)
        self.empirevalue = data.get("empirevalue", self.empirevalue)
        self.points = data.get("points", self.points)
        self.baseseed = data.get("baseseed", self.baseseed)
        self.clienttime = data.get("clienttime", self.clienttime)

        # Research and rewards
        self.researchdata = data.get("researchdata", self.researchdata)
        self.rewards = data.get("rewards", self.rewards)
        self.achieved = data.get("achieved", self.achieved)

        # Stats
        self.stats = Stats.from_dict(data.get("stats", {}))
        self.inventory = data.get("inventory", self.inventory)

        # Locker and academy
        locker_data = data.get("lockerdata", {})
        self.lockerdata = {k: Locker.from_dict(v) for k, v in locker_data.items()}

        academy_data = data.get("academy", {})
        self.academy = {k: Academy.from_dict(v) for k, v in academy_data.items()}

        # Quests and events
        self.quests = data.get("quests", self.quests)
        self.events = data.get("events", self.events)
        self.frontpage = data.get("frontpage", self.frontpage)

        # Monsters
        self.monsters = MonsterData.from_dict(data.get("monsters", {}))
        self.monsterupdate = data.get("monsterupdate", self.monsterupdate)
        self.monsterbaiter = MonsterBaiter.from_dict(data.get("monsterbaiter", {}))
        self.champion = data.get("champion", self.champion)

        # Environment
        self.mushrooms = Mushroom.from_dict(
            data.get("mushrooms", {"s": self.mushrooms.s, "l": self.mushrooms.l})
        )

        # Additional fields
        self.empiredestroyed = data.get("empiredestroyed", self.empiredestroyed)
        self.worldid = data.get("worldid", self.worldid)
        self.event_score = data.get("event_score", self.event_score)
        self.chatenabled = data.get("chatenabled", self.chatenabled)
        self.relationship = data.get("relationship", self.relationship)
        self.healtime = data.get("healtime", self.healtime)
        self.over = data.get("over", self.over)
        self.protect = data.get("protect", self.protect)
        self.purchasecomplete = data.get("purchasecomplete", self.purchasecomplete)
        self.seed = data.get("seed", self.seed)
        self.bookmarked = data.get("bookmarked", self.bookmarked)
        self.fan = data.get("fan", self.fan)
        self.emailshared = data.get("emailshared", self.emailshared)
        self.unreadmessages = data.get("unreadmessages", self.unreadmessages)
        self.giftsentcount = data.get("giftsentcount", self.giftsentcount)
        self.canattack = data.get("canattack", self.canattack)
        self.fortifycellid = data.get("fortifycellid", self.fortifycellid)
        self.name = data.get("name", self.name)
        self.level = data.get("level", self.level)
        self.destroyed = data.get("destroyed", self.destroyed)
        self.locked = data.get("locked", self.locked)
        self.usemap = data.get("usemap", self.usemap)
        self.credits = data.get("credits", self.credits)
        self.iresources = Resources.from_dict(data.get("iresources", {}))
        self.storedata = data.get("storedata", self.storedata)
        self.coords = data.get("coords", self.coords)
        self.player = data.get("player", self.player)
        self.krallen = data.get("krallen", self.krallen)
        self.loot = data.get("loot", self.loot)
        self.homebase = data.get("homebase", self.homebase)
        self.outposts = data.get("outposts", self.outposts)
        self.wmstatus = data.get("wmstatus", self.wmstatus)
        self.chatservers = data.get("chatservers", self.chatservers)
        self.gifts = data.get("gifts", self.gifts)
        self.sentinvites = data.get("sentinvites", self.sentinvites)
        self.sentgifts = data.get("sentgifts", self.sentgifts)
        self.fbpromos = data.get("fbpromos", self.fbpromos)
        self.powerups = data.get("powerups", self.powerups)
        self.attpowerups = data.get("attpowerups", self.attpowerups)
        self.fbid = data.get("fbid", self.fbid)
        self.cantmovetill = data.get("cantmovetill", self.cantmovetill)
        self.attackreport = data.get("attackreport", self.attackreport)
        self.buildingkeydata = data.get("buildingkeydata", self.buildingkeydata)
        self.attacks = data.get("attacks", self.attacks)
        self.lootreport = data.get("lootreport", self.lootreport)
        self.attackloot = data.get("attackloot", self.attackloot)
        self.savetemplate = data.get("savetemplate", self.savetemplate)
        self.updates = data.get("updates", self.updates)
        self.createtime = data.get("createtime", self.createtime)
        self.savetime = data.get("savetime", self.savetime)
        self.id = data.get("id", self.id)
        self.baseid_inferno = data.get("baseid_inferno", self.baseid_inferno)
        self.wmid = data.get("wmid", self.wmid)
        self.type = data.get("type", self.type)


@dataclass
class UpdateSavedRequest:
    """Request data for update saved endpoint."""

    version: int
    lastupdate: int
    type: str
    baseid: int

    def to_dict(self) -> Dict[str, Union[int, str]]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class SaveBaseRequest:
    """Request data for save base endpoint."""

    base_data: BaseData

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return self.base_data.to_dict()
