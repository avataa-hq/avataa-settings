from apscheduler.schedulers.asyncio import AsyncIOScheduler

from v1.utils.singleton import Singleton


class Scheduler(metaclass=Singleton):
    def __init__(self):
        self._scheduler = AsyncIOScheduler()
        self._scheduler.start()

    def add_job(self, function, interval_minutes: int):
        self._scheduler.add_job(
            func=function, trigger="interval", minutes=interval_minutes
        )

    def shutdown(self):
        self._scheduler.shutdown()
