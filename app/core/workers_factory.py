from app.dependencies.dependency_container import DependencyContainer
from app.workers.workers_manager import WorkersManger
from app.workers.page_worker import PageWorker


class WorkersFactory:
    _workers_manger: WorkersManger | None = None

    def __init__(self, container: DependencyContainer, num_page_workers: int) -> None:
        self._container = container
        self._num_page_workers = num_page_workers

    @property
    def workers_manger(self) -> WorkersManger:
        if not self._workers_manger:
            self._workers_manger = WorkersManger(self._container)
        return self._workers_manger

    def configure(self) -> None:
        self._configure_page_workers()

    def _configure_page_workers(self) -> None:
        for _ in range(self._num_page_workers):
            worker = PageWorker(self._container)
            self.workers_manger.registry_worker(worker)
