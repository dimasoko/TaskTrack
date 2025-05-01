import sys
import os
import json
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List

from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont, QPalette, QColor
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QTextEdit, QDateEdit, QComboBox, QPushButton,
    QDialog, QDialogButtonBox, QTabWidget, QLabel, QMessageBox,
    QTreeWidget, QTreeWidgetItem, QToolBar, QHeaderView
)

# логирование
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    filename='task_tracker.log',
    filemode='a'
)

# хранение
class Storage:
    FILENAME = "tasks.json"

    @staticmethod
    def load_data() -> dict:
        if not os.path.exists(Storage.FILENAME):
            return {"users": {}}
        try:
            with open(Storage.FILENAME, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"Failed to load {Storage.FILENAME}: {e}")
            return {"users": {}}

    @staticmethod
    def save_data(data: dict):
        try:
            with open(Storage.FILENAME, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logging.error(f"Failed to save {Storage.FILENAME}: {e}")

class TaskBase(ABC):
    def __init__(self, task_id: int, title: str, description: str,
                 due_date: datetime, priority: str):
        self._id = task_id
        self._title = title
        self._description = description
        self._due_date = due_date
        self._priority = priority  
        self._completed = False

    @property
    def id(self) -> int:
        return self._id

    @property
    def title(self) -> str:
        return self._title

    @property
    def description(self) -> str:
        return self._description

    @property
    def due_date(self) -> datetime:
        return self._due_date

    @property
    def priority(self) -> str:
        return self._priority

    @property
    def completed(self) -> bool:
        return self._completed

    @completed.setter
    def completed(self, val: bool):
        self._completed = val

    @abstractmethod
    def is_overdue(self) -> bool:
        pass

    def to_dict(self) -> dict:
        return {
            "id": self._id,
            "title": self._title,
            "description": self._description,
            "due_date": self._due_date.isoformat(),
            "priority": self._priority,
            "completed": self._completed,
            "__type__": self.__class__.__name__
        }

    @classmethod
    def from_dict(cls, data: dict) -> "TaskBase":
        due = datetime.fromisoformat(data["due_date"])
        t = Task(
            task_id=data["id"],
            title=data["title"],
            description=data["description"],
            due_date=due,
            priority=data["priority"]
        )
        t.completed = data.get("completed", False)
        return t

class Task(TaskBase):
    def is_overdue(self) -> bool:
        return not self.completed and datetime.now() > self.due_date

# юзер и логин
class User:
    def __init__(self, name: str, email: str, password: str):
        self._name = name
        self._email = email
        self._password = password
        self._tasks: List[TaskBase] = []
        self._next_id = 1

    @property
    def name(self) -> str:
        return self._name

    @property
    def email(self) -> str:
        return self._email

    def check_password(self, pwd: str) -> bool:
        return self._password == pwd

    @property
    def tasks(self) -> List[TaskBase]:
        return self._tasks

    def add_task(self, task: TaskBase):
        self._tasks.append(task)
        self._next_id = max(self._next_id, task.id + 1)

    def new_task_id(self) -> int:
        nid = self._next_id
        self._next_id += 1
        return nid

    def to_dict(self) -> dict:
        return {
            "name": self._name,
            "email": self._email,
            "password": self._password,
            "next_id": self._next_id,
            "tasks": [t.to_dict() for t in self._tasks]
        }

class Authenticator:
    def __init__(self):
        self._users: Dict[str, User] = {}
        raw = Storage.load_data()
        for email, ud in raw.get("users", {}).items():
            try:
                user = User(ud["name"], ud["email"], ud["password"])
                user._next_id = ud.get("next_id", 1)
                for td in ud.get("tasks", []):
                    user.add_task(TaskBase.from_dict(td))
                self._users[email] = user
            except Exception as e:
                logging.error(f"Error loading user {email}: {e}")

    def save(self):
        data = {"users": {email: u.to_dict() for email, u in self._users.items()}}
        Storage.save_data(data)

    def register(self, name: str, email: str, password: str):
        if email in self._users:
            raise ValueError("Пользователь с таким email уже существует")
        if not name or not email or not password:
            raise ValueError("Все поля обязательны")
        self._users[email] = User(name, email, password)
        self.save()

    def login(self, email: str, password: str) -> User:
        user = self._users.get(email)
        if not user or not user.check_password(password):
            raise ValueError("Неверный email или пароль")
        return user

class AuthWindow(QMainWindow):
    def __init__(self, auth: Authenticator):
        super().__init__()
        self.auth = auth
        self.setWindowTitle("Вход / Регистрация")
        self.setMinimumSize(400, 250)
        pal = self.palette()
        pal.setColor(QPalette.Window, QColor('#575CEB'))
        self.setPalette(pal)
        tabs = QTabWidget()
        tabs.addTab(self._build_login_tab(), "Вход")
        tabs.addTab(self._build_register_tab(), "Регистрация")
        self.setCentralWidget(tabs)

    def _build_login_tab(self) -> QWidget:
        w = QWidget()
        ly = QVBoxLayout(w)
        ly.setContentsMargins(20, 20, 20, 20)
        ly.addWidget(QLabel("Email:"))
        self.login_email = QLineEdit()
        ly.addWidget(self.login_email)
        ly.addWidget(QLabel("Пароль:"))
        self.login_pass = QLineEdit()
        self.login_pass.setEchoMode(QLineEdit.Password)
        ly.addWidget(self.login_pass)
        btn = QPushButton("Войти")
        btn.clicked.connect(self._do_login)
        ly.addWidget(btn)
        return w

    def _build_register_tab(self) -> QWidget:
        w = QWidget()
        ly = QVBoxLayout(w)
        ly.setContentsMargins(20, 20, 20, 20)
        ly.addWidget(QLabel("Имя:"))
        self.reg_name = QLineEdit()
        ly.addWidget(self.reg_name)
        ly.addWidget(QLabel("Email:"))
        self.reg_email = QLineEdit()
        ly.addWidget(self.reg_email)
        ly.addWidget(QLabel("Пароль:"))
        self.reg_pass = QLineEdit()
        self.reg_pass.setEchoMode(QLineEdit.Password)
        ly.addWidget(self.reg_pass)
        btn = QPushButton("Зарегистрироваться")
        btn.clicked.connect(self._do_register)
        ly.addWidget(btn)
        return w

    def _do_login(self):
        email = self.login_email.text().strip()
        pwd = self.login_pass.text().strip()
        try:
            user = self.auth.login(email, pwd)
            self._open_main(user)
        except ValueError as e:
            QMessageBox.critical(self, "Ошибка", str(e))

    def _do_register(self):
        name = self.reg_name.text().strip()
        email = self.reg_email.text().strip()
        pwd = self.reg_pass.text().strip()
        try:
            self.auth.register(name, email, pwd)
            QMessageBox.information(self, "Ok", "Регистрация успешна")
        except ValueError as e:
            QMessageBox.critical(self, "Ошибка", str(e))

    def _open_main(self, user):
        self.main = MainWindow(self.auth, user)
        self.main.show()
        self.close()

# окно нового таска
class TaskDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Новая задача")
        self.setMinimumWidth(400)
        ly = QVBoxLayout(self)
        ly.addWidget(QLabel("Заголовок:"))
        self.title_edit = QLineEdit()
        ly.addWidget(self.title_edit)
        ly.addWidget(QLabel("Описание:"))
        self.desc_edit = QTextEdit()
        ly.addWidget(self.desc_edit)
        ly.addWidget(QLabel("Срок выполнения:"))
        self.date_edit = QDateEdit(calendarPopup=True)
        self.date_edit.setDate(QDate.currentDate())
        ly.addWidget(self.date_edit)
        ly.addWidget(QLabel("Приоритет:"))
        self.prio_combo = QComboBox()
        self.prio_combo.addItems(["НАДО", "надо", "может и ненадо"])
        ly.addWidget(self.prio_combo)
        btns = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        ly.addWidget(btns)

    def get_data(self):
        title = self.title_edit.text().strip()
        if not title:
            raise ValueError("Заголовок обязателен")
        desc = self.desc_edit.toPlainText().strip()
        dt = self.date_edit.date()
        due = datetime(dt.year(), dt.month(), dt.day())
        prio = self.prio_combo.currentText()
        return title, desc, due, prio

# домашнее окно
class MainWindow(QMainWindow):
    def __init__(self, auth: Authenticator, user: User):
        super().__init__()
        self.auth = auth
        self.user = user
        self.setWindowTitle(f"Task Tracker — {user.name}")
        self.resize(800, 600)
        pal = self.palette()
        pal.setColor(QPalette.Window, QColor('#575CEB'))
        self.setPalette(pal)

        exit_btn = QPushButton("Выход")
        exit_btn.clicked.connect(self.close)
        tb = QToolBar()
        tb.addWidget(exit_btn)
        self.addToolBar(Qt.TopToolBarArea, tb)

        # вкладки
        tabs = QTabWidget()
        tabs.addTab(self._build_current_tab(), "Текущие задачи")
        tabs.addTab(self._build_archive_tab(), "Архив")
        self.setCentralWidget(tabs)

    def _build_current_tab(self) -> QWidget:
        w = QWidget()
        w.setAutoFillBackground(True)
        ly = QVBoxLayout(w)
        self.current_tree = QTreeWidget()
        self.current_tree.setHeaderLabels(["Заголовок", "Приоритет", "Дедлайн", "Действие", "sort"])
        hdr = self.current_tree.header()
        hdr.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        hdr.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        hdr.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        hdr.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        hdr.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        hdr.setTextElideMode(Qt.ElideNone)
        self.current_tree.setColumnHidden(4, True)
        self.current_tree.itemClicked.connect(self._on_current_item_clicked)
        ly.addWidget(self.current_tree)

        add_btn = QPushButton("Добавить задачу")
        add_btn.clicked.connect(self._add_task)
        ly.addWidget(add_btn)

        self._refresh_current()
        return w

    def _build_archive_tab(self) -> QWidget:
        w = QWidget()
        w.setAutoFillBackground(True)
        ly = QVBoxLayout(w)
        self.archive_tree = QTreeWidget()
        self.archive_tree.setHeaderLabels(["Заголовок", "Приоритет", "Дедлайн", "Действие", "sort"])
        hdr = self.archive_tree.header()
        hdr.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        hdr.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        hdr.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        hdr.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        hdr.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        hdr.setTextElideMode(Qt.ElideNone)
        self.archive_tree.setColumnHidden(4, True)
        self.archive_tree.itemClicked.connect(self._on_archive_item_clicked)
        ly.addWidget(self.archive_tree)

        self._refresh_archive()
        return w

    def _refresh_current(self):
        self.current_tree.clear()
        prio_map = {"НАДО": 3, "надо": 2, "может и ненадо": 1}
        items = []
        for t in self.user.tasks:
            if not t.completed and not t.is_overdue():
                itm = QTreeWidgetItem([
                    t.title,
                    t.priority,
                    t.due_date.strftime("%Y-%m-%d"),
                    "",
                    str(prio_map.get(t.priority, 0))
                ])
                items.append((prio_map.get(t.priority, 0), itm, t))
        for _, itm, t in sorted(items, key=lambda x: -x[0]):
            btn = QPushButton("Выполнено")
            btn.clicked.connect(lambda _, task=t: self._complete_task(task))
            self.current_tree.addTopLevelItem(itm)
            self.current_tree.setItemWidget(itm, 3, btn)
            desc_item = QTreeWidgetItem([f"Описание:", t.description, "", "", ""])
            itm.addChild(desc_item)
        self.current_tree.sortItems(4, Qt.DescendingOrder)

    def _refresh_archive(self):
        self.archive_tree.clear()
        items = []
        for t in self.user.tasks:
            if t.completed or t.is_overdue():
                itm = QTreeWidgetItem([
                    t.title,
                    t.priority,
                    t.due_date.strftime("%Y-%m-%d"),
                    "",
                    t.due_date.strftime("%Y%m%d")
                ])
                items.append((t.due_date, itm, t))
        for _, itm, t in sorted(items, key=lambda x: x[0]):
            btn = QPushButton("Удалить")
            btn.clicked.connect(lambda _, task=t: self._delete_task(task))
            self.archive_tree.addTopLevelItem(itm)
            self.archive_tree.setItemWidget(itm, 3, btn)
            desc_item = QTreeWidgetItem([f"Описание:", t.description, "", "", ""])
            itm.addChild(desc_item)
        self.archive_tree.sortItems(4, Qt.AscendingOrder)

    def _add_task(self):
        dlg = TaskDialog(self)
        if dlg.exec() == QDialog.Accepted:
            try:
                title, desc, due, prio = dlg.get_data()
                tid = self.user.new_task_id()
                task = Task(task_id=tid, title=title, description=desc,
                            due_date=due, priority=prio)
                self.user.add_task(task)
                self.auth.save()
                self._refresh_current()
                self._refresh_archive()
            except ValueError as e:
                QMessageBox.warning(self, "Ошибка", str(e))

    def _complete_task(self, task: TaskBase):
        task.completed = True
        self.auth.save()
        self._refresh_current()
        self._refresh_archive()

    def _delete_task(self, task: TaskBase):
        self.user.tasks.remove(task)
        self.auth.save()
        self._refresh_archive()

    def _on_current_item_clicked(self, item, col):
        if item.childCount():
            item.setExpanded(not item.isExpanded())

    def _on_archive_item_clicked(self, item, col):
        if item.childCount():
            item.setExpanded(not item.isExpanded())

def main():
    app = QApplication(sys.argv)
    app.setFont(QFont("Arial", 10))
    auth = Authenticator()
    win = AuthWindow(auth)
    win.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()