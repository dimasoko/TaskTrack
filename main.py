import datetime
import unittest
from typing import Dict, List, Optional
from abc import ABC, abstractmethod

# иерархия исключений
class BaseTaskException(Exception):
    pass

class CustomError(BaseTaskException):
    pass

class SpecificError(CustomError):
    pass

class BaseUser:
    def __init__(self, username: str):
        self._username = username  # защищенный атрибут

    def get_username(self):
        return self._username

class TaskBase(ABC):
    @abstractmethod
    def display(self) -> str:
        pass

    @abstractmethod
    def is_overdue(self) -> bool:
        pass

class Task(TaskBase): # наследуем
    def __init__(self, task_id: int, title: str, description: str, priority: str, due_date: datetime.datetime):
        try:
            if priority not in ["low", "medium", "high"]:
                raise SpecificError("Неверный уровень приоритета")
            self.id = task_id
            self.title = title
            self.description = description
            self.priority = priority
            self.completed = False
            self.due_date = due_date
        except SpecificError as se:
            print(f"Ошибка при создании задачи: {se}")
            raise
        finally:
            print("Задача обработана")

    def is_overdue(self) -> bool:
        return datetime.datetime.now() > self.due_date

    def display(self) -> str:
        status = "✅" if self.completed else "❌"
        return f"[{status}] {self.title} (ID: {self.id}) | Приоритет: {self.priority}"

    def __str__(self):
        return self.display()

    def __repr__(self):
        return f"Task({self.id}, '{self.title}', '{self.description}', '{self.priority}', {self.due_date!r})"

    def __eq__(self, other):
        if isinstance(other, Task):
            return (
                self.id == other.id and
                self.title == other.title and
                self.description == other.description and
                self.priority == other.priority and
                self.due_date == other.due_date and
                self.completed == other.completed
            )
        return False

    def mark_as_completed(self):
        self.completed = True

class User(BaseUser):
    def __init__(self, username: str, password: str):
        super().__init__(username)  # звоним конструктору базового класса
        self._password = password
        self.tasks: List[Task] = []

    def get_protected(self):
        return f"Username: {self._username}, Password: {self._password}"

    def add_task(self, task: Task):
        self.tasks.append(task)

    def archive_completed(self):
        self.tasks = [task for task in self.tasks if not task.completed]

# конструкторы
class Authenticator:
    _total_users = 0

    def __init__(self):
        self.users: Dict[str, User] = {}

    def register(self, username: str, password: str):
        try:
            if not username:
                raise SpecificError("Имя пользователя не может быть пустым")
            if username in self.users:
                raise CustomError("Пользователь уже существует")
            self.users[username] = User(username, password)
            Authenticator._total_users += 1
        except SpecificError as se:
            print(f"Специфическая ошибка: {se}")
            raise
        except CustomError as ce:
            print(f"Общая ошибка: {ce}")
            raise
        finally:
            print("Регистрация завершена")

    def login(self, username: str, password: str) -> Optional[User]:
        user = self.users.get(username)
        return user if user and user._password == password else None  # доступ к защищенному атрибуту

# строковое представление
class TaskManager:
    def __init__(self, user: User):
        self.user = user

    def add_task(self, title: str, description: str, priority: str, due_date_str: str):
        try:
            due_date = datetime.datetime.strptime(due_date_str, "%Y-%m-%d %H:%M")
            task = Task(len(self.user.tasks) + 1, title, description, priority, due_date)
            self.user.add_task(task)
        except ValueError:
            raise CustomError("Неверный формат даты")
        except SpecificError as se:
            print(f"Ошибка при создании задачи: {se}")
            raise
        finally:
            print("Обработка завершена")

# тесты
class TestTaskTracker(unittest.TestCase):
    def test_exceptions(self):
        try:
            Task(1, "Test", "", "invalid", datetime.datetime.now())
        except SpecificError:
            pass

    def test_inheritance(self):
        user = User("test", "123")
        self.assertEqual(user.get_username(), "test")
        self.assertEqual(user.get_protected(), "Username: test, Password: 123")

    def test_str_repr(self):
        task = Task(1, "Test", "", "high", datetime.datetime(2025, 1, 1))
        self.assertIn("Test", str(task))
        reloaded_task = eval(repr(task))
        self.assertEqual(reloaded_task.id, task.id)
        self.assertEqual(reloaded_task.title, task.title)
        self.assertEqual(reloaded_task.description, task.description)
        self.assertEqual(reloaded_task.priority, task.priority)
        self.assertEqual(reloaded_task.due_date, task.due_date)

    def test_auth(self):
        auth = Authenticator()
        auth.register("user1", "pass")
        user = auth.login("user1", "pass")
        self.assertIsInstance(user, User)

if __name__ == "__main__":
    unittest.main()