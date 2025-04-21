import datetime
import unittest
from typing import Dict, List, Optional
from abc import ABC, abstractmethod
import logging
import tkinter as tk
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QListWidget, QPushButton, QVBoxLayout, QWidget, QLineEdit, QLabel, QInputDialog
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    filename='task_tracker.log'
)

class BaseTaskException(Exception):
    def __init__(self, message, context=None):
        super().__init__(message)
        self.message = message
        self.context = context or {}
        self.log()

    def log(self):
        error_details = f"Ошибка: {self.message}"
        if self.context:
            error_details += f" | Контекст: {self.context}"
        logging.error(error_details)

class CustomError(BaseTaskException):
    pass

class SpecificError(CustomError):
    def __init__(self, message, context=None):
        super().__init__(message, context)
        print(f"⚠️ Специфическая ошибка: {message}")

class TaskBase(ABC):
    @abstractmethod
    def display(self) -> str:
        pass

    @abstractmethod
    def is_overdue(self) -> bool:
        pass

    @abstractmethod
    def process(self):
        """Абстрактный метод для полиморфного поведения"""
        pass

    @abstractmethod
    def report(self):
        """Абстрактный метод для отчетов"""
        pass

# Производные классы
class RegularTask(TaskBase):
    def __init__(self, task_id, title, description, priority, due_date):
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
        return f"[{status}] {self.title} (ID: {self.id}) | Приоритет: {self.priority}"

    def process(self):
        logging.info(f"Обработка обычной задачи: {self.title}")
    
    def report(self):
        return f"Задача '{self.title}' завершена"

class RecurringTask(TaskBase):
    def __init__(self, task_id, title, description, priority, due_date, frequency):
        super().__init__()
        self.id = task_id
        self.title = title
        self.description = description
        self.priority = priority
        self.completed = False
        self.due_date = due_date
        self.frequency = frequency  # 'daily', 'weekly'

    def is_overdue(self) -> bool:
        return datetime.datetime.now() > self.due_date

    def display(self) -> str:
        return f"[🔄] {self.title} (ID: {self.id}) | Частота: {self.frequency}"

    def process(self):
        logging.info(f"Обработка повторяющейся задачи: {self.title} (Частота: {self.frequency})")
    
    def report(self):
        return f"Повторяющаяся задача '{self.title}' выполнена"

# Лямбда-выражения
def filter_tasks(tasks, criteria):
    return list(filter(criteria, tasks))

def sort_tasks(tasks, key=lambda x: x.due_date):
    return sorted(tasks, key=key)

# Базовый класс пользователя
class BaseUser:
    def __init__(self, username: str):
        self._username = username

    def get_username(self):
        return self._username

# Производный класс пользователя
class User(BaseUser):
    def __init__(self, username: str, password: str):
        super().__init__(username)
        self._password = password
        self.tasks: List[TaskBase] = []  # Теперь общий интерфейс

    def add_task(self, task: TaskBase):
        self.tasks.append(task)
        logging.info(f"Добавлена задача {task.title} для {self._username}")

    def archive_completed(self):
        self.tasks = [t for t in self.tasks if not t.completed]
        logging.info(f"Архивация завершенных задач для {self._username}")

class Authenticator:
    def __init__(self):
        self.users: Dict[str, User] = {}

    def register(self, username, password):
        logging.info(f"Попытка регистрации {username}")
        if not username:
            raise SpecificError("Имя пользователя не может быть пустым", {"action": "register"})
        if username in self.users:
            raise CustomError("Пользователь уже существует", {"action": "register"})
        self.users[username] = User(username, password)
        logging.info(f"Успешная регистрация {username}")

    def login(self, username, password):
        logging.info(f"Попытка входа {username}")
        user = self.users.get(username)
        if user and user._password == password:
            logging.info(f"Успешный вход {username}")
            return user
        else:
            logging.error(f"Ошибка входа для {username}")
            return None

class TaskManager:
    def __init__(self, user: User):
        self.user = user

    def add_task(self, task_type, title, description, priority, due_date_str, **kwargs):
        due_date = datetime.datetime.strptime(due_date_str, "%Y-%m-%d %H:%M")
        task_id = len(self.user.tasks) + 1
        if task_type == "regular":
            task = RegularTask(task_id, title, description, priority, due_date)
        elif task_type == "recurring":
            frequency = kwargs.get("frequency", "weekly")
            task = RecurringTask(task_id, title, description, priority, due_date, frequency)
        else:
            raise ValueError("Неверный тип задачи")
        self.user.add_task(task)
        return task

    # использование лямбд для сортировки/фильтрации
    def get_overdue_tasks(self):
        return filter_tasks(self.user.tasks, lambda x: x.is_overdue())

    def sort_by_priority(self):
        return sort_tasks(self.user.tasks, lambda x: ["low", "medium", "high"].index(x.priority))

class TaskApp(QMainWindow):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.task_manager = TaskManager(user)

        self.setWindowTitle("Task Tracker")
        self.setGeometry(100, 100, 400, 300)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()

        self.task_list = QListWidget()
        layout.addWidget(self.task_list)

        self.title_label = QLabel("Название задачи:")
        layout.addWidget(self.title_label)
        self.title_input = QLineEdit()
        layout.addWidget(self.title_input)

        self.add_button = QPushButton("Добавить задачу")
        self.add_button.clicked.connect(self.add_task)
        layout.addWidget(self.add_button)

        central_widget.setLayout(layout)

    def add_task(self):
        title = self.title_input.text().strip()
        if not title:
            title, ok = QInputDialog.getText(self, "Новая задача", "Введите название задачи:")
            if not (ok and title.strip()):
                return
        task = self.task_manager.add_task("regular", title, "", "medium", "2025-04-22 12:00")
        self.task_list.addItem(str(task))
        self.title_input.clear()

    def run(self):
        self.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)

    auth = Authenticator()
    auth.register("test_user", "password123")
    user = auth.login("test_user", "password123")

    task_app = TaskApp(user)
    task_app.run()

    sys.exit(app.exec())