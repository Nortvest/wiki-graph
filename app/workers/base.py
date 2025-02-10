from abc import ABC, abstractmethod


class WorkerBase(ABC):
    @abstractmethod
    async def run(self) -> None:
        """Запуск работы воркера. (Асинхронно)"""
        raise NotImplementedError
