import datetime

class User:
    def __init__(self, tgID: int, tgNickName: str, tgName: str):
        self.tgID = tgID
        self.tgNickName = tgNickName
        self.tgName = tgName

    @staticmethod
    def get_user() -> tuple:
        while True:
            try:
                tgID = int(input("Укажите свой ID: "))
                break
            except ValueError:
                print("Ошибка! ID должен быть числом.")
        tgName = input("Укажите ваше имя: ").strip()
        tgNickName = input("Напишите свой никнейм: ").strip()
        return tgID, tgName, tgNickName

    @classmethod
    def create_user(cls) -> 'User':
        data = cls.get_user()
        return cls(*data)

    def print_user(self) -> None: 
        print(f"Имя: {self.tgName}, Ник: {self.tgNickName}, Telegram ID: {self.tgID}")

class Stat:
    @staticmethod
    def get_task_counts() -> tuple[int, int]:
        while True:
            try:
                done = int(input("Выполнено тасков: "))
                inprogress = int(input("Тасков в работе: "))
                if done < 0 or inprogress < 0:
                    raise ValueError
                return done, inprogress
            except ValueError:
                print("Ошибка! Введите целые неотрицательные числа.")

    @classmethod
    def create_stat(cls) -> 'Stat':
        done, inprogress = cls.get_task_counts()
        return cls(done, inprogress)

    def __init__(self, done: int, inprogress: int):
        self.done = done
        self.inprogress = inprogress

    def show_stat(self) -> None:
        print(f"Прогресс: {self.done} завершено, {self.inprogress} в работе")

class RecurringNotification:
    @staticmethod
    def validate_time(time_str: str) -> bool:
        try:
            datetime.datetime.strptime(time_str, "%H:%M")
            return True
        except ValueError:
            return False

    @classmethod
    def create_notification(cls) -> 'RecurringNotification':
        while True:
            time = input("Время уведомления (ЧЧ:ММ): ")
            if cls.validate_time(time):
                break
            print("Неверный формат времени!")
        
        while True:
            try:
                days = int(input("Интервал (дни): "))
                if days <= 0:
                    raise ValueError
                break
            except ValueError:
                print("Ошибка! Введите целое число больше 0.")

        notName = input("Название уведомления: ").strip()
        return cls(time, days, notName)

    def __init__(self, time: str, days: int, notName: str):
        self.time = time
        self.days = days
        self.notName = notName

    def show_notification(self) -> None:
        day_form = "день" if self.days == 1 else "дней"
        print(f"Уведомление '{self.notName}' каждый {self.days} {day_form} в {self.time}")

class Task:
    @classmethod
    def create_task(cls) -> 'Task':
        name = input("Название задачи: ").strip()
        description = input("Описание: ").strip()
        
        while True:
            try:
                priority = int(input("Приоритет (1-5): "))
                if 1 <= priority <= 5:
                    break
                print("Приоритет должен быть от 1 до 5")
            except ValueError:
                print("Ошибка! Введите число.")

        deadline = Schedule.get_deadline()
        return cls(name, description, priority, deadline)

    def __init__(self, name: str, description: str, priority: int, deadline: datetime.datetime):
        self.name = name
        self.description = description
        self.priority = priority
        self.deadline = deadline

    def show_task(self) -> None:
        print(f"""Задача: {self.name}
Описание: {self.description}
Приоритет: {'★'*self.priority}
Срок: {self.deadline.strftime('%d.%m.%Y')}""")

class Schedule:
    @staticmethod
    def get_deadline() -> datetime.datetime:
        while True:
            try:
                date_str = input("Дата окончания (ДД.ММ.ГГГГ): ")
                return datetime.datetime.strptime(date_str, "%d.%m.%Y")
            except ValueError:
                print("Неверный формат даты! Используйте ДД.ММ.ГГГГ")

# тест работы 
if __name__ == "__main__":
    print("=== Тест пользователя ===")
    user = User.create_user()
    user.print_user()

    print("\n=== Тест статистики ===")
    stat = Stat.create_stat()
    stat.show_stat()

    print("\n=== Тест уведомления ===")
    notif = RecurringNotification.create_notification()
    notif.show_notification()

    print("\n=== Тест задачи ===")
    task = Task.create_task()
    task.show_task()