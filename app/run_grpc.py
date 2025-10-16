import logging
import asyncio
from v1.grpc_config.grpc_server import start_grpc_serve


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(start_grpc_serve())
