MAPPING_STATUS = '1'
MAPPING_NAVIGATION = '2'
MAPPING_DEBUG = '3'

SIMPLE_ROBOT_TASK = {
    "IDLE": 0,
    "STAINING_LEFT": 1,
    "STAINING_RIGHT": 2,
    "EXPLORING_LEFT": 3,
    "EXPLORING_RIGHT": 4,
    "AIR_CLEANING": 6,
    "PUMP_CLEANING": 7,
    "DUAL_CLEANING": 8,
    "EMERGENCY_STOP": 15
}

DETAILED_ROBOT_TASK = {
    "ROBOT_IDLE": 0,
    "ROBOT_AUTO_STAINING_LEFT": 1,
    "ROBOT_AUTO_STAINING_RIGHT": 2,
    "ROBOT_AUTO_SCAN_LEFT": 3,
    "ROBOT_AUTO_SCAN_RIGHT": 4,
    "ROBOT_DRY_BEFORE_HALT": 5,
    "ROBOT_CLEAN_CARTRIDGE_1": 6,
    "ROBOT_CLEAN_CARTRIDGE_2": 7,
    "ROBOT_CLEAN_CARTRIDGE_3": 8,
    "ROBOT_FOLLOW_CMD_VEL": 9,
    "ROBOT_FOLLOW_GAP": 10,
    "ROBOT_FOLLOW_LEFT_CLIFF": 11,
    "ROBOT_FOLLOW_RIGHT_CLIFF": 12,
    "ROBOT_FOLLOW_WALL": 13,
    "ROBOT_TEST": 14,
    "ROBOT_EMERGENCY_LOW_LEVEL_STOP": 15
}


class RunningRobot(object):
    def __init__(self):
        self.robot_task = SIMPLE_ROBOT_TASK["IDLE"]
        self.detailed_robot_task = DETAILED_ROBOT_TASK["ROBOT_IDLE"]
        pass

    def get_status(self):
        pass

    def get_robot_health(self):
        pass

    def get_robot_status(self):
        self.get_robot_health()
        pass

    def get_navigation(self):
        pass

    def get_debug(self):
        pass

    def set_robot_parameter(self, key, value):
        pass
