import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from datetime import date as dt
from datetime import timedelta
from app import add_transaction, get_balance, get_all_transactions, close_connection, expense_visualization, daily_expense, predict_future_expenses, anomalous_expenses, set_budget

class FinanceTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Finance Tracker")
        self.root.geometry("500x600")

        # Title
        title_label = tk.Label(root, text="AI Finance Tracker", font=("Impact", 16))
        title_label.pack(pady=20)

        # Amount Entry
        self.amount_label = tk.Label(root, text="Amount:", font=("Arial", 12))
        self.amount_label.pack()
        self.amount_entry = tk.Entry(root)
        self.amount_entry.pack(pady=10)

        # Type (Income/Expense)
        self.type_label = tk.Label(root, text="Type:", font=("Arial", 12))
        self.type_label.pack()
        self.type_var = tk.StringVar(value="income")
        self.type_income_radio = tk.Radiobutton(root, text="Income", variable=self.type_var, value="income", font=("Comic Sans MS ", 10))
        self.type_income_radio.pack(pady=10)
        self.type_expense_radio = tk.Radiobutton(root, text="Expense", variable=self.type_var, value="expense", font=("Comic Sans MS ", 10))
        self.type_expense_radio.pack()

        # Dropdown for expense categories
        self.categories = ['Food', 'Rent', 'Utilities', 'Entertainment', 'Transportation']
        self.category_var = tk.StringVar()
        self.category_var.set(self.categories[0])  # Default category (first item)
        self.category_dropdown = tk.OptionMenu(root, self.category_var, *self.categories)
        self.category_dropdown.pack()

        # Add Transaction Button
        self.add_button = tk.Button(root, text="Add Transaction", command=self.add_transaction, font=("Comic Sans MS ", 10))
        self.add_button.pack(pady=30)

        # Budget Input and Set Button
        self.budget_label = tk.Label(root, text="Set Budget:", font=("Arial", 12))
        self.budget_label.pack()
        self.budget_entry = tk.Entry(root)
        self.budget_entry.pack(pady=5)
        self.set_budget_button = tk.Button(root, text="Set Budget", command=self.set_budget, font=("Comic Sans MS ", 10))
        self.set_budget_button.pack(pady=10)

        # Frame for row wise buttons
        buttons_frame = tk.Frame(root)
        buttons_frame.pack(pady=10)

        # Balance Button (0,0)
        self.balance_button = tk.Button(buttons_frame, text="Show Balance", command=self.show_balance, font=("Comic Sans MS ", 10))
        self.balance_button.grid(row=0, column=0, padx=5, pady=5)

        # Show Transactions Button (0,1)
        self.show_button = tk.Button(buttons_frame, text="Show All Transactions", command=self.show_transactions, font=("Comic Sans MS ", 10))
        self.show_button.grid(row=0, column=1, padx=5, pady=5)

        # Expenses Button (1,0)
        self.expenses_button = tk.Button(buttons_frame, text="Expense Chart", command=self.expense_chart, font=("Comic Sans MS ", 10))
        self.expenses_button.grid(row=1, column=0, padx=5, pady=5)

        # Month's Expenses Button (1,1)
        self.m_expense_button = tk.Button(buttons_frame, text="Month's Expense", command=self.daily_expense, font=("Comic Sans MS ", 10))
        self.m_expense_button.grid(row=1, column=1, padx=5, pady=5)

        # Predict Future Expenses Button (2,0)
        self.predict_button = tk.Button(buttons_frame, text="Predict Expenses (AI)", command=self.predict_future_expenses, font=("Comic Sans MS ", 10))
        self.predict_button.grid(row=2, column=0, padx=5, pady=5)

        # Detect anomalies Button (2,1)
        self.predict_button = tk.Button(buttons_frame, text="Anomalous Expenses", command=self.anamolous_expenses, font=("Comic Sans MS ", 10))
        self.predict_button.grid(row=2, column=1, padx=5, pady=5)

        # Ensure the database connection is closed properly when the window is closed
        root.protocol("WM_DELETE_WINDOW", self.on_closing)

    # Function to add a transaction
    def add_transaction(self):
        try:
            amount = float(self.amount_entry.get())
            category = self.category_var.get()
            type = self.type_var.get()
            date = dt.today()

            if type == "expense":
                if  get_balance() - amount > 0:
                    msg = add_transaction(amount, category, type, date)
                    self.amount_entry.delete(0, tk.END)  # Clear the fields
                    self.category_var.set(self.categories[0])  # Reset to default category
                    messagebox.showinfo("Success", "Transaction added successfully!")
                    if msg != "":
                        messagebox.showinfo("Budget info", msg, parent=self.root)
                else:
                    messagebox.showerror("Error", "Exceeding bank balance!")
            else:
                add_transaction(amount, "Salary", type, date)
                self.amount_entry.delete(0, tk.END)  # Clear the fields
                messagebox.showinfo("Success", "Transaction added successfully!")

        except ValueError:
            messagebox.showerror("Error", "Please enter a valid amount.")

    # Function to set budget
    def set_budget(self):
        try:
            budget_amount = float(self.budget_entry.get())
            if budget_amount > 0:
                set_budget(budget_amount)  # Set the global budget
                messagebox.showinfo("Success", f"Budget set to Rs.{budget_amount:.2f}")
                self.budget_entry.delete(0, tk.END)  # Clear the input field
            else:
                messagebox.showerror("Error", "Please enter a positive amount.")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid budget amount.")

    # Function to show balance
    def show_balance(self):
        balance = get_balance()
        messagebox.showinfo("Balance", f"Current Balance: Rs.{balance:.2f}")

    # Function to show all transactions
    def show_transactions(self):
        transactions = get_all_transactions()

        # Treeview window
        transactions_window = tk.Toplevel(self.root)
        transactions_window.title("All Transactions")
        transactions_window.geometry("600x400")

        # Treeview table
        tree = ttk.Treeview(transactions_window, columns=("ID", "Amount", "Category", "Type", "Date"), show="headings")
        tree.heading("ID", text="ID")
        tree.heading("Amount", text="Amount")
        tree.heading("Category", text="Category")
        tree.heading("Type", text="Type")
        tree.heading("Date", text="Date")
        tree.column("ID", width=50)
        tree.column("Amount", width=100)
        tree.column("Category", width=150)
        tree.column("Type", width=100)
        tree.column("Date", width=100)

        # Insert transactions into the treeview
        for transaction in transactions:
            tree.insert("", "end", values=(transaction[0], f"Rs.{transaction[1]:.2f}", transaction[2], transaction[3], transaction[4]))

        # Scrollbar
        scrollbar = ttk.Scrollbar(transactions_window, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        style = ttk.Style()
        style.configure("Treeview.Heading", font=("Arial", 12, "bold"), foreground="blue")
        style.configure("Treeview", font=("Arial", 10), rowheight=25)
        style.map("Treeview", background=[('selected', 'lightblue')])        
        tree.pack(expand=True, fill="both")

    # Function to show expenses
    def expense_chart(self):
        expense_visualization()

    # Function to show monthly expense graph
    def daily_expense(self):
        daily_expense()

    # Function to predict future expenses
    def predict_future_expenses(self):
        predictions = predict_future_expenses()

        # Treeview window
        predictions_window = tk.Toplevel(self.root)
        predictions_window.title("Predicted Future Expenses")
        predictions_window.geometry("500x300")

        # Treeview table
        tree = ttk.Treeview(predictions_window, columns=("Date", "Predicted Amount"), show="headings")
        tree.heading("Date", text="Date")
        tree.heading("Predicted Amount", text="Predicted Amount")
        tree.column("Date", width=150)
        tree.column("Predicted Amount", width=150)

        # Insert the predictions into the treeview
        for i, prediction in enumerate(predictions):
            predicted_date = (dt.today() + timedelta(days=i+1)).strftime("%Y-%m-%d")
            tree.insert("", "end", values=(predicted_date, f"Rs.{prediction:.2f}"))

        # Scrollbar
        scrollbar = ttk.Scrollbar(predictions_window, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        style = ttk.Style()
        style.configure("Treeview.Heading", font=("Arial", 12, "bold"), foreground="blue")
        style.configure("Treeview", font=("Arial", 10), rowheight=25)
        style.map("Treeview", background=[('selected', 'lightblue')])
        tree.pack(expand=True, fill="both")

    # Function to detect anomalies
    def anamolous_expenses(self):
        anomalies = anomalous_expenses()

        # Treeview window
        anomalies_window = tk.Toplevel(self.root)
        anomalies_window.title("Anomalous Expenses")
        anomalies_window.geometry("600x400")

        # Treeview table
        tree = ttk.Treeview(anomalies_window, columns=("Category", "Amount", "Date", "Average"), show="headings")
        tree.heading("Category", text="Category")
        tree.heading("Amount", text="Amount")
        tree.heading("Date", text="Date")
        tree.heading("Average", text="Average")
        tree.column("Category", width=150)
        tree.column("Amount", width=100)
        tree.column("Date", width=150)
        tree.column("Average", width=100)

        # Insert the anomalies into the Treeview
        if anomalies:
            for anomaly in anomalies:
                tree.insert("", "end", values=(anomaly[0], f"Rs.{anomaly[1]:.2f}", anomaly[2], f"Rs.{anomaly[3]:.2f}"))  # Category, Amount, Date, Average

        # Scrollbar
        scrollbar = ttk.Scrollbar(anomalies_window, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        style = ttk.Style()
        style.configure("Treeview.Heading", font=("Arial", 12, "bold"), foreground="blue")
        style.configure("Treeview", font=("Arial", 10), rowheight=25)
        style.map("Treeview", background=[('selected', 'lightblue')])
        tree.pack(expand=True, fill="both")

    # Properly close the database connection
    def on_closing(self):
        close_connection()
        self.root.destroy() #essential to close window

# Create Tkinter window and run the app
root = tk.Tk()
app = FinanceTrackerApp(root)

root.mainloop()