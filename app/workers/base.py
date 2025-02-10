from abc import ABC, abstractmethod


class WorkerBase(ABC):
    @abstractmethod
    def run(self) -> None:
        """Запуск работы воркера."""
        raise NotImplementedError
