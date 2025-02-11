from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.dependencies.dependency_container import DependencyContainer
    from app.workers.base import WorkerBase


class WorkersManger:
    def __init__(self, container: DependencyContainer) -> None:
        self.container = container
        self.workers: list[WorkerBase] = []

    def registry_worker(self, worker: WorkerBase) -> WorkersManger:
        self.workers.append(worker)
        return self

    async def run(self) -> None:
        tasks = [
            worker.run()
            for worker in self.workers
        ]

        await asyncio.gather(*tasks)
