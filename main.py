import datetime
import unittest
from typing import Dict, List, Optional
from collections import defaultdict
from abc import ABC, abstractmethod

class TaskBase(ABC):
    @abstractmethod
    def display(self) -> str:
        pass

    @abstractmethod
    def is_overdue(self) -> bool:
        pass

class Task(TaskBase):
    def __init__(self, task_id: int, title: str, description: str, priority: str, due_date: datetime.datetime):
        self.id = task_id
        self.title = title
        self.description = description
        self.priority = priority
        self.completed = False
        self.due_date = due_date

    def is_overdue(self) -> bool:
        return datetime.datetime.now() > self.due_date

    def display(self) -> str:
        status = "✅" if self.completed else "❌"
        return f"[{status}] {self.title} (ID: {self.id}) | Приоритет: {self.priority} | Дата: {self.due_date.strftime('%Y-%m-%d %H:%M')}"

    def __str__(self):     # перегрузка операторов
        return self.display()

    def __eq__(self, other):
        if isinstance(other, Task):
            return self.id == other.id
        return False

    def __len__(self):
        return len(self.description)

class Authenticator:
    _total_users = 0

    @staticmethod
    def get_total_users() -> int:
        return Authenticator._total_users

    def __init__(self):
        self.users: Dict[str, User] = {}

    def register(self, username: str, password: str):
        if username in self.users:
            raise ValueError("Username already exists")
        self.users[username] = User(username, password)
        Authenticator._total_users += 1

class User:
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password
        self.tasks: List[Task] = []
        self.archived_tasks: List[Task] = []

    def archive_completed(self):
        self.archived_tasks = [task for task in self.tasks if task.completed]
        self.tasks = [task for task in self.tasks if not task.completed]

    def reset(self):
        self.tasks = []
        self.archived_tasks = []

class TaskManager: # ошибки
    def __init__(self, user: User):
        self.user = user

    def add_task(self, title: str, description: str, priority: str, due_date_str: str):
        try:
            due_date = datetime.datetime.strptime(due_date_str, "%Y-%m-%d %H:%M")
        except ValueError:
            raise ValueError("Неверный формат даты. Используйте 'YYYY-MM-DD HH:MM'")
        task = Task(len(self.user.tasks) + 1, title, description, priority, due_date)
        self.user.tasks.append(task)

    def format_task_list(self) -> str: # обработка строк
        return "\n".join([str(task) for task in self.user.tasks])

class NotificationHandler:
    @staticmethod
    def check_all_reminders(users: Dict[str, User]):
        for user in users.values():
            for task in user.tasks:
                if not task.completed and task.is_overdue():
                    print(f"Напоминание для {user.username}: Задача '{task.title}' просрочена!")

# тесты
class TestTaskTracker(unittest.TestCase):
    def test_abstract_class(self):
        task = Task(1, "Test", "", "high", datetime.datetime.now())
        self.assertIsInstance(task, TaskBase)

    def test_static_methods(self):
        auth = Authenticator()
        auth.register("user1", "pass")
        self.assertEqual(Authenticator.get_total_users(), 1)

    def test_task_str(self):
        task = Task(1, "Test", "Desc", "high", datetime.datetime.now())
        self.assertIn("Test", str(task))

    def test_task_eq(self):
        task1 = Task(1, "Test", "", "high", datetime.datetime.now())
        task2 = Task(1, "Another", "", "high", datetime.datetime.now())
        self.assertTrue(task1 == task2)  # сравнение по ID

    def test_task_len(self):
        task = Task(1, "Test", "Long description", "high", datetime.datetime.now())
        self.assertGreater(len(task), 0)

    def test_add_task(self):
        auth = Authenticator()
        auth.register("user1", "pass")
        user = auth.login("user1", "pass")
        manager = TaskManager(user)
        manager.add_task("Test", "", "medium", "2024-01-01 12:00")
        self.assertEqual(len(user.tasks), 1)

    def test_archive(self):
        user = User("test", "123")
        task = Task(1, "Test", "", "high", datetime.datetime.now())
        task.mark_as_completed()
        user.tasks.append(task)
        user.archive_completed()
        self.assertEqual(len(user.archived_tasks), 1)

if __name__ == "__main__":
    unittest.main()