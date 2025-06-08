# Enhanced Daily Expense Manager with UI & Logic Fixes

from tkinter import *
from tkinter import ttk, messagebox
import datetime as dt
from backend import Database

# Database object
data = Database(db='Jay.db')

# Global variables
count = 0
selected_rowid = 0

# Functions
def saveRecord():
    try:
        amt = int(amtvar.get())
    except ValueError:
        messagebox.showerror("Invalid Input", "\u274C Please enter a valid number for Amount Paid.")
        return
    data.insertRecord(person_name=person_name.get(), amount_paid=amt, edate=edate.get())
    refreshData()

def setDate():
    date = dt.datetime.now()
    doevar.set(f'{date:%d %B %Y}')

def clearEntries():
    person_name.delete(0, 'end')
    amount_paid.delete(0, 'end')
    edate.delete(0, 'end')

def fetch_records():
    f = data.fetchRecord('SELECT rowid, * FROM expense_manager')
    global count
    count = 0
    for rec in f:
        tv.insert(parent='', index='end', iid=count, values=(rec[0], rec[1], rec[2], rec[3]))
        count += 1

def select_record(event):
    global selected_rowid
    selected = tv.focus()
    if not selected:
        return
    val = tv.item(selected, 'values')
    try:
        selected_rowid = val[0]
        namevar.set(val[1])
        amtvar.set(val[2])
        doevar.set(val[3])
    except Exception:
        pass

def update_record():
    global selected_rowid
    selected = tv.focus()
    if not selected_rowid:
        messagebox.showwarning("Warning", "\u26A0 Please select a record to update.")
        return
    try:
        amt = int(amtvar.get())
    except ValueError:
        messagebox.showerror("Invalid Input", "\u274C Please enter a valid number for Amount Paid.")
        return
    try:
        data.updateRecord(namevar.get(), amt, doevar.get(), selected_rowid)
        tv.item(selected, text="", values=(selected_rowid, namevar.get(), amt, doevar.get()))
    except Exception as ep:
        messagebox.showerror('Error', str(ep))
    refreshData()

def refreshData():
    clearEntries()
    for item in tv.get_children():
        tv.delete(item)
    fetch_records()

def deleteRow():
    global selected_rowid
    if not selected_rowid:
        messagebox.showwarning("Warning", "\u26A0 Please select a row to delete.")
        return
    data.removeRecord(selected_rowid)
    refreshData()

def settle_expenses():
    records = data.fetchRecord("SELECT person_name, amount_paid FROM expense_manager")
    if not records:
        messagebox.showinfo("No Data", "\u2139 No expense records found.")
        return

    total_amount = sum([r[1] for r in records])
    people = list(set([r[0] for r in records]))
    num_people = len(people)
    per_head_share = round(total_amount / num_people, 2)

    paid_dict = {}
    for name, amt in records:
        paid_dict[name] = paid_dict.get(name, 0) + amt

    balances = {}
    to_pay = []
    to_receive = []
    settled = []

    for name in people:
        paid = paid_dict.get(name, 0)
        balance = round(paid - per_head_share, 2)
        balances[name] = balance
        if abs(balance) < 0.01:
            settled.append(name)
        elif balance > 0:
            to_receive.append([name, balance])
        else:
            to_pay.append([name, -balance])

    # Sort and copy before mutation
    to_pay.sort(key=lambda x: x[1])
    to_receive.sort(key=lambda x: x[1], reverse=True)
    display_to_pay = [row.copy() for row in to_pay]
    display_to_receive = [row.copy() for row in to_receive]

    transactions = []
    i, j = 0, 0
    while i < len(to_pay) and j < len(to_receive):
        payer, pay_amt = to_pay[i]
        receiver, recv_amt = to_receive[j]
        amount = round(min(pay_amt, recv_amt), 2)
        transactions.append((payer, receiver, amount))
        to_pay[i][1] -= amount
        to_receive[j][1] -= amount
        if to_pay[i][1] <= 0.01:
            i += 1
        if to_receive[j][1] <= 0.01:
            j += 1

    popup = Toplevel(ws)
    popup.title("\U0001F4B0 Expense Settlement Summary")
    popup.geometry("600x550")
    popup.config(bg="white")

    Label(popup, text="\U0001F4BC Expense Settlement Report", font=('Segoe UI', 16, 'bold'), bg="white", fg="#2E8B57").pack(pady=(10, 5))

    text_area = Text(popup, wrap=WORD, font=('Segoe UI', 11), padx=15, pady=10, bg="#f9f9f9")
    text_area.pack(expand=True, fill=BOTH, padx=15, pady=(0, 10))

    text_area.insert(END, f"\U0001F9FE Total Expense: ₹{total_amount}\n")
    text_area.insert(END, f"\U0001F46E Number of People: {num_people}\n")
    text_area.insert(END, f"\U0001F4CC Per Head Share: ₹{per_head_share}\n")
    text_area.insert(END, "\n" + "="*60 + "\n\n")

    text_area.insert(END, "\u25BD People Who Need to Pay:\n\n")
    for name, amt in display_to_pay:
        text_area.insert(END, f"\u2022 {name:<15} \u27A4 PAY ₹{round(amt, 2)}\n")

    text_area.insert(END, "\n\u25B3 People Who Will Receive:\n\n")
    for name, amt in display_to_receive:
        text_area.insert(END, f"\u2022 {name:<15} \u27A4 RECEIVE ₹{round(amt, 2)}\n")

    if settled:
        text_area.insert(END, "\n\u2705 Already Settled:\n\n")
        for name in settled:
            text_area.insert(END, f"\u2022 {name} is SETTLED\n")

    text_area.insert(END, "\n" + "="*60 + "\n\n")
    text_area.insert(END, "\U0001F4A1 Suggested Payment Instructions:\n\n")
    for payer, receiver, amount in transactions:
        text_area.insert(END, f"\uD83D\uDC49 {payer} should PAY ₹{amount} to {receiver}\n")

    text_area.insert(END, "\n" + "="*60 + "\n")
    text_area.config(state=DISABLED)

    scrollbar = Scrollbar(popup, command=text_area.yview)
    scrollbar.pack(side=RIGHT, fill=Y)
    text_area.config(yscrollcommand=scrollbar.set)

    def copy_to_clipboard():
        ws.clipboard_clear()
        ws.clipboard_append(text_area.get("1.0", END))
        messagebox.showinfo("Copied", "\U0001F4CB Settlement Summary copied to clipboard!")

    Button(popup, text="\U0001F4CB Copy Summary", font=('Segoe UI', 10), bg="#ADD8E6", command=copy_to_clipboard).pack(pady=(0, 10))

# GUI Setup
ws = Tk()
ws.title('Daily Expense Manager')
ws.geometry("950x620")
ws.config(bg='#f4f4f4')

f = ('Segoe UI', 12)
namevar = StringVar()
amtvar = StringVar()
doevar = StringVar()

f2 = Frame(ws, bg='#f4f4f4')
f2.pack(pady=10)

f1 = Frame(ws, bg='#f4f4f4', padx=15, pady=15)
f1.pack(expand=True, fill=BOTH)

Label(f1, text='Person Name:', font=f, bg='#f4f4f4').grid(row=0, column=0, sticky=W, pady=5)
Label(f1, text='Amount Paid (₹):', font=f, bg='#f4f4f4').grid(row=1, column=0, sticky=W, pady=5)
Label(f1, text='Date:', font=f, bg='#f4f4f4').grid(row=2, column=0, sticky=W, pady=5)

person_name = Entry(f1, font=f, textvariable=namevar, bd=2, relief=GROOVE)
amount_paid = Entry(f1, font=f, textvariable=amtvar, bd=2, relief=GROOVE)
edate = Entry(f1, font=f, textvariable=doevar, bd=2, relief=GROOVE)

person_name.grid(row=0, column=1, padx=10, sticky=EW)
amount_paid.grid(row=1, column=1, padx=10, sticky=EW)
edate.grid(row=2, column=1, padx=10, sticky=EW)

button_style = dict(font=f, padx=10, pady=5)
Button(f1, text='Current Date', bg='#87CEEB', command=setDate, **button_style).grid(row=2, column=2, padx=10)
Button(f1, text='Save Record', bg='#4CAF50', fg='white', command=saveRecord, **button_style).grid(row=4, column=0, padx=10)
Button(f1, text='Clear Entry', bg='#FFA500', command=clearEntries, **button_style).grid(row=4, column=1, padx=10)
Button(f1, text='Update', bg='#6A5ACD', fg='white', command=update_record, **button_style).grid(row=4, column=2, padx=10)
Button(f1, text='Delete', bg='#DC143C', fg='white', command=deleteRow, **button_style).grid(row=4, column=3, padx=10)
Button(f1, text='Settle Expenses', bg='#FF69B4', fg='white', command=settle_expenses, **button_style).grid(row=4, column=4, padx=10)
Button(f1, text='Exit', bg='#696969', fg='white', command=ws.destroy, **button_style).grid(row=4, column=5, padx=10)

# Treeview setup
tv = ttk.Treeview(f2, columns=(1, 2, 3, 4), show='headings', height=10)
tv.pack(side="left", padx=15)

for i, col in enumerate(["Serial No.", "Person Name", "Amount Paid", "Date"], start=1):
    tv.heading(i, text=col)
tv.column(1, anchor=CENTER, stretch=NO, width=80)
tv.column(2, anchor=W, width=220)
tv.column(3, anchor=CENTER, width=120)
tv.column(4, anchor=CENTER, width=180)

tv.bind("<ButtonRelease-1>", select_record)
scrollbar = Scrollbar(f2, orient='vertical', command=tv.yview)
tv.configure(yscrollcommand=scrollbar.set)
scrollbar.pack(side='right', fill='y')

style = ttk.Style()
style.theme_use("clam")
style.configure("Treeview.Heading", font=('Segoe UI', 12, 'bold'), background="#d3d3d3")
style.configure("Treeview", font=('Segoe UI', 11), rowheight=30, background="white", fieldbackground="white")

fetch_records()
ws.mainloop()
