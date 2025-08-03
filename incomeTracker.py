import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date
import json
import os

class IncomeTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Daily Income Tracker")
        self.root.geometry("800x600")
        self.root.configure(bg='#f0f8ff')
        
        # Data file path
        self.data_file = "income_data.json"
        
        # Load existing data
        self.income_entries = self.load_data()
        
        # Create GUI
        self.create_widgets()
        
        # Update total income display
        self.update_total_display()
        
        # Update income history
        self.update_income_list()
        
        # Save data when closing
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def load_data(self):
        """Load income data from JSON file"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                return []
        return []
    
    def save_data(self):
        """Save income data to JSON file"""
        try:
            with open(self.data_file, 'w') as f:
                json.dump(self.income_entries, f, indent=2)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save data: {str(e)}")
    
    def create_widgets(self):
        """Create all GUI widgets"""
        # Title
        title_frame = tk.Frame(self.root, bg='#f0f8ff')
        title_frame.pack(pady=20)
        
        title_label = tk.Label(
            title_frame, 
            text="Daily Income Tracker",
            font=('Arial', 24, 'bold'),
            bg='#f0f8ff',
            fg='#2c3e50'
        )
        title_label.pack()
        
        subtitle_label = tk.Label(
            title_frame,
            text="Track your daily earnings and watch your income grow",
            font=('Arial', 12),
            bg='#f0f8ff',
            fg='#7f8c8d'
        )
        subtitle_label.pack()
        
        # Total Income Display
        self.total_frame = tk.Frame(self.root, bg='#27ae60', relief='raised', bd=3)
        self.total_frame.pack(pady=20, padx=20, fill='x')
        
        total_label = tk.Label(
            self.total_frame,
            text="Total Income",
            font=('Arial', 16, 'bold'),
            bg='#27ae60',
            fg='white'
        )
        total_label.pack(pady=(10, 5))
        
        self.total_amount_label = tk.Label(
            self.total_frame,
            text="$0.00",
            font=('Arial', 32, 'bold'),
            bg='#27ae60',
            fg='white'
        )
        self.total_amount_label.pack(pady=(0, 10))
        
        # Input Frame
        input_frame = tk.LabelFrame(
            self.root,
            text="Add New Income",
            font=('Arial', 14, 'bold'),
            bg='#f0f8ff',
            fg='#2c3e50',
            padx=20,
            pady=10
        )
        input_frame.pack(pady=20, padx=20, fill='x')
        
        # Amount input
        amount_frame = tk.Frame(input_frame, bg='#f0f8ff')
        amount_frame.pack(fill='x', pady=5)
        
        tk.Label(
            amount_frame,
            text="Income Amount ($):",
            font=('Arial', 12),
            bg='#f0f8ff'
        ).pack(side='left')
        
        self.amount_var = tk.StringVar()
        self.amount_entry = tk.Entry(
            amount_frame,
            textvariable=self.amount_var,
            font=('Arial', 12),
            width=15
        )
        self.amount_entry.pack(side='right', padx=(10, 0))
        
        # Date input
        date_frame = tk.Frame(input_frame, bg='#f0f8ff')
        date_frame.pack(fill='x', pady=5)
        
        tk.Label(
            date_frame,
            text="Date:",
            font=('Arial', 12),
            bg='#f0f8ff'
        ).pack(side='left')
        
        self.date_var = tk.StringVar(value=date.today().strftime('%Y-%m-%d'))
        self.date_entry = tk.Entry(
            date_frame,
            textvariable=self.date_var,
            font=('Arial', 12),
            width=15
        )
        self.date_entry.pack(side='right', padx=(10, 0))
        
        # Add button
        add_button = tk.Button(
            input_frame,
            text="Add Income",
            command=self.add_income,
            font=('Arial', 12, 'bold'),
            bg='#27ae60',
            fg='white',
            padx=20,
            pady=5,
            cursor='hand2'
        )
        add_button.pack(pady=10)
        
        # Income History Frame
        history_frame = tk.LabelFrame(
            self.root,
            text="Income History",
            font=('Arial', 14, 'bold'),
            bg='#f0f8ff',
            fg='#2c3e50',
            padx=10,
            pady=10
        )
        history_frame.pack(pady=20, padx=20, fill='both', expand=True)
        
        # Treeview for income list
        columns = ('Date', 'Amount', 'ID')
        self.tree = ttk.Treeview(history_frame, columns=columns, show='headings', height=10)
        
        # Define headings
        self.tree.heading('Date', text='Date')
        self.tree.heading('Amount', text='Amount ($)')
        self.tree.heading('ID', text='')
        
        # Configure columns
        self.tree.column('Date', width=150, anchor='center')
        self.tree.column('Amount', width=150, anchor='center')
        self.tree.column('ID', width=0, stretch=False)  # Hidden column for ID
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(history_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack treeview and scrollbar
        self.tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Delete button
        delete_button = tk.Button(
            history_frame,
            text="Delete Selected",
            command=self.delete_selected,
            font=('Arial', 10),
            bg='#e74c3c',
            fg='white',
            padx=10,
            pady=5,
            cursor='hand2'
        )
        delete_button.pack(pady=10)
        
        # Statistics Frame
        stats_frame = tk.Frame(self.root, bg='#f0f8ff')
        stats_frame.pack(pady=10, padx=20, fill='x')
        
        self.stats_labels = {}
        stats_info = [
            ('Total Entries', 'entries'),
            ('Average Daily Income', 'average'),
            ('Highest Single Entry', 'highest')
        ]
        
        for i, (label_text, key) in enumerate(stats_info):
            stat_frame = tk.Frame(stats_frame, bg='white', relief='raised', bd=2)
            stat_frame.pack(side='left', fill='x', expand=True, padx=5)
            
            tk.Label(
                stat_frame,
                text=label_text,
                font=('Arial', 10),
                bg='white',
                fg='#7f8c8d'
            ).pack(pady=(5, 0))
            
            self.stats_labels[key] = tk.Label(
                stat_frame,
                text="0",
                font=('Arial', 16, 'bold'),
                bg='white',
                fg='#2c3e50'
            )
            self.stats_labels[key].pack(pady=(0, 5))
        
        # Bind Enter key to add income
        self.root.bind('<Return>', lambda event: self.add_income())
    
    def add_income(self):
        """Add new income entry"""
        try:
            amount_text = self.amount_var.get().strip()
            date_text = self.date_var.get().strip()
            
            if not amount_text:
                messagebox.showerror("Error", "Please enter an income amount")
                return
            
            amount = float(amount_text)
            if amount <= 0:
                messagebox.showerror("Error", "Income amount must be greater than 0")
                return
            
            # Validate date format
            try:
                datetime.strptime(date_text, '%Y-%m-%d')
            except ValueError:
                messagebox.showerror("Error", "Please enter date in YYYY-MM-DD format")
                return
            
            # Create new entry
            new_entry = {
                'id': datetime.now().timestamp(),
                'amount': amount,
                'date': date_text,
                'timestamp': datetime.now().isoformat()
            }
            
            self.income_entries.append(new_entry)
            
            # Clear input fields
            self.amount_var.set("")
            self.date_var.set(date.today().strftime('%Y-%m-%d'))
            
            # Update displays
            self.update_total_display()
            self.update_income_list()
            self.update_statistics()
            
            # Save data
            self.save_data()
            
            messagebox.showinfo("Success", f"Income of ${amount:.2f} added successfully!")
            
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number for income amount")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
    
    def delete_selected(self):
        """Delete selected income entry"""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select an entry to delete")
            return
        
        # Get the ID from the selected item
        item_id = float(self.tree.item(selected_item)['values'][2])
        
        # Confirm deletion
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this entry?"):
            # Remove from data
            self.income_entries = [entry for entry in self.income_entries if entry['id'] != item_id]
            
            # Update displays
            self.update_total_display()
            self.update_income_list()
            self.update_statistics()
            
            # Save data
            self.save_data()
    
    def update_total_display(self):
        """Update the total income display"""
        total = sum(entry['amount'] for entry in self.income_entries)
        self.total_amount_label.config(text=f"${total:.2f}")
    
    def update_income_list(self):
        """Update the income history list"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Sort entries by date (newest first)
        sorted_entries = sorted(self.income_entries, key=lambda x: x['date'], reverse=True)
        
        # Add entries to treeview
        for entry in sorted_entries:
            formatted_date = datetime.strptime(entry['date'], '%Y-%m-%d').strftime('%b %d, %Y')
            self.tree.insert('', 'end', values=(formatted_date, f"{entry['amount']:.2f}", entry['id']))
    
    def update_statistics(self):
        """Update statistics display"""
        if not self.income_entries:
            self.stats_labels['entries'].config(text="0")
            self.stats_labels['average'].config(text="$0.00")
            self.stats_labels['highest'].config(text="$0.00")
            return
        
        total_entries = len(self.income_entries)
        total_amount = sum(entry['amount'] for entry in self.income_entries)
        average_income = total_amount / total_entries
        highest_entry = max(entry['amount'] for entry in self.income_entries)
        
        self.stats_labels['entries'].config(text=str(total_entries))
        self.stats_labels['average'].config(text=f"${average_income:.2f}")
        self.stats_labels['highest'].config(text=f"${highest_entry:.2f}")
    
    def on_closing(self):
        """Handle application closing"""
        self.save_data()
        self.root.destroy()

def main():
    root = tk.Tk()
    app = IncomeTracker(root)
    root.mainloop()

if __name__ == "__main__":
    main()