import random
import time
import threading

from logging import Logger
from threading import Thread, Lock
from typing import Callable, Dict, List, Union
from viam.logging import getLogger

MAPPING_STATUS: str = '1'
MAPPING_NAVIGATION: str = '2'
MAPPING_DEBUG: str = '3'

# always return number
SIMPLE_ROBOT_TASK: Dict[str, int] = {
    'IDLE':             0,
    'STAINING_LEFT':    1,
    'STAINING_RIGHT':   2,
    'EXPLORING_LEFT':   3,
    'EXPLORING_RIGHT':  4,
    'AIR_CLEANING':     6,
    'PUMP_CLEANING':    7,
    'DUAL_CLEANING':    8,
    'EMERGENCY_STOP':   15
}

# idle -> staining (left or right)
#         back to idle
#  after some time move to low level stop (bat)
#   - stain
#   - back to idle (at top)
DETAILED_ROBOT_TASK: Dict[str, int] = {
    'ROBOT_IDLE':                       0,
    'ROBOT_AUTO_STAINING_LEFT':         1,
    'ROBOT_AUTO_STAINING_RIGHT':        2,
    'ROBOT_AUTO_SCAN_LEFT':             3,
    'ROBOT_AUTO_SCAN_RIGHT':            4,
    'ROBOT_DRY_BEFORE_HALT':            5,
    'ROBOT_CLEAN_CARTRIDGE_1':          6,
    'ROBOT_CLEAN_CARTRIDGE_2':          7,
    'ROBOT_CLEAN_CARTRIDGE_3':          8,
    'ROBOT_FOLLOW_CMD_VEL':             9,
    'ROBOT_FOLLOW_GAP':                 10,
    'ROBOT_FOLLOW_LEFT_CLIFF':          11,
    'ROBOT_FOLLOW_RIGHT_CLIFF':         12,
    'ROBOT_FOLLOW_WALL':                13,
    'ROBOT_TEST':                       14,
    'ROBOT_EMERGENCY_LOW_LEVEL_STOP':   15
}

ROBOT_HEALTH: Dict[str, int] = {
    'GREEN':    0,
    'YELLOW':   1,
    'RED':      2
}

FORWARD_STOP_REASON: Dict[str, int] = {
    'BUMPER':       0,
    'CLIFF':        1,
    'MAX_DISTANCE': 2
}

SEARCH_STOP_REASON: Dict[str, int] = {
    'END_SEARCH_ZONE':      0,
    'GAP_NO_LONGER_SEEN':   1,
    'GAP_CENTER_REACHED':   2
}

# 16-bit bitwise
BUMPERS_PRESSED: Dict[str, int] = {
    'LEFT_BACK':    0,
    'LEFT_FRONT':   1,
    'RIGHT_FRONT':  2,
    'RIGHT_BACK':   3
}

DECK_BOARD_WIDTH: Dict[str, int] = {
    '14cm':    0,
    '9cm':     1,
    '7cm':     2
}

GAP_WIDTH: Dict[str, int] = {
    'REGULAR':  0,
    'NARROW':   1,
    'WIDE':     2
}

GAP_POSITION: Dict[str, int] = {
    'RIGHT':    0,
    'LEFT':     1,
    'CENTER':   2
}

CLIFF_MODE: Dict[str, int] = {
    'SEPARATE': 0,
    'COMBINED': 1,
    'DISABLED': 2
}

SCAN_TYPE: Dict[str, int] = {
    'FULL':     0,
    'SINGLE':   1
}

ROBOT_TASK: Dict[int, str] = {
    0: 'PAUSE',
    1: 'STAIN_LEFT',
    2: 'STAIN_RIGHT',
    3: 'EXPLORE_LEFT',
    4: 'EXPLORE_RIGHT',
    6: 'CLEAN_AIR',
    7: 'CLEAN_PUMPS',
    8: 'CLEAN_DUAL'
}


def generate_random(a: float, b: float, r: int = 2) -> float:
    return round(random.uniform(a, b), r)


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

    def __init__(self) -> None:
        self.is_running = False
        self.lock = Lock()
        self.thread: Union[Thread, None] = None
        self.logger: Logger = getLogger(__name__)
        self.updates: List[Callable] = []

        self.robot_task = SIMPLE_ROBOT_TASK['IDLE']                     # P1
        self.detailed_robot_task = DETAILED_ROBOT_TASK['ROBOT_IDLE']    # P1 (detailed)
        self.consumed_capacity = 0                                      # P2 - sensor/status/status.c (CONSUMED_CAP)
        self.consumed_stain = 0                                         # P3 - sensor/status/status.c (CONSUMED_STAIN)
        self.stained_area = 0                                           # P4  - sensor/status/status.c (STAINED_AREA)

        # for time being display green (yellow for low) 0-g, 1-y, 2-r (SBC will use mapping)
        self.robot_health = ROBOT_HEALTH['GREEN']                           # SBC1 (compute?) - sensor/status/status.c (ROBOT_HEALTH)
        self.robot_health_detailed = 0                                      # P5 (16-bit bitwise)
        self.battery_voltage_1 = 24.0                                       # P6 - powersensor/battery/battery.h
        self.battery_voltage_2 = 24.0                                       # P7 - powersensor/battery/battery.h
        self.battery_1_percentage = 100.0                                   # SBC2 - Computed by board
        self.battery_2_percentage = 100.0                                   # SBC3 - Computed by board
        self.battery_current = 150                                          # P8 - powersensor/battery/battery.h
        self.stm_temp = 24.5                                                # P9 - sensor/status/status.c (ST_TEMP)
        self.forward_stop_reason = FORWARD_STOP_REASON['BUMPER']            # P10 - sensor/status/status.c (FWD_STOP_REASON)
        self.search_stop_reason = SEARCH_STOP_REASON['END_SEARCH_ZONE']     # P11 - sensor/status/status.c (SEARCH_STOP_REASON)
        self.search_stop_angle_offset = 95.0                                # P12 - sensor/status/status.c (SEARCH_STOP_ANGLE)
        self.successful_searches_percentage = 0.97                          # P13 - sensor/status/status.c (SUCCESS_SEARCH_RATIO)
        self.left_cliff = 4.0                                               # P14 - sensor/navigation/navigation.c (US_RIGHT)
        self.right_cliff = 3.5                                              # P15 - sensor/navigation/navigation.c (US_LEFT)
        self.bumpers_pressed = 0                                            # P16 - sensor/navigation/navigation.c (GAP1)
        self.gap_1_rx = 33.0                                                # P17 - sensor/navigation/navigation.c (GAP2)
        self.gap_2_rx = 32.0                                                # P18 - sensor/navigation/navigation.c (GAP3)
        self.gap_3_rx = 35.5                                                # P19
        self.deck_board_average_width = 142.0                               # P29
        self.gap_average_width = 9.0                                        # P32

        # P36 & P37 (perf monitors)
        self.missed_slow_cycles = 0
        self.missed_fast_cycles = 0

        # change ops
        self.board_width = 0                                    # C0
        self.gap_width = 0                                      # C1
        self.gap_sensor_position = 0                            # C2
        self.cliff_mode = 0                                     # C3
        self.drive_speed = 15.0                                 # C4
        self.right_pump_flow = 80.0                             # C5
        self.left_pump_flow = 80.0                              # C6
        self.scan_type = SCAN_TYPE['FULL']                      # C7
        self.pre_gap_search_angle = 15.0                        # C9
        self.post_gap_search_angle = 10.0                       # C10
        self.bumper_reverse_distance = 15.0                     # C11
        self.cliff_reverse_distance = 21.5                      # C12
        self.stain_delay_distance = 18.0                        # C13
        self.dynamic_board_width_mode = True                    # C14
        self.minimum_cliff_height = 7.0                         # C15

    def set_defaults(self):
        self.robot_health = ROBOT_HEALTH['GREEN']
        self.battery_voltage_1 = 0
        self.battery_voltage_2 = 0
        self.board_width = 0
        self.gap_sensor_position = 0
        self.cliff_mode = 0
        self.drive_speed = 0
        self.left_pump_flow = 0
        self.scan_type = 0
        self.post_gap_search_angle = 0
        self.cliff_reverse_distance = 0
        self.robot_task = 0
        self.is_running = False
        self.thread = None

    def get_debug(self) -> Dict[str, float]:
        self.logger.debug('returning debug data')
        ret_dict = {}
        for i in range(1, 16):
            ret_dict[f'DEBUG_{i}'] = generate_random(0, 20, 4)

        return ret_dict

    def get_battery_voltage_percentage(self):
        """
        assume dewalt 24v 2000 mAh battery for right now (will use if we need to adjust calculations)
        :return:
        """
        # battery_voltage_percentage = current_battery_voltage / maximum_battery_voltage * 100
        self.battery_voltage_1 -= generate_random(0.0, 0.5, 2)
        self.battery_voltage_2 -= generate_random(0.0, 0.5, 2)
        if self.battery_voltage_1 <= 0.0:
            self.battery_voltage_1 = 24.00
        if self.battery_voltage_2 <= 0.0:
            self.battery_voltage_2 = 24.00

        return (self.battery_voltage_1 + self.battery_voltage_2) / (24+24)

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

    def do_stain_left(self):
        self.detailed_robot_task = DETAILED_ROBOT_TASK['ROBOT_AUTO_STAINING_LEFT']
        self.robot_task = SIMPLE_ROBOT_TASK['STAINING_LEFT']

    def do_stain_right(self):
        self.detailed_robot_task = DETAILED_ROBOT_TASK['ROBOT_AUTO_STAINING_RIGHT']
        self.robot_task = SIMPLE_ROBOT_TASK['STAINING_RIGHT']

    def do_explore_right(self):
        self.detailed_robot_task = DETAILED_ROBOT_TASK['ROBOT_AUTO_SCAN_RIGHT']
        self.robot_task = SIMPLE_ROBOT_TASK['EXPLORING_RIGHT']

    def do_explore_left(self):
        self.detailed_robot_task = DETAILED_ROBOT_TASK['ROBOT_AUTO_SCAN_LEFT']
        self.robot_task = SIMPLE_ROBOT_TASK['EXPLORING_LEFT']

    def clean_air(self):
        self.detailed_robot_task = DETAILED_ROBOT_TASK['ROBOT_CLEAN_CARTRIDGE_1']
        self.robot_task = SIMPLE_ROBOT_TASK['AIR_CLEANING']

    def clean_pumps(self):
        self.detailed_robot_task = DETAILED_ROBOT_TASK['ROBOT_CLEAN_CARTRIDGE_2']
        self.robot_task = SIMPLE_ROBOT_TASK['PUMP_CLEANING']

    def clean_dual(self):
        self.detailed_robot_task = DETAILED_ROBOT_TASK['ROBOT_CLEAN_CARTRIDGE_3']
        self.robot_task = SIMPLE_ROBOT_TASK['DUAL_CLEANING']

    def set_robot_task(self, task: int):
        if task in ROBOT_TASK:
            t = ROBOT_TASK[task]
            self.logger.info(f'robot task: {task}:{t}')
            if t == 'PAUSE':
                self.logger.info(f'task:{task}:{t}, setting idle')
                self.robot_task = SIMPLE_ROBOT_TASK['IDLE']
                self.detailed_robot_task = DETAILED_ROBOT_TASK['ROBOT_IDLE']
                pass
            elif t == 'STAIN_LEFT':
                with self.lock:
                    self.updates.append(self.do_stain_left)
            elif t == 'STAIN_RIGHT':
                with self.lock:
                    self.updates.append(self.do_stain_right)
            elif t == 'EXPLORE_LEFT':
                with self.lock:
                    self.updates.append(self.do_explore_left)
            elif t == 'EXPLORE_RIGHT':
                with self.lock:
                    self.updates.append(self.do_explore_right)
            elif t == 'CLEAN_AIR':
                with self.lock:
                    self.updates.append(self.clean_air)
            elif t == 'CLEAN_PUMPS':
                with self.lock:
                    self.updates.append(self.clean_pumps)
            elif t == 'CLEAN_DUAL':
                with self.lock:
                    self.updates.append(self.clean_dual)
            else:
                self.logger.error(f'Unknown task: {t}')
        else:
            self.logger.warning(f'Unknown task: {task}')

    # TODO: was trying to get slick, and reduce code but this is actually useless
    # TODO: move to simple updates of all values
    # TODO: add threads for jitter values
    def do_update(self):
        try:
            with self.lock:
                self.logger.info(f'current updates: {self.updates}')
                f = self.updates.pop(-1)
                while f is not None:
                    self.logger.info(f'running {f}')
                    f()
                    self.logger.info(f'updates: {self.updates}')
                    f = self.updates.pop(-1)
        except IndexError as e:
            self.logger.error(f'nothing to update: {e}')
            self.updates.append(self.get_battery_voltage_percentage)
            time.sleep(3)

    def start_robot(self):
        self.updates.append(self.get_battery_voltage_percentage)
        with self.lock:
            self.is_running = True
            self.thread = threading.Thread(target=self.run_robot)
        self.thread.start()

    def stop_robot(self):
        with self.lock:
            self.is_running = False

    def run_robot(self):
        while self.is_running:
            self.do_update()
            time.sleep(1)
        self.thread.join()
