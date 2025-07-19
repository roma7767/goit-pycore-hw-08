import pickle
from collections import UserDict
from datetime import datetime, timedelta

# ---------- КЛАСИ ----------

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    pass


class Phone(Field):
    def __init__(self, value):
        if not value.isdigit() or len(value) != 10:
            raise ValueError("Phone number must contain exactly 10 digits.")
        super().__init__(value)


class Birthday(Field):
    def __init__(self, value):
        try:
            datetime.strptime(value, "%d.%m.%Y")
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
        self.value = value


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def remove_phone(self, phone):
        phone_obj = self.find_phone(phone)
        if phone_obj:
            self.phones.remove(phone_obj)
        else:
            raise ValueError("Phone number not found.")

    def edit_phone(self, old_phone, new_phone):
        old = self.find_phone(old_phone)
        if old:
            self.remove_phone(old_phone)
            self.add_phone(new_phone)
        else:
            raise ValueError("Old phone number not found.")

    def find_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                return p
        return None

    def add_birthday(self, bday):
        self.birthday = Birthday(bday)

    def show_birthday(self):
        return self.birthday.value if self.birthday else "No birthday set"

    def __str__(self):
        phones_str = "; ".join(str(p) for p in self.phones)
        bday = f", birthday: {self.show_birthday()}" if self.birthday else ""
        return f"Contact name: {self.name.value}, phones: {phones_str}{bday}"


class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name in self.data:
            del self.data[name]

    def get_upcoming_birthdays(self):
        today = datetime.today().date()
        upcoming = []

        for record in self.data.values():
            if record.birthday:
                try:
                    bday = datetime.strptime(record.birthday.value, "%d.%m.%Y").date()
                except ValueError:
                    continue

                bday_this_year = bday.replace(year=today.year)
                if bday_this_year < today:
                    bday_this_year = bday_this_year.replace(year=today.year + 1)

                days_diff = (bday_this_year - today).days
                if 0 <= days_diff <= 7:
                    if bday_this_year.weekday() >= 5:
                        bday_this_year += timedelta(days=(7 - bday_this_year.weekday()))
                    upcoming.append((record.name.value, bday_this_year.strftime("%d.%m.%Y")))

        return upcoming

    def __str__(self):
        return "\n".join(str(record) for record in self.data.values())

# ---------- СЕРІАЛІЗАЦІЯ ----------

DATA_FILE = "addressbook.pkl"

def save_data(book):
    with open(DATA_FILE, "wb") as f:
        pickle.dump(book, f)

def load_data():
    try:
        with open(DATA_FILE, "rb") as f:
            return pickle.load(f)
    except (FileNotFoundError, EOFError):
        return AddressBook()

# ---------- ДЕКОРАТОР ДЛЯ ОБРОБКИ ПОМИЛОК ----------

def input_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (IndexError, ValueError, KeyError) as e:
            return f"Error: {e}"
    return wrapper

# ---------- КОМАНДНІ ФУНКЦІЇ ----------

@input_error
def add_contact(args, book):
    name, phone = args
    record = book.find(name)
    if not record:
        record = Record(name)
        book.add_record(record)
    record.add_phone(phone)
    return f"Contact updated: {record}"

@input_error
def change_contact(args, book):
    name, old_phone, new_phone = args
    record = book.find(name)
    if not record:
        return f"No contact with name '{name}' found."
    record.edit_phone(old_phone, new_phone)
    return f"Phone updated for {name}."

@input_error
def show_phone(args, book):
    name = args[0]
    record = book.find(name)
    if not record:
        return f"No contact with name '{name}' found."
    phones = "; ".join(p.value for p in record.phones)
    return f"{name}'s phones: {phones}"

@input_error
def show_all(args, book):
    return str(book) if book.data else "Address book is empty."

@input_error
def add_birthday(args, book):
    name, bday = args
    record = book.find(name)
    if not record:
        return f"No contact with name '{name}' found."
    record.add_birthday(bday)
    return f"Birthday added for {name}."

@input_error
def show_birthday(args, book):
    name = args[0]
    record = book.find(name)
    if not record:
        return f"No contact with name '{name}' found."
    return f"{name}'s birthday is {record.show_birthday()}."

@input_error
def birthdays(args, book):
    upcoming = book.get_upcoming_birthdays()
    if not upcoming:
        return "No upcoming birthdays this week."
    return "\n".join(f"{name}: {date}" for name, date in upcoming)

# ---------- ПАРСИНГ КОМАНД ----------

def parse_input(user_input):
    parts = user_input.strip().split()
    if not parts:
        return "", []
    command = parts[0].lower()
    args = parts[1:]
    return command, args

# ---------- ОСНОВНА ФУНКЦІЯ ----------

def main():
    book = load_data()
    print("Welcome! This is your assistant bot. Enter a command.")

    while True:
        user_input = input(">>> ").strip()
        if not user_input:
            continue

        command, args = parse_input(user_input)

        if command == "add":
            print(add_contact(args, book))
        elif command == "change":
            print(change_contact(args, book))
        elif command == "phone":
            print(show_phone(args, book))
        elif command == "add-birthday":
            print(add_birthday(args, book))
        elif command == "show-birthday":
            print(show_birthday(args, book))
        elif command == "birthdays":
            print(birthdays(args, book))
        elif command == "show" and len(args) == 1 and args[0].lower() == "all":
            print(show_all(args, book))
        elif command in ("exit", "close", "goodbye", "good", "bye"):
            save_data(book)
            print("Goodbye!")
            break
        else:
            print("Unknown command. Try again.")

# ---------- ЗАПУСК ----------

if __name__ == "__main__":
    main()

