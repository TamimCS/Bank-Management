import tkinter as tk
from tkinter import messagebox, simpledialog
import sqlite3

class Bank:
    def __init__(self):
        self.conn = sqlite3.connect('bank.db')
        self.cur = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        self.cur.execute('''CREATE TABLE IF NOT EXISTS employees (
                            employee_id INTEGER PRIMARY KEY,
                            username TEXT UNIQUE,
                            password TEXT)''')
        self.cur.execute('''CREATE TABLE IF NOT EXISTS customers (
                            customer_id INTEGER PRIMARY KEY,
                            username TEXT UNIQUE,
                            password TEXT,
                            balance REAL)''')
        self.conn.commit()

    def close_connection(self):
        self.conn.close()

    def create_employee(self, username, password):
        self.cur.execute("INSERT INTO employees (username, password) VALUES (?, ?)", (username, password))
        self.conn.commit()
        messagebox.showinfo("Success", "Employee created successfully")

    def login_employee(self, username, password):
        self.cur.execute("SELECT * FROM employees WHERE username = ? AND password = ?", (username, password))
        employee = self.cur.fetchone()
        return employee

    def create_customer(self, username, password):
        self.cur.execute("INSERT INTO customers (username, password, balance) VALUES (?, ?, ?)", (username, password, 0))
        self.conn.commit()
        messagebox.showinfo("Success", "Customer created successfully")

    def login_customer(self, username, password):
        self.cur.execute("SELECT * FROM customers WHERE username = ? AND password = ?", (username, password))
        customer = self.cur.fetchone()
        return customer

    def get_customers(self):
        self.cur.execute("SELECT * FROM customers")
        return self.cur.fetchall()

    def get_customer_balance(self, customer_id):
        self.cur.execute("SELECT balance FROM customers WHERE customer_id = ?", (customer_id,))
        balance = self.cur.fetchone()[0]
        return balance

    def deposit(self, customer_id, amount):
        current_balance = self.get_customer_balance(customer_id)
        new_balance = current_balance + amount
        self.cur.execute("UPDATE customers SET balance = ? WHERE customer_id = ?", (new_balance, customer_id))
        self.conn.commit()
        messagebox.showinfo("Success", f"Deposited {amount} successfully")

    def withdraw(self, customer_id, amount):
        current_balance = self.get_customer_balance(customer_id)
        if current_balance < amount:
            messagebox.showerror("Error", "Insufficient balance")
        else:
            new_balance = current_balance - amount
            self.cur.execute("UPDATE customers SET balance = ? WHERE customer_id = ?", (new_balance, customer_id))
            self.conn.commit()
            messagebox.showinfo("Success", f"Withdrew {amount} successfully")

class LoginGUI:
    def __init__(self, root, bank):
        self.root = root
        self.bank = bank
        self.root.title("Bank Login")
        self.create_widgets()

    def create_widgets(self):
        # Create labels and entry fields
        self.username_label = tk.Label(self.root, text="Username:")
        self.username_label.grid(row=0, column=0, padx=20, pady=10)
        self.username_entry = tk.Entry(self.root)
        self.username_entry.grid(row=0, column=1, padx=20, pady=10)

        self.password_label = tk.Label(self.root, text="Password:")
        self.password_label.grid(row=1, column=0, padx=20, pady=10)
        self.password_entry = tk.Entry(self.root, show="*")
        self.password_entry.grid(row=1, column=1, padx=20, pady=10)

        # Create login buttons
        self.employee_button = tk.Button(self.root, text="Employee Login", command=self.employee_login)
        self.employee_button.grid(row=2, column=0, columnspan=2, padx=20, pady=10)

        self.customer_button = tk.Button(self.root, text="Customer Login", command=self.customer_login)
        self.customer_button.grid(row=3, column=0, columnspan=2, padx=20, pady=10)

    def employee_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        employee = self.bank.login_employee(username, password)
        if employee:
            messagebox.showinfo("Success", "Employee login successful")
            self.root.destroy()  # Close login window
            employee_menu = EmployeeMenu(tk.Tk(), self.bank)
            employee_menu.run()
        else:
            messagebox.showerror("Error", "Invalid username or password")

    def customer_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        customer = self.bank.login_customer(username, password)
        if customer:
            messagebox.showinfo("Success", "Customer login successful")
            self.root.destroy()  # Close login window
            customer_menu = CustomerMenu(tk.Tk(), self.bank, customer[0])  # Pass customer_id
            customer_menu.run()
        else:
            messagebox.showerror("Error", "Invalid username or password")

class EmployeeMenu:
    def __init__(self, root, bank):
        self.root = root
        self.bank = bank
        self.root.title("Employee Menu")
        self.create_widgets()

    def create_widgets(self):
        # Create buttons for employee options
        self.create_customer_button = tk.Button(self.root, text="Create Customer Account", command=self.create_customer)
        self.create_customer_button.grid(row=0, column=0, padx=20, pady=10)

        self.delete_customer_button = tk.Button(self.root, text="Delete Customer Account", command=self.delete_customer)
        self.delete_customer_button.grid(row=1, column=0, padx=20, pady=10)

        self.list_customers_button = tk.Button(self.root, text="List Customer Accounts", command=self.list_customers)
        self.list_customers_button.grid(row=2, column=0, padx=20, pady=10)

        self.logout_button = tk.Button(self.root, text="Logout", command=self.logout)
        self.logout_button.grid(row=3, column=0, padx=20, pady=10)

    def create_customer(self):
        username = simpledialog.askstring("Create Customer Account", "Enter customer username:")
        password = simpledialog.askstring("Create Customer Account", "Enter customer password:")
        if username and password:
            self.bank.create_customer(username, password)

    def delete_customer(self):
        customer_id = simpledialog.askinteger("Delete Customer Account", "Enter customer ID:")
        if customer_id:
            self.bank.delete_customer(customer_id)

    def list_customers(self):
        customers = self.bank.get_customers()
        if customers:
            customer_info = "\n".join([f"ID: {customer[0]}, Username: {customer[1]}, Balance: {customer[3]}" for customer in customers])
            messagebox.showinfo("Customer Accounts", customer_info)
        else:
            messagebox.showinfo("Customer Accounts", "No customers found")

    def logout(self):
        self.root.destroy()  # Close employee menu window
        root = tk.Tk()  # Create new root window
        login = LoginGUI(root, bank)  # Show login window
        root.mainloop()

    def run(self):
        self.root.mainloop()

class CustomerMenu:
    def __init__(self, root, bank, customer_id):
        self.root = root
        self.bank = bank
        self.customer_id = customer_id
        self.root.title("Customer Menu")
        self.create_widgets()

    def create_widgets(self):
        # Create buttons for customer options
        self.check_balance_button = tk.Button(self.root, text="Check Balance", command=self.check_balance)
        self.check_balance_button.grid(row=0, column=0, padx=20, pady=10)

        self.deposit_money_button = tk.Button(self.root, text="Deposit Money", command=self.deposit_money)
        self.deposit_money_button.grid(row=1, column=0, padx=20, pady=10)

        self.withdraw_money_button = tk.Button(self.root, text="Withdraw Money", command=self.withdraw_money)
        self.withdraw_money_button.grid(row=2, column=0, padx=20, pady=10)

        self.logout_button = tk.Button(self.root, text="Logout", command=self.logout)
        self.logout_button.grid(row=3, column=0, padx=20, pady=10)

    def check_balance(self):
        balance = self.bank.get_customer_balance(self.customer_id)
        messagebox.showinfo("Balance", f"Your balance is: {balance}")

    def deposit_money(self):
        amount = simpledialog.askfloat("Deposit Money", "Enter amount to deposit:")
        if amount:
            self.bank.deposit(self.customer_id, amount)

    def withdraw_money(self):
        amount = simpledialog.askfloat("Withdraw Money", "Enter amount to withdraw:")
        if amount:
            self.bank.withdraw(self.customer_id, amount)

    def logout(self):
        self.root.destroy()  # Close customer menu window
        root = tk.Tk()  # Create new root window
        login = LoginGUI(root, bank)  # Show login window
        root.mainloop()

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    root = tk.Tk()
    bank = Bank()
    login = LoginGUI(root, bank)
    root.mainloop()
