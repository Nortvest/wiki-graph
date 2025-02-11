from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.dependencies.dependency_container import DependencyContainer
    from app.workers.base import WorkerBase


class WorkersManger:
    def __init__(self, container: DependencyContainer) -> None:
        self._container = container
        self._workers: list[WorkerBase] = []
        self._init_worker: WorkerBase | None = None

    def registry_init_worker(self, worker: WorkerBase) -> WorkersManger:
        self._init_worker = worker
        return self

    def registry_worker(self, worker: WorkerBase) -> WorkersManger:
        self._workers.append(worker)
        return self

    async def run(self) -> None:
        if self._init_worker:
            await self._init_worker.run()

        tasks = [
            worker.run()
            for worker in self._workers
        ]

        await asyncio.gather(*tasks)
