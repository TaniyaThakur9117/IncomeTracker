import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, date
import plotly.express as px
import plotly.graph_objects as go

# Page configuration
st.set_page_config(
    page_title="Daily Income Tracker",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #2c3e50;
        margin-bottom: 2rem;
    }
    .metric-container {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #27ae60;
    }
    .total-income {
        background: linear-gradient(90deg, #27ae60, #2ecc71);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin: 1rem 0;
    }
    .stButton > button {
        background-color: #27ae60;
        color: white;
        border: none;
        border-radius: 5px;
        padding: 0.5rem 1rem;
    }
    .stButton > button:hover {
        background-color: #219a52;
    }
</style>
""", unsafe_allow_html=True)

class IncomeTracker:
    def __init__(self):
        self.data_file = "income_data.json"
    
    def load_data(self):
        """Load income data from JSON file"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    return data if data else []
            except (json.JSONDecodeError, FileNotFoundError):
                return []
        return []
    
    def save_data(self, income_entries):
        """Save income data to JSON file"""
        try:
            with open(self.data_file, 'w') as f:
                json.dump(income_entries, f, indent=2)
            return True
        except Exception as e:
            st.error(f"Failed to save data: {str(e)}")
            return False
    
    def add_income(self, amount, date_input):
        """Add new income entry"""
        income_entries = self.load_data()
        
        new_entry = {
            'id': datetime.now().timestamp(),
            'amount': float(amount),
            'date': date_input.strftime('%Y-%m-%d'),
            'timestamp': datetime.now().isoformat()
        }
        
        income_entries.append(new_entry)
        return self.save_data(income_entries)
    
    def delete_entry(self, entry_id):
        """Delete income entry by ID"""
        income_entries = self.load_data()
        income_entries = [entry for entry in income_entries if entry['id'] != entry_id]
        return self.save_data(income_entries)
    
    def get_statistics(self):
        """Calculate and return statistics"""
        income_entries = self.load_data()
        
        if not income_entries:
            return {
                'total_amount': 0,
                'total_entries': 0,
                'average_income': 0,
                'highest_entry': 0
            }
        
        total_amount = sum(entry['amount'] for entry in income_entries)
        total_entries = len(income_entries)
        average_income = total_amount / total_entries
        highest_entry = max(entry['amount'] for entry in income_entries)
        
        return {
            'total_amount': total_amount,
            'total_entries': total_entries,
            'average_income': average_income,
            'highest_entry': highest_entry
        }
    
    def get_dataframe(self):
        """Convert income entries to pandas DataFrame"""
        income_entries = self.load_data()
        
        if not income_entries:
            return pd.DataFrame(columns=['Date', 'Amount', 'ID'])
        
        df = pd.DataFrame(income_entries)
        df['Date'] = pd.to_datetime(df['date'])
        df = df.sort_values('Date', ascending=False)
        df['Formatted_Date'] = df['Date'].dt.strftime('%b %d, %Y')
        
        return df

def main():
    # Initialize the tracker
    tracker = IncomeTracker()
    
    # Header
    st.markdown('<h1 class="main-header">💰 Daily Income Tracker</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #7f8c8d; font-size: 18px;">Track your daily earnings and watch your income grow</p>', unsafe_allow_html=True)
    
    # Get current statistics
    stats = tracker.get_statistics()
    
    # Total Income Display (prominent)
    st.markdown(f"""
    <div class="total-income">
        <h2 style="margin: 0; font-size: 1.5rem;">Total Income</h2>
        <h1 style="margin: 0; font-size: 3rem;">${stats['total_amount']:.2f}</h1>
    </div>
    """, unsafe_allow_html=True)
    
    # Create two columns for layout
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # Income Input Form
        st.subheader("📝 Add New Income")
        
        with st.form("income_form", clear_on_submit=True):
            amount_input = st.number_input(
                "Income Amount ($)",
                min_value=0.01,
                value=None,
                step=0.01,
                format="%.2f",
                placeholder="Enter amount..."
            )
            
            date_input = st.date_input(
                "Date",
                value=date.today(),
                max_value=date.today()
            )
            
            submitted = st.form_submit_button("Add Income", use_container_width=True)
            
            if submitted:
                if amount_input is not None and amount_input > 0:
                    if tracker.add_income(amount_input, date_input):
                        st.success(f"Income of ${amount_input:.2f} added successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to add income entry")
                else:
                    st.error("Please enter a valid income amount greater than 0")
        
        # Statistics
        st.subheader("📊 Statistics")
        
        col_stat1, col_stat2 = st.columns(2)
        
        with col_stat1:
            st.metric("Total Entries", stats['total_entries'])
            st.metric("Highest Entry", f"${stats['highest_entry']:.2f}")
        
        with col_stat2:
            st.metric("Average Income", f"${stats['average_income']:.2f}")
            if stats['total_entries'] > 0:
                st.metric("Per Day Avg", f"${stats['total_amount'] / max(1, stats['total_entries']):.2f}")
    
    with col2:
        # Income History
        st.subheader("📈 Income History & Analytics")
        
        df = tracker.get_dataframe()
        
        if not df.empty:
            # Create tabs for different views
            tab1, tab2, tab3 = st.tabs(["📋 History Table", "📊 Charts", "🗑️ Manage Entries"])
            
            with tab1:
                # Display income history table
                display_df = df[['Formatted_Date', 'amount']].copy()
                display_df.columns = ['Date', 'Amount ($)']
                display_df['Amount ($)'] = display_df['Amount ($)'].apply(lambda x: f"${x:.2f}")
                
                st.dataframe(
                    display_df,
                    use_container_width=True,
                    hide_index=True,
                    height=400
                )
            
            with tab2:
                # Charts
                if len(df) > 1:
                    # Line chart for income over time
                    fig_line = px.line(
                        df.sort_values('Date'),
                        x='Date',
                        y='amount',
                        title='Income Over Time',
                        labels={'amount': 'Income ($)', 'Date': 'Date'}
                    )
                    fig_line.update_traces(line_color='#27ae60', line_width=3)
                    fig_line.update_layout(title_font_size=16)
                    st.plotly_chart(fig_line, use_container_width=True)
                    
                    # Bar chart for recent entries
                    recent_df = df.head(10).sort_values('Date')
                    fig_bar = px.bar(
                        recent_df,
                        x='Formatted_Date',
                        y='amount',
                        title='Recent Income Entries',
                        labels={'amount': 'Income ($)', 'Formatted_Date': 'Date'}
                    )
                    fig_bar.update_traces(marker_color='#27ae60')
                    fig_bar.update_layout(title_font_size=16, xaxis_tickangle=-45)
                    st.plotly_chart(fig_bar, use_container_width=True)
                else:
                    st.info("Add more entries to see charts and analytics")
            
            with tab3:
                # Delete entries
                st.write("Select entries to delete:")
                
                for _, row in df.iterrows():
                    col_info, col_delete = st.columns([4, 1])
                    
                    with col_info:
                        st.write(f"**{row['Formatted_Date']}** - ${row['amount']:.2f}")
                    
                    with col_delete:
                        if st.button("🗑️", key=f"delete_{row['id']}", help="Delete this entry"):
                            if tracker.delete_entry(row['id']):
                                st.success("Entry deleted!")
                                st.rerun()
                            else:
                                st.error("Failed to delete entry")
        else:
            st.info("No income entries yet. Add your first entry using the form on the left!")
    
    # Footer
    st.markdown("---")
    st.markdown(
        '<p style="text-align: center; color: #7f8c8d; font-size: 14px;">💡 Tip: Use the sidebar to navigate and track your financial progress!</p>',
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()