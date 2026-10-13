from pathlib import Path

from prelude.parser_imports import *

USER_DIR = Path.home()
STEAM_ID = "76561198276345085"
_STEAM_PROFILE_DIR = USER_DIR / "Games" / "Age of Empires 2 DE" / STEAM_ID
_INSTALL_DIR = Path(r"C:\Program Files (x86)\Steam\steamapps\common\AoE2DE")

class Paths:
    STEAM_PROFILE_DIR = f"{_STEAM_PROFILE_DIR}/"
    MODS_LOCAL_DIR = f"{_STEAM_PROFILE_DIR}/mods/local/"
    SCENARIO_DIR = f"{_STEAM_PROFILE_DIR}/resources/_common/scenario/"
    PROFILE_DIR = f"{_STEAM_PROFILE_DIR}/profile/"
    XS_DIR = f"{_STEAM_PROFILE_DIR}/resources/_common/xs/"
    DESKTOP = f"{USER_DIR}/Desktop/"
    INSTALL_DIR = f"{_INSTALL_DIR}/"
    DAT_FILE = rf"{_INSTALL_DIR}/resources/_common/dat/empires2_x2_p1.dat"

class GameInfo:
    MESO_CIVS = [TechInfo.AZTECS, TechInfo.MAYA]
    LATAM_CIVS = [TechInfo.INCA, TechInfo.TUPI, TechInfo.MUISCA, TechInfo.MAPUCHE]

    CIVS = [
        TechInfo.BRITONS,
        TechInfo.BYZANTINES,
        TechInfo.CELTS,
        TechInfo.CHINESE,
        TechInfo.FRANKS,
        TechInfo.GOTHS,
        TechInfo.JAPANESE,
        TechInfo.MONGOLS,
        TechInfo.PERSIANS,
        TechInfo.SARACENS,
        TechInfo.TEUTONS,
        TechInfo.TURKS,
        TechInfo.VIKINGS,
        TechInfo.AZTECS,
        TechInfo.HUNS,
        TechInfo.KOREANS,
        TechInfo.MAYA,
        TechInfo.SPANISH,
        TechInfo.INCA,
        TechInfo.HINDUSTANIS,
        TechInfo.ITALIANS,
        TechInfo.MAGYARS,
        TechInfo.SLAVS,
        TechInfo.BERBERS,
        TechInfo.ETHIOPIANS,
        TechInfo.MALIANS,
        TechInfo.PORTUGUESE,
        TechInfo.BURMESE,
        TechInfo.KHMER,
        TechInfo.MALAY,
        TechInfo.VIETNAMESE,
        TechInfo.BULGARIANS,
        TechInfo.CUMANS,
        TechInfo.LITHUANIANS,
        TechInfo.TATARS,
        TechInfo.BURGUNDIANS,
        TechInfo.SICILIANS,
        TechInfo.POLES,
        TechInfo.BOHEMIANS,
        TechInfo.DRAVIDIANS,
        TechInfo.BENGALIS,
        TechInfo.GURJARAS,
        TechInfo.ROMANS,
        TechInfo.ARMENIANS,
        TechInfo.GEORGIANS,
        TechInfo.JURCHENS,
        TechInfo.KHITANS,
        TechInfo.SHU,
        TechInfo.WU,
        TechInfo.WEI,
        TechInfo.MUISCA,
        TechInfo.MAPUCHE,
        TechInfo.TUPI,
    ]

    COLOUR = ["", "<BLUE>", "<RED>", "<GREEN>", "<YELLOW>", "<AQUA>", "<PURPLE>", "<GREY>", "<ORANGE>"]

    BUTTON_LOCATIONS = [1, 2, 3, 4, 6, 7, 8, 9, 10, 11, 12, 13]

    HOTKEY_ID_MAP = {
        1: 16344,
        2: 16157,
        3: 16487,
        4: 16464,
        6: 16149,
        7: 16131,
        8: 16161,
        9: 16138,
        10: 16176,
        11: 16164,
        12: 16182,
        13: 16159,
        14: 19054
    }

    BARRACK_UNITS = [
        UnitInfo.CHAMPI_SCOUT,
        UnitInfo.CHAMPI_RUNNER,
        UnitInfo.CHAMPI_WARRIOR,
        UnitInfo.ELITE_CHAMPI_WARRIOR,

        UnitInfo.MILITIA,
        UnitInfo.MAN_AT_ARMS,
        UnitInfo.LONG_SWORDSMAN,
        UnitInfo.TWO_HANDED_SWORDSMAN,
        UnitInfo.CHAMPION,

        UnitInfo.SPEARMAN,
        UnitInfo.PIKEMAN,
        UnitInfo.HALBERDIER,

        UnitInfo.EAGLE_SCOUT,
        UnitInfo.EAGLE_WARRIOR,
        UnitInfo.ELITE_EAGLE_WARRIOR,

        UnitInfo.LEGIONARY,
        UnitInfo.CONDOTTIERO,
        UnitInfo.FLEMISH_MILITIA,
        UnitInfo.TEMPLE_GUARD,
        UnitInfo.ELITE_TEMPLE_GUARD,
    ]

    ARCHERY_RANGE_UNITS = [
        UnitInfo.ARCHER,
        UnitInfo.CROSSBOWMAN,
        UnitInfo.ARBALESTER,

        UnitInfo.SKIRMISHER,
        UnitInfo.ELITE_SKIRMISHER,
        UnitInfo.IMPERIAL_SKIRMISHER,

        UnitInfo.SLINGER,
        UnitInfo.HAND_CANNONEER,

        UnitInfo.CAVALRY_ARCHER,
        UnitInfo.HEAVY_CAVALRY_ARCHER,

        UnitInfo.ELEPHANT_ARCHER,
        UnitInfo.ELITE_ELEPHANT_ARCHER,

        UnitInfo.GENITOUR,
        UnitInfo.ELITE_GENITOUR,
    ]

    STABLE_UNITS = [
        UnitInfo.SCOUT_CAVALRY,
        UnitInfo.LIGHT_CAVALRY,
        UnitInfo.HUSSAR,
        UnitInfo.WINGED_HUSSAR,

        UnitInfo.SHRIVAMSHA_RIDER,
        UnitInfo.ELITE_SHRIVAMSHA_RIDER,

        UnitInfo.KNIGHT,
        UnitInfo.CAVALIER,
        UnitInfo.PALADIN,
        UnitInfo.SAVAR,

        UnitInfo.STEPPE_LANCER,
        UnitInfo.ELITE_STEPPE_LANCER,

        UnitInfo.CAMEL_SCOUT,
        UnitInfo.CAMEL_RIDER,
        UnitInfo.HEAVY_CAMEL_RIDER,
        UnitInfo.IMPERIAL_CAMEL_RIDER,

        UnitInfo.BATTLE_ELEPHANT,
        UnitInfo.ELITE_BATTLE_ELEPHANT,

        UnitInfo.XOLOTL_WARRIOR,
    ]

    SIEGE_WORKSHOP_UNITS = [
        UnitInfo.BATTERING_RAM,
        UnitInfo.CAPPED_RAM,
        UnitInfo.SIEGE_RAM,

        UnitInfo.ARMORED_ELEPHANT,
        UnitInfo.SIEGE_ELEPHANT,
        UnitInfo.FLAMING_CAMEL,

        UnitInfo.MANGONEL,
        UnitInfo.ONAGER,
        UnitInfo.SIEGE_ONAGER,

        UnitInfo.SCORPION,
        UnitInfo.HEAVY_SCORPION,

        UnitInfo.BOMBARD_CANNON,
        UnitInfo.HOUFNICE,

        UnitInfo.SIEGE_TOWER,
        UnitInfo.FLAMING_CAMEL,
    ]

    DOCK_UNITS = [
        UnitInfo.FISHING_SHIP,
        UnitInfo.TRANSPORT_SHIP,
        UnitInfo.TRADE_COG,

        UnitInfo.FIRE_GALLEY,
        UnitInfo.FIRE_SHIP,
        UnitInfo.FAST_FIRE_SHIP,

        UnitInfo.DEMOLITION_RAFT,
        UnitInfo.DEMOLITION_SHIP,
        UnitInfo.HEAVY_DEMOLITION_SHIP,

        UnitInfo.GALLEY,
        UnitInfo.WAR_GALLEY,
        UnitInfo.GALLEON,

        UnitInfo.CANNON_GALLEON,
        UnitInfo.ELITE_CANNON_GALLEON,

        UnitInfo.TURTLE_SHIP,
        UnitInfo.ELITE_TURTLE_SHIP,
        UnitInfo.LONGSHIP,
        UnitInfo.ELITE_LONGSHIP,
        UnitInfo.CARAVEL,
        UnitInfo.ELITE_CARAVEL,
        UnitInfo.THIRISADAI,
        UnitInfo.DROMON,
    ]

    CASTLE_UNITS = [
        *UnitInfo.unique_units(exclude_non_castle_units = True),
        UnitInfo.ELITE_KIPCHAK_CUMAN_MERCENARIES,
        UnitInfo.PETARD,
        UnitInfo.TREBUCHET_PACKED,
    ]

    KREPOST_UNITS = [
        UnitInfo.KONNIK_KREPOST,
        UnitInfo.ELITE_KONNIK_KREPOST,
    ]

    DONJON_UNITS = [
        UnitInfo.SERJEANT_DONJON,
        UnitInfo.ELITE_SERJEANT_DONJON,

        UnitInfo.SPEARMAN_DONJON,
        UnitInfo.PIKEMAN_DONJON,
        UnitInfo.HALBERDIER_DONJON,
    ]

    MONASTERY_UNITS = [
        UnitInfo.MONK,
        UnitInfo.MISSIONARY,
        UnitInfo.WARRIOR_PRIEST,
    ]

    TOWN_CENTRE_UNITS = [
        UnitInfo.VILLAGER_MALE,
    ]

    MARKET_UNITS = [
        UnitInfo.TRADE_CART_EMPTY,
    ]

    GARRISONABLE_BY_ALL = [
        BuildingInfo.TOWN_CENTER,
        BuildingInfo.WATCH_TOWER,
        BuildingInfo.GUARD_TOWER,
        BuildingInfo.KEEP,
        BuildingInfo.BOMBARD_TOWER,
        BuildingInfo.HOUSE,
        BuildingInfo.DONJON,
        BuildingInfo.KREPOST,
        BuildingInfo.CASTLE,
        UnitInfo.BATTERING_RAM,
        UnitInfo.CAPPED_RAM,
        UnitInfo.SIEGE_RAM,
        UnitInfo.SIEGE_TOWER,
        UnitInfo.TRANSPORT_SHIP
    ]

    GARRISONABLE_BY_MILITARY = [
        BuildingInfo.ARCHERY_RANGE,
        BuildingInfo.BARRACKS,
        BuildingInfo.STABLE,
        BuildingInfo.SIEGE_WORKSHOP,
        BuildingInfo.DOCK,
        BuildingInfo.MONASTERY,
    ]

    LOADABLE = [
        UnitInfo.BATTERING_RAM,
        UnitInfo.CAPPED_RAM,
        UnitInfo.SIEGE_RAM,
        UnitInfo.SIEGE_TOWER,
        UnitInfo.TRANSPORT_SHIP,
    ]

    SIEGE_UNITS = [
        UnitInfo.MANGONEL,
        UnitInfo.ONAGER,
        UnitInfo.SIEGE_ONAGER,
        UnitInfo.SIEGE_TOWER,
        UnitInfo.BATTERING_RAM,
        UnitInfo.CAPPED_RAM,
        UnitInfo.SIEGE_RAM,
        UnitInfo.SCORPION,
        UnitInfo.HEAVY_SCORPION,
        UnitInfo.BOMBARD_CANNON,
        UnitInfo.TREBUCHET,
        UnitInfo.TREBUCHET_PACKED,
    ]

    @staticmethod
    def where(unit: UnitInfo) -> BuildingInfo:
        if unit in GameInfo.BARRACK_UNITS:
            return BuildingInfo.BARRACKS
        elif unit in GameInfo.ARCHERY_RANGE_UNITS:
            return BuildingInfo.ARCHERY_RANGE
        elif unit in GameInfo.STABLE_UNITS:
            return BuildingInfo.STABLE
        return BuildingInfo.HOUSE

    @staticmethod
    def where_all(units: list[UnitInfo]) -> BuildingInfo:
        if all(map(lambda x: x in GameInfo.BARRACK_UNITS, units)):
            return BuildingInfo.BARRACKS
        elif all(map(lambda x: x in GameInfo.ARCHERY_RANGE_UNITS, units)):
            return BuildingInfo.ARCHERY_RANGE
        elif all(map(lambda x: x in GameInfo.STABLE_UNITS, units)):
            return BuildingInfo.STABLE
        return BuildingInfo.HOUSE
