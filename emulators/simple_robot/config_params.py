"""
config_params.py

"""
from logging import Logger
from viam.logging import getLogger
from .robot_constants import CliffMode, DeckBoardWidth, GapPosition, GapWidth, RobotTask, ScanType


class ConfigParams(object):
    def __init__(self):
        self.logger: Logger = getLogger(__name__)

        # change ops
        self.board_width = DeckBoardWidth.W_14cm # C0
        self.gap_width = GapWidth.REGULAR                   # C1
        self.gap_sensor_position = GapPosition.RIGHT # C2
        self.cliff_mode = CliffMode.SEPARATE                 # C3
        self.drive_speed = 15.0                         # C4
        self.right_pump_flow = 80.0                     # C5
        self.left_pump_flow = 80.0                      # C6
        self.scan_type = ScanType.FULL                   # C7
        self.pre_gap_search_angle = 15.0                # C9
        self.post_gap_search_angle = 10.0               # C10
        self.bumper_reverse_distance = 15.0             # C11
        self.cliff_reverse_distance = 21.5              # C12
        self.stain_delay_distance = 18.0                # C13
        self._dynamic_board_width_mode = True           # C14 - bool must initialize the type first
        self.minimum_cliff_height = 7.0                 # C15
        self.robot_task = RobotTask.PAUSE                 # C17 - current robot task (starts at pause)

    @property
    def board_width(self) -> DeckBoardWidth:
        return self._board_width

    @board_width.setter
    def board_width(self, value: DeckBoardWidth) -> None:
        if value in DeckBoardWidth:
            self._board_width = value
        else:
            self.logger.warning(f'invalid board_width value: {value}')

    @property
    def gap_width(self) -> GapWidth:
        return self._gap_width

    @gap_width.setter
    def gap_width(self, value: GapWidth) -> None:
        if value in GapWidth:
            self._gap_width = value
        else:
            self.logger.warning(f'invalid gap_width value: {value}')

    @property
    def gap_sensor_position(self) -> GapPosition:
        return self._gap_sensor_position

    @gap_sensor_position.setter
    def gap_sensor_position(self, value: GapPosition) -> None:
        if value in GapPosition:
            self._gap_sensor_position = value
        else:
            self.logger.warning(f'invalid gap_sensor_position value: {value}')

    @property
    def cliff_mode(self) -> CliffMode:
        return self._cliff_mode

    @cliff_mode.setter
    def cliff_mode(self, value: CliffMode) -> None:
        if value in CliffMode:
            self._cliff_mode = value
        else:
            self.logger.warning(f'invalid cliff_mode value: {value}')

    @property
    def drive_speed(self) -> float:
        return self._drive_speed

    @drive_speed.setter
    def drive_speed(self, value: float) -> None:
        if 8 <= value <= 20:
            self._drive_speed = value
        else:
            self.logger.warning(f'Invalid drive speed: {value}')

    @property
    def right_pump_flow(self) -> float:
        return self._right_pump_flow

    @right_pump_flow.setter
    def right_pump_flow(self, value: float) -> None:
        if 1 <= value <= 200:
            self._right_pump_flow = value
        else:
            self.logger.warning(f'Invalid right pump flow: {value}')

    @property
    def left_pump_flow(self) -> float:
        return self._left_pump_flow

    @left_pump_flow.setter
    def left_pump_flow(self, value: float) -> None:
        if 1 <= value <= 200:
            self._left_pump_flow = value
        else:
            self.logger.warning(f'Invalid left pump flow: {value}')

    @property
    def scan_type(self) -> ScanType:
        return self._scan_type

    @scan_type.setter
    def scan_type(self, value: ScanType) -> None:
        if value in ScanType:
            self._scan_type = value
        else:
            self.logger.warning(f'invalid scan type: {value}')

    @property
    def pre_gap_search_angle(self) -> float:
        return self._pre_gap_search_angle

    @pre_gap_search_angle.setter
    def pre_gap_search_angle(self, value: float) -> None:
        if 0 <= value <= 30:
            self._pre_gap_search_angle = value
        else:
            self.logger.warning(f'invalid pre_gap_search_angle: {value}')

    @property
    def post_gap_search_angle(self) -> float:
        return self._post_gap_search_angle

    @post_gap_search_angle.setter
    def post_gap_search_angle(self, value: float) -> None:
        if 0 <= value <= 15:
            self._post_gap_search_angle = value
        else:
            self.logger.warning(f'invalid post_gap_search_angle: {value}')

    @property
    def bumper_reverse_distance(self) -> float:
        return self._bumper_reverse_distance

    @bumper_reverse_distance.setter
    def bumper_reverse_distance(self, value: float) -> None:
        if 10 <= value <= 30:
            self._bumper_reverse_distance = value
        else:
            self.logger.warning(f'invalid bumper_reverse_distance: {value}')

    @property
    def cliff_reverse_distance(self) -> float:
        return self._cliff_reverse_distance

    @cliff_reverse_distance.setter
    def cliff_reverse_distance(self, value: float) -> None:
        if 10 <= value <= 30:
            self._cliff_reverse_distance = value
        else:
            self.logger.warning(f'invalid cliff_reverse_distance: {value}')

    @property
    def stain_delay_distance(self) -> float:
        return self._stain_delay_distance

    @stain_delay_distance.setter
    def stain_delay_distance(self, value: float) -> None:
        if 0 <= value <= 30:
            self._stain_delay_distance = value
        else:
            self.logger.warning(f'invalid stain_delay_distance: {value}')

    @property
    def dynamic_board_width_mode(self) -> bool:
        return self._dynamic_board_width_mode

    @dynamic_board_width_mode.setter
    def dynamic_board_width_mode(self, value: bool) -> None:
        if type(value) is bool:
            self.dynamic_board_width_mode = value
        else:
            self.logger.warning(f'invalid dynamic board width mode: {value}')

    @property
    def minimum_cliff_height(self) -> float:
        return self._minimum_cliff_height

    @minimum_cliff_height.setter
    def minimum_cliff_height(self, value: float) -> None:
        if 1 <= value <= 10:
            self._minimum_cliff_height = value
        else:
            self.logger.warning(f'invalid minimum_cliff_height: {value}')

    @property
    def robot_task(self) -> RobotTask:
        return self._robot_task

    @robot_task.setter
    def robot_task(self, value: RobotTask) -> None:
        if value in RobotTask:
            self._robot_task = value
        else:
            self.logger.warning(f'invalid robot_task: {value}')
