import tkinter as tk
from tkinter import ttk
import datetime
from queries.queries import fetch_funding, fetch_total_fund, fetch_positions

def main():
    
    # Get the positions data
    data = fetch_positions()

    # Initialize helper variables
    important_positions = []
    funding_payments = {}
    max_position_notional = 0
    min_position_size = 0

    # Erase previous information from the vPERP
    tree.delete(*tree.get_children())

    # Iterate through every position
    for element in data:
        # Turn elements to float
        exchanged_position_size = float(element['exchangedPositionSize'])
        exchanged_position_notional = float(element['exchangedPositionNotional'])
        # position_size_after = float(element['positionSizeAfter'])
        # open_notional = float(element['openNotional'])

        # Check if the exchanged position size is negative, then check if exchanged position notional
        # is greater than $10,000 or the position size after greater than $10,000 SHORT
        if exchanged_position_size < 0 and abs(exchanged_position_notional) > 10000:

            # Find the most important trades
            max_position_notional = max(exchanged_position_notional, max_position_notional)
            min_position_size = min(exchanged_position_size, min_position_size)

            # Fetch trader's funding payment if we don't have it in funding_payments
            if funding_payments.get(element["trader"]) == None:
                # Code to display the total funding payment of the trader
                funding_payments[element["trader"]] = fetch_total_fund(element["trader"])
                
            # Add funding_payments to element dict
            element["fundingPayment"] = funding_payments[element["trader"]]
            important_positions.append(element)
            
    
    # Sort important positions so greater exchange position notionals are at the top.
    important_positions.sort(key=lambda x: float(x['exchangedPositionNotional']), reverse=True)

    # Iterate through important trades
    for trade in important_positions:
        trader = trade['trader']

        # Format displayed information
        exchanged_notional = "${:,}".format(int(float(trade['exchangedPositionNotional'])))
        position_size = int(float(trade['exchangedPositionSize']))
        swapped_price = str(float(trade['swappedPrice']))
        funding_payment = "${:,}".format(int(float(trade['fundingPayment'])))
        
        # Tag important positions and add them to the tree
        if float(trade['exchangedPositionNotional']) == max_position_notional:
            tree.insert("", tk.END, values=(trader, exchanged_notional, position_size, swapped_price, funding_payment), tags='important')
        elif float(trade['exchangedPositionSize']) == min_position_size:
            tree.insert("", tk.END, values=(trader, exchanged_notional, position_size, swapped_price, funding_payment), tags='important')
        else:
            tree.insert("", tk.END, values=(trader, exchanged_notional, position_size, swapped_price, funding_payment))

    # Call main every minute
    root.after(60000, main)


# Open new window with the trader's last 5 funding actvities
def show_funding_payment(trader_id, funding_data):
    # Find the most recent funding activities
    most_recent_entries = sorted(funding_data, key=lambda x: int(x["date"]), reverse=True)[:5]

    # Prepare variables for display
    for entry in most_recent_entries:
        entry["tradingVolume"] = int(float(entry["tradingVolume"]))
        entry["tradingFee"] = "${:,}".format(int(float(entry["tradingFee"])))
        timestamp = int(entry["date"])
        date = datetime.datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
        entry["date"] = date
    
    # Create a new window
    new_window = tk.Toplevel()
    new_window.title(f"Recent Fund History {trader_id}")
    new_window.geometry("700x200")

    # Create a table
    table = ttk.Treeview(new_window)
    table['columns'] = ('Trading Volume', 'Trading Fee', 'Date')

    # Format columns
    table.column("#0", width=1, stretch=tk.NO)
    table.column("Trading Volume", anchor=tk.CENTER, width=120)
    table.column("Trading Fee", anchor=tk.CENTER, width=120)
    table.column("Date", anchor=tk.CENTER, width=120)

    # Set column headings
    table.heading("#0", text="", anchor=tk.CENTER)
    table.heading("Trading Volume", text="Trading Volume", anchor=tk.CENTER)
    table.heading("Trading Fee", text="Trading Fee", anchor=tk.CENTER)
    table.heading("Date", text="Date", anchor=tk.CENTER)

    # Insert data into the table
    for entry in most_recent_entries:
        table.insert("", 'end', text="", values=(entry["tradingVolume"], entry["tradingFee"], entry["date"]))

    # Pack the table to occupy the whole window
    table.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

    new_window.mainloop()

# Event that opens the fund history
def on_row_click(event):
    item = tree.focus()
    # Getting trader ID from first column
    trader_id = tree.item(item, 'values')[0]
    # Fetch funding information
    funding = fetch_funding(trader_id)
    # Open fund history window
    show_funding_payment(trader_id, funding)

# Create the Tkinter window
root = tk.Tk()
root.title("Significant PERP Trades Information")
root.geometry("1240x600") 

# Create the Treeview widget
tree = ttk.Treeview(root)
tree["columns"] = ("Trader", "Exchanged Position Notional", "Exchanged Position Size", "Swapped Price", "Total Funding Payment")

# Configure columns
tree.column("#0", width=0, stretch=tk.NO)
tree.column("Trader", width=300)
tree.column("Exchanged Position Notional", width=200)
tree.column("Exchanged Position Size", width=200)
tree.column("Swapped Price", width=150)
tree.column("Total Funding Payment", width=200)

# Set column headings
tree.heading("#0", text="", anchor=tk.W)
tree.heading("Trader", text="Trader", anchor=tk.W)
tree.heading("Exchanged Position Notional", text="Exchanged Position Notional", anchor=tk.W)
tree.heading("Exchanged Position Size", text="Exchanged Position Size", anchor=tk.W)
tree.heading("Swapped Price", text="Swapped Price", anchor=tk.W)
tree.heading("Total Funding Payment", text="Total Funding Payment", anchor=tk.W)

# Bind function to row
tree.bind('<ButtonRelease-1>', on_row_click)

# Pack the Treeview to fill the window
tree.pack(expand=True, fill='both')

# Configure the style for Treeview (to change font and row height)
style = ttk.Style(root)
style.configure("Treeview", font=('Arial', 12), rowheight=30)
style.configure("Treeview", rowheight=30, tags={'important': {'background': 'lightgreen'}})

# Function to close window
def close_window():
    root.destroy()

# Close the window when x button pressed
root.protocol("WM_DELETE_WINDOW", close_window)

# Start fetching positions
main()

def apply_styles():
    tree.tag_configure('important', background='lightgreen')

# Call the apply_styles function after a delay to ensure all rows are inserted before applying styles
root.after(1000, apply_styles)

# Start the main Tkinter event loop
root.mainloop()
