from collections import UserDict
from datetime import datetime
import pickle

                                                                            # classes for working with address book
class Field:                                                                # present generic field in contact record
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):                                                           # present name field in contact record
    pass

class Phone(Field):                                                          # present phone number field in contact record
    def __init__(self, value):
        if not value.isdigit() or len(value) != 10:
            raise ValueError("Phone number must be a 10-digit number")
        super().__init__(value)

class Birthday(Field):                                                       # present birthday field in contact record
    def __init__(self, value):
        try:
            datetime.strptime(value, "%d.%m.%Y")
        except ValueError as exception:
            raise ValueError("Invalid date format. Use DD.MM.YYYY") from exception
        super().__init__(value)

class Record:                                                                # present contact record
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def remove_phone(self, phone_number):
        for phone in self.phones:
            if phone.value == phone_number:
                self.phones.remove(phone)
                return
        raise ValueError("Phone number not found")

    def edit_phone(self, old_phone, new_phone):                               # replace old_phone with new_phone
        phone_to_edit = self.find_phone(old_phone)
        if phone_to_edit:
            phone_to_edit.value = new_phone
        else:
            raise ValueError("Phone number not found")

    def __str__(self):
        phones_str = ', '.join(p.value for p in self.phones)
        birthday_str = self.birthday.value if self.birthday else "No birthday"
        return f"Contact name: {self.name.value}, phones: {phones_str}, birthday: {birthday_str}"

    def find_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                return p
        return None

class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name, None)

    def delete(self, name):
        if name in self.data:
            del self.data[name]
        else:
            raise KeyError("Contact not found")

    def get_upcoming_birthdays(self):                                        # get upcoming birthdays within next 7 days
        today = datetime.today().date()
        upcoming_birthdays = []

        for record in self.data.values():
            if record.birthday:
                birthday_date = datetime.strptime(record.birthday.value, "%d.%m.%Y").date()
                birthday_this_year = birthday_date.replace(year=today.year)

                if birthday_this_year < today:
                    birthday_this_year = birthday_this_year.replace(year=today.year + 1)

                days_until_birthday = (birthday_this_year - today).days

                if 0 <= days_until_birthday <= 7:
                    upcoming_birthdays.append({
                        "name": record.name.value,
                        "congratulation_date": birthday_this_year.strftime('%Y-%m-%d')
                    })

        return upcoming_birthdays

                                                                             # functionality of assistant
def save_address_book_to_file(address_book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(address_book, f)

def load_address_book_from_file(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            address_book = pickle.load(f)
            print('Existing addressbook loaded.')
            return address_book
    except FileNotFoundError:
        print("Address book not found. A new one has been created.")
        return AddressBook()                                  

def input_error(func):                                        # initialization of decorator for different exceptions during using bot
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            return str(e)
        except KeyError:
            return "Contact not found."
        except IndexError:
            return "Invalid command arguments."
    return inner

@input_error
def add_contact(address_book, name, phone):                    # extract name and phone number from args and add to dictionary
    record = address_book.find(name)
    if not record:
        record = Record(name)
        address_book.add_record(record)
    record.add_phone(phone)
    return "Contact added."

@input_error
def change_contact(address_book, name, old_phone, new_phone):  # extract name and phone number from args and update dictionary
    record = address_book.find(name)
    if record:
        record.edit_phone(old_phone, new_phone)
        return "Contact changed."
    else:
        return "Contact not found."

@input_error
def show_phone(address_book, name):                             # extract name from args and look up phone number in dictionary
    record = address_book.find(name)
    if record:
        return ', '.join(p.value for p in record.phones)
    else:
        return "Contact not found."

@input_error
def show_all(address_book):                                     # show all contacts in dictionary
    return '\n'.join(str(record) for record in address_book.values())

@input_error
def add_birthday(address_book, name, birthday):                 # add birthday to existing contact in dictionary
    record = address_book.find(name)
    if record:
        record.add_birthday(birthday)
        return "Birthday added."        
    else:                                                       # if contact not exist -> msg
        return "Contact not found."

@input_error
def show_birthday(address_book, name):                          # show bdate for current user if record is in dictionary
    record = address_book.find(name)
    if record and record.birthday:
        return f"Birthday for contact {name}: {record.birthday}"
    elif record:
        return f"No birthday found for contact {name}."
    else:                                                       # if contact not exist -> msg
        return "Contact not found."

@input_error
def birthdays(address_book):                                    # show upcoming birthdays within the next 7 days
    upcoming_birthdays = address_book.get_upcoming_birthdays()
    if upcoming_birthdays:
        return "\n".join(f"Contact name: {ub['name']}, congratulation date: {ub['congratulation_date']}" for ub in upcoming_birthdays)
    else:
        return "No upcoming birthdays."

def parse_input(user_input):                                    # parse input from user
    if not user_input.strip():                                  # empty enter check
        return "Invalid command.", []
    cmd, *args = user_input.split()                             # split input into command and arguments
    cmd = cmd.strip().lower()                                   # convert to lowercase for case insensitivity
    return cmd, args

def main():
    print("Welcome to the assistant bot!")                      # 1st action - show greeting msg
    address_book = load_address_book_from_file()                # 2nd action - call load function
    
    while True:
        user_input = input("Enter a command: ")
        command, args = parse_input(user_input)
                                                                # commands block
        if command in ["close", "exit"]:
            print("Contact data saved. Good bye!")
            save_address_book_to_file(address_book)
            break

        elif command == "hello":
            print("How can I help you?")

        elif command == "add":
            if len(args) < 2:
                print("Give me name and phone please.")
            elif len(args[1]) != 10 or not args[1].isdigit():
                print("Phone number must be a 10-digit number")
            else:
                name, phone = args
                print(add_contact(address_book, name, phone))

        elif command == "change":
            if len(args) < 3:
                print("Give me name, old phone, and new phone please.")
            else:
                name, old_phone, new_phone = args
                print(change_contact(address_book, name, old_phone, new_phone))

        elif command == "phone":
            if len(args) < 1:
                print("Enter the name for the command")
            else:
                name = args[0]
                result = show_phone(address_book, name)
                if result:
                    print(f'Phone number for contact {name}: {result}')
                else:
                    print('Contact not found.')

        elif command == "remove":
            if len(args) < 1:
                print("Enter the name for the command 'remove'")
            else:
                name = args[0]
                try:
                    address_book.delete(name)
                    print(f"Contact '{name}' removed.")
                except KeyError:
                    print(f"Contact '{name}' not found.")

        elif command == "all":
            if not address_book:
                print("Contact list is empty")
            else:
                print(show_all(address_book))

        elif command == "add-birthday":
            if len(args) < 2:
                print("Give me name and birthday please.")
            else:
                name, birthday = args
                print(add_birthday(address_book, name, birthday))

        elif command == "show-birthday":
            if len(args) < 1:
                print("Enter the name for the command 'show-birthday'")
            else:
                name = args[0]
                print(show_birthday(address_book, name))

        elif command == "birthdays":
            print(birthdays(address_book))

        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()
