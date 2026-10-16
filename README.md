Linux Shake to Find Cursor 🖱️✨
A lightweight Python utility designed for Linux to solve the common struggle of losing a small cursor. Inspired by macOS's "Shake-to-Find" feature, this script detects rapid back-and-forth mouse movements to temporarily enlarge and stylize your cursor with smooth animations, automatically returning it to normal after a short delay.

Features
·	Shake-to-Find Gesture: Prevents accidental triggers during normal fast movements by requiring a rapid back-and-forth shaking motion.
·	Dynamic Size & Theme Changes: Customize both your normal cursor size/color and its expanded state.
·	Smooth Animations: Gradual fade-in and fade-out transitions using step-based interpolation.
·	Background Service: Runs seamlessly as a user-level systemd service so it's always active upon login.

Prerequisites
Make sure you have Python 3 installed on your system along with the required package:
sudo apt update
sudo apt install python3-pynput dmz-cursor-theme xcursor-themes


Installation & Setup
1. Clone or Download the Script
Place your main.py script in your preferred directory (e.g., inside your project folder or home directory).
2. Configure Your Preferences
Open cursor_booster.py and adjust the configuration variables at the top of the file to match your desired themes and sizes:
# --- CONFIGURATION ---
NORMAL_THEME = "redglass"    # Normal cursor theme/color
NORMAL_SIZE = 24              # Normal cursor size (px)

LARGE_THEME = "redglass"     # Expanded cursor theme/color
LARGE_SIZE = 72               # Expanded cursor size (px)

HOLD_DELAY = 1.2              # Duration to hold expanded state (seconds)

To see available themes installed on your system, run:
ls /usr/share/icons

3. Setup as a Systemd Background Service
To keep the script running automatically in the background:
1.	Create the systemd user directory if it doesn't exist:
2.	mkdir -p ~/.config/systemd/user

3.	Create a new service file:
4.	nano ~/.config/systemd/user/cursor-booster.service

5.	Paste the following configuration (make sure to replace /home/name/DirectoriName/main.py with your actual file path):
6.	[Unit]
Description=Cursor Booster Shake-to-Find Service
After=graphical-session.target

[Service]
Type=simple
Environment=DISPLAY=:0
Environment=DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/%U/bus
ExecStart=/usr/bin/python3 "/home/name/DirectoriName/main.py"
Restart=always
RestartSec=3

[Install]
WantedBy=default.target

7.	Enable and start your service:
8.	systemctl --user daemon-reload
systemctl --user enable cursor-booster.service
systemctl --user start cursor-booster.service

9.	Check the status to ensure it's running smoothly:
10.	systemctl --user status cursor-booster.service


Usage
Simply shake your mouse back and forth rapidly (left-right-left-right) within a fraction of a second. Your cursor will smoothly expand and highlight itself, then shrink back automatically!
