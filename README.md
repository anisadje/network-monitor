# Network Monitor

A network monitoring tool in Python for Linux that checks the availability of machines in real time.

> Personal project, built to get a better grasp of my networking course.

---

## Features

- **Automatic ICMP ping** of each machine, at its own interval
- **Real-time dashboard** in the terminal, with colors (UP in green, DOWN in red)
- **Timestamped log** of every state change
- **Visual alerts** in the terminal when a machine goes down
- **Availability report** (% uptime per machine) when the program stops

---

## Project structure

```
network-monitor/
├── config/
│   └── hosts.conf       # machines to monitor
├── logs/
│   └── monitor.log      # timestamped events (created automatically)
├── monitor.py           # main script
└── README.md
```

---

## Installation

No external dependency: only modules from the Python standard library.

```bash
git clone https://github.com/anisadje/network-monitor.git
cd network-monitor
```

---

## Usage

### 1. Choose the machines to monitor

Edit `config/hosts.conf`:

```
# Format: IP_or_hostname   display_name   interval_seconds
192.168.1.1      Router           5
8.8.8.8          Google-DNS       10
github.com       GitHub           15
```

- Lines starting with `#` are ignored
- The interval is optional (default: 10 seconds)

### 2. Start monitoring

```bash
python3 monitor.py
```

### 3. Stop and show the report

```
Ctrl+C
```

The availability report is printed automatically.

---

## Example output

```
=== NETWORK MONITOR - 2026-03-21 18:22:03 ===
------------------------------------------------
Router          192.168.1.1        DOWN
Google-DNS      8.8.8.8            UP
GitHub          github.com         UP

⚠️  ALERT: Router (192.168.1.1) is DOWN!
```

```
              AVAILABILITY REPORT
------------------------------------------------
Router          192.168.1.1        0/12 pings   0.0% uptime
Google-DNS      8.8.8.8            6/6 pings    100.0% uptime
GitHub          github.com         4/4 pings    100.0% uptime
```

---

## Log format

Only state changes are logged, so the file stays short:

```
[2026-03-21 18:22:03] 192.168.1.1 (Router) -> DOWN
[2026-03-21 18:22:03] 8.8.8.8 (Google-DNS) -> UP
```

---

## Compatibility

- **OS:** Linux / WSL
- **Python:** 3.6+
- **Dependencies:** none (standard modules only: `subprocess`, `datetime`, `os`, `shutil`, `time`)

---

## Concepts

- **ICMP** protocol and ping-based monitoring
- Configuration file parsing
- State tracking and change detection
- Timestamped logging
- Terminal output with **ANSI** codes
- Clean shutdown on `KeyboardInterrupt`
