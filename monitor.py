import subprocess
from datetime import datetime
import os
import shutil
import time

DEFAULT_INTERVAL = 10  # default ping interval (seconds) when hosts.conf does not give one

# ANSI colors

GREEN = "\033[32m"
RED = "\033[31m"
RESET = "\033[0m"
BOLD = "\033[1m"
RED_BG = "\033[41m"

# CONFIGURATION

def load_hosts(filepath):
    """
    Reads the configuration file and returns the list of hosts to monitor.
    """
    hosts = []
    try:
        with open(filepath, "r") as f:
            lines = f.readlines()
            for line in lines:
                line = line.strip()

                # Skip empty lines and comments
                if line == "" or line.startswith("#"):
                    continue

                fields = line.split()
                if len(fields) < 2:
                    print(f"Skipped line (invalid format): '{line}'")
                    continue
                host = {"ip": fields[0],
                        "name": fields[1],
                        "interval": int(fields[2]) if len(fields) >= 3 else DEFAULT_INTERVAL}
                hosts.append(host)

    except FileNotFoundError:
        print(f"Error: file '{filepath}' not found.")
        return []

    return hosts

# PING

def ping_host(ip):
    """
    Sends one ICMP ping to the given address and returns whether it answered.

    Uses the system ping command:
        -c 1 : send a single packet
        -W 1 : wait at most 1 second

    Returns True if the host answers (exit code 0), False otherwise.
    """
    result = subprocess.run(
        ["ping", "-c", "1", "-W", "1", ip],
        stdout=subprocess.DEVNULL,  # hide the ping output
        stderr=subprocess.DEVNULL
    )
    return result.returncode == 0

# LOGGING

def log_event(ip, name, status):
    """
    Writes a state change to the log file.

    The file is opened in append mode so the history is never overwritten.
    """
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    state = "UP" if status else "DOWN"
    os.makedirs("logs", exist_ok=True)
    with open("logs/monitor.log", "a") as f:
        f.write(f"[{now}] {ip} ({name}) -> {state}\n")

# CHECKING A HOST

def check_host(host, previous_states):
    """
    Pings a host and detects state changes.

    If the state changed since the last ping (e.g. UP then DOWN),
    the event is written to the log.

    Returns the current status (True = UP, False = DOWN).
    """
    ip = host["ip"]
    name = host["name"]
    new_status = ping_host(ip)

    # Only log when the state changes (avoids duplicates in the log)
    if new_status != previous_states.get(ip):
        previous_states[ip] = new_status
        log_event(ip, name, new_status)

    return new_status

# DASHBOARD

def show_dashboard(hosts, previous_states):
    """
    Clears the terminal and shows the current state of every host,
    followed by an alert for each host that is DOWN.
    """
    os.system("clear")

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"{BOLD}=== NETWORK MONITOR - {now} ==={RESET}")
    print("-" * 48)

    for host in hosts:
        ip = host["ip"]
        name = host["name"]
        status = previous_states.get(ip)

        if status == True:
            state = "UP"
            color = GREEN
        elif status == False:
            state = "DOWN"
            color = RED
        else:
            state = "..."
            color = ""

        print(f"{name.ljust(15)} {ip.ljust(18)} {color}{BOLD}{state}{RESET}")

    # Alerts are printed after the table, otherwise "clear" would erase them
    for host in hosts:
        if previous_states.get(host["ip"]) == False:
            print(f"\n{RED_BG}{BOLD}⚠️  ALERT: {host['name']} ({host['ip']}) is DOWN! {RESET}")


def show_report(hosts, total_pings, total_up):
    """
    Prints the final availability report.
    """
    width = shutil.get_terminal_size().columns
    print(f"\n{BOLD}{'AVAILABILITY REPORT'.center(width)}{RESET}")
    print("-".center(width, "-"))
    for host in hosts:
        ip = host["ip"]
        name = host["name"]
        total = total_pings[ip]
        up = total_up[ip]
        pct = (up / total * 100) if total > 0 else 0

        line = f"{name.ljust(15)} {ip.ljust(18)} {up}/{total} pings   {pct:.1f}% uptime"
        print(line.center(width))

def monitor(hosts):
    previous_states = {}
    total_pings = {}
    total_up = {}
    last_check = {}
    for host in hosts:
        previous_states[host["ip"]] = None
        total_pings[host["ip"]] = 0
        total_up[host["ip"]] = 0
        last_check[host["ip"]] = 0
    try:
        while True:
            now = time.time()
            for host in hosts:
                ip = host["ip"]
                # each host is pinged at its own interval
                if now - last_check[ip] < host["interval"]:
                    continue
                last_check[ip] = now
                status = check_host(host, previous_states)
                total_pings[ip] += 1
                if status:
                    total_up[ip] += 1
            show_dashboard(hosts, previous_states)
            time.sleep(1)
    except KeyboardInterrupt:
        show_report(hosts, total_pings, total_up)

if __name__ == "__main__":
    hosts = load_hosts("config/hosts.conf")
    monitor(hosts)
