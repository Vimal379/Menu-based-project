import streamlit as st
import psutil
from datetime import datetime 
import pywhatkit
import smtplib
from email.message import EmailMessage
from twilio.rest import Client
from googlesearch import search
import requests
from bs4 import BeautifulSoup
import numpy as np
import matplotlib.pyplot as plt
import cv2
import subprocess
import speech_recognition as sr
import os
from PIL import Image
import time
import paramiko
from io import StringIO
import socket
import boto3
import folium
import geocoder
from streamlit_folium import folium_static
import pytz
from instagrapi import Client
from tempfile import NamedTemporaryFile
import google.generativeai as genai
from dotenv import load_dotenv

# Load variables from .env
load_dotenv()

# Twilio credentials
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")

# Email credentials
EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_SENDER_PASSWORD = os.getenv("EMAIL_SENDER_PASSWORD")

# API keys
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
# Set page config
st.set_page_config(page_title="Multi-Tool Application", layout="wide")

# Sidebar menu
st.sidebar.title("Navigation")
menu_choice = st.sidebar.radio("Select a Task", [
    "System Info",
    "Messaging",
    "Email",
    "Instagram",
    "Coding Assistant Chatbot",
    "Web Automation",
    "Image Processing",
    "Linux Automation",
    "GitHub Automation",
    "AWS Automation",
    "Linux Commands",
    "Geo Location",
    "Weather Explorer",
    "Blogs & More"
])


# Task 1 - Read RAM
def show_ram_info():
    st.header("Real-Time RAM Monitor")
    
    # Initialize session state
    if 'monitoring' not in st.session_state:
        st.session_state.monitoring = False
    if 'ram_history' not in st.session_state:
        st.session_state.ram_history = []
    
    # Create toggle button
    start_stop = st.button(
        label="▶️ Start Monitoring" if not st.session_state.monitoring else "⏹️ Stop Monitoring",
        key="monitor_toggle"
    )
    
    # Toggle monitoring state
    if start_stop:
        st.session_state.monitoring = not st.session_state.monitoring
        st.rerun()
    
    # Create placeholders
    metric_placeholder = st.empty()
    progress_placeholder = st.empty()
    chart_placeholder = st.empty()
    
    # Main monitoring logic
    if st.session_state.monitoring:
        # Get current RAM usage
        mem = psutil.virtual_memory()
        
        # Update metrics
        with metric_placeholder.container():
            col1, col2, col3 = st.columns(3)
            col1.metric("Total RAM", f"{mem.total / (1024**3):.2f} GB")
            col2.metric("Available RAM", f"{mem.available / (1024**3):.2f} GB")
            col3.metric("Used RAM", f"{mem.used / (1024**3):.2f} GB", 
                       delta=f"{mem.percent}% used")
        
        # Update progress bar
        progress_placeholder.progress(mem.percent / 100, text=f"RAM Usage: {mem.percent}%")
        
        # Update history chart
        st.session_state.ram_history.append(mem.percent)
        if len(st.session_state.ram_history) > 60:  # Keep last 60 seconds
            st.session_state.ram_history.pop(0)
        
        # Display chart
        with chart_placeholder.container():
            st.subheader("Usage History (Last 60 seconds)")
            st.line_chart(st.session_state.ram_history)
        
        # Schedule next update
        time.sleep(1)
        st.rerun()
    else:
        # Static display when not monitoring
        mem = psutil.virtual_memory()
        
        with metric_placeholder.container():
            col1, col2, col3 = st.columns(3)
            col1.metric("Total RAM", f"{mem.total / (1024**3):.2f} GB")
            col2.metric("Available RAM", f"{mem.available / (1024**3):.2f} GB")
            col3.metric("Used RAM", f"{mem.used / (1024**3):.2f} GB")
        
        progress_placeholder.progress(mem.percent / 100, text=f"RAM Usage: {mem.percent}%")
        
        if st.session_state.ram_history:
            with chart_placeholder.container():
                st.subheader("Usage History")
                st.line_chart(st.session_state.ram_history)
                
# Task 2 - Send WhatsApp Message
def send_whatsapp_message():
    st.header("Send WhatsApp Message")
    phone = st.text_input("Enter phone number with country code (e.g., +919001232345)")
    message = st.text_area("Message content")
    
    if st.button("Schedule Message"):
        now = datetime.now()  # Correct usage after proper import
        hrs = now.hour
        mins = now.minute + 1  # Send 1 minute from now
        
        try:
            pywhatkit.sendwhatmsg(phone, message, hrs, mins)
            st.success(f"Message scheduled to send at {hrs}:{mins}")
        except Exception as e:
            st.error(f"Error: {e}")

# Task 3 - Send Email
def send_email():
    st.header("Send Email with Attachment")
    if not EMAIL_SENDER or not EMAIL_SENDER_PASSWORD:
        st.error("Please set your email sender and password in the code.")
        return
    
    sender = EMAIL_SENDER 
    sender_password = EMAIL_SENDER_PASSWORD

    receiver = st.text_input("Receiver Email")
    subject = st.text_input("Subject")
    message = st.text_area("Message")
    
    uploaded_file = st.file_uploader("Attach File", type=['txt'])
    
    if st.button("Send Email"):
        if not receiver:
            st.warning("Please enter receiver email")
            return
            
        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = sender
        msg['To'] = receiver
        msg.set_content(message)
        
        if uploaded_file:
            file_content = uploaded_file.getvalue()
            msg.add_attachment(file_content, maintype='application', subtype='octet-stream', filename=uploaded_file.name)
        
        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(sender, sender_password)
                server.send_message(msg)
            st.success("Email sent successfully!")
        except Exception as e:
            st.error(f"Error: {e}")

# Task 4/5 - Send SMS/Call (Twilio)
def twilio_messaging():
    st.header("📞 Twilio Messaging Services")

    service = st.radio("Select Service", ["SMS", "Voice Call"])
    recipient_number = st.text_input("Recipient Phone Number (with country code)")

    if service == "SMS":
        message_body = st.text_area("Message Content")
        if st.button("Send SMS"):
            if not all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER]):
                st.error("❌ Twilio credentials are missing or invalid.")
                return
            try:
                client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
                message = client.messages.create(
                    body=message_body,
                    from_=TWILIO_PHONE_NUMBER,
                    to=recipient_number
                )
                st.success(f"✅ Message sent! SID: {message.sid}")
            except Exception as e:
                st.error(f"⚠️ Error sending SMS: {e}")

    elif service == "Voice Call":
        if st.button("Make Call"):
            if not all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER]):
                st.error("❌ Twilio credentials are missing or invalid.")
                return
            try:
                client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
                call = client.calls.create(
                    to=recipient_number,
                    from_=TWILIO_PHONE_NUMBER,
                    url="http://demo.twilio.com/docs/voice.xml"
                )
                st.success(f"📞 Call initiated! SID: {call.sid}")
            except Exception as e:
                st.error(f"⚠️ Error making call: {e}")

# Task 7 - Google Search
def google_search():
    st.header("Google Search from Python")
    query = st.text_input("Search Query")
    num_results = st.slider("Number of Results", 1, 20, 5)
    
    if st.button("Search"):
        try:
            results = list(search(query, num_results=num_results))
            st.write("Search Results:")
            for i, result in enumerate(results, 1):
                st.write(f"{i}. {result}")
        except Exception as e:
            st.error(f"An error occurred: {e}")

# Task 9 - Web Scraping
def web_scraping():
    st.header("Website Scraper")
    url = st.text_input("Enter URL to scrape", "https://www.geeksforgeeks.org/")
    
    if st.button("Scrape"):
        try:
            headers = {"User-Agent": "Mozilla/5.0"}
            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Extract text content
            page_text = soup.get_text()
            
            # Clean up the text (remove excessive whitespace)
            cleaned_text = "\n".join([line.strip() for line in page_text.split('\n') if line.strip()])
            
            st.subheader("Page Text Content")
            st.text_area("Extracted Content", 
                        value=cleaned_text[:5000] + ("..." if len(cleaned_text) > 5000 else ""), 
                        height=300)
            
            st.subheader("Links Found")
            links = [a.get('href') for a in soup.find_all('a', href=True) if a.get('href')]
            links_text = "\n".join(links[:20])  # Show first 20 links
            st.text_area("Links", 
                        value=links_text, 
                        height=150)
            
            # Show basic stats
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total Characters", len(page_text))
            with col2:
                st.metric("Links Found", len(links))
                
        except Exception as e:
            st.error(f"Error: {str(e)}")

# Task 12 - Create Digital Image
def create_image():
    st.header("Create Digital Image")
    
    size = st.slider("Image Size (pixels)", 50, 500, 100)
    color = st.color_picker("Select Color", "#FFCC00")
    shape = st.selectbox("Select Shape", ["Circle", "Square", "Triangle"])
    
    # Convert hex color to RGB
    rgb = tuple(int(color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
    
    if st.button("Generate Image"):
        img_matrix = np.zeros((size, size, 3), dtype=np.uint8)
        center = size // 2
        radius = size // 3
        
        if shape == "Circle":
            for x in range(size):
                for y in range(size):
                    if (x - center)**2 + (y - center)**2 <= radius**2:
                        img_matrix[x, y] = rgb
        elif shape == "Square":
            start = center - radius
            end = center + radius
            img_matrix[start:end, start:end] = rgb
        else:  # Triangle
            for x in range(size):
                for y in range(size):
                    if (y >= center - x) and (y >= x - center) and (x >= center - radius):
                        img_matrix[x, y] = rgb
        
        fig, ax = plt.subplots()
        ax.imshow(img_matrix)
        ax.axis("off")
        st.pyplot(fig)

# Task 13 - Face Swap
def face_swap():
    st.header("Face Swap")
    
    st.warning("This feature requires webcam access and OpenCV. It works best in local environments.")
    
    if st.button("Start Face Capture (Press SPACE to capture, ESC to cancel)"):
        cap = cv2.VideoCapture(0)
        captured_images = []
        
        while len(captured_images) < 2:
            ret, frame = cap.read()
            if not ret:
                break
            
            cv2.imshow("Capture Faces", frame)
            key = cv2.waitKey(1)
            
            if key == 32:  # SPACE
                captured_images.append(frame.copy())
                st.write(f"✔ Captured Image {len(captured_images)}")
            elif key == 27:  # ESC
                break
        
        cap.release()
        cv2.destroyAllWindows()
        
        if len(captured_images) == 2:
            # Load Haar cascade for face detection
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            
            def detect_face(img):
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)
                if len(faces) == 0:
                    return None, None
                x, y, w, h = faces[0]
                face_region = img[y:y+h, x:x+w]
                return face_region, (x, y, w, h)
            
            img1, img2 = captured_images
            face1, coords1 = detect_face(img1)
            face2, coords2 = detect_face(img2)
            
            if face1 is None or face2 is None:
                st.error("Could not detect face in one or both images")
                return
            
            # Resize and swap faces
            face2_resized = cv2.resize(face2, (coords1[2], coords1[3]))
            face1_resized = cv2.resize(face1, (coords2[2], coords2[3]))
            
            img1_result = img1.copy()
            img2_result = img2.copy()
            
            x1, y1, w1, h1 = coords1
            x2, y2, w2, h2 = coords2
            
            img1_result[y1:y1+h1, x1:x1+w1] = face2_resized
            img2_result[y2:y2+h2, x2:x2+w2] = face1_resized
            
            # Display results
            col1, col2 = st.columns(2)
            with col1:
                st.image(cv2.cvtColor(img1_result, cv2.COLOR_BGR2RGB), caption="Image 1 with Face 2", use_column_width=True)
            with col2:
                st.image(cv2.cvtColor(img2_result, cv2.COLOR_BGR2RGB), caption="Image 2 with Face 1", use_column_width=True)

# Task 14/15 - Linux Automation
def linux_automation():
    st.header("Linux Command Automation")
    
    # Connection settings with default values
    st.subheader("SSH Connection Settings")
    col1, col2 = st.columns(2)
    ssh_host = col1.text_input("SSH Host", "192.168.89.146")
    ssh_user = col2.text_input("SSH Username", "vimal")
    ssh_pass = st.text_input("SSH Password", type="password")
    
    # Command selection from reference
    st.subheader("Command Selection")
    command_categories = {
    'File Operations': {
        '1': ('List files (detailed)', 'ls -la'),
        '2': ('Print current directory', 'pwd')
    },

    'System Information': {
        '1': ('Kernel/system info', 'uname -a'),
        '2': ('Disk space (human)', 'df -h'),
        '3': ('Memory usage', 'free -m'),
        '4': ('Process monitor (basic)', 'top'),
        '5': ('Current logged-in users', 'who'),
        '6': ('System uptime', 'uptime'),
        '7': ('List all processes', 'ps aux'),
        '8': ('Check OS version', 'cat /etc/redhat-release'),
        '9': ('Check CPU info', 'lscpu')
    },

    'Networking': {
        '1': ('Show IP address', 'ip addr show'),
        '2': ('Check network connections', 'netstat -tuln'),
        '3': ('Check open ports', 'ss -tuln'),
        '4': ('Restart networking service', 'sudo systemctl restart NetworkManager')
    },

    'User Management': {
        '1': ('List all users', 'cut -d: -f1 /etc/passwd')
    },

    'Package Management (RHEL/CentOS/Fedora)': {
        '1': ('Update package list', 'sudo dnf check-update'),
        '2': ('Upgrade all packages', 'sudo dnf upgrade -y'),
        '3': ('List installed packages', 'dnf list installed')
    },

    'Service Management (systemd)': {
        '1': ('Check service status (example: sshd)', 'systemctl status sshd')
    },

    'SELinux': {
        '1': ('Check SELinux status', 'sestatus')
    },

    'Firewall (firewalld)': {
        '1': ('Check firewall status', 'sudo firewall-cmd --state'),
        '2': ('List open ports', 'sudo firewall-cmd --list-ports'),
        '3': ('Reload firewall', 'sudo firewall-cmd --reload')
    }
    }

    
    # Create two columns: one for command selection, one for custom command
    col1, col2 = st.columns(2)
    
    with col1:
        selected_category = st.selectbox("Command Category", list(command_categories.keys()))
        commands = command_categories[selected_category]
        selected_command = st.selectbox(
            "Select Command", 
            [f"{k}. {v[0]}" for k, v in commands.items()],
            index=0
        )
        
        # Get the command key (e.g., '1' from '1. List files (detailed)')
        command_key = selected_command.split('.')[0]
        base_command = commands[command_key][1]
        
        # Handle commands with parameters
        if '[dir]' in base_command:
            param = st.text_input("Directory path", ".")
            ssh_cmd = base_command.replace('[dir]', param)
        elif '[file]' in base_command:
            param = st.text_input("File name", "example.txt")
            ssh_cmd = base_command.replace('[file]', param)
        elif '[name]' in base_command:
            param = st.text_input("Name", "new_directory")
            ssh_cmd = base_command.replace('[name]', param)
        else:
            ssh_cmd = base_command
            
    with col2:
        st.subheader("Or enter custom command")
        ssh_cmd_custom = st.text_area("Command to Execute", ssh_cmd, height=100)
        use_custom = st.checkbox("Use custom command instead")
    
    if use_custom:
        ssh_cmd = ssh_cmd_custom
    
    if st.button("🚀 Run Command"):
        if not all([ssh_host, ssh_user]):
            st.error("Host and username are required!")
            return
        
        status = st.empty()
        output_container = st.empty()
        
        try:
            # Initialize SSH client
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            status.info("⌛ Connecting to server...")
            
            try:
                # Test basic connectivity first
                socket.create_connection((ssh_host, 22), timeout=10)
                
                # Attempt SSH connection
                ssh.connect(
                    hostname=ssh_host,
                    username=ssh_user,
                    password=ssh_pass,
                    timeout=20,
                    banner_timeout=20,
                    auth_timeout=20
                )
                
                status.success("✅ Connected! Executing command...")
                
                # Execute command with timeout
                stdin, stdout, stderr = ssh.exec_command(ssh_cmd, timeout=30)
                
                # Read output progressively
                output = []
                error = []
                
                while not stdout.channel.exit_status_ready():
                    if stdout.channel.recv_ready():
                        output.append(stdout.channel.recv(1024).decode())
                        output_container.code("".join(output))
                    
                    if stderr.channel.recv_stderr_ready():
                        error.append(stderr.channel.recv_stderr(1024).decode())
                        output_container.error("".join(error))
                    
                    time.sleep(0.1)
                
                # Get remaining output
                output.append(stdout.read().decode())
                error.append(stderr.read().decode())
                
                # Display final results
                with st.expander("📋 Full Command Output", expanded=True):
                    if "".join(output).strip():
                        st.subheader("Output")
                        st.code("".join(output), language='bash')
                    
                    if "".join(error).strip():
                        st.subheader("Errors")
                        st.error("".join(error))
                    
                    st.success(f"Command completed with exit code: {stdout.channel.recv_exit_status()}")
                
            except socket.timeout:
                st.error("Connection timed out. Possible issues:")
                st.error("- Server is not reachable")
                st.error("- SSH service not running on port 22")
                st.error("- Network firewall blocking the connection")
            except paramiko.AuthenticationException:
                st.error("Authentication failed. Please check:")
                st.error("- Username is correct")
                st.error("- Password is correct")
                st.error("- User has SSH access")
            except paramiko.SSHException as e:
                st.error(f"SSH Protocol Error: {str(e)}")
            except Exception as e:
                st.error(f"Unexpected error: {str(e)}")
                
        except socket.gaierror:
            st.error("Hostname resolution failed. Please check:")
            st.error("- The hostname/IP is correct")
            st.error("- Your DNS settings")
        except Exception as e:
            st.error(f"Connection failed: {str(e)}")
        finally:
            try:
                if 'ssh' in locals():
                    ssh.close()
            except:
                pass


#Task 16 - GitHub Automation Tool
def run_command(command, cwd=None):
    result = subprocess.run(command, shell=True, text=True, capture_output=True, cwd=cwd)
    st.code(result.stdout)
    if result.stderr:
        st.warning(result.stderr)

def init_and_push_ui():
    st.subheader("Initialize New Repo & Push to GitHub")
    repo_path = st.text_input("Enter the full path of your local directory")
    github_url = st.text_input("Enter your GitHub repo URL")

    if st.button("Initialize & Push"):
        if not os.path.isdir(repo_path):
            st.error("Invalid path.")
            return

        os.chdir(repo_path)
        if not os.path.exists(".git"):
            run_command("git init")

        if not os.path.exists("README.md"):
            with open("README.md", "w") as f:
                f.write("# MyRepo")

        run_command("git add .")
        run_command('git commit -m "Initial commit"')
        run_command("git branch -M main")

        result = subprocess.run("git remote", shell=True, capture_output=True, text=True)
        if "origin" not in result.stdout:
            run_command(f"git remote add origin {github_url}")

        run_command("git push -u origin main")

def update_existing_repo_ui():
    st.subheader("Push Updated Code to Existing Repo")
    repo_path = st.text_input("Enter the path of your local Git repo")
    commit_msg = st.text_input("Enter commit message")

    if st.button("Update Repo"):
        if not os.path.isdir(os.path.join(repo_path, ".git")):
            st.error("Not a Git repository.")
            return

        os.chdir(repo_path)
        run_command("git add .")
        run_command(f'git commit -m "{commit_msg}"')
        run_command("git push")

def create_and_merge_branch_ui():
    st.subheader("Create and Merge Feature Branch")
    repo_path = st.text_input("Enter your Git repo path")
    branch_name = st.text_input("Enter new branch name")

    if st.button("Create Branch"):
        if not os.path.isdir(os.path.join(repo_path, ".git")):
            st.error("Not a Git repo.")
            return

        os.chdir(repo_path)
        run_command(f"git checkout -b {branch_name}")
        st.success(f"Now make your changes in branch '{branch_name}', then press the button below to merge.")

    if st.button("Merge Branch"):
        os.chdir(repo_path)
        run_command("git add .")
        run_command(f'git commit -m "Changes in {branch_name}"')
        run_command("git checkout main")
        run_command(f"git merge {branch_name}")
        run_command("git push")

def fork_and_pr_ui():
    st.subheader("Fork + Clone and Submit Pull Request")
    fork_url = st.text_input("Enter the forked GitHub repo URL")
    local_path = st.text_input("Enter the local path where you want to clone")
    pr_message = st.text_input("Enter pull request commit message")

    if st.button("Clone Forked Repo"):
        os.chdir(local_path)
        run_command(f"git clone {fork_url}")

    if st.button("Commit and Push Changes"):
        repo_name = fork_url.rstrip('/').split('/')[-1].replace('.git', '')
        repo_path = os.path.join(local_path, repo_name)
        os.chdir(repo_path)

        run_command("git add .")
        run_command(f'git commit -m "{pr_message}"')
        run_command("git push")

        st.success("Now go to GitHub and create a Pull Request from your forked repo to the original repo.")

def github_Automation():
    st.title("Git Automation Tool")
    task = st.selectbox(
        "Choose a task:",
        ["Select...", "Initialize New Repo & Push to GitHub", "Push Updated Code to Existing Repo",
         "Create & Merge Feature Branch", "Fork + Clone and Submit Pull Request"]
    )

    if task == "Initialize New Repo & Push to GitHub":
        init_and_push_ui()
    elif task == "Push Updated Code to Existing Repo":
        update_existing_repo_ui()
    elif task == "Create & Merge Feature Branch":
        create_and_merge_branch_ui()
    elif task == "Fork + Clone and Submit Pull Request":
        fork_and_pr_ui()

#Task 17 - AWS SERVICE
def get_session():
    return boto3.session.Session()

AWS_REGIONS = [
    "us-east-1", "us-west-1", "us-west-2",
    "eu-west-1", "eu-central-1", "ap-south-1",
    "ap-northeast-1", "ap-southeast-1"
]

INSTANCE_TYPES = [
    "t2.micro", "t2.small", "t2.medium",
    "t3.micro", "t3.small", "t3.medium",
    "m5.large", "m5.xlarge", "c5.large"
]

def ec2_task():
    st.title("☁️ EC2 Manager — Launch or Terminate Instance")

    # Region selection
    region = st.selectbox("Select AWS Region", AWS_REGIONS, index=AWS_REGIONS.index("ap-south-1"))
    session = get_session()
    ec2 = session.resource('ec2', region_name=region)
    ec2_client = session.client('ec2', region_name=region)

    # Choose Action
    action = st.radio("Choose Action", ["Launch EC2 Instance", "Terminate EC2 Instance"])

    if action == "Launch EC2 Instance":
        st.subheader("🚀 Launch EC2 Instance")

        ami_id = st.text_input("Enter AMI ID", value="ami-0c02fb55956c7d316")
        instance_type = st.selectbox("Select Instance Type", INSTANCE_TYPES, index=INSTANCE_TYPES.index("t2.micro"))
        key_name = st.text_input("Key Pair Name (already exists in AWS)")
        min_count = st.number_input("Minimum Instance Count", min_value=1, value=1)
        max_count = st.number_input("Maximum Instance Count", min_value=1, value=1)

        if st.button("Launch"):
            try:
                instances = ec2.create_instances(
                    ImageId=ami_id,
                    InstanceType=instance_type,
                    KeyName=key_name,
                    MinCount=min_count,
                    MaxCount=max_count
                )
                ids = [inst.id for inst in instances]
                st.success(f"Launched EC2 Instance(s): {', '.join(ids)}")
            except Exception as e:
                st.error(f"Launch failed: {e}")

    elif action == "Terminate EC2 Instance":
        st.subheader("🛑 Terminate EC2 Instance")

        try:
            instances = ec2_client.describe_instances(
                Filters=[{'Name': 'instance-state-name', 'Values': ['running', 'pending']}]
            )

            instance_options = []
            for reservation in instances['Reservations']:
                for instance in reservation['Instances']:
                    instance_options.append(f"{instance['InstanceId']} ({instance['InstanceType']})")

            if instance_options:
                selected_instance = st.selectbox("Select EC2 instance to terminate", instance_options)
                instance_id = selected_instance.split()[0]

                if st.button("Terminate"):
                    instance = ec2.Instance(instance_id)
                    instance.terminate()
                    st.success(f"Instance {instance_id} termination initiated.")
            else:
                st.info("No running/pending instances found.")

        except Exception as e:
            st.error(f"Error fetching instances: {e}")


#Task 18 -  linux Command 
def linux_command():
    st.header("📚 Linux Command Reference Guide")
    
    command_categories = {
        'File Operations': {
            '1': ('List files (detailed)', 'ls -la'),
            '2': ('Change directory', 'cd [dir]'),
            '3': ('Print current directory', 'pwd'),
            '4': ('Create directory', 'mkdir [name]'),
            '5': ('Remove empty directory', 'rmdir [name]'),
            '6': ('Remove file/directory', 'rm -r [name]'),
            '7': ('Copy file/directory', 'cp -r [src] [dest]'),
            '8': ('Move/rename file', 'mv [old] [new]'),
            '9': ('Create empty file', 'touch [file]'),
            '10': ('Show file content', 'cat [file]')
        },
        'File Viewing/Editing': {
            '1': ('View file (paginated)', 'less [file]'),
            '2': ('View file (basic)', 'more [file]'),
            '3': ('Show first 10 lines', 'head [file]'),
            '4': ('Show last 10 lines', 'tail [file]'),
            '5': ('Follow log file', 'tail -f [file]'),
            '6': ('Edit file (nano)', 'nano [file]'),
            '7': ('Edit file (vim)', 'vim [file]')
        },
        'System Information': {
            '1': ('Kernel/system info', 'uname -a'),
            '2': ('Disk space (human)', 'df -h'),
            '3': ('Directory size', 'du -sh [dir]'),
            '4': ('Memory usage', 'free -m'),
            '5': ('Process monitor (basic)', 'top'),
            '6': ('Process monitor (advanced)', 'htop'),
            '7': ('System uptime', 'uptime'),
            '8': ('Command history', 'history'),
            '9': ('Environment variables', 'printenv')
        },
        'Process Management': {
            '1': ('List processes', 'ps aux'),
            '2': ('Kill process by PID', 'kill [pid]'),
            '3': ('Force kill process', 'kill -9 [pid]'),
            '4': ('Kill by name', 'killall [name]'),
            '5': ('Kill by pattern', 'pkill [pattern]'),
            '6': ('Background jobs', 'jobs'),
            '7': ('Move job to background', 'bg [job]'),
            '8': ('Bring job to foreground', 'fg [job]')
        },
        'Networking': {
            '1': ('Ping host', 'ping [host]'),
            '2': ('Network interfaces (old)', 'ifconfig'),
            '3': ('Network interfaces (new)', 'ip addr'),
            '4': ('Network statistics', 'netstat -tulnp'),
            '5': ('Socket statistics', 'ss -tulnp'),
            '6': ('Download file (wget)', 'wget [url]'),
            '7': ('Download file (curl)', 'curl -O [url]'),
            '8': ('SSH connection', 'ssh [user]@[host]'),
            '9': ('Secure copy', 'scp [file] [user]@[host]:[path]'),
            '10': ('Check listening ports', 'lsof -i')
        },
        'Permissions/Ownership': {
            '1': ('Change permissions', 'chmod [mode] [file]'),
            '2': ('Change owner', 'chown [user] [file]'),
            '3': ('Change group', 'chgrp [group] [file]'),
            '4': ('Default permissions', 'umask'),
            '5': ('Execute as superuser', 'sudo [command]')
        },
        'Search/Text Processing': {
            '1': ('Search text in files', 'grep "[pattern]" [file]'),
            '2': ('Find files', 'find [dir] -name "[pattern]"'),
            '3': ('Text processor', 'awk \'{print $1}\' [file]'),
            '4': ('Stream editor', 'sed \'s/old/new/g\' [file]'),
            '5': ('Count lines/words', 'wc [file]'),
            '6': ('Sort lines', 'sort [file]'),
            '7': ('Remove duplicates', 'uniq [file]')
        },
        'Compression/Archives': {
            '1': ('Create tar.gz', 'tar -czvf [archive].tar.gz [dir]'),
            '2': ('Extract tar.gz', 'tar -xzvf [archive].tar.gz'),
            '3': ('Create zip', 'zip -r [archive].zip [dir]'),
            '4': ('Extract zip', 'unzip [archive].zip')
        }
    }

    # Create tabs for each category
    tabs = st.tabs(list(command_categories.keys()))
    
    for tab, category in zip(tabs, command_categories):
        with tab:
            st.subheader(f"{category} Commands")
            
            # Create a table-like display for each command
            for key in command_categories[category]:
                description, command = command_categories[category][key]
                col1, col2 = st.columns([3, 7])
                with col1:
                    st.markdown(f"**{key}. {description}**")
                with col2:
                    st.code(command, language='bash')
            
            st.markdown("---")


#Task 19 - Geo Location Tool
def geo_location():
    st.title("📍 Device Geolocation Finder")
    
    # Get device IP and location
    try:
        # Get public IP
        ip = geocoder.ip('me').ip
        # Get location details
        g = geocoder.ip(ip)
        
        with st.expander("🌍 Your Location Details"):
            st.subheader("Device Information")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Public IP Address", ip)
                st.metric("City", g.city)
                st.metric("ISP", g.org)
            with col2:
                st.metric("Country", g.country)
                st.metric("Region/State", g.state)
                st.metric("Postal Code", g.postal)
            
            st.subheader("Map View")
            # Create map centered at the location
            m = folium.Map(location=[g.lat, g.lng], zoom_start=10)
            folium.Marker(
                [g.lat, g.lng],
                popup=f"Your Location: {g.city}",
                tooltip="Click for details"
            ).add_to(m)
            folium_static(m)
            
            st.warning("Note: This shows your approximate location based on your public IP. Accuracy depends on your ISP.")
            
    except Exception as e:
        st.error(f"Could not determine location. Error: {e}")
        st.info("This might happen if you're on a local network or behind a VPN.")
    
    # Additional network information
    with st.expander("🔍 Network Details"):
        try:
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            
            st.write("**Local Network Information**")
            st.code(f"""
            Hostname: {hostname}
            Local IP: {local_ip}
            Public IP: {ip if 'ip' in locals() else 'Not available'}
            """)
            
            st.write("**How This Works**")
            st.markdown("""
            - Uses your public IP address to estimate location
            - Accuracy depends on your ISP's geolocation data
            - Typically accurate to city-level
            - VPNs/proxies will show the exit node location
            """)
            
        except Exception as e:
            st.error(f"Could not fetch network details: {e}")

    st.success("Location detection complete!")

# Task 20 - Weather App
def weather_app():
    st.title("⛅ Weather Explorer")
    
    # API configuration (replace with your OpenWeather API key)
    API_KEY = OPENWEATHER_API_KEY  # Use your own API key here
    BASE_URL = "https://api.openweathermap.org/data/2.5/weather"
    FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"
    
    # Location input
    with st.expander("🔍 Search Location", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            city = st.text_input("City Name", "London")
        with col2:
            country = st.text_input("Country Code (optional)", "UK")
        
        search_query = f"{city},{country}" if country else city
    
    # Fetch weather data
    if st.button("Get Weather"):
        try:
            # Current weather
            current_params = {
                'q': search_query,
                'appid': API_KEY,
                'units': 'metric'  # For Celsius
            }
            current_response = requests.get(BASE_URL, params=current_params).json()
            
            # 5-day forecast
            forecast_params = {
                'q': search_query,
                'appid': API_KEY,
                'units': 'metric',
                'cnt': 40  # 5 days data (8 forecasts per day)
            }
            forecast_response = requests.get(FORECAST_URL, params=forecast_params).json()
            
            # Display current weather
            with st.expander("🌤️ Current Weather", expanded=True):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Temperature", f"{current_response['main']['temp']}°C")
                    st.metric("Feels Like", f"{current_response['main']['feels_like']}°C")
                with col2:
                    st.metric("Humidity", f"{current_response['main']['humidity']}%")
                    st.metric("Pressure", f"{current_response['main']['pressure']} hPa")
                with col3:
                    st.metric("Wind Speed", f"{current_response['wind']['speed']} m/s")
                    st.metric("Visibility", f"{current_response.get('visibility', 'N/A')} m")
                
                # Weather description with icon
                weather_desc = current_response['weather'][0]['description'].title()
                weather_icon = current_response['weather'][0]['icon']
                st.image(f"http://openweathermap.org/img/wn/{weather_icon}@2x.png", width=100)
                st.subheader(weather_desc)
                
                # Sunrise/sunset
                sunrise = datetime.fromtimestamp(current_response['sys']['sunrise'], pytz.UTC)
                sunset = datetime.fromtimestamp(current_response['sys']['sunset'], pytz.UTC)
                st.write(f"**Sunrise:** {sunrise.strftime('%H:%M')} | **Sunset:** {sunset.strftime('%H:%M')}")
            
            # Display forecast
            with st.expander("📅 5-Day Forecast"):
                # Group by day
                daily_forecasts = {}
                for forecast in forecast_response['list']:
                    date = datetime.fromtimestamp(forecast['dt']).strftime('%Y-%m-%d')
                    if date not in daily_forecasts:
                        daily_forecasts[date] = []
                    daily_forecasts[date].append(forecast)
                
                # Display each day
                for date, forecasts in daily_forecasts.items():
                    day_name = datetime.strptime(date, '%Y-%m-%d').strftime('%A')
                    st.subheader(f"{day_name} ({date})")
                    
                    cols = st.columns(len(forecasts))
                    for idx, forecast in enumerate(forecasts):
                        time = datetime.fromtimestamp(forecast['dt']).strftime('%H:%M')
                        temp = forecast['main']['temp']
                        icon = forecast['weather'][0]['icon']
                        
                        with cols[idx]:
                            st.write(f"**{time}**")
                            st.image(f"http://openweathermap.org/img/wn/{icon}.png", width=50)
                            st.write(f"{temp}°C")
                            st.write(forecast['weather'][0]['description'].title())
            
            st.success("Weather data fetched successfully!")
            
        except Exception as e:
            st.error(f"Error fetching weather data: {str(e)}")
            st.info("Please check the city name or your API key.")
    
    # API documentation reference
    st.markdown("""
    ---
    *Using [OpenWeatherMap API](https://openweathermap.org/api)*
    """)

# Task 21 - Instagram Photo Poster
def instagram_post_app():
    # Streamlit UI setup
    # st.set_page_config(page_title="Instagram Photo Poster", page_icon="📸", layout="centered")
    st.title("📸 Instagram Photo Poster")

    # Sidebar login credentials
    st.header("Login Credentials")
    username = st.text_input("Instagram Username")
    password = st.text_input("Instagram Password", type="password")

    # Image upload & caption
    uploaded_file = st.file_uploader("Upload an image to post", type=["jpg", "jpeg", "png"])
    caption = st.text_area("Write your caption here...")

    # Post button
    if st.button("🚀 Post to Instagram"):
        if not username or not password:
            st.error("Please enter both username and password in the sidebar.")
        elif not uploaded_file:
            st.error("Please upload an image.")
        else:
            with st.spinner("Logging in and uploading..."):
                try:
                    cl = Client()
                    cl.login(username, password)

                    # Save uploaded image temporarily
                    with NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_file:
                        tmp_file.write(uploaded_file.read())
                        temp_path = tmp_file.name

                    # Upload to Instagram
                    cl.photo_upload(path=temp_path, caption=caption or "")
                    st.success("✅ Photo uploaded successfully!")

                    # Cleanup temp file
                    os.remove(temp_path)
                    cl.logout()

                except Exception as e:
                    st.error(f"❌ Error: {e}")

# Task 22 - Coding Assistant Chatbot
def coding_assistant_chatbot():
    # Hardcoded API Key and Model
    API_KEY = GEMINI_API_KEY  # Replace with your actual key
    MODEL_NAME = "gemini-1.5-flash"

    # Configure Gemini
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel(MODEL_NAME)

    st.title("💻 Coding Assistant Chatbot (Gemini API)")

    # Initialize chat history
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Input box for user query
    user_input = st.text_input("Ask your coding question here:", key="user_input")

    if st.button("Send"):
        if user_input.strip():
            # Add user query to chat history
            st.session_state.chat_history.append({"role": "user", "text": user_input})

            # Get response from Gemini
            try:
                response = model.generate_content(
                    f"You are a coding assistant. Format answers with markdown and syntax highlighting when showing code.\nUser: {user_input}"
                )
                bot_reply = response.text.strip()

                # Ensure code formatting
                if "```" not in bot_reply and any(word in bot_reply.lower() for word in ["code", "python", "example", "function"]):
                    bot_reply = f"```python\n{bot_reply}\n```"

                # Add bot reply to chat history
                st.session_state.chat_history.append({"role": "assistant", "text": bot_reply})

            except Exception as e:
                bot_reply = f"⚠️ Error: {str(e)}"
                st.session_state.chat_history.append({"role": "assistant", "text": bot_reply})

    # Display chat history
    for chat in st.session_state.chat_history:
        if chat["role"] == "user":
            st.markdown(f"**🧑 You:** {chat['text']}")
        else:
            st.markdown(f"**🤖 Bot:**\n\n{chat['text']}", unsafe_allow_html=False)


# Blogs and More 
def blog_More():
    # st.set_page_config(page_title="Linux Exploration Blog", layout="wide")

    st.title("🌐 Linux Exploration Blog")
    
    # Blog links section with interactive buttons
    st.subheader("📚 Explore My Latest Tech Blogs")
    
    # Create columns for better layout
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### Linux & DevOps")
        if st.button("🏢 Why Big Companies Love Linux", use_container_width=True):
            st.markdown("[Why Big Companies Love Linux: The Ultimate Guide to Enterprise Adoption](https://medium.com/@vimalprajapat379/why-big-companies-love-linux-the-ultimate-guide-to-enterprise-adoption-5dc11124330a)", unsafe_allow_html=True)
        if st.button("🔄 Git & GitHub Mastery", use_container_width=True):
            st.markdown("[Mastering Git & GitHub: From Zero to Pull Requests](https://medium.com/@vimalprajapat379/mastering-git-github-from-zero-to-pull-requests-e4362c8f1bb5)", unsafe_allow_html=True)
    
    with col2:
        st.markdown("### AWS & Cloud")
        if st.button("☁️ AWS Success Stories", use_container_width=True):
            st.markdown("[AWS Success Stories: How Top Companies Leverage Cloud Computing](https://medium.com/@vimalprajapat379/aws-success-stories-how-top-companies-leverage-cloud-computing-%EF%B8%8F-dbf45c8c5280)", unsafe_allow_html=True)
        if st.button("🗃️ AWS S3 Storage Classes", use_container_width=True):
            st.markdown("[☁️ AWS S3 Storage Classes Demystified](https://medium.com/@vimalprajapat379/%EF%B8%8F-aws-s3-storage-classes-demystified-from-basics-to-expert-level-insights-9d766100fb5a)", unsafe_allow_html=True)
        if st.button("🤖 Amazon Q AI Assistant", use_container_width=True):
            st.markdown("[Amazon Q: The Smart AI Assistant for AWS](https://medium.com/@vimalprajapat379/amazon-q-the-smart-ai-assistant-for-aws-beginner-advanced-3e13f0029a5e)", unsafe_allow_html=True)
    
    with col3:
        st.markdown("### Web Development")
        if st.button("🖥️ 50 Essential HTML Tags", use_container_width=True):
            st.markdown("[50 Essential HTML Tags Every Web Developer Should Know](https://medium.com/@vimalprajapat379/50-essential-html-tags-every-web-developer-should-know-c0772a5180e4)", unsafe_allow_html=True)
    
    # Blog links section
    st.markdown("""---""")

    with st.expander("1. 🏢 Companies Using Linux"):
        st.markdown("""
        - **Google** – Uses Linux on servers for scalability and security.
        - **Facebook** – Customizes Linux (e.g., CentOS) for performance in data centers.
        - **NASA** – Chooses Linux for its reliability in critical missions.
        - **Amazon** – Powers AWS with Linux for flexibility and cost-effectiveness.
        - **IBM** – Major contributor to Linux, uses it for enterprise servers.

        **Benefits:**
        - Open-source and cost-effective.
        - Highly customizable and secure.
        - Reliable performance at scale.
        """)

    with st.expander("2. 🧠 GUI Programs and Their Backend Commands"):
        st.table({
            "GUI Program": ["GNOME Files (Nautilus)", "Gedit", "Terminal", "Screenshot Tool", "System Monitor"],
            "Command Behind": ["nautilus", "gedit", "gnome-terminal", "gnome-screenshot", "gnome-system-monitor"]
        })

    with st.expander("3. 🎨 Change Logo/Icon of a Linux Program"):
        st.markdown("""
        1. Locate `.desktop` file in `/usr/share/applications/` or `~/.local/share/applications/`
        2. Edit the line: `Icon=/path/to/new/icon.png`
        3. Refresh desktop icons or log out and log in again.
        """)

    with st.expander("4. 💻 Add More Terminals & GUI Interfaces"):
        st.markdown("""
        - **Terminals**: Install `tilix`, `guake`, `terminator`
        - **GUIs**: Install desktop environments like `KDE`, `XFCE`, `MATE`

        Example command:
        ```bash
        sudo apt install xfce4
        ```
        """)

    with st.expander("5. 📬 Communication via Linux Terminal"):
        st.markdown("""
        - **Email**: `mail` or `mutt`
        - **WhatsApp**: Use Twilio API with `curl` or Python
        - **Tweet**: Use `t` CLI tool (with Twitter API)
        - **SMS**: Twilio CLI or Python Boto3 + AWS SNS
        """)

    with st.expander("6. ⌨️ Linux Keyboard Shortcuts (Ctrl+C and Ctrl+Z)"):
        st.table({
            "Shortcut": ["Ctrl+C", "Ctrl+Z"],
            "Command Equivalent": ["kill -2 (SIGINT)", "kill -20 (SIGTSTP)"],
            "Purpose": ["Interrupts the process", "Suspends the process"]
        })
        st.code("""
    kill -2 <PID>   # equivalent to Ctrl+C
    kill -20 <PID>  # equivalent to Ctrl+Z
        """)

    with st.expander("7. 🐍 Technical Difference Between Tuple and List (Python)"):
        st.markdown("""
        ### Key Differences:
        
        | Feature        | Tuple                      | List                       |
        |---------------|---------------------------|---------------------------|
        | Mutability    | Immutable (cannot be changed after creation) | Mutable (can be modified) |
        | Syntax        | Uses parentheses `()`     | Uses square brackets `[]` |
        | Performance   | Faster iteration          | Slightly slower           |
        | Memory        | More memory efficient     | Less memory efficient     |
        | Use Cases     | Fixed data, dictionary keys | Dynamic collections      |
        
        ### Example Code:
        ```python
        # Tuple creation
        coordinates = (10.5, 20.3)
        
        # List creation
        colors = ['red', 'green', 'blue']
        
        # Attempting to modify (will raise error for tuple)
        colors[0] = 'yellow'  # Works
        # coordinates[0] = 15.2  # TypeError: 'tuple' object does not support item assignment
        ```
        
        ### When to Use Each:
        - **Use tuples** for:
          - Data that shouldn't change (like coordinates, dates)
          - Dictionary keys (since they're hashable)
          - Function arguments and return values when order matters
          
        - **Use lists** for:
          - Collections that need to grow/shrink
          - When you need to modify elements
          - Implementing stacks/queues
        """)

    st.success("✍️ Created as part of Linux learning ")


# Main app logic
if menu_choice == "System Info":
    show_ram_info()
elif menu_choice == "Messaging":
    messaging_option = st.selectbox("Select Messaging Service", ["WhatsApp", "Twilio SMS/Call"])
    if messaging_option == "WhatsApp":
        send_whatsapp_message()
    else:
        twilio_messaging()
elif menu_choice == "Email":
    send_email()
elif menu_choice == "Web Automation":
    web_option = st.selectbox("Select Web Task", ["Google Search", "Web Scraping"])
    if web_option == "Google Search":
        google_search()
    else:
        web_scraping()
elif menu_choice == "Image Processing":
    image_option = st.selectbox("Select Image Task", ["Create Digital Image", "Face Swap"])
    if image_option == "Create Digital Image":
        create_image()
    else:
        face_swap()
elif menu_choice == "Linux Automation":
    linux_automation()
elif menu_choice == "GitHub Automation":
    github_Automation()
elif menu_choice == "AWS Automation":
    ec2_task()
elif menu_choice == "Linux Commands":
    linux_command()
elif menu_choice == "Geo Location":
    geo_location()
elif menu_choice == "Blogs & More":
    blog_More()
elif menu_choice == "Weather Explorer":
    weather_app()
elif menu_choice == "Instagram":
    instagram_post_app()
elif menu_choice == "Coding Assistant Chatbot":
    coding_assistant_chatbot()

# Footer
st.sidebar.markdown("---")
st.sidebar.info("Multi-Tool Application | Created with Streamlit")