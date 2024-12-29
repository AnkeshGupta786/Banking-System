import random
import mysql.connector
from decimal import Decimal
from datetime import datetime
import re

# Database setup
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Ankeshgupta@416",
    database="banking_system"
)
cursor = conn.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS clients (
    id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(255),
    account_id VARCHAR(10) UNIQUE,
    birth_date DATE,
    residence VARCHAR(255),
    user_password VARCHAR(255),
    account_balance DECIMAL(10, 2),
    phone_number VARCHAR(10),
    email_address VARCHAR(255),
    home_address TEXT,
    is_active TINYINT DEFAULT 1
)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS financial_transactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    account_id VARCHAR(10),
    transaction_type VARCHAR(50),
    transaction_amount DECIMAL(10, 2),
    transaction_date DATETIME
)''')

conn.commit()

def create_account_number():
    return str(random.randint(1000000000, 9999999999))

def check_valid_email(email):
    return re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", email)

def check_valid_contact(contact):
    return re.match(r"^\d{10}$", contact)

def check_valid_password(password):
    return (len(password) >= 8 and
            any(c.isupper() for c in password) and
            any(c.isdigit() for c in password) and
            any(c in '!@#$%^&*()-_+=' for c in password))

def register_user():
    full_name = input("Enter name: ")
    birth_date = input("Enter date of birth (YYYY-MM-DD): ")
    residence = input("Enter city: ")
    user_password = input("Enter password: ")

    while not check_valid_password(user_password):
        print("Password must be at least 8 characters long, include an uppercase letter, a number, and a special character.")
        user_password = input("Enter password: ")

    account_balance = float(input("Enter initial balance (minimum 2000): "))
    while account_balance < 2000:
        print("Initial balance must be at least 2000.")
        account_balance = float(input("Enter initial balance (minimum 2000): "))

    phone_number = input("Enter contact number: ")
    while not check_valid_contact(phone_number):
        print("Invalid contact number. It must contain 10 digits.")
        phone_number = input("Enter contact number: ")

    email_address = input("Enter email ID: ")
    while not check_valid_email(email_address):
        print("Invalid email address.")
        email_address = input("Enter email ID: ")

    home_address = input("Enter address: ")

    account_id = create_account_number()

    try:
        cursor.execute('''INSERT INTO clients (full_name, account_id, birth_date, residence, user_password, account_balance, phone_number, email_address, home_address)
                         VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)''',
                       (full_name, account_id, birth_date, residence, user_password, account_balance, phone_number, email_address, home_address))
        conn.commit()
        print(f"User added successfully. Account Number: {account_id}")
    except mysql.connector.Error as err:
        print(f"Error: {err}")

def display_clients():
    cursor.execute("SELECT * FROM clients")
    clients = cursor.fetchall()
    if clients:
        for client in clients:
            print(f"ID: {client[0]}\nName: {client[1]}\nAccount Number: {client[2]}\nDOB: {client[3]}\nCity: {client[4]}\nBalance: {client[5]}\nContact: {client[6]}\nEmail: {client[7]}\nAddress: {client[8]}\nActive: {'Yes' if client[9] else 'No'}\n")
    else:
        print("No users found.")

def deposit_transfer(client):
    # Transfer amount functionality
    transfer_amount = float(input("Enter amount to transfer: "))
    if Decimal(transfer_amount) > Decimal(client[6]):
        print("Insufficient balance.")
    else:
        recipient_account = Decimal(input("Enter recipient's account number: "))
        cursor.execute("SELECT * FROM clients WHERE account_id = %s", (recipient_account,))
        recipient = cursor.fetchone()

        if recipient:
            new_sender_balance = (Decimal(client[6]) - Decimal(transfer_amount))
            new_recipient_balance = Decimal(recipient[6]) + Decimal(transfer_amount)
            cursor.execute("UPDATE clients SET account_balance = %s WHERE account_id = %s", (new_sender_balance, client[2]))
            cursor.execute("UPDATE clients SET account_balance = %s WHERE account_id = %s", (new_recipient_balance, recipient_account))
            cursor.execute("INSERT INTO financial_transactions (account_id, transaction_type, transaction_amount, transaction_date) VALUES (%s, 'Debit', %s, %s)",
                           (client[2], transfer_amount, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            cursor.execute("INSERT INTO financial_transactions (account_id, transaction_type, transaction_amount, transaction_date) VALUES (%s, 'Credit', %s, %s)",
                           (recipient_account, transfer_amount, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            conn.commit()
            print("Transfer successful.")
        else:
            print("Recipient account not found.")

def change_status(client):
    if client[9] == 1:
        cursor.execute("UPDATE clients SET is_active = 0 WHERE account_id = %s", (client[2],))
        print("Account deactivated.")
    else:
        cursor.execute("UPDATE clients SET is_active = 1 WHERE account_id = %s", (client[2],))
        print("Account activated.")
    conn.commit()

def modify_password(client):
    old_password = input("Enter your old password: ")
    if old_password == client[5]:
        new_password = input("Enter your new password: ")
        while not check_valid_password(new_password):
            print("Password must be at least 8 characters long, include an uppercase letter, a number, and a special character.")
            new_password = input("Enter new password: ")
        cursor.execute("UPDATE clients SET user_password = %s WHERE account_id = %s", (new_password, client[2]))
        conn.commit()
        print("Password changed successfully.")
    else:
        print("Old password is incorrect.")

def edit_profile(client):
    print("Updating profile...")
    full_name = input(f"Enter new name (Current: {client[1]}): ") or client[1]
    residence = input(f"Enter new city (Current: {client[4]}): ") or client[4]
    phone_number = input(f"Enter new contact number (Current: {client[6]}): ") or client[6]
    while not check_valid_contact(phone_number):
        print("Invalid contact number. It must contain 10 digits.")
        phone_number = input("Enter contact number: ")
    
    email_address = input(f"Enter new email (Current: {client[7]}): ") or client[7]
    while not check_valid_email(email_address):
        print("Invalid email address.")
        email_address = input("Enter email ID: ")
    
    home_address = input(f"Enter new address (Current: {client[8]}): ") or client[8]

    cursor.execute('''UPDATE clients SET full_name = %s, residence = %s, phone_number = %s, email_address = %s, home_address = %s 
                     WHERE account_id = %s''',
                   (full_name, residence, phone_number, email_address, home_address, client[2]))
    conn.commit()
    print("Profile updated successfully.")

def authenticate():
    account_id = input("Enter account number: ")
    user_password = input("Enter password: ")

    cursor.execute("SELECT * FROM clients WHERE account_id = %s AND user_password = %s", (account_id, user_password))
    client = cursor.fetchone()

    if client:
        print("Login successful!")
        while True:
            print("\n1. Show Balance\n2. Show Transactions\n3. Credit Amount\n4. Debit Amount\n5. Transfer Amount\n6. Activate/Deactivate Account\n7. Change Password\n8. Update Profile\n9. Logout")
            option = int(input("Enter your choice: "))

            if option == 1:
                print(f"Current Balance: {client[6]}")
            elif option == 2:
                cursor.execute("SELECT * FROM financial_transactions WHERE account_id = %s", (account_id,))
                transactions = cursor.fetchall()
                for t in transactions:
                    print(f"Type: {t[2]}, Amount: {t[3]}, Date: {t[4]}")
            elif option == 3:
                amount = float(input("Enter amount to credit: "))
                new_balance = client[6] + Decimal(amount)
                cursor.execute("UPDATE clients SET account_balance = %s WHERE account_id = %s", (new_balance, account_id))
                cursor.execute("INSERT INTO financial_transactions (account_id, transaction_type, transaction_amount, transaction_date) VALUES (%s, 'Credit', %s, %s)",
                               (account_id, amount, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
                conn.commit()
                client = list(client)
                client[6] = Decimal(new_balance)
                print("Amount credited successfully.")
            elif option == 4:
                amount = Decimal(input("Enter amount to debit: "))
                if amount > client[6]:
                    print("Insufficient balance.")
                else:
                    new_balance = client[6] - Decimal(amount)
                    cursor.execute("UPDATE clients SET account_balance = %s WHERE account_id = %s", (new_balance, account_id))
                    cursor.execute("INSERT INTO financial_transactions (account_id, transaction_type, transaction_amount, transaction_date) VALUES (%s, 'Debit', %s, %s)",
                                   (account_id, amount, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
                    conn.commit()
                    client = list(client)
                    client[6] = Decimal(new_balance)
                    print("Amount debited successfully.")
            elif option == 5:
                deposit_transfer(client)
            elif option == 6:
                change_status(client)
            elif option == 7:
                modify_password(client)
            elif option == 8:
                edit_profile(client)        
            elif option == 9:
                print("Logged out.")
                break
            else:
                print("Invalid choice.")
    else:
        print("Invalid account number or password.")

def start_system():
    while True:
        print("\nBANKING SYSTEM")
        print("1. Register User\n2. Display Users\n3. Login\n4. Exit")
        action = int(input("Enter your choice: "))

        if action == 1:
            register_user()
        elif action == 2:
            display_clients()
        elif action == 3:
            authenticate()
        elif action == 4:
            print("Exiting system.")
            break
        else:
            print("Invalid choice. Try again.")

if _name_ == "_main_":
    start_system()

conn.close()
