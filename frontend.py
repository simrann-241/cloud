import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from streamlit_plotly_events import plotly_events
import time
import datetime
import random
import json
import base64
from io import BytesIO
import matplotlib.pyplot as plt
import seaborn as sns
from PIL import Image
import cv2
import mediapipe as mp
import speech_recognition as sr
import pyttsx3
import threading
import requests
import uuid
import os
import scipy.signal as signal
import networkx as nx
import google.generativeai as genai
from stmol import showmol
import py3Dmol
import matplotlib.colors as mcolors
from matplotlib.animation import FuncAnimation
from mpl_toolkits.mplot3d import Axes3D
from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration
from streamlit_option_menu import option_menu
from streamlit_lottie import st_lottie
from streamlit_autorefresh import st_autorefresh
from streamlit_extras.switch_page_button import switch_page
from streamlit_extras.add_vertical_space import add_vertical_space
from streamlit_extras.colored_header import colored_header
from streamlit_extras.metric_cards import style_metric_cards
from streamlit_extras.chart_container import chart_container
from streamlit_extras.stylable_container import stylable_container
from streamlit_timeline import timeline
import altair as alt

# Initialize session state variables if they don't exist
if 'initialized' not in st.session_state:
    st.session_state.initialized = True
    st.session_state.dark_mode = True
    st.session_state.system_status = "Nominal"
    st.session_state.emergency_mode = False
    st.session_state.selected_module = "Dashboard"
    st.session_state.voice_assistant_active = False
    st.session_state.notifications = []
    st.session_state.crew_data = []
    st.session_state.resource_levels = {}
    st.session_state.maintenance_tasks = []
    st.session_state.power_systems = {}
    st.session_state.environmental_data = {}
    st.session_state.quantum_predictions = {}
    st.session_state.voice_log = []
    st.session_state.gesture_enabled = True
    st.session_state.last_refresh = time.time()

# Configure page settings
st.set_page_config(
    page_title="Space Habitat Management System",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS styling
def load_css():
    css = """
    <style>
        /* Main theme */
        .dark-theme {
            --background-color: #0e1117;
            --text-color: #f0f2f6;
            --card-bg: #1a1f29;
            --sidebar-bg: #262c3a;
            --highlight: #4c78e0;
            --warning: #ff9f00;
            --danger: #ff4b4b;
            --success: #00cc96;
        }
        .light-theme {
            --background-color: #f0f2f6;
            --text-color: #0e1117;
            --card-bg: #ffffff;
            --sidebar-bg: #e6e9ef;
            --highlight: #4c78e0;
            --warning: #ff9f00;
            --danger: #ff4b4b;
            --success: #00cc96;
        }
        
        /* Dashboard panels */
        .info-card {
            background-color: var(--card-bg);
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin-bottom: 20px;
            transition: transform 0.3s ease;
        }
        .info-card:hover {
            transform: translateY(-5px);
        }
        
        /* Status indicators */
        .status-nominal {
            color: var(--success);
            font-weight: bold;
        }
        .status-warning {
            color: var(--warning);
            font-weight: bold;
        }
        .status-critical {
            color: var(--danger);
            font-weight: bold;
            animation: pulse 1.5s infinite;
        }
        
        /* Animations */
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
        
        /* Override Streamlit defaults */
        .stApp {
            background-color: var(--background-color);
            color: var(--text-color);
        }
        .sidebar .sidebar-content {
            background-color: var(--sidebar-bg);
        }
        .stButton>button {
            border-radius: 20px;
            padding: 10px 24px;
            font-weight: bold;
            transition: all 0.3s ease;
        }
        .stButton>button:hover {
            transform: scale(1.05);
        }
        
        /* Custom header and footer */
        .custom-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }
        .system-time {
            font-family: 'Courier New', monospace;
            font-size: 14px;
        }
        
        /* Progress bars */
        .resource-bar {
            height: 10px;
            border-radius: 5px;
            margin-bottom: 5px;
        }
        
        /* Emergency mode styling */
        .emergency-active {
            background: rgba(255, 75, 75, 0.1);
            border: 2px solid #ff4b4b;
            animation: emergency-pulse 2s infinite;
        }
        @keyframes emergency-pulse {
            0% { box-shadow: 0 0 0 0 rgba(255, 75, 75, 0.4); }
            70% { box-shadow: 0 0 0 10px rgba(255, 75, 75, 0); }
            100% { box-shadow: 0 0 0 0 rgba(255, 75, 75, 0); }
        }
        
        /* Voice assistant styles */
        .voice-assistant-container {
            position: fixed;
            bottom: 20px;
            right: 20px;
            z-index: 1000;
        }
        .voice-button {
            width: 60px;
            height: 60px;
            border-radius: 30px;
            background-color: var(--highlight);
            display: flex;
            justify-content: center;
            align-items: center;
            cursor: pointer;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
            transition: all 0.3s ease;
        }
        .voice-button:hover {
            transform: scale(1.1);
        }
        .voice-active {
            animation: voice-pulse 1.5s infinite;
        }
        @keyframes voice-pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.1); }
            100% { transform: scale(1); }
        }
        
        /* 3D visualization container */
        .visualization-container {
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        }
        
        /* Hologram effect */
        .hologram {
            position: relative;
            overflow: hidden;
        }
        .hologram::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: linear-gradient(45deg, rgba(66, 133, 244, 0.1), rgba(66, 133, 244, 0));
            z-index: 1;
            pointer-events: none;
        }
        .hologram::after {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: repeating-linear-gradient(
                0deg,
                rgba(66, 133, 244, 0.05),
                rgba(66, 133, 244, 0.05) 1px,
                transparent 1px,
                transparent 2px
            );
            z-index: 2;
            pointer-events: none;
            animation: scan 3s linear infinite;
        }
        @keyframes scan {
            0% { background-position: 0 0; }
            100% { background-position: 0 100px; }
        }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# Load theme based on session state
theme_class = "dark-theme" if st.session_state.dark_mode else "light-theme"
st.markdown(f"""
    <div class="{theme_class}">
        <script>
            document.body.classList.add('{theme_class}');
        </script>
    </div>
""", unsafe_allow_html=True)

# Load CSS
load_css()

# Auto-refresh for real-time updates (every 30 seconds)
refresh_interval = 30
st_autorefresh(interval=refresh_interval * 1000, key="refresh")

# Helper Functions
def get_current_time():
    """Return formatted current time string."""
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def generate_resource_data():
    """Generate simulated resource levels data."""
    return {
        "Oxygen": random.uniform(85, 98),
        "Water": random.uniform(75, 95),
        "Food": random.uniform(80, 92),
        "Power": random.uniform(82, 97),
        "Fuel": random.uniform(70, 90)
    }

def generate_crew_data():
    """Generate simulated crew data."""
    crew_members = [
        {"id": 1, "name": "Cmdr. Sarah Chen", "role": "Commander", "status": "On Duty", "location": "Command Center", "health": 97},
        {"id": 2, "name": "Dr. Michael Rodriguez", "role": "Medical Officer", "status": "On Duty", "location": "Medical Bay", "health": 94},
        {"id": 3, "name": "Eng. Aisha Kapoor", "role": "Chief Engineer", "status": "On Duty", "location": "Engine Room", "health": 92},
        {"id": 4, "name": "Dr. James Wilson", "role": "Science Officer", "status": "Off Duty", "location": "Quarters", "health": 98},
        {"id": 5, "name": "Lt. Yuki Tanaka", "role": "Navigation Specialist", "status": "On Duty", "location": "Bridge", "health": 95},
        {"id": 6, "name": "Eng. Carlos Mendez", "role": "Systems Engineer", "status": "Off Duty", "location": "Recreation", "health": 91},
        {"id": 7, "name": "Dr. Elena Petrov", "role": "Botanist", "status": "On Duty", "location": "Hydroponics", "health": 96},
        {"id": 8, "name": "Tech. Daniel Kim", "role": "Communications", "status": "On Duty", "location": "Comms Center", "health": 93}
    ]
    return crew_members

def generate_maintenance_tasks():
    """Generate simulated maintenance tasks."""
    tasks = [
        {"id": "T-1001", "description": "Filter replacement in Section A", "priority": "High", "assigned_to": "Eng. Aisha Kapoor", "status": "In Progress", "due": "2025-04-01"},
        {"id": "T-1002", "description": "Calibrate radiation sensors", "priority": "Medium", "assigned_to": "Tech. Daniel Kim", "status": "Pending", "due": "2025-04-02"},
        {"id": "T-1003", "description": "Life support system check", "priority": "High", "assigned_to": "Eng. Carlos Mendez", "status": "Completed", "due": "2025-03-30"},
        {"id": "T-1004", "description": "Hydroponics nutrient cycle", "priority": "Medium", "assigned_to": "Dr. Elena Petrov", "status": "Pending", "due": "2025-04-03"},
        {"id": "T-1005", "description": "Quantum computer cooling system", "priority": "High", "assigned_to": "Eng. Aisha Kapoor", "status": "Pending", "due": "2025-04-01"}
    ]
    return tasks

def generate_environmental_data():
    """Generate simulated environmental data."""
    return {
        "temperature": random.uniform(20.5, 22.5),
        "pressure": random.uniform(99.5, 101.5),
        "humidity": random.uniform(40, 60),
        "co2_level": random.uniform(350, 450),
        "radiation": random.uniform(0.05, 0.15),
        "sound_level": random.uniform(30, 45)
    }

def generate_power_systems_data():
    """Generate simulated power systems data."""
    return {
        "solar_array": random.uniform(85, 99),
        "main_battery": random.uniform(70, 95),
        "backup_generators": random.uniform(98, 100),
        "power_consumption": random.uniform(60, 85),
        "efficiency": random.uniform(88, 97)
    }

def generate_quantum_predictions():
    """Generate simulated quantum predictions for space events."""
    return {
        "solar_storms": [
            {"time": "2025-04-02T14:35:00", "intensity": random.uniform(1.5, 7.5), "probability": random.uniform(0.6, 0.95)},
            {"time": "2025-04-05T08:12:00", "intensity": random.uniform(2.5, 5.5), "probability": random.uniform(0.5, 0.85)}
        ],
        "cosmic_radiation": [
            {"time": "2025-04-01T22:45:00", "intensity": random.uniform(0.5, 3.5), "duration": f"{random.randint(1, 5)} hours", "probability": random.uniform(0.7, 0.9)}
        ],
        "asteroid_threats": [
            {"object_id": f"NEO-{random.randint(10000, 99999)}", "closest_approach": "2025-04-07T11:30:00", "distance": f"{random.uniform(0.5, 3.5):.2f} lunar distances", "diameter": f"{random.uniform(10, 100):.1f}m", "probability": random.uniform(0.01, 0.1)}
        ]
    }

def update_simulation_data():
    """Update all simulation data."""
    # Only update if enough time has passed since last refresh
    current_time = time.time()
    if current_time - st.session_state.last_refresh >= refresh_interval:
        st.session_state.resource_levels = generate_resource_data()
        st.session_state.crew_data = generate_crew_data()
        st.session_state.maintenance_tasks = generate_maintenance_tasks()
        st.session_state.environmental_data = generate_environmental_data()
        st.session_state.power_systems = generate_power_systems_data()
        st.session_state.quantum_predictions = generate_quantum_predictions()
        
        # Random chance of generating a notification
        if random.random() < 0.3:  # 30% chance
            system = random.choice(["Environmental", "Power", "Life Support", "Navigation", "Communications"])
            message = random.choice([
                f"{system} systems showing slight anomaly",
                f"{system} performance optimized",
                f"Scheduled maintenance for {system} system due",
                f"{system} diagnostic complete"
            ])
            severity = random.choice(["info", "warning", "critical"])
            add_notification(message, severity)
            
        st.session_state.last_refresh = current_time

def add_notification(message, severity="info"):
    """Add a notification to the notification center."""
    notification = {
        "id": str(uuid.uuid4()),
        "time": get_current_time(),
        "message": message,
        "severity": severity,
        "read": False
    }
    st.session_state.notifications.insert(0, notification)
    # Keep only the last 50 notifications
    if len(st.session_state.notifications) > 50:
        st.session_state.notifications = st.session_state.notifications[:50]

def process_voice_command(command):
    """Process voice commands from the AI assistant."""
    command = command.lower()
    response = "I didn't understand that command."
    
    # General commands
    if "status" in command or "report" in command:
        response = f"All systems are {st.session_state.system_status.lower()}. Current time is {get_current_time()}."
    elif "switch to" in command or "open" in command or "show" in command:
        for module in ["dashboard", "crew", "resources", "maintenance", "environmental", "power", "3d view", "quantum"]:
            if module in command:
                st.session_state.selected_module = module.title().replace("3d", "3D")
                response = f"Switching to {module} module."
                break
    elif "emergency" in command:
        if "activate" in command or "enable" in command:
            st.session_state.emergency_mode = True
            response = "Emergency protocols activated."
        elif "deactivate" in command or "disable" in command:
            st.session_state.emergency_mode = False
            response = "Emergency protocols deactivated."
    elif "dark mode" in command or "light mode" in command:
        st.session_state.dark_mode = "dark" in command
        response = f"Switching to {'dark' if st.session_state.dark_mode else 'light'} mode."
    
    # Add the response to the voice log
    st.session_state.voice_log.append({"role": "assistant", "content": response})
    return response

def get_3d_habitat_visualization():
    """Generate a 3D visualization of the space habitat."""
    # This would ideally be a complex 3D model, but for simplicity, we'll create a basic 3D plot
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')
    
    # Create a cylinder (main habitat body)
    theta = np.linspace(0, 2*np.pi, 100)
    z = np.linspace(-3, 3, 100)
    theta, z = np.meshgrid(theta, z)
    r = 1
    x = r * np.cos(theta)
    y = r * np.sin(theta)
    
    # Plot the main cylinder
    ax.plot_surface(x, y, z, color='silver', alpha=0.7)
    
    # Add solar panels
    panel_x = np.array([[-3, -3], [3, 3]])
    panel_y = np.array([[-0.5, 0.5], [-0.5, 0.5]])
    panel_z = np.array([[0, 0], [0, 0]])
    ax.plot_surface(panel_x, panel_y, panel_z, color='blue', alpha=0.6)
    
    # Add a sphere for the command module
    u = np.linspace(0, 2 * np.pi, 100)
    v = np.linspace(0, np.pi, 100)
    x = 0.7 * np.outer(np.cos(u), np.sin(v)) + 0
    y = 0.7 * np.outer(np.sin(u), np.sin(v)) + 0
    z = 0.7 * np.outer(np.ones(np.size(u)), np.cos(v)) + 3.5
    ax.plot_surface(x, y, z, color='gold', alpha=0.7)
    
    # Remove axis labels and ticks
    ax.set_xlabel('')
    ax.set_ylabel('')
    ax.set_zlabel('')
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_zticks([])
    
    # Set limits
    ax.set_xlim([-3, 3])
    ax.set_ylim([-3, 3])
    ax.set_zlim([-3, 3])
    
    # Set the view angle
    ax.view_init(elev=20, azim=45)
    
    # Set a dark background
    ax.set_facecolor((0.1, 0.1, 0.2))
    fig.patch.set_facecolor((0.1, 0.1, 0.2))
    
    # Convert to a plotly figure for better interactivity
    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', transparent=True)
    buf.seek(0)
    return buf

# Main Interface Components
def render_sidebar():
    """Render the sidebar with navigation and controls."""
    with st.sidebar:
        st.image("https://via.placeholder.com/150x150.png?text=SSHS", width=150)
        st.title("Space Habitat Management")
        
        # Main navigation
        st.subheader("Navigation")
        selected = option_menu(
            menu_title=None,
            options=[
                "Dashboard", "3D View", "Crew", "Resources", 
                "Environmental", "Power", "Maintenance", "Quantum"
            ],
            icons=[
                "speedometer2", "box", "people", "droplet", 
                "thermometer-half", "lightning", "tools", "cpu"
            ],
            menu_icon="cast",
            default_index=0,
            key="main_menu"
        )
        st.session_state.selected_module = selected
        
        # System status indicator
        st.subheader("System Status")
        status_color = {
            "Nominal": "status-nominal",
            "Warning": "status-warning",
            "Critical": "status-critical"
        }
        st.markdown(f"""
            <div class="info-card">
                <div class="{status_color.get(st.session_state.system_status, 'status-nominal')}">
                    {st.session_state.system_status}
                </div>
                <div class="system-time">
                    {get_current_time()}
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # Controls
        st.subheader("Controls")
        cols = st.columns(2)
        with cols[0]:
            if st.button("🌙 Dark" if not st.session_state.dark_mode else "☀️ Light"):
                st.session_state.dark_mode = not st.session_state.dark_mode
                st.rerun()
        with cols[1]:
            emergency_text = "🚨 Emergency" if not st.session_state.emergency_mode else "✓ Normal"
            if st.button(emergency_text):
                st.session_state.emergency_mode = not st.session_state.emergency_mode
                if st.session_state.emergency_mode:
                    add_notification("EMERGENCY PROTOCOLS ACTIVATED", "critical")
                else:
                    add_notification("Emergency protocols deactivated", "info")
        
        # Gesture control toggle
        st.checkbox("Enable Gesture Control", value=st.session_state.gesture_enabled, key="gesture_toggle")
        
        # Voice assistant toggle
        if st.button("🎤 Voice Assistant"):
            st.session_state.voice_assistant_active = not st.session_state.voice_assistant_active
        
        # Notifications
        st.subheader("Notifications")
        if not st.session_state.notifications:
            st.info("No new notifications")
        else:
            for i, notification in enumerate(st.session_state.notifications[:5]):
                severity_class = {
                    "info": "status-nominal",
                    "warning": "status-warning",
                    "critical": "status-critical"
                }.get(notification["severity"], "status-nominal")
                
                with st.container():
                    st.markdown(f"""
                        <div class="info-card" style="padding: 10px; margin-bottom: 10px;">
                            <div class="{severity_class}" style="font-size: 14px;">
                                {notification["message"]}
                            </div>
                            <div style="font-size: 12px; color: gray;">
                                {notification["time"]}
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
            
            if len(st.session_state.notifications) > 5:
                st.info(f"{len(st.session_state.notifications) - 5} more notifications...")

def render_dashboard():
    """Render the main dashboard with overview of all systems."""
    st.header("Habitat Command Dashboard")
    
    # System overview cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("Life Support")
        oxygen = st.session_state.resource_levels.get("Oxygen", 95)
        oxygen_color = "green" if oxygen > 90 else "orange" if oxygen > 80 else "red"
        st.metric("Oxygen Level", f"{oxygen:.1f}%", delta=f"{(oxygen-90):.1f}%")
        
        st.progress(oxygen/100, text="")
        
        water = st.session_state.resource_levels.get("Water", 85)
        st.metric("Water Reserves", f"{water:.1f}%", delta=f"{(water-80):.1f}%")
        st.progress(water/100, text="")
    
    with col2:
        st.subheader("Power Systems")
        power = st.session_state.power_systems.get("solar_array", 90)
        st.metric("Solar Array Efficiency", f"{power:.1f}%", delta=f"{(power-88):.1f}%")
        st.progress(power/100, text="")
        
        battery = st.session_state.power_systems.get("main_battery", 80)
        st.metric("Main Battery", f"{battery:.1f}%", delta=f"{(battery-75):.1f}%")
        st.progress(battery/100, text="")
    
    with col3:
        st.subheader("Crew Status")
        on_duty = sum(1 for member in st.session_state.crew_data if member["status"] == "On Duty")
        total_crew = len(st.session_state.crew_data)
        st.metric("On Duty", f"{on_duty}/{total_crew}", delta=f"{on_duty-total_crew//2}")
        
        avg_health = sum(member["health"] for member in st.session_state.crew_data) / total_crew
        st.metric("Average Health", f"{avg_health:.1f}%", delta=f"{(avg_health-90):.1f}%")
        st.progress(avg_health/100, text="")
    
    # Quick stats row
    st.subheader("Current Status")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Temperature", f"{st.session_state.environmental_data.get('temperature', 21.5):.1f}°C")
    with col2:
        st.metric("Pressure", f"{st.session_state.environmental_data.get('pressure', 101.3):.1f} kPa")
    with col3:
        st.metric("CO₂ Level", f"{st.session_state.environmental_data.get('co2_level', 400):.1f} ppm")
    with col4:
        st.metric("Radiation", f"{st.session_state.environmental_data.get('radiation', 0.1):.3f} μSv/h")
    
    # Charts
    st.subheader("System Trends")
    col1, col2 = st.columns(2)
    
    with col1:
        # Generate resource usage data
        days = 14
        dates = [datetime.datetime.now() - datetime.timedelta(days=i) for i in range(days)]
        dates.reverse()
        
        # Generate synthetic resource usage data with some patterns
        oxygen_data = [95 + random.uniform(-2, 2) + 3*np.sin(i/5) for i in range(days)]
        water_data = [90 + random.uniform(-3, 1) - i/10 for i in range(days)]
        power_data = [92 + random.uniform(-4, 2) + 5*np.sin(i/3) for i in range(days)]
        
        # Create dataframe
        df = pd.DataFrame({
            'Date': dates,
            'Oxygen': oxygen_data,
            'Water': water_data,
            'Power': power_data
        })
        
        # Plot with Plotly
        fig = px.line(df, x='Date', y=['Oxygen', 'Water', 'Power'],
                      title='Resource Levels (Last 14 Days)',
                      labels={'value': 'Level (%)', 'variable': 'Resource'})
        fig.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Generate power consumption data
        hours = 24
        times = [datetime.datetime.now() - datetime.timedelta(hours=i) for i in range(hours)]
        times.reverse()
        
        # Synthetic power consumption with day/night pattern
        base_consumption = [65 + 20*np.sin(np.pi*i/12) + random.uniform(-5, 5) for i in range(hours)]
        
        # Create dataframe
        power_df = pd.DataFrame({
            'Time': times,
            'Consumption': base_consumption
        })
        
        # Plot with Plotly
        fig = px.area(power_df, x='Time', y='Consumption',
                     title='Power Consumption (Last 24 Hours)',
                     labels={'Consumption': 'Power Usage (kW)'})
        st.plotly_chart(fig, use_container_width=True)
    
    # Active tasks and alerts
    col1, col2 = st.columns(2)
    
    with col1:
                st.subheader("Priority Tasks")
                high_priority_tasks = [task for task in st.session_state.maintenance_tasks if task["priority"] == "High"]
        if high_priority_tasks:
            for task in high_priority_tasks:
                with st.container():
                    cols = st.columns([3, 1, 1])
                    with cols[0]:
                        st.markdown(f"**{task['description']}**")
                    with cols[1]:
                        st.markdown(f"Due: {task['due']}")
                    with cols[2]:
                        status_color = {
                            "Completed": "status-nominal",
                            "In Progress": "status-warning",
                            "Pending": "status-critical"
                        }.get(task["status"], "")
                        st.markdown(f"<span class='{status_color}'>{task['status']}</span>", unsafe_allow_html=True)
        else:
            st.info("No high priority tasks at this time.")

def render_3d_view():
    """Render the 3D habitat visualization."""
    st.header("3D Habitat Digital Twin")
    
    # View mode selection
    view_modes = ["Exterior", "Systems", "Cutaway", "Thermal"]
    cols = st.columns(len(view_modes))
    for i, mode in enumerate(view_modes):
        with cols[i]:
            if st.button(mode):
                st.session_state.habitat_view = mode.lower()
    
    # Main 3D visualization
    with st.container():
        st.markdown('<div class="visualization-container hologram">', unsafe_allow_html=True)
        
        # For a more advanced 3D visualization, we would use Unity WebGL or Three.js
        # For this example, we'll use Plotly's 3D capabilities
        
        if st.session_state.habitat_view == "thermal":
            # Thermal view - use a heatmap on the 3D surface
            fig = go.Figure(data=[
                go.Surface(
                    z=[[random.uniform(0, 1) for _ in range(20)] for _ in range(20)],
                    colorscale='Inferno',
                    showscale=True
                )
            ])
            fig.update_layout(
                title="Thermal Analysis View",
                scene=dict(
                    xaxis_title="",
                    yaxis_title="",
                    zaxis_title="",
                    xaxis=dict(showticklabels=False),
                    yaxis=dict(showticklabels=False),
                    zaxis=dict(showticklabels=False)
                ),
                height=700
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            # Use py3Dmol for more advanced molecular-style visualization
            # This is a placeholder - in a real application, you would load actual 3D models
            view = py3Dmol.view(width=800, height=600)
            view.addModel('@<sdf>\n'+
                        'c1ccccc1\n'+
                        '@</sdf>', 'sdf')
            view.setStyle({'stick':{}})
            view.zoomTo()
            showmol(view, height=700)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Controls for the 3D view
    with st.container():
        st.subheader("View Controls")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.slider("Zoom", min_value=0.5, max_value=2.0, value=1.0, step=0.1)
        with col2:
            st.slider("Rotation X", min_value=0, max_value=360, value=45, step=15)
        with col3:
            st.slider("Rotation Y", min_value=0, max_value=360, value=45, step=15)
    
    # System highlights
    with st.container():
        st.subheader("System Highlights")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.checkbox("Life Support", value=True)
        with col2:
            st.checkbox("Power Systems", value=True)
        with col3:
            st.checkbox("Structural Integrity", value=True)
        with col4:
            st.checkbox("Communication Arrays", value=False)

def render_crew():
    """Render the crew management interface."""
    st.header("Crew Management")
    
    # Crew filtering
    filter_options = ["All", "On Duty", "Off Duty"]
    selected_filter = st.radio("Filter by status:", filter_options, horizontal=True)
    
    # Filter crew data based on selection
    filtered_crew = st.session_state.crew_data
    if selected_filter != "All":
        filtered_crew = [member for member in st.session_state.crew_data if member["status"] == selected_filter]
    
    # Crew grid
    st.subheader("Crew Status")
    
    # Create a grid of crew members
    cols_per_row = 4
    rows = [filtered_crew[i:i+cols_per_row] for i in range(0, len(filtered_crew), cols_per_row)]
    
    for row in rows:
        cols = st.columns(cols_per_row)
        for i, member in enumerate(row):
            with cols[i]:
                health_color = "green" if member["health"] > 95 else "orange" if member["health"] > 85 else "red"
                
                st.markdown(f"""
                <div class="info-card" style="padding: 15px;">
                    <h4>{member["name"]}</h4>
                    <p><strong>Role:</strong> {member["role"]}</p>
                    <p><strong>Status:</strong> {member["status"]}</p>
                    <p><strong>Location:</strong> {member["location"]}</p>
                    <div style="margin-top: 10px;">
                        <span>Health: </span>
                        <span style="color: {health_color}; font-weight: bold;">{member["health"]}%</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    # Crew location tracking
    st.subheader("Crew Location Tracking")
    
    # Create a network graph of crew locations
    G = nx.Graph()
    
    # Add nodes for locations
    locations = set(member["location"] for member in st.session_state.crew_data)
    for location in locations:
        G.add_node(location, type="location")
    
    # Add nodes for crew members and edges to their locations
    for member in st.session_state.crew_data:
        G.add_node(member["name"], type="crew")
        G.add_edge(member["name"], member["location"])
    
    # Create positions for the graph
    pos = nx.spring_layout(G, seed=42)
    
    # Create the plot
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Draw location nodes
    location_nodes = [node for node, attr in G.nodes(data=True) if attr.get("type") == "location"]
    nx.draw_networkx_nodes(G, pos, nodelist=location_nodes, node_color="skyblue", node_size=500, alpha=0.8)
    
    # Draw crew nodes
    crew_nodes = [node for node, attr in G.nodes(data=True) if attr.get("type") == "crew"]
    nx.draw_networkx_nodes(G, pos, nodelist=crew_nodes, node_color="orange", node_size=300, alpha=0.8)
    
    # Draw edges
    nx.draw_networkx_edges(G, pos, width=1.0, alpha=0.5)
    
    # Draw labels
    nx.draw_networkx_labels(G, pos, font_size=10, font_family="sans-serif")
    
    plt.axis("off")
    st.pyplot(fig)
    
    # Crew schedule
    st.subheader("Crew Schedule")
    
    # Create a timeline of crew activities
    timeline_data = {
        "events": [
            {
                "start_date": {
                    "year": "2025",
                    "month": "04",
                    "day": "01",
                    "hour": "08",
                    "minute": "00"
                },
                "end_date": {
                    "year": "2025",
                    "month": "04",
                    "day": "01",
                    "hour": "16",
                    "minute": "00"
                },
                "text": {
                    "headline": "Cmdr. Sarah Chen",
                    "text": "Command Center Duty"
                },
                "group": "Command"
            },
            {
                "start_date": {
                    "year": "2025",
                    "month": "04",
                    "day": "01",
                    "hour": "08",
                    "minute": "00"
                },
                "end_date": {
                    "year": "2025",
                    "month": "04",
                    "day": "01",
                    "hour": "16",
                    "minute": "00"
                },
                "text": {
                    "headline": "Dr. Michael Rodriguez",
                    "text": "Medical Bay Duty"
                },
                "group": "Medical"
            },
            {
                "start_date": {
                    "year": "2025",
                    "month": "04",
                    "day": "01",
                    "hour": "16",
                    "minute": "00"
                },
                "end_date": {
                    "year": "2025",
                    "month": "04",
                    "day": "02",
                    "hour": "00",
                    "minute": "00"
                },
                "text": {
                    "headline": "Lt. Yuki Tanaka",
                    "text": "Navigation Duty"
                },
                "group": "Navigation"
            }
        ]
    }
    
    timeline(timeline_data, height=400)

def render_resources():
    """Render the resource management interface."""
    st.header("Resource Management")
    
    # Resource overview
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Current Resource Levels")
        
        # Create a radar chart for resource levels
        categories = list(st.session_state.resource_levels.keys())
        values = list(st.session_state.resource_levels.values())
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            name='Current Levels'
        ))
        
        fig.add_trace(go.Scatterpolar(
            r=[100] * len(categories),
            theta=categories,
            fill='toself',
            name='Maximum',
            opacity=0.2
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100]
                )
            ),
            showlegend=True
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Resource Consumption")
        
        # Generate synthetic consumption data
        days = 30
        dates = [datetime.datetime.now() - datetime.timedelta(days=i) for i in range(days)]
        dates.reverse()
        
        # Create consumption patterns with some randomness
        oxygen_consumption = [0.8 + 0.2 * np.sin(i/5) + random.uniform(-0.05, 0.05) for i in range(days)]
        water_consumption = [1.2 + 0.3 * np.sin(i/7) + random.uniform(-0.1, 0.1) for i in range(days)]
        food_consumption = [1.5 + 0.2 * np.sin(i/3) + random.uniform(-0.15, 0.15) for i in range(days)]
        
        # Create dataframe
        consumption_df = pd.DataFrame({
            'Date': dates,
            'Oxygen (kg)': oxygen_consumption,
            'Water (L)': water_consumption,
            'Food (kg)': food_consumption
        })
        
        # Plot with Plotly
        fig = px.line(consumption_df, x='Date', y=['Oxygen (kg)', 'Water (L)', 'Food (kg)'],
                      title='Daily Resource Consumption',
                      labels={'value': 'Consumption', 'variable': 'Resource'})
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Resource flow visualization
    st.subheader("Resource Flow Visualization")
    
    # Create a Sankey diagram for resource flow
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=["Solar Panels", "Batteries", "Life Support", "Hydroponics", 
                   "Water Recycling", "Crew", "Waste Processing", "Atmosphere"],
            color="blue"
        ),
        link=dict(
            source=[0, 0, 1, 2, 3, 4, 5, 5, 6, 6],
            target=[1, 2, 2, 5, 5, 5, 4, 6, 3, 7],
            value=[80, 20, 60, 30, 20, 50, 30, 20, 10, 10],
            color="rgba(100, 100, 200, 0.2)"
        )
    )])
    
    fig.update_layout(title_text="Resource Flow Diagram", font_size=12)
    st.plotly_chart(fig, use_container_width=True)
    
    # Resource predictions
    st.subheader("Resource Consumption Predictions")
    
    # Create tabs for different prediction timeframes
    tabs = st.tabs(["7 Days", "30 Days", "90 Days"])
    
    with tabs[0]:
        # Generate prediction data for 7 days
        days = 7
        future_dates = [datetime.datetime.now() + datetime.timedelta(days=i) for i in range(days)]
        
        # Create synthetic prediction data with confidence intervals
        oxygen_pred = [st.session_state.resource_levels.get("Oxygen", 95) - i*0.5 + random.uniform(-0.2, 0.2) for i in range(days)]
        oxygen_upper = [val + 2 for val in oxygen_pred]
        oxygen_lower = [val - 2 for val in oxygen_pred]
        
        water_pred = [st.session_state.resource_levels.get("Water", 85) - i*0.7 + random.uniform(-0.3, 0.3) for i in range(days)]
        water_upper = [val + 3 for val in water_pred]
        water_lower = [val - 3 for val in water_pred]
        
        food_pred = [st.session_state.resource_levels.get("Food", 90) - i*0.6 + random.uniform(-0.25, 0.25) for i in range(days)]
        food_upper = [val + 2.5 for val in food_pred]
        food_lower = [val - 2.5 for val in food_pred]
        
        # Create dataframe
        pred_df = pd.DataFrame({
            'Date': future_dates,
            'Oxygen': oxygen_pred,
            'Oxygen_Upper': oxygen_upper,
            'Oxygen_Lower': oxygen_lower,
            'Water': water_pred,
            'Water_Upper': water_upper,
            'Water_Lower': water_lower,
            'Food': food_pred,
            'Food_Upper': food_upper,
            'Food_Lower': food_lower
        })
        
        # Plot with confidence intervals
        fig = go.Figure()
        
        # Oxygen
        fig.add_trace(go.Scatter(
            x=pred_df['Date'], y=pred_df['Oxygen_Upper'],
            fill=None, mode='lines', line_color='rgba(0, 100, 80, 0.2)',
            showlegend=False
        ))
        fig.add_trace(go.Scatter(
            x=pred_df['Date'], y=pred_df['Oxygen_Lower'],
            fill='tonexty', mode='lines', line_color='rgba(0, 100, 80, 0.2)',
            name='Oxygen (95% CI)'
        ))
        fig.add_trace(go.Scatter(
            x=pred_df['Date'], y=pred_df['Oxygen'],
            mode='lines', line_color='rgb(0, 100, 80)',
            name='Oxygen'
        ))
        
        # Water
        fig.add_trace(go.Scatter(
            x=pred_df['Date'], y=pred_df['Water_Upper'],
            fill=None, mode='lines', line_color='rgba(0, 176, 246, 0.2)',
            showlegend=False
        ))
        fig.add_trace(go.Scatter(
            x=pred_df['Date'], y=pred_df['Water_Lower'],
            fill='tonexty', mode='lines', line_color='rgba(0, 176, 246, 0.2)',
            name='Water (95% CI)'
        ))
        fig.add_trace(go.Scatter(
            x=pred_df['Date'], y=pred_df['Water'],
            mode='lines', line_color='rgb(0, 176, 246)',
            name='Water'
        ))
        
        # Food
        fig.add_trace(go.Scatter(
            x=pred_df['Date'], y=pred_df['Food_Upper'],
            fill=None, mode='lines', line_color='rgba(231, 107, 243, 0.2)',
            showlegend=False
        ))
        fig.add_trace(go.Scatter(
            x=pred_df['Date'], y=pred_df['Food_Lower'],
            fill='tonexty', mode='lines', line_color='rgba(231, 107, 243, 0.2)',
            name='Food (95% CI)'
        ))
        fig.add_trace(go.Scatter(
            x=pred_df['Date'], y=pred_df['Food'],
            mode='lines', line_color='rgb(231, 107, 243)',
            name='Food'
        ))
        
        fig.update_layout(
            title='7-Day Resource Level Predictions',
            yaxis_title='Resource Level (%)',
            hovermode="x unified"
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with tabs[1]:
        st.info("30-day predictions would be displayed here with similar visualization.")
    
    with tabs[2]:
        st.info("90-day predictions would be displayed here with similar visualization.")

def render_emergency():
    """Render the emergency management interface."""
    st.header("Emergency Management")
    
    # Emergency status
    if st.session_state.emergency_mode:
        st.markdown("""
        <div class="info-card emergency-active" style="padding: 20px; text-align: center;">
            <h2 style="color: #ff4b4b;">⚠️ EMERGENCY MODE ACTIVE ⚠️</h2>
            <p>Emergency protocols have been activated. All non-essential systems are in standby mode.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="info-card" style="padding: 20px; text-align: center;">
            <h2 style="color: var(--success);">✓ Systems Normal</h2>
            <p>No emergency protocols active. All systems operating within normal parameters.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Emergency protocols
    st.subheader("Emergency Protocols")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Critical Systems")
        protocols = [
            {"name": "Life Support Failure", "status": "Ready", "severity": "Critical"},
            {"name": "Hull Breach", "status": "Ready", "severity": "Critical"},
            {"name": "Fire Suppression", "status": "Ready", "severity": "Critical"},
            {"name": "Radiation Alert", "status": "Ready", "severity": "Critical"}
        ]
        
        for protocol in protocols:
            status_class = "status-nominal" if protocol["status"] == "Ready" else "status-critical"
            st.markdown(f"""
            <div class="info-card" style="padding: 10px; margin-bottom: 10px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <strong>{protocol["name"]}</strong>
                        <div style="font-size: 12px;">Severity: {protocol["severity"]}</div>
                    </div>
                    <div class="{status_class}">{protocol["status"]}</div>
                </div>
                <div style="margin-top: 10px;">
                    <button style="background-color: #ff4b4b; color: white; border: none; padding: 5px 10px; border-radius: 4px; cursor: pointer;">
                        Activate
                    </button>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("### Secondary Systems")
        protocols = [
            {"name": "Power Conservation", "status": "Ready", "severity": "High"},
            {"name": "Communication Backup", "status": "Ready", "severity": "High"},
            {"name": "Crew Evacuation", "status": "Ready", "severity": "High"},
            {"name": "Medical Emergency", "status": "Ready", "severity": "High"}
        ]
        
        for protocol in protocols:
            status_class = "status-nominal" if protocol["status"] == "Ready" else "status-critical"
            st.markdown(f"""
            <div class="info-card" style="padding: 10px; margin-bottom: 10px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <strong>{protocol["name"]}</strong>
                        <div style="font-size: 12px;">Severity: {protocol["severity"]}</div>
                    </div>
                    <div class="{status_class}">{protocol["status"]}</div>
                </div>
                <div style="margin-top: 10px;">
                    <button style="background-color: #ff9f00; color: white; border: none; padding: 5px 10px; border-radius: 4px; cursor: pointer;">
                        Activate
                    </button>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # Emergency simulation
    st.subheader("Emergency Simulation")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.selectbox("Scenario Type", ["Hull Breach", "Fire", "Power Failure", "Medical Emergency", "Cosmic Radiation"])
    
    with col2:
        st.selectbox("Severity Level", ["Low", "Medium", "High", "Critical"])
    
    with col3:
        st.selectbox("Location", ["Command Center", "Crew Quarters", "Engineering", "Life Support", "Research Lab"])
    
    if st.button("Run Simulation"):
        st.info("Emergency simulation would be executed here, testing response protocols and crew readiness.")

def render_ar():
    """Render the augmented reality interface."""
    st.header("Augmented Reality Maintenance")
    
    # AR mode selection
    ar_modes = ["Inspect", "Repair", "Diagnostic"]
    selected_mode = st.radio("AR Mode:", ar_modes, horizontal=True)
    
    # AR viewport
    st.subheader("AR Viewport")
    
    # Simulated AR view using an image with overlays
    ar_image = Image.new('RGB', (800, 600), color=(20, 20, 40))
    st.image(ar_image, use_column_width=True)
    
    # AR controls
    st.subheader("AR Controls")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.button("Scan Component")
    
    with col2:
        st.button("Show Schematics")
    
    with col3:
        st.button("Record Procedure")
    
    # AR information panels
    st.subheader("Component Information")
    
    with st.expander("Technical Specifications", expanded=True):
        st.markdown("""
        - **Component ID:** HVAC-2305
        - **Manufacturer:** SpaceTech Industries
        - **Installation Date:** 2024-06-15
        - **Last Maintenance:** 2025-03-10
        - **Expected Lifespan:** 5 years
        - **Current Status:** Operational
        """)
    
    with st.expander("Maintenance History"):
        st.markdown("""
        - **2025-03-10:** Routine inspection, replaced air filter
        - **2024-12-05:** Calibration of temperature sensors
        - **2024-09-22:** Firmware update v2.3.1
        - **2024-06-15:** Initial installation and configuration
        """)
    
    with st.expander("Repair Procedures"):
        st.markdown("""
        1. Power down the system using the main control panel
        2. Remove access panel A-7 using a hex wrench
        3. Disconnect the power coupling (marked in red)
        4. Remove the faulty component
        5. Install the replacement component
        6. Reconnect the power coupling
        7. Replace access panel A-7
        8. Power up the system
        9. Run diagnostic test sequence
        """)

def render_environmental():
    """Render the environmental control interface."""
    st.header("Environmental Control Systems")
    
    # Environmental status overview
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("Temperature Control")
        
        current_temp = st.session_state.environmental_data.get("temperature", 21.5)
        
        # Temperature gauge
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=current_temp,
            domain={'x': [0, 1], 'y': [0, 1]},
            delta={'reference': 21.0, 'increasing': {'color': "red"}, 'decreasing': {'color': "green"}},
            gauge={
                'axis': {'range': [18, 25], 'tickwidth': 1, 'tickcolor': "darkblue"},
                'bar': {'color': "darkblue"},
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "gray",
                'steps': [
                    {'range': [18, 19.5], 'color': 'cyan'},
                    {'range': [19.5, 22.5], 'color': 'royalblue'},
                    {'range': [22.5, 25], 'color': 'red'}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 23
                }
            }
        ))
        
        fig.update_layout(height=250)
        st.plotly_chart(fig, use_container_width=True)
        
        # Temperature controls
        st.slider("Temperature Set Point", min_value=18.0, max_value=25.0, value=21.0, step=0.5)
        
        col1, col2 = st.columns(2)
        with col1:
            st.button("Apply Settings")
        with col2:
            st.button("Reset to Default")
    
    with col2:
        st.subheader("Pressure Control")
        
        current_pressure = st.session_state.environmental_data.get("pressure", 101.3)
        
        # Pressure gauge
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=current_pressure,
            domain={'x': [0, 1], 'y': [0, 1]},
            delta={'reference': 101.3, 'increasing': {'color': "red"}, 'decreasing': {'color': "red"}},
            gauge={
                'axis': {'range': [95, 105], 'tickwidth': 1, 'tickcolor': "darkblue"},
                'bar': {'color': "darkblue"},
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "gray",
                'steps': [
                    {'range': [95, 98], 'color': 'red'},
                    {'range': [98, 102.5], 'color': 'royalblue'},
                    {'range': [102.5, 105], 'color': 'red'}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 103
                }
            }
        ))
        
        fig.update_layout(height=250)
        st.plotly_chart(fig, use_container_width=True)
        
        # Pressure controls
        st.slider("Pressure Set Point", min_value=98.0, max_value=103.0, value=101.3, step=0.1)
        
        col1, col2 = st.columns(2)
        with col1:
            st.button("Apply Pressure")
        with col2:
            st.button("Reset Pressure")
    
    with col3:
        st.subheader("Humidity Control")
        
        current_humidity = st.session_state.environmental_data.get("humidity", 45)
        
        # Humidity gauge
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=current_humidity,
            domain={'x': [0, 1], 'y': [0, 1]},
            delta={'reference': 45, 'increasing': {'color': "red"}, 'decreasing': {'color': "red"}},
            gauge={
                'axis': {'range': [20, 70], 'tickwidth': 1, 'tickcolor': "darkblue"},
                'bar': {'color': "darkblue"},
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "gray",
                'steps': [
                    {'range': [20, 30], 'color': 'red'},
                    {'range': [30, 60], 'color': 'royalblue'},
                    {'range': [60, 70], 'color': 'red'}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 65
                }
            }
        ))
