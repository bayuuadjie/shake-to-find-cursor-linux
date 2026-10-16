import time
import subprocess
import threading
from pynput import mouse
from collections import deque

# ==================== KONFIGURASI ====================
NORMAL_THEME = "redglass"    # Tema warna kursor normal
NORMAL_SIZE = 24              # Ukuran normal (px)

LARGE_THEME = "redglass"     # Tema warna kursor saat besar
LARGE_SIZE = 72               # Ukuran maksimum saat membesar (px)

HOLD_DELAY = 1.2              # Lama kursor bertahan di ukuran maksimum (detik)

# --- KONFIGURASI SHAKE (GOYANGAN) ---
SHAKE_WINDOW = 0.6       # Batas waktu untuk mendeteksi goyangan bolak-balik (detik)
REQUIRED_REVERSALS = 4   # Jumlah perubahan arah (kiri-kanan-kiri-kanan) yang diperlukan
MIN_MOVE_DIST = 8        # Jarak minimal pergerakan per event (pixel)

# --- KONFIGURASI ANIMASI ---
ANIM_STEPS = 6                
ANIM_INTERVAL = 0.02          
# =====================================================

current_size = float(NORMAL_SIZE)
current_theme = NORMAL_THEME
is_expanded = False

timer_hold = None
anim_thread = None
anim_lock = threading.Lock()

last_pos = None
last_dir = 0  # -1 untuk kiri/atas, 1 untuk kanan/bawah
shake_events = deque()

def apply_system_cursor(size, theme):
    global current_size, current_theme
    int_size = int(round(size))
    
    if int_size != int(round(current_size)) or theme != current_theme:
        current_size = float(int_size)
        current_theme = theme
        
        subprocess.run(
            ['gsettings', 'set', 'org.cinnamon.desktop.interface', 'cursor-size', str(int_size)],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        subprocess.run(
            ['gsettings', 'set', 'org.cinnamon.desktop.interface', 'cursor-theme', theme],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )

def animate_size(target_size, target_theme, on_complete=None):
    global current_size
    start_size = current_size
    diff = target_size - start_size
    
    if abs(diff) < 1:
        apply_system_cursor(target_size, target_theme)
        if on_complete:
            on_complete()
        return

    step_size = diff / ANIM_STEPS
    for i in range(1, ANIM_STEPS + 1):
        next_size = start_size + (step_size * i)
        apply_system_cursor(next_size, target_theme)
        time.sleep(ANIM_INTERVAL)
        
    if on_complete:
        on_complete()

def start_expand():
    global is_expanded, anim_thread
    with anim_lock:
        is_expanded = True
        anim_thread = threading.Thread(
            target=animate_size, 
            args=(LARGE_SIZE, LARGE_THEME)
        )
        anim_thread.start()

def start_shrink():
    global is_expanded, anim_thread
    with anim_lock:
        is_expanded = False
        anim_thread = threading.Thread(
            target=animate_size, 
            args=(NORMAL_SIZE, NORMAL_THEME)
        )
        anim_thread.start()

def trigger_boost():
    global timer_hold
    if timer_hold and timer_hold.is_alive():
        timer_hold.cancel()
        
    if not is_expanded:
        start_expand()
        
    timer_hold = threading.Timer(HOLD_DELAY, start_shrink)
    timer_hold.start()

def on_move(x, y):
    global last_pos, last_dir, shake_events
    now = time.time()
    
    if last_pos is not None:
        dx = x - last_pos[0]
        dy = y - last_pos[1]
        
        # Deteksi arah dominan (horizontal atau vertikal)
        if abs(dx) > abs(dy) and abs(dx) > MIN_MOVE_DIST:
            current_dir = 1 if dx > 0 else -1
        elif abs(dy) >= abs(dx) and abs(dy) > MIN_MOVE_DIST:
            current_dir = 1 if dy > 0 else -1
        else:
            current_dir = 0
            
        if current_dir != 0:
            if last_dir != 0 and current_dir != last_dir:
                # Terjadi perubahan arah (goyangan bolak-balik)
                shake_events.append(now)
            last_dir = current_dir
            
        # Hapus riwayat goyangan yang sudah melewati batas waktu SHAKE_WINDOW
        while shake_events and now - shake_events[0] > SHAKE_WINDOW:
            shake_events.popleft()
            
        # Jika jumlah perubahan arah mencapai syarat, kursor membesar!
        if len(shake_events) >= REQUIRED_REVERSALS:
            trigger_boost()
            shake_events.clear()
            last_dir = 0
            
    last_pos = (x, y)

# Inisialisasi awal
apply_system_cursor(NORMAL_SIZE, NORMAL_THEME)

print("Skrip Shake-to-Find Aktif! Goyangkan mouse bolak-balik dengan cepat untuk memperbesar kursor.")
with mouse.Listener(on_move=on_move) as listener:
    listener.join()