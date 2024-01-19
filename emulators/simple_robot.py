MAPPING_STATUS = '1'
MAPPING_NAVIGATION = '2'
MAPPING_DEBUG = '3'

SIMPLE_ROBOT_TASK = {
    0: 'IDLE',
    1: 'STAINING_LEFT',
    2: 'STAINING_RIGHT',
    3: 'EXPLORING_LEFT',
    4: 'EXPLORING_RIGHT',
    6: 'AIR_CLEANING',
    7: 'PUMP_CLEANING',
    8: 'DUAL_CLEANING',
    15: 'EMERGENCY_STOP'
}

DETAILED_ROBOT_TASK = {
    0: 'ROBOT_IDLE',
    1: 'ROBOT_AUTO_STAINING_LEFT',
    2: 'ROBOT_AUTO_STAINING_RIGHT',
    3: 'ROBOT_AUTO_SCAN_LEFT',
    4: 'ROBOT_AUTO_SCAN_RIGHT',
    5: 'ROBOT_DRY_BEFORE_HALT',
    6: 'ROBOT_CLEAN_CARTRIDGE_1',
    7: 'ROBOT_CLEAN_CARTRIDGE_2',
    8: 'ROBOT_CLEAN_CARTRIDGE_3',
    9: 'ROBOT_FOLLOW_CMD_VEL',
    10: 'ROBOT_FOLLOW_GAP',
    11: 'ROBOT_FOLLOW_LEFT_CLIFF',
    12: 'ROBOT_FOLLOW_RIGHT_CLIFF',
    13: 'ROBOT_FOLLOW_WALL',
    14: 'ROBOT_TEST',
    15: 'ROBOT_EMERGENCY_LOW_LEVEL_STOP'
}

ROBOT_HEALTH = {
    0: 'GREEN',
    1: 'YELLOW',
    2: 'RED'
}

FORWARD_STOP_REASON = {
    0: 'BUMPER',
    1: 'CLIFF',
    2: 'MAX_DISTANCE'
}

SEARCH_STOP_REASON = {
    0: 'END_SEARCH_ZONE',
    1: 'GAP_NO_LONGER_SEEN',
    2: 'GAP_CENTER_REACHED'
}

# 16-bit bitwise
BUMPERS_PRESSED = {
    0: 'LEFT_BACK',
    1: 'LEFT_FRONT',
    2: 'RIGHT_FRONT',
    3: 'RIGHT_BACK'
}

DECK_BOARD_WIDTH = {
    0: '14 cm',
    1: '9 cm',
    2: '7 cm'
}

GAP_WIDTH = {
    0: 'REGULAR',
    1: 'NARROW',
    2: 'WIDE'
}

GAP_POSITION = {
    0: 'RIGHT',
    1: 'LEFT',
    2: 'CENTER'
}

CLIFF_MODE = {
    0: 'SEPARATE',
    1: 'COMBINED',
    2: 'DISABLED'
}

SCAN_TYPE = {
    0: 'FULL',
    1: 'SINGLE'
}

ROBOT_TASK = {
    0: 'PAUSE',
    1: 'STAIN_LEFT',
    2: 'STAIN_RIGHT',
    3: 'EXPLORE_LEFT',
    4: 'EXPLORE_RIGHT',
    6: 'CLEAN_AIR',
    7: 'CLEAN_PUMPS',
    8: 'CLEAN_DUAL'
}


class RunningRobot(object):
    """
    not a true singleton
    not extremely worried as this is only used in this robot
    """
    _robot = None

    @classmethod
    def get_robot(cls):
        if cls._robot is None:
            return cls()
        else:
            return cls._robot

    def __init__(self):
        self.robot_task = SIMPLE_ROBOT_TASK[0]                  # P1
        self.detailed_robot_task = DETAILED_ROBOT_TASK[0]       # P1 - Detailed
        self.consumed_capacity = 0                              # P2
        self.consumed_stain = 0                                 # P3
        self.stained_area = 0                                   # P4
        self.robot_health = ROBOT_HEALTH[0]                     # SBC1 - we can compute from health?
        self.robot_health_detailed = 0                          # P5 (16-bit bitwise)
        self.battery_voltage_1 = 24.0                           # P6
        self.battery_voltage_2 = 24.0                           # P7
        self.battery_1_percentage = 100.0                       # SBC2
        self.battery_2_percentage = 100.0                       # SBC3
        self.battery_current = 150                              # P8
        self.stm_temp = 24.5                                    # P9
        self.forward_stop_reason = FORWARD_STOP_REASON[1]       # P10
        self.search_stop_reason = SEARCH_STOP_REASON[1]         # P11
        self.search_stop_angle_offset = 95.0                    # P12
        self.successful_searches_percentage = 0.97              # P13
        self.left_cliff = 4.0                                   # P14
        self.right_cliff = 3.5                                  # P15
        self.bumpers_pressed = 0                                # P16
        self.gap_1_rx = 33.0                                    # P17
        self.gap_2_rx = 32.0                                    # P18
        self.gap_3_rx = 35.5                                    # P19
        self.deck_board_average_width = 142.0                   # P29
        self.gap_average_width = 9.0                            # P32

        self.board_width = 0                                    # C0
        self.gap_width = 0                                      # C1
        self.gap_sensor_position = 0                            # C2
        self.cliff_mode = 0                                     # C3
        self.drive_speed = 15.0                                 # C4
        self.right_pump_flow = 80.0                             # C5
        self.left_pump_flow = 80.0                              # C6
        self.scan_type = SCAN_TYPE[0]                           # C7
        self.pre_gap_search_angle = 15.0                        # C9
        self.post_gap_search_angle = 10.0                       # C10
        self.bumper_reverse_distance = 15.0                     # C11
        self.cliff_reverse_distance = 21.5                      # C12
        self.stain_delay_distance = 18.0                        # C13
        self.dynamic_board_width_mode = True                    # C14
        self.minimum_cliff_height = 7.0                         # C15

    def get_status(self):
        pass

    def get_navigation(self):
        pass

    def get_debug(self):
        pass

    def set_robot_parameter(self, key, value):
        pass

    def get_battery_voltage_percentage(self):
        """
        assume dewalt 24v 2000 mAh battery for right now (will use if we need to adjust calculations)
        :return:
        """
        # battery_voltage_percentage = current_battery_voltage / maximum_battery_voltage * 100
        return ((self.battery_voltage_1 + self.battery_voltage_2) / (24+24)) * 100

    def set_deck_board_width(self, width):
        if width in DECK_BOARD_WIDTH:
            self.board_width = DECK_BOARD_WIDTH[width]

    def set_gap_width(self, width):
        if width in GAP_WIDTH:
            self.gap_width = GAP_WIDTH[width]

    def set_gap_sensor_position(self, pos):
        if pos in GAP_POSITION:
            self.gap_sensor_position = GAP_POSITION[pos]

    def set_cliff_sensor_mode(self, mode):
        if mode in CLIFF_MODE:
            self.cliff_mode = CLIFF_MODE[mode]

    def set_drive_speed(self, speed):
        if 8 <= speed <= 20:
            self.drive_speed = speed

    def set_right_pump_flow(self, flow):
        if 1 <= flow <= 200:
            self.right_pump_flow = flow

    def set_left_pump_flow(self, flow):
        if 1 <= flow <= 200:
            self.left_pump_flow = flow

    def set_scan_type(self, type):
        if type in SCAN_TYPE:
            self.scan_type = SCAN_TYPE[type]

    def set_pre_gap_search_angle(self, angle):
        if 0 <= angle <= 30:
            self.pre_gap_search_angle = angle

    def set_post_gap_search_angle(self, angle):
        if 0 <= angle <= 15:
            self.post_gap_search_angle = angle

    def set_bumper_reverse_distance(self, distance):
        if 10 <= distance <= 30:
            self.bumper_reverse_distance = distance

    def set_cliff_reverse_distance(self, distance):
        if 10 <= distance <= 30:
            self.cliff_reverse_distance = distance

    def set_stain_delay_distance(self, distance):
        if 0 <= distance <= 30:
            self.stain_delay_distance = distance

    def set_dynamic_board_width_mode(self, mode):
        if type(mode) is bool:
            self.dynamic_board_width_mode = mode

    def set_minimum_cliff_height(self, height):
        if 1 <= height <= 10:
            self.minimum_cliff_height = height

    def set_robot_task(self, task):
        if task in ROBOT_TASK and ROBOT_TASK[task] is not 'EMERGENCY_STOP':
            self.robot_task = task
