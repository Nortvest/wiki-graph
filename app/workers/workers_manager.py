from __future__ import annotations

import asyncio

from app.dependencies.dependency_container import DependencyContainer
from app.workers.base import WorkerBase


class WorkersManger:
    def __init__(self, container: DependencyContainer):
        self.container = container
        self.workers: list[WorkerBase] = []

    def registry_worker(self, worker: WorkerBase) -> WorkersManger:
        self.workers.append(worker)

    async def run(self) -> None:
        tasks = [
            worker.run()
            for worker in self.workers
        ]

        await asyncio.gather(*tasks)
