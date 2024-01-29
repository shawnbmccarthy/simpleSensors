import asyncio
import os
import sys
import time

from logging import Logger
from typing import List, Union

from viam.components.power_sensor import PowerSensor
from viam.components.sensor import Sensor
from viam.logging import getLogger
from viam.robot.client import RobotClient

from emulators.simple_robot import ROBOT_TASK

logger: Logger = getLogger(__name__)


async def connect() -> RobotClient:
    opts: RobotClient.Options = RobotClient.Options.with_api_key(
        api_key=os.environ['API_KEY'],
        api_key_id=os.environ['API_KEY_ID']
    )
    return await RobotClient.at_address(os.environ['ROBOT_ADDRESS'], opts)


async def main() -> None:
    robot: RobotClient = await connect()

    for rn in robot.resource_names:
        logger.info(f'resource name: {rn}')

    debug: Sensor = Sensor.from_robot(robot, 'debug')

    components: List[Union[PowerSensor, Sensor]] = [
        Sensor.from_robot(robot, 'status'),
        Sensor.from_robot(robot, 'navigation'),
        PowerSensor.from_robot(robot, 'battery1'),
        PowerSensor.from_robot(robot, 'battery2')
    ]

    for component in components:
        reading = await component.get_readings()
        logger.info(f'reading: {reading}')

    for key in ROBOT_TASK.keys():
        result = await debug.do_command(command={'ROBOT_TASK': int(key)})
        logger.info(f'ROBOT_TASK[{ROBOT_TASK[key]}] - result: {result}')
        time.sleep(2)

    await robot.close()


if __name__ == '__main__':
    try:
        a = os.environ['API_KEY']
        i = os.environ['API_KEY_ID']
        r = os.environ['ROBOT_ADDRESS']
    except KeyError as ke:
        logger.error(f'missing key: {ke}')
        sys.exit(1)
    asyncio.run(main())
