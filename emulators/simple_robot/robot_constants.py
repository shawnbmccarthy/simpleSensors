import random
from enum import Enum

# STM32 Protobuf values
MAPPING_STATUS: str = '1'
MAPPING_NAVIGATION: str = '2'
MAPPING_DEBUG: str = '3'
MAPPING_PRESET: str = '4'


class SimpleRobotTask(Enum):
    IDLE = 0
    STAINING_LEFT = 1
    STAINING_RIGHT = 2
    EXPLORING_LEFT = 3
    EXPLORING_RIGHT = 4
    AIR_CLEANING = 6
    PUMP_CLEANING = 7
    DUAL_CLEANING = 8
    EMERGENCY_STOP = 15


class DetailedRobotTask(Enum):
    ROBOT_IDLE = 0
    ROBOT_AUTO_STAINING_LEFT = 1
    ROBOT_AUTO_STAINING_RIGHT = 2
    ROBOT_AUTO_SCAN_LEFT = 3
    ROBOT_AUTO_SCAN_RIGHT = 4
    ROBOT_DRY_BEFORE_HALT = 5
    ROBOT_CLEAN_CARTRIDGE_1 = 6
    ROBOT_CLEAN_CARTRIDGE_2 = 7
    ROBOT_CLEAN_CARTRIDGE_3 = 8
    ROBOT_FOLLOW_CMD_VEL = 9
    ROBOT_FOLLOW_GAP = 10
    ROBOT_FOLLOW_LEFT_CLIFF = 11
    ROBOT_FOLLOW_RIGHT_CLIFF = 12
    ROBOT_FOLLOW_WALL = 13
    ROBOT_TEST = 14
    ROBOT_EMERGENCY_LOW_LEVEL_STOP = 15


class RobotHealth(Enum):
    GREEN = 0
    YELLOW = 1
    RED = 2


class ForwardStopReason(Enum):
    BUMPER = 0
    CLIFF = 1
    MAX_DISTANCE = 2


class SearchStopReason(Enum):
    END_SEARCH_ZONE = 0
    GAP_NO_LONGER_SEEN = 1
    GAP_CENTER_REACHED = 2


class BumpersPressed(Enum):
    LEFT_BACK = 0
    LEFT_FRONT = 1
    RIGHT_FRONT = 2
    RIGHT_BACK = 3


class DeckBoardWidth(Enum):
    W_14cm = 0
    W_9cm = 1
    W_7cm = 2


class GapWidth(Enum):
    REGULAR = 0
    NARROW = 1
    WIDE = 2


class GapPosition(Enum):
    RIGHT = 0
    LEFT = 1
    CENTER = 2


class CliffMode(Enum):
    SEPARATE = 0
    COMBINED = 1
    DISABLED = 2


class ScanType(Enum):
    FULL = 0
    SINGLE = 1


class RobotTask(Enum):
    PAUSE = 0
    STAIN_LEFT = 1
    STAIN_RIGHT = 2
    EXPLORE_LEFT = 3
    EXPLORE_RIGHT = 4
    CLEAN_AIR = 6
    CLEAN_PUMPS = 7
    CLEAN_DUAL = 8
