python3 termux_guardian.py proxy \
  --listen 0.0.0.0:8080 \
  --to 127.0.0.1:5000 \
  --per-minute 120 \
  --burst 60 \
  --fail-threshold 30 \
  --ban-mins 120
