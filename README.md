# 🔐 Router Automation Script (Python)

A Python-based automation tool to **log in to a router via JSON-RPC**, generate **secure passwords**, fetch system information, capture packets, and safely log out — all using a persistent session.

> Built for learning, automation, and controlled network environments ⚙️

---

## ✨ Features

✅ Secure router login using JSON-RPC  
✅ Token-based authentication handling  
✅ Cryptographically secure password generation  
✅ Session-based requests using `requests.Session()`  
✅ Packet capture & download (`.pcap`)  
✅ Fetch router/system/network information  
✅ Clean logout handling  
✅ Modular & extensible design

---

## 📁 Project Structure

```
.
├── main.py
├── config.ini
├── credentials.json
├── newpass.txt
├── capture.pcap
└── README.md
```

---

## ⚙️ Configuration

### `config.ini`

```ini
[IP]
ip = 192.168.1.1
```

### `credentials.json`

```json
{
	"username": "admin",
	"password": "your_router_password"
}
```

⚠️ **Never commit `credentials.json` to GitHub**  
Add it to `.gitignore`.

---

## 🔑 Secure Password Generator

Passwords are generated using:

-   Random names
-   Random digits
-   Special characters
-   `secrets` module (cryptographically secure)

Saved automatically to:

```
newpass.txt
```

---

## 🚀 Usage

```bash
python main.py
```

---

## 🧪 Available API Calls

```python
getLanClients
getCpuUtilisation
getSystemInformation
getWirelessConfiguration
```

---

## 📡 Packet Capture

```python
connection.capture_packet(interface="any", size=5)
```

---

## 🛡️ Security Notice

Use this script **only on routers/networks you own or have permission to test(for JIO)**.

---

## 👨‍💻 Author

**Susilcreation_68**

---

⭐ If you like this project, consider giving it a star!
