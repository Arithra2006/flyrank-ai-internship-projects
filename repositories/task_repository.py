from abc import ABC, abstractmethod


class TaskRepository(ABC):

    @abstractmethod
    def get_all(self):
        pass

    @abstractmethod
    def get_by_id(self, task_id: int):
        pass

    @abstractmethod
    def create(self, task):
        pass

    @abstractmethod
    def update(self, task_id: int, task):
        pass

    @abstractmethod
    def delete(self, task_id: int):
        pass