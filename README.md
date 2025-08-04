# Multi-Tool Streamlit App 🚀

A powerful and user-friendly **Streamlit** application that brings together multiple everyday utilities and automation tools in a single interactive dashboard. Ideal for students, developers, and professionals!

## 🔧 Features

### 🧠 System Utilities
- **Monitor System RAM** usage in real-time.
- **Remote Command Execution** via SSH on Linux servers.
- **Linux Command Reference Guide** for learning & usage.

### 💬 Communication
- **Send WhatsApp Messages** using PyWhatKit.
- **Send SMS / Make Calls** using Twilio API.
- **Send Emails** with attachments using SMTP.

### 🌐 Web & GitHub Automation
- **Automated Google Search** and result scraping.
- **GitHub Integration**:
  - Create branches
  - Push code
  - Fork repositories
  - Open pull requests

### 📷 Image & Audio Processing
- **Digital Image Generator** using OpenCV and Pillow.
- **Face Swap Tool**
- **Voice-to-Text Conversion** (Speech Recognition).
- **Text-to-Speech** (optional feature using `pyttsx3` or similar).

### ☁️ AWS Cloud Integration
- Launch and Terminate **AWS EC2 Instances** using `boto3`.
- Monitor logs using **CloudWatch**.
- Upload files to **S3** (no Console required).
- Transcribe audio using **AWS Transcribe** (event-driven via Lambda).

### 📚 Learning Resources
- Built-in **Linux tutorials**, **AWS blogs**, and **hands-on examples**.

---

## 🛠️ Tech Stack

- **Frontend**: Streamlit
- **Backend**: Python
- **Cloud**: AWS (EC2, S3, Lambda, CloudWatch)
- **Automation APIs**: Twilio, GitHub, Google Search
- **Libraries**: OpenCV, Pillow, Paramiko, Boto3, SpeechRecognition, Requests

---

## 🚀 Getting Started

### Prerequisites

Ensure you have Python 3.8+ installed.

Install dependencies:

```bash
pip install -r requirements.txt
```

### Run the App

```bash
streamlit run app.py
```

---

## 🔐 Environment Setup

Create a `.env` file or securely manage the following:

- `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`
- `EMAIL_USER`, `EMAIL_PASSWORD`
- `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`
- SSH credentials for remote Linux machines



## 🤝 Contribution

Pull requests are welcome! For major changes, open an issue first to discuss what you’d like to change.

---

## 📜 License

MIT License

---

## ✨ Author

Made with ❤️ by **Vimal Kumar**  
[GitHub](https://github.com/Vimal379) | [LinkedIn](https://www.linkedin.com/in/vimal-kumar-93b60a23b) | Jaipur, Rajasthan 🇮🇳

---

## 📷 Preview

> Screenshot or GIF of your Streamlit app UI for better clarity!_
> <img width="1791" height="922" alt="Screenshot 2025-08-04 135118" src="https://github.com/user-attachments/assets/3eaec434-e9f2-4683-9796-a84472808a8a" />

> <img width="1751" height="920" alt="Screenshot 2025-08-04 135141" src="https://github.com/user-attachments/assets/20f092c1-814f-40ae-b95b-0999a81efb76" />

> <img width="1882" height="829" alt="Screenshot 2025-08-04 135208" src="https://github.com/user-attachments/assets/6b4748ed-f513-4347-a5b0-25a44a09dfc1" />



