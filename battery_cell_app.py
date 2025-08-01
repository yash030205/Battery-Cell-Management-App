import streamlit as st
import random
import json
import pandas as pd
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

# Configure page
st.set_page_config(
    page_title="Battery Cell Management System",
    page_icon="🔋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'cells_data' not in st.session_state:
    st.session_state.cells_data = {}
if 'tasks_data' not in st.session_state:
    st.session_state.tasks_data = {}
if 'task_counter' not in st.session_state:
    st.session_state.task_counter = 0

def get_cell_parameters(cell_type):
    """Get default parameters for different cell types"""
    if cell_type.lower() == "lfp":
        return {
            "voltage": 3.2,
            "min_voltage": 2.8,
            "max_voltage": 3.6
        }
    else:  # NMC or other
        return {
            "voltage": 3.6,
            "min_voltage": 3.2,
            "max_voltage": 4.0
        }

def calculate_capacity(voltage, current):
    """Calculate capacity based on voltage and current"""
    return round(voltage * current, 2)

def validate_cc_cp_input(input_str):
    """Validate CC/CP input format (e.g., '5A' or '10W')"""
    if not input_str:
        return False, "Input cannot be empty"
    
    input_str = input_str.strip().upper()
    if input_str.endswith('A') or input_str.endswith('W'):
        try:
            float(input_str[:-1])
            return True, "Valid format"
        except ValueError:
            return False, "Invalid number format"
    else:
        return False, "Must end with 'A' (Amperes) or 'W' (Watts)"

def reset_all_data():
    """Reset all session state data"""
    st.session_state.cells_data = {}
    st.session_state.tasks_data = {}
    st.session_state.task_counter = 0
    st.success("All data has been reset!")

def export_data():
    """Export all data as JSON"""
    export_data = {
        "timestamp": datetime.now().isoformat(),
        "cells": st.session_state.cells_data,
        "tasks": st.session_state.tasks_data
    }
    return json.dumps(export_data, indent=2)

# Main app title
st.title("🔋 Battery Cell Management System")
st.markdown("---")

# Sidebar for theme and controls
with st.sidebar:
    st.header("🎛️ Controls")
    
    # Theme toggle (visual only)
    theme = st.selectbox("🎨 Theme", ["Light", "Dark"])
    
    st.markdown("---")
    
    # Data management buttons
    st.header("📊 Data Management")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ Reset All", type="secondary"):
            reset_all_data()
    
    with col2:
        if st.button("📥 Export JSON", type="primary"):
            export_json = export_data()
            st.download_button(
                label="💾 Download",
                data=export_json,
                file_name=f"battery_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
    
    # Display summary stats
    st.markdown("---")
    st.header("📈 Summary")
    st.metric("Total Cells", len(st.session_state.cells_data))
    st.metric("Total Tasks", len(st.session_state.tasks_data))

# Main content area with tabs
tab1, tab2, tab3 = st.tabs(["🔋 Cell Configuration", "⚙️ Task Management", "📊 Data Overview"])

# Tab 1: Cell Configuration
with tab1:
    st.header("Battery Cell Configuration")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Cell input form
        with st.form("cell_form"):
            st.subheader("Add New Cell")
            
            cell_type = st.selectbox(
                "Cell Type",
                ["LFP", "NMC", "LTO", "LCO"],
                help="Select the battery cell chemistry type"
            )
            
            num_cells = st.number_input(
                "Number of Cells to Add",
                min_value=1,
                max_value=20,
                value=1,
                help="How many cells of this type to add"
            )
            
            # Advanced options in expander
            with st.expander("🔧 Advanced Options"):
                custom_voltage = st.checkbox("Custom Voltage Settings")
                if custom_voltage:
                    voltage = st.number_input("Voltage (V)", value=3.2, min_value=0.1, max_value=5.0, step=0.1)
                    min_voltage = st.number_input("Min Voltage (V)", value=2.8, min_value=0.1, max_value=5.0, step=0.1)
                    max_voltage = st.number_input("Max Voltage (V)", value=3.6, min_value=0.1, max_value=5.0, step=0.1)
                else:
                    params = get_cell_parameters(cell_type)
                    voltage = params["voltage"]
                    min_voltage = params["min_voltage"]
                    max_voltage = params["max_voltage"]
                
                custom_current = st.checkbox("Set Initial Current")
                if custom_current:
                    current = st.number_input("Current (A)", value=0.0, step=0.1)
                else:
                    current = 0.0
            
            submitted = st.form_submit_button("➕ Add Cells", type="primary")
            
            if submitted:
                for i in range(num_cells):
                    cell_id = len(st.session_state.cells_data) + 1
                    cell_key = f"cell_{cell_id}_{cell_type.lower()}"
                    
                    temp = round(random.uniform(25, 40), 1)
                    capacity = calculate_capacity(voltage, current)
                    
                    st.session_state.cells_data[cell_key] = {
                        "cell_type": cell_type,
                        "voltage": voltage,
                        "current": current,
                        "temperature": temp,
                        "capacity": capacity,
                        "min_voltage": min_voltage,
                        "max_voltage": max_voltage
                    }
                
                st.success(f"Added {num_cells} {cell_type} cell(s) successfully!")
                st.rerun()
    
    with col2:
        # Quick stats
        if st.session_state.cells_data:
            st.subheader("Quick Stats")
            
            # Cell type distribution
            cell_types = [cell['cell_type'] for cell in st.session_state.cells_data.values()]
            type_counts = pd.Series(cell_types).value_counts()
            
            fig = px.pie(
                values=type_counts.values,
                names=type_counts.index,
                title="Cell Type Distribution"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Display existing cells
    if st.session_state.cells_data:
        st.subheader("Current Cells")
        
        # Convert to DataFrame for better display
        cells_df = pd.DataFrame.from_dict(st.session_state.cells_data, orient='index')
        cells_df.index.name = 'Cell ID'
        
        # Interactive dataframe
        st.dataframe(
            cells_df,
            use_container_width=True,
            column_config={
                "voltage": st.column_config.NumberColumn("Voltage (V)", format="%.2f V"),
                "current": st.column_config.NumberColumn("Current (A)", format="%.2f A"),
                "temperature": st.column_config.NumberColumn("Temperature (°C)", format="%.1f °C"),
                "capacity": st.column_config.NumberColumn("Capacity", format="%.2f"),
                "min_voltage": st.column_config.NumberColumn("Min V", format="%.2f V"),
                "max_voltage": st.column_config.NumberColumn("Max V", format="%.2f V"),
            }
        )
        
        # Temperature visualization
        if len(cells_df) > 1:
            fig = px.bar(
                x=cells_df.index,
                y=cells_df['temperature'],
                title="Cell Temperature Distribution",
                labels={'x': 'Cell ID', 'y': 'Temperature (°C)'}
            )
            st.plotly_chart(fig, use_container_width=True)

# Tab 2: Task Management
with tab2:
    st.header("Task Configuration")
    
    # Task input form
    with st.form("task_form"):
        st.subheader("Add New Task")
        
        task_type = st.selectbox(
            "Task Type",
            ["CC_CV", "IDLE", "CC_CD"],
            help="Select the type of task to configure"
        )
        
        # Common fields
        time_seconds = st.number_input(
            "Duration (seconds)",
            min_value=1,
            value=60,
            help="How long should this task run"
        )
        
        # Task-specific fields
        if task_type == "CC_CV":
            st.markdown("**Constant Current - Constant Voltage Parameters**")
            col1, col2 = st.columns(2)
            
            with col1:
                cc_input = st.text_input(
                    "CC/CP Value",
                    placeholder="e.g., 5A or 10W",
                    help="Enter current in Amperes (A) or power in Watts (W)"
                )
                cv_voltage = st.number_input("CV Voltage (V)", value=3.6, step=0.1)
            
            with col2:
                current = st.number_input("Current (A)", value=1.0, step=0.1)
                capacity = st.number_input("Capacity", value=1.0, step=0.1)
        
        elif task_type == "IDLE":
            st.markdown("**Idle Task Parameters**")
            st.info("This task will keep the system idle for the specified duration.")
        
        elif task_type == "CC_CD":
            st.markdown("**Constant Current - Constant Discharge Parameters**")
            col1, col2 = st.columns(2)
            
            with col1:
                cc_input = st.text_input(
                    "CC/CP Value",
                    placeholder="e.g., 5A or 10W",
                    help="Enter current in Amperes (A) or power in Watts (W)"
                )
                voltage = st.number_input("Voltage (V)", value=3.2, step=0.1)
            
            with col2:
                capacity = st.number_input("Capacity", value=1.0, step=0.1)
        
        task_submitted = st.form_submit_button("➕ Add Task", type="primary")
        
        if task_submitted:
            # Validate inputs
            valid = True
            error_messages = []
            
            if task_type in ["CC_CV", "CC_CD"]:
                is_valid, msg = validate_cc_cp_input(cc_input)
                if not is_valid:
                    valid = False
                    error_messages.append(f"CC/CP Input: {msg}")
            
            if valid:
                st.session_state.task_counter += 1
                task_key = f"task_{st.session_state.task_counter}"
                
                task_data = {
                    "task_type": task_type,
                    "time_seconds": time_seconds
                }
                
                if task_type == "CC_CV":
                    task_data.update({
                        "cc_cp": cc_input,
                        "cv_voltage": cv_voltage,
                        "current": current,
                        "capacity": capacity
                    })
                elif task_type == "CC_CD":
                    task_data.update({
                        "cc_cp": cc_input,
                        "voltage": voltage,
                        "capacity": capacity
                    })
                
                st.session_state.tasks_data[task_key] = task_data
                st.success(f"Added {task_type} task successfully!")
                st.rerun()
            else:
                for error in error_messages:
                    st.error(error)
    
    # Display existing tasks
    if st.session_state.tasks_data:
        st.subheader("Current Tasks")
        
        for i, (task_key, task_data) in enumerate(st.session_state.tasks_data.items(), 1):
            with st.expander(f"📋 Task {i}: {task_data['task_type']}", expanded=False):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    # Display task details
                    st.json(task_data)
                
                with col2:
                    if st.button(f"🗑️ Delete", key=f"delete_{task_key}"):
                        del st.session_state.tasks_data[task_key]
                        st.rerun()
        
        # Task timeline visualization
        if len(st.session_state.tasks_data) > 1:
            st.subheader("Task Timeline")
            
            # Create timeline data
            timeline_data = []
            cumulative_time = 0
            
            for task_key, task_data in st.session_state.tasks_data.items():
                start_time = cumulative_time
                end_time = cumulative_time + task_data['time_seconds']
                timeline_data.append({
                    'Task': task_key,
                    'Start': start_time,
                    'Finish': end_time,
                    'Type': task_data['task_type']
                })
                cumulative_time = end_time
            
            # Create Gantt chart
            fig = px.timeline(
                timeline_data,
                x_start="Start",
                x_end="Finish",
                y="Task",
                color="Type",
                title="Task Execution Timeline"
            )
            st.plotly_chart(fig, use_container_width=True)

# Tab 3: Data Overview
with tab3:
    st.header("Complete Data Overview")
    
    if st.session_state.cells_data or st.session_state.tasks_data:
        col1, col2 = st.columns(2)
        
        with col1:
            if st.session_state.cells_data:
                st.subheader("🔋 Cells Summary")
                
                # Summary metrics
                total_capacity = sum(cell['capacity'] for cell in st.session_state.cells_data.values())
                avg_temp = sum(cell['temperature'] for cell in st.session_state.cells_data.values()) / len(st.session_state.cells_data)
                avg_voltage = sum(cell['voltage'] for cell in st.session_state.cells_data.values()) / len(st.session_state.cells_data)
                
                metric_col1, metric_col2, metric_col3 = st.columns(3)
                with metric_col1:
                    st.metric("Total Capacity", f"{total_capacity:.2f}")
                with metric_col2:
                    st.metric("Avg Temperature", f"{avg_temp:.1f}°C")
                with metric_col3:
                    st.metric("Avg Voltage", f"{avg_voltage:.2f}V")
                
                # Detailed cell data
                with st.expander("📊 Detailed Cell Data"):
                    st.json(st.session_state.cells_data)
        
        with col2:
            if st.session_state.tasks_data:
                st.subheader("⚙️ Tasks Summary")
                
                # Task metrics
                total_duration = sum(task['time_seconds'] for task in st.session_state.tasks_data.values())
                task_types = [task['task_type'] for task in st.session_state.tasks_data.values()]
                most_common_task = max(set(task_types), key=task_types.count) if task_types else "None"
                
                metric_col1, metric_col2 = st.columns(2)
                with metric_col1:
                    st.metric("Total Duration", f"{total_duration}s")
                with metric_col2:
                    st.metric("Most Common Task", most_common_task)
                
                # Detailed task data
                with st.expander("📋 Detailed Task Data"):
                    st.json(st.session_state.tasks_data)
        
        # Combined visualization
        if st.session_state.cells_data and st.session_state.tasks_data:
            st.subheader("🔄 System Overview")
            
            # Create a combined dashboard
            fig = go.Figure()
            
            # Add cell voltages
            cell_names = list(st.session_state.cells_data.keys())
            cell_voltages = [cell['voltage'] for cell in st.session_state.cells_data.values()]
            
            fig.add_trace(go.Bar(
                name='Cell Voltages',
                x=cell_names,
                y=cell_voltages,
                yaxis='y',
                offsetgroup=1
            ))
            
            fig.update_layout(
                title='Cell Voltage Overview',
                xaxis_title='Cells',
                yaxis_title='Voltage (V)',
                hovermode='x unified'
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Export section
        st.subheader("💾 Export Options")
        
        export_col1, export_col2, export_col3 = st.columns(3)
        
        with export_col1:
            if st.button("📄 Export as JSON", type="primary"):
                export_json = export_data()
                st.download_button(
                    label="💾 Download JSON",
                    data=export_json,
                    file_name=f"battery_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
        
        with export_col2:
            if st.button("📊 Export Cells as CSV"):
                if st.session_state.cells_data:
                    cells_df = pd.DataFrame.from_dict(st.session_state.cells_data, orient='index')
                    csv = cells_df.to_csv()
                    st.download_button(
                        label="💾 Download CSV",
                        data=csv,
                        file_name=f"cells_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
        
        with export_col3:
            if st.button("🔄 Submit All Data"):
                st.success("✅ All data submitted successfully!")
                st.balloons()
                
                # Display submission summary
                with st.expander("📋 Submission Summary"):
                    st.write(f"**Cells Submitted:** {len(st.session_state.cells_data)}")
                    st.write(f"**Tasks Submitted:** {len(st.session_state.tasks_data)}")
                    st.write(f"**Timestamp:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    else:
        st.info("👆 Add some cells and tasks using the tabs above to see the complete overview!")
        
        # Show getting started guide
        with st.expander("🚀 Getting Started Guide"):
            st.markdown("""
            ### Quick Start Guide:
            
            1. **🔋 Cell Configuration**
               - Go to the "Cell Configuration" tab
               - Select your cell type (LFP, NMC, etc.)
               - Choose how many cells to add
               - Click "Add Cells"
            
            2. **⚙️ Task Management**
               - Switch to the "Task Management" tab
               - Select a task type (CC_CV, IDLE, CC_CD)
               - Fill in the required parameters
               - Click "Add Task"
            
            3. **📊 Data Overview**
               - Come back to this tab to see all your data
               - Export your configuration as JSON or CSV
               - Submit your final configuration
            
            **Pro Tips:**
            - Use the sidebar controls to reset data or export anytime
            - The app automatically calculates capacity and generates random temperatures
            - All data persists during your session
            """)

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        🔋 Battery Cell Management System | Built with Streamlit
    </div>
    """,
    unsafe_allow_html=True
)