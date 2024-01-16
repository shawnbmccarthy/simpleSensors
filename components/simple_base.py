from threading import Lock
from typing import ClassVar, Dict, Mapping, Sequence, Optional, Any
from typing_extensions import Self
from viam.components.component_base import ValueTypes
from viam.components.base import Base, Vector3
from viam.module.types import Reconfigurable
from viam.proto.app.robot import ComponentConfig
from viam.proto.common import ResourceName
from viam.resource.base import ResourceBase
from viam.resource.registry import Registry, ResourceCreatorRegistration
from viam.resource.types import Model, ModelFamily


class SimpleBase(Base, Reconfigurable):
    MODEL: ClassVar[Model] = Model(ModelFamily('acme', 'robodeck'), 'base')

    mapped_name: str
    board: str
    moving: bool
    lock: Lock

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
        self.moving = False
        self.lock = Lock()

    def reconfigure(self, config: ComponentConfig, dependencies: Mapping[ResourceName, ResourceBase]) -> None:
        self.mapped_name = config.attributes.fields['mapped_name'].string_value
        self.board = config.attributes.fields['board'].string_value

    async def move_straight(
        self,
        distance: int,
        velocity: float,
        *,
        extra: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None,
        **kwargs,
    ):
        with self.lock.acquire():
            self.moving = True
            for _ in range(distance):
                pass
            self.moving = False

    async def set_power(
        self,
        linear: Vector3,
        angular: Vector3,
        *,
        extra: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None,
        **kwargs,
    ):
        with self.lock.acquire():
            if (
                    linear.x == 0 and linear.y == 0 and linear.z == 0 and
                    angular.x == 0 and angular.y == 0 and angular.z == 0
            ):
                self.moving = False
            else:
                self.moving = True

    async def set_velocity(
            self,
            linear: Vector3,
            angular: Vector3,
            *,
            extra: Optional[Dict[str, Any]] = None,
            timeout: Optional[float] = None,
            **kwargs,
    ):
        await self.set_power(linear, angular, extra=extra, timeout=timeout, **kwargs)

    async def spin(
        self,
        angle: float,
        velocity: float,
        *,
        extra: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None,
        **kwargs,
    ):
        with self.lock.acquire():
            self.moving = True
            for _ in range(int(angle)):
                pass
            self.moving = False

    async def stop(
        self,
        *,
        extra: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None,
        **kwargs,
    ):
        with self.lock.acquire():
            self.moving = False

    async def is_moving(self) -> bool:
        return self.moving

    async def get_properties(self, *, timeout: Optional[float] = None, **kwargs) -> Base.Properties:
        raise NotImplementedError()

    async def do_command(
        self,
        command: Mapping[str, ValueTypes],
        *,
        timeout: Optional[float] = None,
        **kwargs
    ) -> Mapping[str, ValueTypes]:
        pass


Registry.register_resource_creator(
    Base.SUBTYPE,
    SimpleBase.MODEL,
    ResourceCreatorRegistration(SimpleBase.new, SimpleBase.validate_config)
)