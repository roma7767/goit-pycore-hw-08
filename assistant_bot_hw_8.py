import pickle
from collections import UserDict
from datetime import datetime, timedelta

# --- Класи ---
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
        super().__init__(value)

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
            self.add_phone(new_phone)
            self.remove_phone(old_phone)
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

# --- Серіалізація (збереження/завантаження) ---

def save_to_file(address_book, filename="addressbook.pkl"):
    with open(filename, "wb") as file:
        pickle.dump(address_book, file)

def load_from_file(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as file:
            return pickle.load(file)
    except (FileNotFoundError, EOFError):
        return AddressBook()

# --- Декоратор для обробки помилок ---

def input_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (IndexError, ValueError, KeyError) as e:
            return f"Error: {e}"
    return wrapper

# --- Командні функції ---

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
def edit_contact(args, book):
    name, old_phone, new_phone = args
    record = book.find(name)
    if not record:
        return f"No contact with name '{name}' found."
    record.edit_phone(old_phone, new_phone)
    return f"Phone updated for {name}."

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

@input_error
def show_all(args, book):
    return str(book) if book.data else "Address book is empty."

# --- Парсинг команд ---

def parse_input(user_input):
    parts = user_input.strip().split()
    command = parts[0]
    args = parts[1:]
    return command, args

# --- Головна функція ---

def main():
    book = load_from_file()
    print("👋 Welcome to the assistant bot!")

    while True:
        user_input = input("Enter a command: ")
        command, args = parse_input(user_input)

        if command in ("close", "exit"):
            save_to_file(book)
            print("Good bye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact(args, book))
        elif command == "add-birthday":
            print(add_birthday(args, book))
        elif command == "show-birthday":
            print(show_birthday(args, book))
        elif command == "birthdays":
            print(birthdays(args, book))
        elif command == "all":
            print(show_all(args, book))
        elif command == "edit":
            print(edit_contact(args, book))   
        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()