# Termux Guardian 🛡️

A lightweight **defensive anti-cybercrime toolkit** for [Termux](https://termux.dev).  
Created and maintained by **[NINIA AND CHRISTIAN]**.  

✅ Works without root (proxy/honeypot defense layer)  
✅ Written in pure Python 3 (asyncio)  
✅ Designed for **educational and defensive use only**

---

## 📌 Purpose

The purpose of Termux Guardian is **to stop attacks before they harm you**, by:

- Acting as a **reverse-proxy shield** with per-IP rate-limiting and automatic bans.  
- Running a **honeypot** service to detect and trap malicious scanners.  
- Optionally watching your **SSH logs** (if you run `sshd -E` with a dedicated log file).  
- Logging and optionally sending **Termux notifications** when bans occur.  

⚠️ **Important**: This tool is defensive only.  
Do not use it for offensive hacking. Only deploy it on systems you **own or have explicit permission** to protect.  

---

## 🚀 Installation (Termux)

```bash
# Update Termux
pkg update && pkg upgrade -y

# Install Python
pkg install python -y

# (Optional: Termux notifications support)
pkg install termux-api -y

# Clone this repository
git clone https://github.com/YourGitHubUsername/termux-guardian.git
cd termux-guardian

# Make script executable
chmod +x termux_guardian.py
