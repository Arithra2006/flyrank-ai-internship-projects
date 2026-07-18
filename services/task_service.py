from repositories.task_repository import TaskRepository


class TaskService:

    def __init__(self, repository: TaskRepository):
        self.repository = repository


    def get_tasks(self):
        return self.repository.get_all()


    def get_task(self, task_id: int):

        task = self.repository.get_by_id(task_id)

        if not task:
            return None

        return task


    def create_task(self, task):

        title = task.title.strip()

        if not title:
            return None

        return self.repository.create({
            "title": title
        })


    def update_task(self, task_id: int, updated_task):

        data = {}

        if updated_task.title is not None:
            title = updated_task.title.strip()

            if not title:
                return None

            data["title"] = title


        if updated_task.done is not None:
            data["done"] = updated_task.done


        return self.repository.update(
            task_id,
            data
        )


    def delete_task(self, task_id: int):

        return self.repository.delete(task_id)