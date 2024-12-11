from collections import UserDict
from datetime import *
import pickle



class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    def __init__(self, value):
        if len(value) <= 1:
            raise ValueError("Ім'я не може бути менше 1 букви")
        super().__init__(value)
        
class Phone(Field):
    def __init__(self, value):
        if len(value) != 10:
            raise ValueError("Невірна довжина номера")
        elif not value.isdigit():
            raise ValueError('Введіть лише цифри')
        super().__init__(value)

        
class Birthday(Field):
    def __init__(self, value):
        if datetime.strptime(value, "%d.%m.%Y").date():
            self.data = value
            super().__init__(value)
        else:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
        

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self,phone):
        self.phones.append(Phone(phone))
        
    def add_birthday(self,birthday):
        self.birthday = Birthday(birthday)
        
    def find_phone(self,user_phone):
        for phone in self.phones:
            if phone.value == user_phone:
                return phone

    def edit_phone(self,old_phone, new_phone):
        
        for phone in self.phones:  
            if phone.value == old_phone:
                self.phones.append(Phone(new_phone))
                self.phones.remove(phone)
                return
        raise ValueError('Відсутній телефон')
                
            
    def remove_phone(self,remove):
        for phone in self.phones:  
            if phone.value == remove:
                self.phones.remove(phone)
                break
    
    def __str__(self):
        return f"Contact name: {self.name.value.title()}, phones: {'; '.join(p.value for p in self.phones)}, birthday: {self.birthday}"

class AddressBook(UserDict):
    
    def add_record(self,rec):
        self.data[rec.name.value] = rec

    def find(self,obj):
        return self.data.get(obj)
    
    def delete(self,user):
        return self.data.pop(user)
    
    def find_next_weekday(self,start_date, weekday):
        days_ahead = weekday - start_date.weekday()
        if days_ahead <= 0:
            days_ahead += 7
        return start_date + timedelta(days=days_ahead)
    
    def get_upcoming_birthdays(self, days=7):
        upcoming_birthdays = []
        now = datetime.today().date()

        for user in self.data.values():
            
            if user.birthday:
                datetime_birthday = datetime.strptime(user.birthday.value, "%d.%m.%Y").date()
                this_year = datetime_birthday.replace(year=now.year)
                if this_year < now:
                    this_year = this_year.replace(year=now.year + 1)
        
                if 0 <= (this_year - now).days <= days:
                    if this_year.weekday() >= 5:
                        this_year = self.find_next_weekday(this_year,0)
                    birth_date = this_year.strftime("%Y.%m.%d")
                    upcoming_birthdays.append(f'{user.name.value.title()} birthday is coming up soon - {birth_date}')
        return upcoming_birthdays

    def __str__(self):
        return '\n'.join([str(x) for x in self.data.values()])

def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError:
            return "Not found"
        except ValueError as e:
            return e  
        except IndexError:
            return "Index error."
    return inner


# Додавання контактів
@input_error
def add_contact(args, book=None):
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message



# Зміна контактів
@input_error
def change_contact(args, book):
    name, old_phone, new_phone, *_ = args
    record = book.find(name)
    if record:
        record.edit_phone(old_phone, new_phone)
        return f'{name.title()} have new phone {new_phone}'
    else:
        raise KeyError

# # Виведення контакту
@input_error
def show_phone(args, book = None):
    name = args[0]
    record = book.find(name)
    if record:
        return "; ".join([str(phone) for phone in record.phones])
    else:
        return KeyError

# Вивід всіх контактів
def all(book):
    return "\n".join([str(record) for record in book.data.values()])

@input_error
def add_birthday(args, book):
    name, birthday, *_ = args
    record = book.find(name)
    if record:
        record.add_birthday(birthday)
        return "Birthday added."
    else:
        raise KeyError

@input_error
def show_birthday(args, book):
    name = args[0]
    record = book.find(name)
    return str(record.birthday)

def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd,*args



def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()  # Повернення нової адресної книги, якщо файл не знайдено



def main():
    book = load_data()
    print("Welcome to the assistant bot!")

    while True:
        user_input = input("Enter a command: ").strip().lower()
        command, *args = parse_input(user_input)

        try:
            if command in ["close", "exit","0"]:
                print("Good buy!")
                save_data(book)
                break
            elif command == "hello":
                print("How can i help you?\nadd *name *phone - added contact\nchange *name *new-phone *old-phone - change contact\nphone *name - show contact\nadd-birthday *name *date(DD.MM.YYYY)\nshow-birthday *name - show contact birthday\nbirthdays - shows upcoming birthdays\nall - all contacts")
            elif command == "add":
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
                birthdays = book.get_upcoming_birthdays()
                if birthdays:
                    for i in birthdays:
                        print(i)
                else:
                    print('No one has a birthday coming up.')
            elif command == "all":
                print(all(book))
            else:
                print("Invalid command.")
        finally:
            save_data(book)



if __name__ == '__main__':
    main()