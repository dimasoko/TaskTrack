import datetime
import unittest
from typing import Dict, List

class Task:
    def __init__(self, task_id: int, title: str, description: str, priority: str, due_date: datetime.datetime):
        self.id = task_id
        self.title = title
        self.description = description
        self.priority = priority
        self.completed = False
        self.due_date = due_date 

    def mark_as_completed(self):
        self.completed = True

    def is_overdue(self) -> bool:
        return datetime.datetime.now() > self.due_date

    def __str__(self):
        status = "✅" if self.completed else "❌"
        return f"[{status}] {self.title} (ID: {self.id}) | Приоритет: {self.priority} | Дата: {self.due_date.strftime('%Y-%m-%d %H:%M')}"

class User:
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password
        self.tasks: List[Task] = []

    def add_task(self, task: Task):
        self.tasks.append(task)

    def remove_task(self, task_id: int):
        self.tasks = [task for task in self.tasks if task.id != task_id]

class Authenticator:
    def __init__(self):
        self.users: Dict[str, User] = {}

    def register(self, username: str, password: str):
        if username in self.users:
            raise ValueError("Username already exists")
        self.users[username] = User(username, password)

    def login(self, username: str, password: str) -> User | None:
        user = self.users.get(username)
        return user if user and user.password == password else None

class TaskManager:
    def __init__(self, user: User):
        self.user = user

    def list_tasks(self):
        return self.user.tasks

    def add_task(self, title: str, description: str, priority: str, due_date_str: str):
        due_date = datetime.datetime.strptime(due_date_str, "%Y-%m-%d %H:%M")
        task = Task(len(self.user.tasks) + 1, title, description, priority, due_date)
        self.user.add_task(task)

    def mark_as_completed(self, task_id: int):
        task = next((t for t in self.user.tasks if t.id == task_id), None)
        if task:
            task.mark_as_completed()

class NotificationHandler:
    @staticmethod
    def check_all_reminders(users: Dict[str, User]):
        for user in users.values():
            for task in user.tasks:
                if not task.completed and task.is_overdue():
                    print(f"Напоминание для {user.username}: Задача '{task.title}' просрочена!")

class Storage:
    def __init__(self):
        self.data = {}

    def save(self):
        # потом дополним
        print("Данные сохранены")

# тесты
class TestTaskTracker(unittest.TestCase):
    def test_reminder(self):
        user = User("test", "123")
        task = Task(1, "Buy milk", "", "high", datetime.datetime.now() - datetime.timedelta(days=1))
        user.add_task(task)
        NotificationHandler.check_all_reminders({"test": user})
        self.assertTrue(task.is_overdue())

    def test_add_task(self):
        auth = Authenticator()
        auth.register("user1", "pass")
        user = auth.login("user1", "pass")
        manager = TaskManager(user)
        manager.add_task("Test", "", "medium", "2024-01-01 12:00")
        self.assertEqual(len(user.tasks), 1)

    def test_mark_completed(self):
        task = Task(1, "Test", "", "high", datetime.datetime.now())
        task.mark_as_completed()
        self.assertTrue(task.completed)

if __name__ == "__main__":
    unittest.main()