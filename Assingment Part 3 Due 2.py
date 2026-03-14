# 1. I learned how to use Object-Oriented Programming (OOP).
# 2. I learned how to create classes and objects in Python.
# 3. I understood how inheritance works using parent and child classes.
# 4. I learned about the Strategy Design Pattern for flexible sorting.
# 5. I learned how to use @dataclass to reduce boilerplate code.
# 6. I understood private variables using double underscore (__).
# 7. I learned how to use @property to safely access private data.
# 8. I learned how to store tasks inside a dictionary.
# 9. I understood how to manage task status like TODO, DOING, DONE.
# 10. I learned how history tracking works using lists and tuples.



STATUS = ("TODO", "DOING", "DONE")


class SortStrategy:
    def sort(self, tasks: list["Task"]) -> list["Task"]:
        # TODO: override in subclasses
        return tasks


class SortByPriority(SortStrategy):
    def sort(self, tasks: list["Task"]) -> list["Task"]:
        # TODO: high priority first
        pass


class SortByCreated(SortStrategy):
    def sort(self, tasks: list["Task"]) -> list["Task"]:
        # TODO: sort by task_id
        pass
# Imports
from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Optional

@dataclass
class Task:
    task_id: int
    title: str
    desc: str
    priority: int
    __status: str = field(default="TODO", repr=False)
    tags: set[str] = field(default_factory=set)
    history: List[Tuple[int, str, str, str]] = field(default_factory=list)
    _step: int = field(default=0, repr=False)

    @property
    def status(self) -> str:
        return self.__status

    def change_status(self, new_status: str) -> None:
        # TODO: validate new_status in STATUS
        # TODO: append history tuple
        pass


class Project:
    def __init__(self, project_id: str, name: str):
        self.project_id = project_id
        self.name = name
        self.tasks: Dict[int, Task] = {}
        self._next_task_id = 1

    def add_task(self, title: str, desc: str, priority: int) -> Task:
        # TODO: validate priority 1-5
        t = Task(self._next_task_id, title, desc, priority)
        self.tasks[t.task_id] = t
        self._next_task_id += 1
        return t

    def list_tasks(self, status: Optional[str], sorter: SortStrategy) -> list[Task]:
        # TODO: filter by status and then sorter.sort  Task Tracker (Trello-lite)
        pass