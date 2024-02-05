import time
import threading

from logging import Logger
from threading import Thread, Lock
from typing import Callable, List, Union
from viam.logging import getLogger

from emulators.utilities import generate_random, bounded_jitter, bounded_jitter_down, reset_value
from .robot_constants import (
    DetailedRobotTask,
    ForwardStopReason,
    RobotHealth,
    RobotTask,
    SearchStopReason,
    SimpleRobotTask,
)

from .config_params import ConfigParams
from .debug_params import DebugParams

logger = getLogger('global robot emulator')


class RunningRobot(ConfigParams, DebugParams):
    """
    not a true singleton
    not extremely worried as this is only used in this robot
    """
    _robot = None

    @classmethod
    def get_robot(cls):
        if cls._robot is None:
            cls._robot = cls()
            return cls._robot
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
        self.consumed_capacity = 0                                 # P2 - sensor/status/status.c (CONSUMED_CAP)
        self.consumed_stain = 0                                    # P3 - sensor/status/status.c (CONSUMED_STAIN)
        self.stained_area = 0                                      # P4  - sensor/status/status.c (STAINED_AREA)

        # for time being display green (yellow for low) 0-g, 1-y, 2-r (SBC will use mapping)
        self.robot_health = RobotHealth.GREEN                          # SBC1 - sensor/status/status.c (ROBOT_HEALTH)
        self.robot_health_detailed = 0                                 # P5 (16-bit bitwise)
        self.battery_voltage_1 = 99.9                                  # P6 - powersensor/battery/battery.h
        self.battery_voltage_2 = 99.9                                  # P7 - powersensor/battery/battery.h
        self.battery_current = 150                                     # P8 - powersensor/battery/battery.h
        self.stm_temp = 24.5                                           # P9 - sensor/status/status.c
        self.forward_stop_reason = ForwardStopReason.BUMPER            # P10 - sensor/status/status.c
        self.search_stop_reason = SearchStopReason.END_SEARCH_ZONE     # P11 - sensor/status/status.c
        self.search_stop_angle_offset = 95.0                           # P12 - sensor/status/status.c
        self.successful_searches_percentage = 0.97                     # P13 - sensor/status/status.c
        self.left_cliff = 4.0                                          # P14 - sensor/navigation/navigation.c
        self.right_cliff = 3.5                                         # P15 - sensor/navigation/navigation.c
        self.bumpers_pressed = 0                                       # P16 - sensor/navigation/navigation.c
        self.gap_1_rx = 33.0                                           # P17 - sensor/navigation/navigation.c
        self.gap_2_rx = 32.0                                           # P18 - sensor/navigation/navigation.c
        self.gap_3_rx = 35.5                                           # P19
        self.deck_board_average_width = 142.0                          # P29
        self.gap_average_width = 9.0                                   # P32

        # P36 & P37 (perf monitors)
        self.missed_slow_cycles = 0
        self.missed_fast_cycles = 0

    def reset_parameters(self):
        self.consumed_capacity = 0  # P2 - sensor/status/status.c (CONSUMED_CAP)
        self.consumed_stain = 0  # P3 - sensor/status/status.c (CONSUMED_STAIN)
        self.stained_area = 0  # P4  - sensor/status/status.c (STAINED_AREA)
        # for time being display green (yellow for low) 0-g, 1-y, 2-r (SBC will use mapping)
        self.forward_stop_reason = ForwardStopReason.BUMPER  # P10 - sensor/status/status.c
        self.search_stop_reason = SearchStopReason.END_SEARCH_ZONE  # P11 - sensor/status/status.c
        self.search_stop_angle_offset = 95.0  # P12 - sensor/status/status.c
        self.successful_searches_percentage = 0.97  # P13 - sensor/status/status.c
        self.left_cliff = 4.0  # P14 - sensor/navigation/navigation.c
        self.right_cliff = 3.5  # P15 - sensor/navigation/navigation.c
        self.bumpers_pressed = 0  # P16 - sensor/navigation/navigation.c
        self.gap_1_rx = 33.0  # P17 - sensor/navigation/navigation.c
        self.gap_2_rx = 32.0  # P18 - sensor/navigation/navigation.c
        self.gap_3_rx = 35.5  # P19
        self.deck_board_average_width = 142.0  # P29
        self.gap_average_width = 9.0  # P32

    def get_battery_voltage_percentage(self):
        """
        assume 24v 2000 mAh battery for right now (will use if we need to adjust calculations)
        :return:
        """
        # battery_voltage_percentage = current_battery_voltage / maximum_battery_voltage * 100
        return (self.battery_voltage_1 + self.battery_voltage_2) / 2

    def do_jitter(self):
        """

        Returns:
        """
        self.stm_temp = round(bounded_jitter(self.stm_temp, 8.0, 60.0, generate_random(0.5, 2.0, 2)), 4)
        self.battery_voltage_1 = round(
            bounded_jitter_down(self.battery_voltage_1, 0.5, 99.9, generate_random(0.5, 1, 2)), 4
        )
        self.battery_voltage_2 = round(
            bounded_jitter_down(self.battery_voltage_2, 0.5, 99.9, generate_random(0.5, 1, 2)), 4)
        self.logger.info(
            f'do_jitter: bv1:{self.battery_voltage_1}, bv2:{self.battery_voltage_2}, stm_temp:{self.stm_temp}'
        )

        if self.robot_task in [RobotTask.STAIN_LEFT, RobotTask.STAIN_RIGHT]:
            if self.consumed_stain == 0:
                self.consumed_stain = 5000
                self.consumed_stain = bounded_jitter_down(
                    self.consumed_stain,
                    0.5,
                    5000.0,
                    generate_random(0.5, 1.0, 2)
                )
            self.stained_area = bounded_jitter(
                self.stained_area,
                2.0,
                999.0,
                generate_random(0.5, 1.0, 2)
            )
        if self.robot_task in [
            RobotTask.STAIN_LEFT,
            RobotTask.STAIN_RIGHT,
            RobotTask.EXPLORE_LEFT,
            RobotTask.STAIN_RIGHT
        ]:
            self.gap_1_rx = bounded_jitter(self.gap_1_rx, 0.0, 1000.0, generate_random(1, 2, 2))
            self.gap_2_rx = bounded_jitter(self.gap_2_rx, 0.0, 1000.0, generate_random(1, 2, 2))
            self.gap_3_rx = bounded_jitter(self.gap_3_rx, 0.0, 1000.0, generate_random(1, 2, 2))
            self.deck_board_average_width = bounded_jitter(
                self.deck_board_average_width,
                0.0, 200,
                generate_random(0, 2, 2)
            )
            self.gap_average_width = bounded_jitter(
                self.gap_average_width,
                0.0,
                50.0,
                generate_random(0, 0.5, 2)
            )
            self.bumpers_pressed = generate_random(0, 16, 0)
            self.left_cliff = bounded_jitter(self.left_cliff, 0, 200, generate_random(0.25, 1, 2))
            self.right_cliff = bounded_jitter(self.right_cliff, 0, 200, generate_random(0.25, 1, 2))
            self.successful_searches_percentage = generate_random(0, 1, 2)
            self.search_stop_angle_offset = bounded_jitter(
                self.search_stop_angle_offset,
                -30.0,
                30.0,
                generate_random(1, 2, 2)
            )
        if self.robot_task == RobotTask.PAUSE:
            self.reset_parameters()

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
        self.logger.info('clean_air')
        self.robot_task = RobotTask.CLEAN_AIR
        self.detailed_robot_task = DetailedRobotTask.ROBOT_CLEAN_CARTRIDGE_1
        self.simple_robot_task = SimpleRobotTask.AIR_CLEANING

    def clean_pumps(self):
        self.logger.info('clean_pumps')
        self.robot_task = RobotTask.CLEAN_PUMPS
        self.detailed_robot_task = DetailedRobotTask.ROBOT_CLEAN_CARTRIDGE_2
        self.simple_robot_task = SimpleRobotTask.PUMP_CLEANING

    def clean_dual(self):
        self.logger.info('clean_dual')
        self.robot_task = RobotTask.CLEAN_DUAL
        self.detailed_robot_task = DetailedRobotTask.ROBOT_CLEAN_CARTRIDGE_3
        self.simple_robot_task = SimpleRobotTask.DUAL_CLEANING

    def do_clean(self):
        self.logger.info('do_clean')
        self.robot_task = RobotTask.CLEANING

    # TODO: was trying to get slick, and reduce code but this is actually useless
    # TODO: move to simple updates of all values
    # TODO: add threads for jitter values
    def do_update(self):
        try:
            with self.lock:
                f = self.updates.pop(-1)
                while f is not None:
                    self.logger.info(f'running: {f}')
                    f()
                    f = self.updates.pop(-1)
        except IndexError as e:
            self.logger.debug(f'nothing to update: {e}')
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
            if self.robot_task is self.robot_task.EXPLORE_LEFT:
                self.updates.append(self.do_explore_left)
            elif self.robot_task is self.robot_task.EXPLORE_RIGHT:
                self.updates.append(self.do_explore_right)
            elif self.robot_task is self.robot_task.STAIN_LEFT:
                self.updates.append(self.do_stain_left)
            elif self.robot_task is self.robot_task.STAIN_RIGHT:
                self.updates.append(self.do_stain_right)
            elif self.robot_task is self.robot_task.CLEANING:
                self.updates.append(self.clean_air)
            elif self.robot_task is self.robot_task.CLEAN_AIR:
                self.updates.append(self.clean_pumps)
            elif self.robot_task is self.robot_task.CLEAN_PUMPS:
                self.updates.append(self.clean_dual)
            elif self.robot_task is self.robot_task.CLEAN_DUAL:
                self.updates.append(self.do_clean)
            self.updates.append(self.do_jitter)
            self.do_update()
            # some resets just in case
            self.stm_temp = reset_value(self.stm_temp, 24.5, 0.5)
            self.battery_voltage_1 = reset_value(self.battery_voltage_1, 100.0, 0.5)
            self.battery_voltage_2 = reset_value(self.battery_voltage_2, 100.0, 0.5)
            time.sleep(1)
        self.thread.join()
