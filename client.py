import asyncio

from viam.robot.client import RobotClient
from viam.rpc.dial import Credentials, DialOptions
from viam.components.camera import Camera
from viam.components.sensor import Sensor


async def connect():
    opts = RobotClient.Options.with_api_key(
        api_key='<API-KEY>',
        api_key_id='<API-KEY-ID>'
    )
    return await RobotClient.at_address('<ADDRESS>', opts)


async def main():
    robot = await connect()

    print('Resources:')
    print(robot.resource_names)

    await robot.close()


if __name__ == '__main__':
    asyncio.run(main())
