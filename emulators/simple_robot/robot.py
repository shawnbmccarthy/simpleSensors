import time
import threading

from logging import Logger
from threading import Thread, Lock
from typing import Any, Callable, Dict, List, Union
from viam.logging import getLogger

from .robot_constants import (
    DetailedRobotTask,
    ForwardStopReason,
    RobotHealth,
    RobotTask,
    SearchStopReason,
    SimpleRobotTask,
    generate_random
)

from .config_params import ConfigParams
from .debug_params import DebugParams


class RunningRobot(ConfigParams, DebugParams):
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
        ConfigParams.__init__(self)
        DebugParams.__init__(self)
        # Robot internals
        self._dynamic_board_width_mode = True
        self.is_running = False
        self.lock = Lock()
        self.thread: Union[Thread, None] = None
        self.logger: Logger = getLogger(__name__)
        self.updates: List[Callable] = []

        # Robot parameters
        self.simple_robot_task = SimpleRobotTask.IDLE              # P1
        self.detailed_robot_task = DetailedRobotTask.ROBOT_IDLE    # P1 (detailed)
        self.consumed_capacity = 0                                      # P2 - sensor/status/status.c (CONSUMED_CAP)
        self.consumed_stain = 0                                         # P3 - sensor/status/status.c (CONSUMED_STAIN)
        self.stained_area = 0                                           # P4  - sensor/status/status.c (STAINED_AREA)

        # for time being display green (yellow for low) 0-g, 1-y, 2-r (SBC will use mapping)
        self.robot_health = RobotHealth.GREEN                           # SBC1 (compute?) - sensor/status/status.c (ROBOT_HEALTH)
        self.robot_health_detailed = 0                                      # P5 (16-bit bitwise)
        self.battery_voltage_1 = 24.0                                       # P6 - powersensor/battery/battery.h
        self.battery_voltage_2 = 24.0                                       # P7 - powersensor/battery/battery.h
        self.battery_1_percentage = 100.0                                   # SBC2 - Computed by board
        self.battery_2_percentage = 100.0                                   # SBC3 - Computed by board
        self.battery_current = 150                                          # P8 - powersensor/battery/battery.h
        self.stm_temp = 24.5                                                # P9 - sensor/status/status.c (ST_TEMP)
        self.forward_stop_reason = ForwardStopReason.BUMPER            # P10 - sensor/status/status.c (FWD_STOP_REASON)
        self.search_stop_reason = SearchStopReason.END_SEARCH_ZONE     # P11 - sensor/status/status.c (SEARCH_STOP_REASON)
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

    def set_defaults(self) -> None:
        """
        set default values for robot parameters

        Returns:
        """
        self.robot_health = RobotHealth.GREEN
        self.battery_voltage_1 = 0
        self.battery_voltage_2 = 0
        self.simple_robot_task = SimpleRobotTask.IDLE
        self.is_running = False
        self.thread = None

    def get_presents(self) -> Dict[str, Any]:
        pass

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

    def do_stain_left(self):
        self.detailed_robot_task = DetailedRobotTask.ROBOT_AUTO_STAINING_LEFT
        self.simple_robot_task = SimpleRobotTask.STAINING_LEFT

    def do_stain_right(self):
        self.detailed_robot_task = DetailedRobotTask.ROBOT_AUTO_STAINING_RIGHT
        self.simple_robot_task = SimpleRobotTask.STAINING_RIGHT

    def do_explore_right(self):
        self.detailed_robot_task = DetailedRobotTask.ROBOT_AUTO_SCAN_RIGHT
        self.simple_robot_task = SimpleRobotTask.EXPLORING_RIGHT

    def do_explore_left(self):
        self.detailed_robot_task = DetailedRobotTask.ROBOT_AUTO_SCAN_LEFT
        self.simple_robot_task = SimpleRobotTask.EXPLORING_LEFT

    def clean_air(self):
        self.detailed_robot_task = DetailedRobotTask.ROBOT_CLEAN_CARTRIDGE_1
        self.simple_robot_task = SimpleRobotTask.AIR_CLEANING

    def clean_pumps(self):
        self.detailed_robot_task = DetailedRobotTask.ROBOT_CLEAN_CARTRIDGE_2
        self.simple_robot_task = SimpleRobotTask.PUMP_CLEANING

    def clean_dual(self):
        self.detailed_robot_task = DetailedRobotTask.ROBOT_CLEAN_CARTRIDGE_3
        self.simple_robot_task = SimpleRobotTask.DUAL_CLEANING

    def set_robot_task(self, task: RobotTask):
        self.logger.info(f'robot task: {task}:{task.name}')
        if task == RobotTask.PAUSE:
            self.logger.info(f'task:{task}:{task.name}, setting idle')
            self.simple_robot_task = SimpleRobotTask.IDLE
            self.detailed_robot_task = DetailedRobotTask.ROBOT_IDLE
            pass
        elif task == RobotTask.STAIN_LEFT:
            with self.lock:
                self.updates.append(self.do_stain_left)
        elif task == RobotTask.STAIN_RIGHT:
            with self.lock:
                self.updates.append(self.do_stain_right)
        elif task == RobotTask.EXPLORE_LEFT:
            with self.lock:
                self.updates.append(self.do_explore_left)
        elif task == RobotTask.EXPLORE_RIGHT:
            with self.lock:
                self.updates.append(self.do_explore_right)
        elif task == RobotTask.CLEAN_AIR:
            with self.lock:
                self.updates.append(self.clean_air)
        elif task == RobotTask.CLEAN_PUMPS:
            with self.lock:
                self.updates.append(self.clean_pumps)
        elif task == RobotTask.CLEAN_DUAL:
            with self.lock:
                self.updates.append(self.clean_dual)
        else:
            self.logger.error(f'Unknown task: {task}')

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
