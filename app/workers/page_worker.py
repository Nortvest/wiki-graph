import asyncio

from app.dependencies.dependency_container import DependencyContainer
from app.workers.base import WorkerBase


class PageWorker(WorkerBase):
    def __init__(self, container: DependencyContainer) -> None:
        self._container = container
        self._logger = container.logger

    async def run(self) -> None:
        await asyncio.sleep(3)
        self._logger.debug(f"Run application!")
