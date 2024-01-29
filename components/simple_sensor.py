from logging import Logger
from threading import Lock
from typing import Any, ClassVar, Mapping, Sequence, Optional, Union
from typing_extensions import Self
from viam.components.component_base import ValueTypes
from viam.components.sensor import Sensor
from viam.logging import getLogger
from viam.module.types import Reconfigurable
from viam.proto.app.robot import ComponentConfig
from viam.proto.common import ResourceName
from viam.resource.base import ResourceBase
from viam.resource.registry import Registry, ResourceCreatorRegistration
from viam.resource.types import Model, ModelFamily
from viam.utils import SensorReading
from emulators.simple_robot import (
    MAPPING_DEBUG,
    MAPPING_PRESET,
    MAPPING_NAVIGATION,
    MAPPING_STATUS,
    CliffMode,
    DeckBoardWidth,
    GapPosition,
    GapWidth,
    RobotTask,
    RunningRobot,
    ScanType
)


class SimpleSensor(Sensor, Reconfigurable):
    MODEL: ClassVar[Model] = Model(ModelFamily('acme', 'robodeck'), 'sensor')

    mapped_name: str
    board: str
    lock: Lock
    robot: Union[RunningRobot, None]
    logger: Logger

    @classmethod
    def new(cls, config: ComponentConfig, dependencies: Mapping[ResourceName, ResourceBase]) -> Self:
        sensor = cls(config.name)
        sensor.reconfigure(config, dependencies)
        return sensor

    @classmethod
    def validate_config(cls, config: ComponentConfig) -> Sequence[str]:
        mapped_name = config.attributes.fields['mapped_name'].string_value
        board = config.attributes.fields['board'].string_value

        if mapped_name is None or mapped_name == '':
            raise Exception('mapped_name is a required attribute')

        if board is None or board == '':
            raise Exception('board is a required attribute')

        return []

    def __init__(self, name: str) -> None:
        super().__init__(name)
        self.mapped_name = ''
        self.board = ''
        self.robot = None
        self.logger = getLogger(__name__)
        self.lock = Lock()

    def reconfigure(self, config: ComponentConfig, dependencies: Mapping[ResourceName, ResourceBase]) -> None:
        self.robot = RunningRobot.get_robot()
        self.mapped_name = config.attributes.fields['mapped_name'].string_value
        self.board = config.attributes.fields['board'].string_value

    async def get_readings(
        self,
        *,
        extra: Optional[Mapping[str, Any]] = None,
        timeout: Optional[float] = None,
        **kwargs
    ) -> Mapping[str, SensorReading]:
        if self.mapped_name == MAPPING_NAVIGATION:
            return {
                'BUMPER': self.robot.bumpers_pressed,
                'GAP1': self.robot.gap_1_rx,
                'GAP2': self.robot.gap_2_rx,
                'GAP3': self.robot.gap_3_rx,
                'MISSED_SLOW_CYCLES': self.robot.missed_slow_cycles,
                'US_LEFT': self.robot.left_cliff,
                'US_RIGHT': self.robot.right_cliff
            }
        elif self.mapped_name == MAPPING_STATUS:
            return {
                'CONSUMED_CAP': self.robot.consumed_capacity,       # estimation related to time & rate to stain/pumps
                                                                    # & operations
                                                                    # for use with battery consumption (turbines consume
                                                                    # 95% of amp hours) - air pumps & stain pumps
                                                                    # turbines, drive system, stain pumps
                'CONSUMED_STAIN': self.robot.consumed_stain,
                'FWD_STOP_REASON': self.robot.forward_stop_reason.value,
                'ROBOT_HEALTH': self.robot.robot_health.value,
                'ROBOT_MODE': self.robot.robot_task.value,
                'SEARCH_STOP_ANGLE': self.robot.search_stop_angle_offset,
                'SEARCH_STOP_REASON': self.robot.search_stop_reason.value,
                'STAINED_AREA': self.robot.stained_area,
                'ST_TEMP': self.robot.stm_temp,
                'SUCC_SEARCH_RATIO': self.robot.successful_searches_percentage
            }
        elif self.mapped_name == MAPPING_DEBUG:
            return self.robot.get_debug_data()
        elif self.mapped_name == MAPPING_PRESET:
            return {
                'BOARD_WIDTH': self.robot.board_width.value,
                'GAP_WIDTH': self.robot.gap_width.value,
                'GAP_SENSOR_POSITION': self.robot.gap_sensor_position.value,
                'CLIFF_SENSOR_MODE': self.robot.cliff_mode.value,
                'DRIVE_SPEED': self.robot.drive_speed,
                'RIGHT_PUMP_FLOW': self.robot.right_pump_flow,
                'LEFT_PUMP_FLOW': self.robot.left_pump_flow,
                'SCAN_TYPE': self.robot.scan_type.value,
                'PRE_GAP_SEARCH_ANGLE': self.robot.pre_gap_search_angle,
                'POST_GAP_SEARCH_ANGLE': self.robot.post_gap_search_angle,
                'BUMPER_REVERSE_DISTANCE': self.robot.bumper_reverse_distance,
                'CLIFF_REVERSE_DISTANCE': self.robot.cliff_reverse_distance,
                'STAIN_DELAY_DISTANCE': self.robot.stain_delay_distance,
                'DYNAMIC_BOARD_WIDTH_MODE': 'ON' if self.robot.dynamic_board_width_mode else 'OFF',
                'ROBOT_TASK': self.robot.robot_task.value
            }
        self.logger.warning(f'{self.mapped_name} not supported')
        return {}

    async def do_command(
        self,
        command: Mapping[str, ValueTypes],
        *,
        timeout: Optional[float] = None,
        **kwargs
    ) -> Mapping[str, ValueTypes]:
        ret_data = {}
        for key in command.keys():
            val = command[key]
            try:
                ret_val = True
                if 'BOARD_WIDTH' == key:
                    self.robot.board_width = DeckBoardWidth(val)
                elif 'GAP_WIDTH' == key:
                    self.robot.gap_width = GapWidth(val)
                elif 'GAP_SENSOR_POSITION' == key:
                    self.robot.gap_sensor_position = GapPosition(val)
                elif 'CLIFF_SENSOR_MODE' == key:
                    self.robot.cliff_sensor_mode = CliffMode(val)
                elif 'DRIVE_SPEED' == key:
                    self.robot.drive_speed = val
                elif 'RIGHT_PUMP_FLOW' == key:
                    self.robot.right_pump_flow = val
                elif 'LEFT_PUMP_FLOW' == key:
                    self.robot.left_pump_flow = val
                elif 'SCAN_TYPE' == key:
                    self.robot.scan_type = ScanType(val)
                elif 'PRE_GAP_SEARCH_ANGLE' == key:
                    self.robot.pre_gap_search_angle = val
                elif 'POST_GAP_SEARCH_ANGLE' == key:
                    self.robot.post_gap_search_angle = val
                elif 'BUMPER_REVERSE_DISTANCE' == key:
                    self.robot.bumper_reverse_distance = val
                elif 'CLIFF_REVERSE_DISTANCE' == key:
                    self.robot.cliff_reverse_distance = val
                elif 'STAIN_DELAY_DISTANCE' == key:
                    self.robot.stain_delay_distance = val
                elif 'DYNAMIC_BOARD_WIDTH_MODE' == key:
                    self.robot.dynamic_board_width_mode = val.lower().strip() == 'true'
                elif 'MINIMUM_CLIFF_HEIGHT' == key:
                    self.robot.minimum_cliff_height = key
                elif 'ROBOT_TASK' == key:
                    self.robot.robot_task = RobotTask(val)
                else:
                    self.logger.warning(f'Unknown command: {key}')
                    ret_val = False
                ret_data[key] = ret_val
            except ValueError as ve:
                self.logger.error(f'Value error occurred: {ve}')
                ret_data[key] = str(ve)
        return ret_data


Registry.register_resource_creator(
    Sensor.SUBTYPE,
    SimpleSensor.MODEL,
    ResourceCreatorRegistration(SimpleSensor.new, SimpleSensor.validate_config)
)
