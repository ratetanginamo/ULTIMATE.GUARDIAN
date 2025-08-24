# 1️⃣ Start Reverse Proxy Shield
# Protects a backend service (e.g., Flask app on 127.0.0.1:5000)
python3 termux_guardian.py proxy \
  --listen 0.0.0.0:8080 \
  --to 127.0.0.1:5000 \
  --per-minute 120 \
  --burst 60 \
  --fail-threshold 30 \
  --ban-mins 120

# 2️⃣ Run Honeypot
# Creates a fake service to trap attackers and auto-ban them
python3 termux_guardian.py honeypot \
  --listen 0.0.0.0:2222 \
  --ban-mins 240

# 3️⃣ Watch SSH Logs
# Monitor SSH log file for brute-force attempts and ban attackers
sshd -E $PREFIX/var/log/sshd.log
python3 termux_guardian.py watch-ssh \
  --log $PREFIX/var/log/sshd.log \
  --ban-mins 180

# 4️⃣ Banlist Management
# Show, unban, or clear active bans
python3 termux_guardian.py banlist --show
python3 termux_guardian.py banlist --unban 1.2.3.4
python3 termux_guardian.py banlist --clear
