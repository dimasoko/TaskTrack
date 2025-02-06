from datetime import datetime, timedelta

class User:
    def __init__(self, tgID: int, tgNickName: str, tgName: str):
        self.tgID = tgID
        self.tgNickName = tgNickName
        self.tgName = tgName

    def get_tgName(self) -> str:
        return self.tgName

    def get_tgNickName(self) -> str:
        return self.tgNickName

class Stat:
    def __init__(self, done: int, improgress: int):
        self.done = done
        self.improgress = improgress

    def count_done_tasks(self) -> int:
        return self.done

    def count_improgress_tasks(self) -> int:
        return self.improgress

    def get_stat(self) -> dict:
        return {
            'done': self.done,
            'inprogress': self.improgress
        }

class RecturingNotification:
    def __init__(self, time: datetime, days: int):
        self.time = time
        self.days = days

    def get_date_s_by_days(self) -> datetime:
        return datetime.now() + timedelta(days=self.days)

    def get_time(self) -> datetime:
        return self.time

    def get_days(self) -> int:
        return self.days

    def do_notify(self):
        # Логика для отправки уведомления
        pass

class Task:
    def __init__(self, name: str, description: str, priority: int):
        self.name = name
        self.description = description
        self.priority = priority

    def get_taskname(self) -> str:
        return self.name

    def get_taskdescription(self) -> str:
        return self.description

    def get_taskpriority(self) -> int:
        return self.priority

class Schedule:
    def __init__(self, endingDate: datetime):
        self.endingDate = endingDate

    def get_endingDate(self) -> datetime:
        return self.endingDate