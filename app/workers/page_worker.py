from app.dependencies.dependency_container import DependencyContainer
from app.workers.base import WorkerBase


class PageWorker(WorkerBase):
    def __init__(self, container: DependencyContainer) -> None:
        self._container = container

    def run(self) -> None:
        pass
