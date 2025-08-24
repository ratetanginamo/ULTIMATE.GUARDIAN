#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Termux Guardian 🛡️
Defensive anti-cybercrime toolkit for Termux.
Created and maintained by NINIA AND CHRISTIAN
"""

import argparse
import asyncio
import time
import re
import sys
from collections import defaultdict
from pathlib import Path

# === Simple Ban Manager ===
class BanManager:
    def __init__(self):
        self.banned = {}  # ip -> until_timestamp

    def is_banned(self, ip):
        until = self.banned.get(ip, 0)
        return time.time() < until

    def ban(self, ip, minutes):
        self.banned[ip] = time.time() + minutes * 60
        print(f"[!] BANNED {ip} for {minutes} minutes")

    def unban(self, ip):
        if ip in self.banned:
            del self.banned[ip]
            print(f"[+] UNBANNED {ip}")

    def list(self):
        now = time.time()
        return {ip: until for ip, until in self.banned.items() if until > now}

    def clear(self):
        self.banned.clear()
        print("[+] Banlist cleared")

# === Global ban manager instance ===
ban_manager = BanManager()

# === Proxy Shield ===
async def handle_proxy(reader, writer, target_host, target_port,
                       per_minute, burst, fail_threshold, ban_minutes):
    peer = writer.get_extra_info("peername")
    if not peer:
        writer.close()
        return
    ip, _ = peer

    if ban_manager.is_banned(ip):
        writer.close()
        return

    try:
        remote_reader, remote_writer = await asyncio.open_connection(target_host, target_port)
    except Exception as e:
        print(f"[!] Could not connect to target: {e}")
        writer.close()
        return

    async def pipe(src, dst, ip):
        fails = 0
        while not src.at_eof():
            try:
                data = await src.read(1024)
                if not data:
                    break
                dst.write(data)
                await dst.drain()
            except Exception:
                fails += 1
                if fails > fail_threshold:
                    ban_manager.ban(ip, ban_minutes)
                    break
        dst.close()

    asyncio.create_task(pipe(reader, remote_writer, ip))
    asyncio.create_task(pipe(remote_reader, writer, ip))

async def start_proxy(listen_host, listen_port, to_host, to_port,
                      per_minute, burst, fail_threshold, ban_minutes):
    server = await asyncio.start_server(
        lambda r, w: handle_proxy(r, w, to_host, to_port,
                                  per_minute, burst, fail_threshold, ban_minutes),
        listen_host, listen_port
    )
    print(f"[+] Proxy shield running on {listen_host}:{listen_port} → {to_host}:{to_port}")
    async with server:
        await server.serve_forever()

# === Honeypot ===
async def handle_honeypot(reader, writer, ban_minutes):
    peer = writer.get_extra_info("peername")
    if not peer:
        writer.close()
        return
    ip, _ = peer
    print(f"[!] Honeypot connection from {ip}")
    ban_manager.ban(ip, ban_minutes)
    writer.write(b"Fake Service Ready\r\n")
    await writer.drain()
    writer.close()

async def start_honeypot(host, port, ban_minutes):
    server = await asyncio.start_server(
        lambda r, w: handle_honeypot(r, w, ban_minutes),
        host, port
    )
    print(f"[+] Honeypot running on {host}:{port}")
    async with server:
        await server.serve_forever()

# === SSH Watcher ===
async def watch_ssh_log(logfile, ban_minutes):
    path = Path(logfile)
    if not path.exists():
        print(f"[!] Log file {logfile} not found")
        return
    print(f"[+] Watching SSH log {logfile}")
    with path.open("r") as f:
        f.seek(0, 2)  # go to end
        while True:
            line = f.readline()
            if not line:
                await asyncio.sleep(1)
                continue
            if "Failed password" in line:
                m = re.search(r"from ([0-9.]+)", line)
                if m:
                    ip = m.group(1)
                    print(f"[!] SSH brute-force from {ip}")
                    ban_manager.ban(ip, ban_minutes)

# === Banlist CLI ===
def manage_banlist(show, unban, clear):
    if show:
        active = ban_manager.list()
        if not active:
            print("[+] No active bans")
        else:
            print("[+] Active bans:")
            for ip, until in active.items():
                remaining = int(until - time.time())
                print(f"  {ip} → {remaining//60} min left")
    if unban:
        ban_manager.unban(unban)
    if clear:
        ban_manager.clear()

# === CLI Parser ===
def main():
    parser = argparse.ArgumentParser(description="Termux Guardian 🛡️ - Defensive anti-cybercrime toolkit")
    sub = parser.add_subparsers(dest="command")

    # Proxy
    p = sub.add_parser("proxy")
    p.add_argument("--listen", required=True, help="Listen host:port")
    p.add_argument("--to", required=True, help="Target host:port")
    p.add_argument("--per-minute", type=int, default=60)
    p.add_argument("--burst", type=int, default=30)
    p.add_argument("--fail-threshold", type=int, default=10)
    p.add_argument("--ban-mins", type=int, default=60)

    # Honeypot
    h = sub.add_parser("honeypot")
    h.add_argument("--listen", required=True, help="Listen host:port")
    h.add_argument("--ban-mins", type=int, default=120)

    # SSH watcher
    w = sub.add_parser("watch-ssh")
    w.add_argument("--log", required=True, help="SSH log file")
    w.add_argument("--ban-mins", type=int, default=120)

    # Banlist
    b = sub.add_parser("banlist")
    b.add_argument("--show", action="store_true")
    b.add_argument("--unban", help="IP to unban")
    b.add_argument("--clear", action="store_true")

    args = parser.parse_args()

    if args.command == "proxy":
        host, port = args.listen.split(":")
        to_host, to_port = args.to.split(":")
        asyncio.run(start_proxy(host, int(port), to_host, int(to_port),
                                args.per_minute, args.burst, args.fail_threshold, args.ban_mins))
    elif args.command == "honeypot":
        host, port = args.listen.split(":")
        asyncio.run(start_honeypot(host, int(port), args.ban_mins))
    elif args.command == "watch-ssh":
        asyncio.run(watch_ssh_log(args.log, args.ban_mins))
    elif args.command == "banlist":
        manage_banlist(args.show, args.unban, args.clear)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
