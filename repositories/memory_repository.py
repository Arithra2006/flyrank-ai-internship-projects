from repositories.task_repository import TaskRepository


class MemoryTaskRepository(TaskRepository):

    def __init__(self):
        self.tasks = [
            {
                "id": 1,
                "title": "Study FastAPI",
                "done": False
            },
            {
                "id": 2,
                "title": "Complete Assignment",
                "done": False
            },
            {
                "id": 3,
                "title": "Watch Movie",
                "done": True
            }
        ]


    def get_all(self):
        return self.tasks


    def get_by_id(self, task_id):

        for task in self.tasks:
            if task["id"] == task_id:
                return task

        return None


    def create(self, task):

        new_task = {
            "id": max([t["id"] for t in self.tasks], default=0) + 1,
            "title": task["title"],
            "done": False
        }

        self.tasks.append(new_task)

        return new_task


    def update(self, task_id, updated_task):

        task = self.get_by_id(task_id)

        if task:

            if "title" in updated_task:
                task["title"] = updated_task["title"]

            if "done" in updated_task:
                task["done"] = updated_task["done"]

        return task


    def delete(self, task_id):

        task = self.get_by_id(task_id)

        if task:
            self.tasks.remove(task)
            return True

        return False