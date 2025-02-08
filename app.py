import sqlite3
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

# Function to create a connection
def create_connection():
    conn = sqlite3.connect('finance_tracker.db')
    return conn

# Function to create a database (1st time)
def initialize_db():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS transactions (id INTEGER PRIMARY KEY, amount REAL, category TEXT, type TEXT, date TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS budget (id INTEGER PRIMARY KEY, budget_amount REAL, last_set_month TEXT)''')
    conn.commit()
    conn.close()

# Function to set budget
def set_budget(amount):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM budget")  # Reset any existing budget
    cursor.execute("INSERT INTO budget (budget_amount) VALUES (?)", (amount,))
    conn.commit()
    conn.close()

# Function to insert transactions
def add_transaction(amount, category, type, date):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO transactions (amount, category, type, date) VALUES (?, ?, ?, ?)", (amount, category, type, date))
    budget = cursor.execute("SELECT budget_amount FROM budget").fetchone()[0] or 0
    str_msg = ""
    
    # Check for budget
    if type == "expense":
        cursor.execute("SELECT SUM(amount) FROM transactions WHERE type = 'expense'")
        total_expenses = cursor.fetchone()[0] or 0
        if budget > 0:
            percent_used = (total_expenses / budget) * 100
            if percent_used >= 100:
                str_msg = ("Budget exceeded by : " + str(percent_used - 100) + "%")
            else:
                str_msg = ("Budget used : " + str(percent_used) + "%")

    conn.commit()
    conn.close()
    return str_msg

# Function to get the balance
def get_balance():
    conn = create_connection()
    cursor = conn.cursor() 
    cursor.execute("SELECT SUM(amount) FROM transactions WHERE type = 'income'")
    income = cursor.fetchone()[0] or 0
    cursor.execute("SELECT SUM(amount) FROM transactions WHERE type = 'expense'")
    expenses = cursor.fetchone()[0] or 0
    conn.close()
    return income - expenses

# Function to get all transactions
def get_all_transactions():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM transactions")
    transactions = cursor.fetchall()
    conn.close()
    return transactions

# Function to close the database connection
def close_connection():
    conn = create_connection()
    conn.close()

# Function to visualize expenses (pie chart)
def expense_visualization():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT category, SUM(amount) FROM transactions WHERE type = 'expense' GROUP BY category ORDER BY SUM(amount) DESC")
    data = cursor.fetchall()
    conn.close()

    # Create a pie chart
    categories, amounts = zip(*data)
    plt.pie(amounts, labels=categories, autopct='%1.1f%%')
    plt.title('Expense Breakdown')
    plt.show()

def daily_expense():
    current_month = datetime.now().strftime("%Y-%m")
    conn = create_connection()
    cursor = conn.cursor()

    # Get expenses for the current month
    cursor.execute("""SELECT date, SUM(amount) FROM transactions WHERE type = 'expense' AND strftime('%Y-%m', date) = ? GROUP BY date ORDER BY date""", (current_month,))
    data = cursor.fetchall()
    conn.close()

    # Create a bar graph
    days = [datetime.strptime(record[0], '%Y-%m-%d').day for record in data]
    expenses = [record[1] for record in data]
    plt.bar(days, expenses)
    plt.xlabel('Date')
    plt.ylabel('Expense')
    plt.title('Month\'s Expense')
    plt.xticks(days)
    plt.tight_layout()
    plt.show()

# Function to predict future expenses
def predict_future_expenses():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""SELECT date, SUM(amount) FROM transactions WHERE type = 'expense' GROUP BY date ORDER BY date""")
    data = cursor.fetchall()
    conn.close()

    dates = [datetime.strptime(record[0], '%Y-%m-%d') for record in data]
    amounts = [record[1] for record in data]
    days = [(date - dates[0]).days for date in dates]

    # Reshaping for the model
    days = np.array(days).reshape(-1, 1)
    amounts = np.array(amounts)

    model = LinearRegression()
    model.fit(days, amounts)

    # Predict future expenses (next 7 days)
    future_days = np.array([days[-1][0] + i for i in range(1, 8)]).reshape(-1, 1)
    predicted_expenses = model.predict(future_days)
    for i in range(len(predicted_expenses)):
        predicted_expenses[i] = int(abs(predicted_expenses[i]))

    return predicted_expenses

# Function to detect anamolous expenses
def anomalous_expenses():
    conn = create_connection()
    cursor = conn.cursor()

    # Get the total amount and count of expenses per category
    cursor.execute("""SELECT category, SUM(amount), COUNT(*) FROM transactions WHERE type = 'expense' GROUP BY category""")
    data = cursor.fetchall()

    # Average expense per category
    category_avg = {}
    for category, amount, count in data:
        category_avg[category] = amount / count

    # Get all expense transactions
    cursor.execute("""SELECT amount, category, date FROM transactions WHERE type = 'expense'ORDER BY date""")
    data = cursor.fetchall()
    conn.close()

    anomalies = []
    
    # Check transactions for anomalies
    for amount, category, date in data:
        # Anomolous if 2x the average
        if amount > category_avg[category] * 2:
            anomalies.append((category, amount, date, category_avg[category]))

    return anomalies

# Initialize the database
initialize_db()
