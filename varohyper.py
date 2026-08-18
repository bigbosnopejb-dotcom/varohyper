
#!/usr/bin/env python3
import os, sys, re, time, random, threading, json, subprocess, webbrowser, importlib
from pathlib import Path
from datetime import datetime

# ============================================================
# AUTO-INSTALL DEPENDENSI
# ============================================================
def install_and_import(package):
    try:
        importlib.import_module(package)
        print(f"✅ {package} sudah terinstal.")
    except ImportError:
        print(f"📦 {package} tidak ditemukan. Menginstall...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package, "--quiet"])
            print(f"✅ {package} berhasil diinstall.")
        except Exception as e:
            print(f"❌ Gagal menginstall {package}: {e}")
            print(f"Silakan install manual: pip install {package}")

print("🔍 Mengecek dependensi...")
for pkg in ["twilio", "colorama", "yt-dlp", "requests"]:
    install_and_import(pkg)
print("✅ Semua dependensi siap!\n")
time.sleep(1)

# ============================================================
# WARNA ANSI
# ============================================================
G = "\033[1;32m"; R = "\033[1;31m"; W = "\033[1;37m"; Y = "\033[1;33m"
C = "\033[1;36m"; B = "\033[1;34m"; P = "\033[1;35m"; X = "\033[0m"

# ============================================================
# KONFIGURASI
# ============================================================
BOX_WIDTH = 50
USER_COUNT_FILE = os.path.expanduser("~/.tool_users_count")
CONFIG_FILE = "twilio_config.json"
OTP_LOG_FILE = "otp_codes.txt"
VIDEO_LOG_FILE = "video_download_log.txt"
VIDEO_CONFIG_FILE = "video_downloader_config.json"
USERNAME_FILE = os.path.expanduser("~/.tool_username.txt")
ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")

ASCII_ART = """⠀⠀⠀⠀⠀⠀⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢰⡆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⢠⣷⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣷⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⣸⣿⣧⡀⢀⣠⣤⣶⣶⣶⣶⣶⣦⣤⣀⠀⣠⣿⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠈⣿⣿⣷⣜⣿⣿⣿⣿⣿⣿⣿⣿⣿⢏⣵⣿⣿⡟⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⣻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⣴⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠸⣿⣿⣿⡙⠿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠛⣼⣿⣿⡇⠀⠀⠀⠀⠀⠀⢀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⢻⣿⣿⣷⣦⣀⣉⣽⣿⣿⣿⣿⣍⣁⣠⣾⣿⣿⣿⠁⠀⠀⠀⠀⣀⣀⡙⣷⣦⣄⠀⠀⠀
⠀⠀⠀⣀⡀⠀⢻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠃⢀⣠⣴⣾⠿⠟⠛⢉⣿⡿⠿⢿⣦⡀
⠀⢀⣴⠏⠀⠀⠀⠙⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠿⣅⣴⣿⡿⠟⠁⠀⠀⠀⠉⠁⠀⠀⠀⠀⠁
⠀⣾⣿⠀⠀⠀⠀⠀⠀⠉⠛⠿⣿⣿⣿⣿⣿⡿⠟⠋⣹⣿⣿⡿⠋⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⢸⣿⣿⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣴⣾⣿⡿⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠈⣿⣿⣷⣄⠀⠀⠀⠀⠀⠀⠀⠀⢀⣠⣴⣾⣿⣿⠿⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠘⢿⣿⣿⣿⣷⣶⣤⣤⣴⣶⣿⣿⣿⣿⡿⠟⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠈⠙⠻⣿⣿⣿⣿⣿⣿⣿⣿⠿⠛⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠈⠉⠉⠉⠉⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀"""

def clear_screen(): os.system('clear' if os.name == 'posix' else 'cls')
def strip_ansi(s): return ANSI_RE.sub("", s)

def get_current_datetime():
    now = datetime.now()
    days = ["Senin","Selasa","Rabu","Kamis","Jumat","Sabtu","Minggu"]
    months = ["Januari","Februari","Maret","April","Mei","Juni","Juli","Agustus","September","Oktober","November","Desember"]
    return f"{days[now.weekday()]}, {now.day} {months[now.month-1]} {now.year} | {now.hour:02d}:{now.minute:02d}:{now.second:02d}"

def read_user_count(d=20):
    try:
        if os.path.exists(USER_COUNT_FILE):
            with open(USER_COUNT_FILE,'r') as f:
                v = f.read().strip()
                return int(v) if v.isdigit() else d
        return d
    except: return d

def write_user_count(n):
    try:
        with open(USER_COUNT_FILE,'w') as f: f.write(str(n))
    except: pass

def maybe_increment_from_installer():
    if "--install" in sys.argv:
        c = read_user_count(); c += 1; write_user_count(c); return True
    return False

def load_username():
    try:
        if os.path.exists(USERNAME_FILE):
            with open(USERNAME_FILE,'r') as f:
                u = f.read().strip()
                if u: return u
    except: pass
    return None

def save_username(u):
    try:
        with open(USERNAME_FILE,'w') as f: f.write(u.strip())
        return True
    except: return False

def login():
    clear_screen()
    saved = load_username()
    if saved: return saved
    print(f"\n{P}╔{'═'*48}╗{X}")
    print(f"{P}║{X} {W}🔐 SELAMAT DATANG DI TOOLS VAROHYPER{X} {P}║{X}")
    print(f"{P}║{X} {Y}Silakan masukkan username Anda untuk melanjutkan{X} {P}║{X}")
    print(f"{P}╚{'═'*48}╝{X}\n")
    while True:
        u = input(f"{W}└─[ USERNAME ]─> {X}").strip()
        if u:
            save_username(u)
            print(f"\n{G}[+] Selamat datang, {u}!{X}")
            time.sleep(1)
            return u
        print(f"{R}[!] Username tidak boleh kosong!{X}")

def print_box(lines, width=BOX_WIDTH, bc=G, cc=R):
    print(bc + "┌" + "─"*width + "┐" + X)
    for line in lines:
        vis = strip_ansi(line)
        if len(vis) > width:
            tr = ""; cv = 0; i = 0
            while i < len(line) and cv < width:
                if line[i] == "\033":
                    m = ANSI_RE.match(line, i)
                    if m: seq = m.group(0); tr += seq; i += len(seq); continue
                tr += line[i]; cv += 1; i += 1
            line = tr; vis = strip_ansi(line)
        pad = width - len(vis)
        print(bc + "│" + X + cc + line + " "*pad + X + bc + "│" + X)
    print(bc + "└" + "─"*width + "┘" + X)

def print_menu_box(items, width=BOX_WIDTH, bc=G, title=None, cc=W):
    print(bc + "┌" + "─"*width + "┐" + X)
    if title:
        tv = strip_ansi(title); pl = max(0,(width-len(tv))//2); pr = width-pl-len(tv)
        print(bc + "│" + X + cc + " "*pl + title + " "*pr + X + bc + "│" + X)
        print(bc + "│" + X + cc + "─"*width + X + bc + "│" + X)
    for item in items:
        vis = strip_ansi(item); pad = width - len(vis)
        print(bc + "│" + X + item + " "*pad + bc + "│" + X)
    print(bc + "└" + "─"*width + "┘" + X)

def fmt_item(num, txt): return W + "[ " + R + num + W + " ] " + P + txt + X
def fmt_col(l, r, lw, rw):
    lv, rv = strip_ansi(l), strip_ansi(r)
    return l + " "*(lw-len(lv)) + " " + r + " "*(rw-len(rv))

def colorize_art(art, ct=R, cb=W):
    lines = art.splitlines(); n = len(lines); half = n//2; out=[]
    for i,line in enumerate(lines):
        c = ct if i < half else cb
        colored = ""
        for ch in line:
            colored += c + ch + X if ch.strip() else ch
        out.append(colored)
    return out

def print_ascii_box(ascii_lines, warn_lines, bc=G):
    ac = [strip_ansi(l) for l in ascii_lines]; wc = [strip_ansi(l) for l in warn_lines]
    aw = max((len(l) for l in ac), default=0); ww = max((len(l) for l in wc), default=0)
    tw = aw + 4 + ww + 2; mh = max(len(ascii_lines), len(warn_lines))
    print(bc + "┌" + "─"*tw + "┐" + X)
    for i in range(mh):
        al = ascii_lines[i] if i < len(ascii_lines) else ""; ac2 = ac[i] if i < len(ac) else ""
        wl = warn_lines[i] if i < len(warn_lines) else ""; wc2 = wc[i] if i < len(wc) else ""
        ap = aw - len(ac2); wp = ww - len(wc2)
        combined = al + " "*ap + " "*4 + wl + " "*wp
        print(bc + "│" + X + combined + bc + "│" + X)
    print(bc + "└" + "─"*tw + "┘" + X)

def _load_config():
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE,'r') as f:
                c = json.load(f)
                return c.get("account_sid"), c.get("auth_token"), c.get("sandbox")
    except: pass
    return None,None,None

def _save_config(sid, token, sandbox):
    with open(CONFIG_FILE,'w') as f:
        json.dump({"account_sid":sid,"auth_token":token,"sandbox":sandbox}, f, indent=4)

def _setup_twilio():
    clear_screen()
    print(f"{C}  SETUP TWILIO CONFIG{X}")
    print(f"{W}┌" + "─"*48 + "┐" + X)
    print(f"{W}│  Dapatkan credential dari:                 │{X}")
    print(f"{W}│  https://console.twilio.com                │{X}")
    print(f"{W}└" + "─"*48 + "┘" + X + "\n")
    sid = input(f"{W}Account SID: {X}").strip()
    if not sid: print(f"{R}❌ Tidak boleh kosong!{X}"); input("Tekan Enter..."); return False
    token = input(f"{W}Auth Token: {X}").strip()
    if not token: print(f"{R}❌ Tidak boleh kosong!{X}"); input("Tekan Enter..."); return False
    sandbox = input(f"{W}Sandbox Number (default: whatsapp:+14155238886): {X}").strip()
    if not sandbox: sandbox = "whatsapp:+14155238886"
    if not sandbox.startswith("whatsapp:"): sandbox = f"whatsapp:{sandbox}"
    try:
        from twilio.rest import Client
        client = Client(sid, token); client.api.accounts(sid).fetch()
        _save_config(sid, token, sandbox)
        print(f"{G}✅ Konfigurasi berhasil!{X}"); input("Tekan Enter..."); return True
    except ImportError:
        print(f"{R}❌ Twilio library belum terinstall!{X}")
        print(f"{Y}Jalankan: pip install twilio{X}"); input("Tekan Enter..."); return False
    except Exception as e:
        print(f"{R}❌ Gagal: {e}{X}"); input("Tekan Enter..."); return False

def _validate_phone(p):
    p = p.strip()
    if p.startswith('0'): p = '62' + p[1:]
    if not p.isdigit(): return None
    if len(p) < 10 or len(p) > 15: return None
    return p

def _send_otp_real(phone):
    try:
        sid, token, sandbox = _load_config()
        if not sid or not token: return False, "Konfigurasi Twilio belum diatur!"
        try: from twilio.rest import Client
        except ImportError: return False, "Twilio belum diinstall"
        otp = str(random.randint(100000, 999999))
        client = Client(sid, token)
        client.messages.create(
            from_=sandbox if sandbox else "whatsapp:+14155238886",
            to=f"whatsapp:{phone}",
            body=f"🔐 Kode OTP Anda: {otp}\n\nJangan berikan kode ini kepada siapa pun."
        )
        with open(OTP_LOG_FILE,'a') as f:
            f.write(f"{phone}:{otp}:{time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        return True, f"OTP: {otp}"
    except Exception as e: return False, str(e)

def spam_otp(phone, total=10, threads=3, delay=1.0):
    if not _validate_phone(phone): raise ValueError("Nomor HP tidak valid!")
    success = failed = 0; lock = threading.Lock(); start = time.time()
    def worker(wid):
        nonlocal success, failed
        for _ in range(max(1, total//threads)):
            if success + failed >= total: break
            status, msg = _send_otp_real(phone)
            with lock:
                if status: success += 1; print(f"{G}✅ Worker {wid} - Berhasil ({success}/{total}){X}")
                else: failed += 1; print(f"{R}❌ Worker {wid} - Gagal ({failed}/{total}) - {msg}{X}")
            time.sleep(delay + random.uniform(0,0.5))
    threads_list = []
    for i in range(min(threads, total)):
        t = threading.Thread(target=worker, args=(i+1,)); t.start(); threads_list.append(t)
    for t in threads_list: t.join()
    elapsed = time.time() - start
    print(f"\n{G}┌{'═'*48}┐{X}")
    print(f"{G}│{X} {W}HASIL SPAM OTP (REAL){X} {G}│{X}")
    print(f"{G}├{'─'*48}┤{X}")
    print(f"{G}│{X} {W}Berhasil : {G}{success}{X}  {W}Gagal : {R}{failed}{X}{G}{'│':>17}{X}")
    print(f"{G}│{X} {W}Total    : {C}{success+failed}{X}  {W}Waktu : {C}{elapsed:.2f}s{X}{G}{'│':>14}{X}")
    print(f"{G}└{'═'*48}┘{X}")
    return {"success": success, "failed": failed, "total": success+failed}

def menu_spam_otp():
    while True:
        clear_screen()
        print(f"\n{C}  SPAM OTP REAL v2.0 (Twilio){X}")
        print_box([
            f"{B}Author{X}   : {X}VARO & COPILOT",
            f"{B}Version{X}  : {X}2.0 (Real)",
            f"{B}Tanggal{X}  : {X}{get_current_datetime()}",
            f"{R}Status{X}   : {X}MENGIRIM OTP NYATA!"
        ])
        items = [
            fmt_item("01","Spam OTP (Kirim)"),
            fmt_item("02","Setup Twilio"),
            fmt_item("03","Lihat Riwayat OTP"),
            fmt_item("04","Hapus Riwayat"),
            fmt_item("00","Kembali ke Menu Utama")
        ]
        print_menu_box(items, title=W+"MENU SPAM OTP"+X)
        choice = input(f"{W}└─[ PILIH ]─> {X}").strip()
        if choice in ["1","01"]:
            clear_screen()
            print(f"\n{C}  SPAM OTP - REAL (TWILIO){X}")
            print_box([f"{R}⚠️  Mengirim OTP nyata via WhatsApp!{X}", f"{R}Hanya untuk testing dengan nomor sendiri!{X}"])
            sid,_,_ = _load_config()
            if not sid:
                print(f"\n{R}❌ Konfigurasi Twilio belum diatur!{X}")
                if input(f"{W}Setup sekarang? (y/n): {X}").lower() == 'y': _setup_twilio()
                input("Tekan Enter..."); continue
            phone = input(f"\n{W}[?] Nomor target (contoh: 628123456789): {X}")
            phone = _validate_phone(phone)
            if not phone: print(f"{R}[!] Nomor tidak valid!{X}"); input("Tekan Enter..."); continue
            try: total = int(input(f"{W}[?] Jumlah OTP (default 10): {X}") or "10")
            except: total = 10
            try: threads = max(1, min(5, int(input(f"{W}[?] Thread (1-5, default 3): {X}") or "3")))
            except: threads = 3
            try: delay = float(input(f"{W}[?] Delay (detik, default 1.0): {X}") or "1.0")
            except: delay = 1.0
            print(f"\n{R}⚠️  PERINGATAN:{X}")
            print(f"{Y}   Anda akan mengirim {total} OTP ke {phone}{X}")
            print(f"{Y}   Ini adalah PESAN NYATA via WhatsApp!{X}")
            print(f"{R}   ILEGAL jika digunakan tanpa izin!{X}")
            if input(f"{W}Lanjutkan? (y/n): {X}").lower() != 'y':
                print(f"{R}Dibatalkan.{X}"); input("Tekan Enter..."); continue
            try: spam_otp(phone, total, threads, delay)
            except Exception as e: print(f"{R}Error: {e}{X}")
            input("\nTekan Enter untuk kembali...")
        elif choice in ["2","02"]: _setup_twilio()
        elif choice in ["3","03"]:
            clear_screen(); print(f"\n{C}  RIWAYAT OTP TERKIRIM{X}")
            print_box([f"{R}Daftar OTP yang berhasil dikirim{X}"])
            if os.path.exists(OTP_LOG_FILE):
                try:
                    with open(OTP_LOG_FILE,'r') as f:
                        lines = f.readlines()
                        if lines:
                            for line in lines[-20:]: print(f"  {line.strip()}")
                        else: print(f"  {Y}Belum ada riwayat.{X}")
                except: print(f"  {R}Error membaca file.{X}")
            else: print(f"  {Y}Belum ada riwayat.{X}")
            input("\nTekan Enter...")
        elif choice in ["4","04"]:
            clear_screen()
            if os.path.exists(OTP_LOG_FILE):
                try: os.remove(OTP_LOG_FILE); print(f"{G}[+] Riwayat berhasil dihapus.{X}")
                except: print(f"{R}[!] Gagal menghapus.{X}")
            else: print(f"{Y}[!] Tidak ada riwayat.{X}")
            input("Tekan Enter...")
        elif choice in ["0","00"]: break
        else: print(f"{R}[!] Pilihan tidak valid!{X}"); input("Tekan Enter...")

def _send_report_real(phone):
    try:
        sid, token, sandbox = _load_config()
        if not sid or not token: return False, "Konfigurasi Twilio belum diatur!"
        try: from twilio.rest import Client
        except ImportError: return False, "Twilio belum diinstall"
        reasons = ["Spam", "Penipuan", "Pelecehan", "Konten Tidak Pantas", "Impersonasi", "Hoax", "Ujaran Kebencian"]
        msg = f"⚠️ LAPORAN: {random.choice(reasons)}\n\nKode referensi: {random.randint(100000,999999)}"
        client = Client(sid, token)
        client.messages.create(
            from_=sandbox if sandbox else "whatsapp:+14155238886",
            to=f"whatsapp:{phone}",
            body=msg
        )
        with open("report_log.txt",'a') as f:
            f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {phone} - REPORT SENT\n")
        return True, "Berhasil"
    except Exception as e: return False, str(e)

def spam_report(phone, total=10, threads=3, delay=1.0):
    if not _validate_phone(phone): raise ValueError("Nomor HP tidak valid!")
    success = failed = 0; lock = threading.Lock(); start = time.time()
    def worker(wid):
        nonlocal success, failed
        for _ in range(max(1, total//threads)):
            if success + failed >= total: break
            status, msg = _send_report_real(phone)
            with lock:
                if status: success += 1; print(f"{G}✅ Worker {wid} - Berhasil ({success}/{total}){X}")
                else: failed += 1; print(f"{R}❌ Worker {wid} - Gagal ({failed}/{total}) - {msg}{X}")
            time.sleep(delay + random.uniform(0,0.5))
    threads_list = []
    for i in range(min(threads, total)):
        t = threading.Thread(target=worker, args=(i+1,)); t.start(); threads_list.append(t)
    for t in threads_list: t.join()
    elapsed = time.time() - start
    print(f"\n{G}┌{'═'*48}┐{X}")
    print(f"{G}│{X} {W}HASIL SPAM REPORT (REAL){X} {G}│{X}")
    print(f"{G}├{'─'*48}┤{X}")
    print(f"{G}│{X} {W}Berhasil : {G}{success}{X}  {W}Gagal : {R}{failed}{X}{G}{'│':>17}{X}")
    print(f"{G}│{X} {W}Total    : {C}{success+failed}{X}  {W}Waktu : {C}{elapsed:.2f}s{X}{G}{'│':>14}{X}")
    print(f"{G}└{'═'*48}┘{X}")
    return {"success": success, "failed": failed, "total": success+failed}

def menu_spam_report():
    while True:
        clear_screen()
        print(f"\n{C}  SPAM REPORT REAL v2.0 (Twilio){X}")
        print_box([
            f"{B}Author{X}   : {X}VARO & COPILOT",
            f"{B}Version{X}  : {X}2.0 (Real)",
            f"{B}Tanggal{X}  : {X}{get_current_datetime()}",
            f"{R}Status{X}   : {X}MENGIRIM PESAN NYATA!"
        ])
        items = [
            fmt_item("01","Spam Report (Kirim)"),
            fmt_item("02","Setup Twilio"),
            fmt_item("03","Lihat Log"),
            fmt_item("04","Hapus Log"),
            fmt_item("00","Kembali ke Menu Utama")
        ]
        print_menu_box(items, title=W+"MENU SPAM REPORT"+X)
        choice = input(f"{W}└─[ PILIH ]─> {X}").strip()
        if choice in ["1","01"]:
            clear_screen()
            print(f"\n{C}  SPAM REPORT - REAL (TWILIO){X}")
            print_box([f"{R}⚠️  Mengirim pesan nyata via WhatsApp!{X}", f"{R}Hanya untuk testing dengan nomor sendiri!{X}"])
            sid,_,_ = _load_config()
            if not sid:
                print(f"\n{R}❌ Konfigurasi Twilio belum diatur!{X}")
                if input(f"{W}Setup sekarang? (y/n): {X}").lower() == 'y': _setup_twilio()
                input("Tekan Enter..."); continue
            phone = input(f"\n{W}[?] Nomor target (contoh: 628123456789): {X}")
            phone = _validate_phone(phone)
            if not phone: print(f"{R}[!] Nomor tidak valid!{X}"); input("Tekan Enter..."); continue
            try: total = int(input(f"{W}[?] Jumlah pesan (default 10): {X}") or "10")
            except: total = 10
            try: threads = max(1, min(5, int(input(f"{W}[?] Thread (1-5, default 3): {X}") or "3")))
            except: threads = 3
            try: delay = float(input(f"{W}[?] Delay (detik, default 1.0): {X}") or "1.0")
            except: delay = 1.0
            print(f"\n{R}⚠️  PERINGATAN:{X}")
            print(f"{Y}   Anda akan mengirim {total} pesan ke {phone}{X}")
            print(f"{Y}   Ini adalah PESAN NYATA via WhatsApp!{X}")
            print(f"{R}   ILEGAL jika digunakan tanpa izin!{X}")
            if input(f"{W}Lanjutkan? (y/n): {X}").lower() != 'y':
                print(f"{R}Dibatalkan.{X}"); input("Tekan Enter..."); continue
            try: spam_report(phone, total, threads, delay)
            except Exception as e: print(f"{R}Error: {e}{X}")
            input("\nTekan Enter untuk kembali...")
        elif choice in ["2","02"]: _setup_twilio()
        elif choice in ["3","03"]:
            clear_screen(); print(f"\n{C}  LOG SPAM REPORT{X}")
            print_box([f"{R}Daftar Log Aktivitas{X}"])
            if os.path.exists("report_log.txt"):
                try:
                    with open("report_log.txt",'r') as f:
                        lines = f.readlines()
                        if lines:
                            for line in lines[-20:]: print(f"  {line.strip()}")
                        else: print(f"  {Y}Belum ada log.{X}")
                except: print(f"  {R}Error membaca log.{X}")
            else: print(f"  {Y}Belum ada log.{X}")
            input("\nTekan Enter...")
        elif choice in ["4","04"]:
            clear_screen()
            if os.path.exists("report_log.txt"):
                try: os.remove("report_log.txt"); print(f"{G}[+] Log berhasil dihapus.{X}")
                except: print(f"{R}[!] Gagal menghapus log.{X}")
            else: print(f"{Y}[!] Tidak ada log.{X}")
            input("Tekan Enter...")
        elif choice in ["0","00"]: break
        else: print(f"{R}[!] Pilihan tidak valid!{X}"); input("Tekan Enter...")

def get_gallery_path():
    if os.name == 'posix':
        home = os.path.expanduser("~")
        for p in ["Pictures","DCIM/Camera","Movies","Downloads"]:
            path = os.path.join(home, p)
            if os.path.exists(path): return path
        return os.path.join(home, "Downloads")
    return os.path.join(os.path.expanduser("~"), "Downloads")

def create_output_dir():
    d = os.path.join(get_gallery_path(), "VideoDownloads")
    os.makedirs(d, exist_ok=True); return d

def load_video_config():
    try:
        if os.path.exists(VIDEO_CONFIG_FILE):
            with open(VIDEO_CONFIG_FILE,'r') as f: return json.load(f)
    except: pass
    return {"resolution":"720p","remove_watermark":True}

def save_video_config(c):
    try: with open(VIDEO_CONFIG_FILE,'w') as f: json.dump(c, f, indent=4)
    except: pass

def detect_platform(url):
    u = url.lower()
    if "tiktok.com" in u or "vt.tiktok.com" in u: return "tiktok"
    if "instagram.com" in u or "ig.me" in u: return "instagram"
    if "facebook.com" in u or "fb.watch" in u: return "facebook"
    return None

def validate_url(url):
    url = url.strip()
    if not url.startswith(("http://","https://")): url = "https://" + url
    p = detect_platform(url)
    return (url, p) if p else (None, None)

def download_video(url, out_dir, config):
    try:
        platform = detect_platform(url)
        if not platform: return False, "Platform tidak didukung"
        try:
            subprocess.run(["yt-dlp","--version"], capture_output=True, check=True)
        except:
            print(f"{R}[!] yt-dlp tidak terinstall!{X}")
            print(f"{Y}Jalankan: pip install yt-dlp{X}")
            return False, "yt-dlp tidak terinstall"
        res = config.get("resolution","720p")
        res_map = {"320p":"worst","480p":"worstvideo[height<=480]","720p":"best[height<=720]"}
        fmt = res_map.get(res, "best")
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        out = os.path.join(out_dir, f"{platform}_{ts}.mp4")
        cmd = ["yt-dlp","-f",fmt,"-o",out,"--no-warnings",url]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if result.returncode == 0 and os.path.exists(out):
            size = os.path.getsize(out)/(1024*1024)
            print(f"{G}[+] Download berhasil!{X}")
            print(f"{G}[+] File: {os.path.basename(out)}{X}")
            print(f"{G}[+] Ukuran: {size:.2f} MB{X}")
            with open(VIDEO_LOG_FILE,'a') as f:
                f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {platform.upper()} | {url} | SUCCESS\n")
            return True, os.path.basename(out)
        return False, result.stderr[:200]
    except subprocess.TimeoutExpired: return False, "Timeout"
    except Exception as e: return False, str(e)

def menu_download_video():
    config = load_video_config(); out = create_output_dir()
    while True:
        clear_screen()
        print(f"\n{C}  VIDEO DOWNLOADER{X}")
        print_box([
            f"{B}Platform{X} : TikTok, Instagram, Facebook",
            f"{B}Fitur{X}    : Remove Watermark, Multi Resolution",
            f"{B}Output{X}   : {X}{out}"
        ])
        items = [
            fmt_item("01","Download Video"),
            fmt_item("02","Pengaturan"),
            fmt_item("03","Lihat Download Log"),
            fmt_item("04","Buka Folder Output"),
            fmt_item("00","Kembali ke Menu Utama")
        ]
        print_menu_box(items, title=W+"MENU VIDEO DOWNLOADER"+X)
        choice = input(f"{W}└─[ PILIH ]─> {X}").strip()
        if choice in ["1","01"]:
            clear_screen(); print(f"\n{C}  DOWNLOAD VIDEO{X}")
            print_box([f"{R}⚠️  Pastikan URL valid dan video dapat diakses{X}"])
            url = input(f"\n{W}[?] Masukkan URL video: {X}").strip()
            if not url: print(f"{R}[!] URL tidak boleh kosong!{X}"); input("Tekan Enter..."); continue
            url, platform = validate_url(url)
            if not url or not platform:
                print(f"{R}[!] URL tidak valid atau platform tidak didukung!{X}")
                print(f"{Y}Platform yang didukung: TikTok, Instagram, Facebook{X}")
                input("Tekan Enter..."); continue
            print(f"\n{G}[+] Platform terdeteksi: {platform.upper()}{X}")
            if input(f"{W}Lanjutkan download? (y/n): {X}").lower() != 'y':
                print(f"{R}[!] Dibatalkan.{X}"); input("Tekan Enter..."); continue
            success, msg = download_video(url, out, config)
            if success: print(f"\n{G}[+] Video berhasil didownload ke:{X}\n{G}{out}{X}")
            else: print(f"\n{R}[!] Gagal download: {msg}{X}")
            input("\nTekan Enter untuk kembali...")
        elif choice in ["2","02"]:
            while True:
                clear_screen(); print(f"\n{C}  PENGATURAN VIDEO DOWNLOADER{X}")
                print_box([
                    f"{B}Resolution{X}       : {G}{config.get('resolution','720p')}{X}",
                    f"{B}Remove Watermark{X} : {G}{'Aktif' if config.get('remove_watermark',True) else 'Nonaktif'}{X}"
                ])
                sub_items = [
                    fmt_item("01","Ubah Resolution (320p, 480p, 720p)"),
                    fmt_item("02","Toggle Remove Watermark"),
                    fmt_item("00","Kembali")
                ]
                print_menu_box(sub_items, title=W+"PENGATURAN"+X)
                s_choice = input(f"{W}└─[ PILIH ]─> {X}").strip()
                if s_choice in ["1","01"]:
                    clear_screen(); print(f"\n{C}  PILIH RESOLUTION{X}")
                    res_items = [
                        fmt_item("1","320p (Rendah)"),
                        fmt_item("2","480p (Sedang)"),
                        fmt_item("3","720p (Tinggi)"),
                        fmt_item("0","Batal")
                    ]
                    print_menu_box(res_items, title=W+"RESOLUTION"+X)
                    r_choice = input(f"{W}└─[ PILIH ]─> {X}").strip()
                    res_map = {"1":"320p","2":"480p","3":"720p"}
                    if r_choice in res_map:
                        config["resolution"] = res_map[r_choice]
                        save_video_config(config)
                        print(f"{G}[+] Resolution diubah ke {res_map[r_choice]}{X}")
                        input("Tekan Enter...")
                elif s_choice in ["2","02"]:
                    config["remove_watermark"] = not config.get("remove_watermark", True)
                    save_video_config(config)
                    print(f"{G}[+] Remove Watermark: {'Aktif' if config['remove_watermark'] else 'Nonaktif'}{X}")
                    input("Tekan Enter...")
                elif s_choice in ["0","00"]: break
                else: print(f"{R}[!] Pilihan tidak valid!{X}"); input("Tekan Enter...")
        elif choice in ["3","03"]:
            clear_screen(); print(f"\n{C}  DOWNLOAD LOG{X}")
            print_box([f"{R}Riwayat Download{X}"])
            if os.path.exists(VIDEO_LOG_FILE):
                try:
                    with open(VIDEO_LOG_FILE,'r') as f:
                        lines = f.readlines()
                        if lines:
                            print(f"\n{Y}Total: {len(lines)} download{X}\n")
                            for line in lines[-20:]: print(f"  {line.rstrip()}")
                        else: print(f"\n  {Y}Belum ada log.{X}")
                except: print(f"\n  {R}Error membaca log.{X}")
            else: print(f"\n  {Y}Belum ada log.{X}")
            input("\nTekan Enter untuk kembali...")
        elif choice in ["4","04"]:
            try:
                if os.name == 'posix': subprocess.run(["xdg-open", out])
                elif os.name == 'nt': subprocess.run(["start", out], shell=True)
                else: subprocess.run(["open", out])
                print(f"{G}[+] Membuka folder...{X}")
            except: print(f"{R}[!] Gagal membuka folder{X}")
            time.sleep(1)
        elif choice in ["0","00"]: break
        else: print(f"{R}[!] Pilihan tidak valid!{X}"); input("Tekan Enter...")

def run_video_downloader(): menu_download_video()

def run_camera_tool():
    clear_screen()
    print(f"\n{C}  CAMERA H4CK{X}")
    print_box([
        f"{Y}📷 Menjalankan HACK-CAMERA tools...{X}",
        f"{Y}Script ini dibuat oleh XPH4N70M{X}",
        f"{Y}Pastikan file hack_camera.sh ada di direktori ini!{X}"
    ])
    if not os.path.exists("hack_camera.sh"):
        print(f"\n{R}[!] File hack_camera.sh tidak ditemukan!{X}")
        print(f"{Y}Silakan download dari:{X}")
        print(f"{C}https://github.com/XPH4N70M/HACK-CAMERA{X}")
        print(f"{Y}atau jalankan:{X}")
        print(f"{C}git clone https://github.com/XPH4N70M/HACK-CAMERA.git{X}")
        print(f"{Y}dan copy hack_camera.sh ke direktori ini.{X}")
        input("\nTekan Enter untuk kembali..."); return
    try: os.chmod("hack_camera.sh", 0o755)
    except: pass
    print(f"\n{G}[+] Menjalankan hack_camera.sh...{X}")
    print(f"{Y}[!] Untuk kembali ke menu utama, tekan Ctrl+C atau pilih opsi 0 (Exit) di menu camera.{X}")
    print(f"{Y}[!] Setelah keluar, Anda akan otomatis kembali ke menu utama.{X}\n")
    try:
        subprocess.call(["bash", "hack_camera.sh"])
        print(f"\n{G}[+] Kembali ke menu utama.{X}")
    except KeyboardInterrupt:
        print(f"\n{Y}[!] Camera tools dihentikan. Kembali ke menu utama...{X}")
    except Exception as e:
        print(f"{R}[!] Gagal menjalankan: {e}{X}")
    input("Tekan Enter untuk kembali ke menu utama...")

def open_jailbreak_link():
    url = "https://pastelink.net/azc45j2z"
    clear_screen()
    print(f"\n{C}  JAILBREAK CODE{X}")
    print_box([
        f"{Y}🔓 Membuka link Jailbreak Code...{X}",
        f"{W}URL: {url}{X}",
        f"{Y}Mohon tunggu sebentar...{X}"
    ])
    try:
        webbrowser.open(url)
        print(f"\n{G}[+] Link berhasil dibuka di browser.{X}")
    except:
        try:
            if os.name == 'posix': subprocess.run(["xdg-open", url])
            elif os.name == 'nt': subprocess.run(["start", url], shell=True)
            else: subprocess.run(["open", url])
            print(f"\n{G}[+] Link berhasil dibuka di browser.{X}")
        except:
            print(f"\n{R}[!] Gagal membuka browser otomatis.{X}")
            print(f"{Y}Silakan buka link secara manual:{X}")
            print(f"{C}{url}{X}")
    input("\nTekan Enter untuk kembali ke menu...")

def draw_interface():
    clear_screen()
    users_count = read_user_count()
    username = load_username() or "Guest"
    current_time = get_current_datetime()

    banner = f"{R}VAROHYPER{X}"
    vis = strip_ansi(banner)
    left_pad = max(0, (BOX_WIDTH - len(vis)) // 2)
    print(" " * left_pad + banner)
    print()

    warning_text = [
        f"{R}VAROHYPER | V1.0{X}",
        f"{R}gunakan{X}",
        f"{R}sebijak mungkin,{X}",
        f"{R}author dan yang{X}",
        f"{R}bersangkutan{X}",
        f"{R}tidak akan{X}",
        f"{R}bertanggung jawab{X}",
        f"{R}ini urusanmu,{X}",
        f"{R}kami hanya{X}",
        f"{R}membuat tools{X}",
        f"{R}ini untuk edukasi{X}",
        f"{R}dan simulasi{X}"
    ]
    colored_art = colorize_art(ASCII_ART, R, W)
    print_ascii_box(colored_art, warning_text, bc=G)
    print()

    banner_text = """
    _  _ ____ ____ ____ _  _ _   _ ___  ____ ____    
__ |  | |__| |__/ |  | |__|  \_/  |__] |___ |__/ __ 
    \/  |  | |  \ |__| |  |   |   |    |___ |  \    
"""
    print(f"{P}{banner_text}{X}")
    print()

    print_box([
        f"{B}Author{X}   : {X}VARO & COPILOT",
        f"{B}Version{X}  : {X}1.2",
        f"{B}Users{X}    : {X}{users_count} users",
        f"{B}Tanggal{X}  : {X}{current_time}"
    ])

    lw = (BOX_WIDTH - 1)//2; rw = BOX_WIDTH - lw - 1
    print_box([
        fmt_col(f"{B}NAMA{X}   : {X}{username}", f"{B}TIKTOK{X}  : {X}@_rohyper", lw, rw),
        fmt_col(f"{B}STATUS{X} : {X}Berjalan", f"{B}YOUTUBE{X} : {X}@belajarbareng", lw, rw),
        ""
    ])

    print_box([
        f"{W}OPEN JASA PEMBUATAN TOOLS - PERFITUR 7-30K{X}",
        f"{W}BUY TOOLS YANG PREMIUM - KE DM TIKTOK{X}"
    ], bc=G, cc=W)
    print()

    items = [
        fmt_item("01","Spam OTP"),
        fmt_item("02","Spam Report"),
        fmt_item("03","Video Downloader"),
        fmt_item("04","CAMERA H4CK"),
        fmt_item("05","JAILBREAK CODE"),
        fmt_item("00","EXIT")
    ]
    print_menu_box(items, title=R+"×××"+W+"[MENU]"+R+"×××"+X)

def main():
    username = login()
    if maybe_increment_from_installer():
        print(f"{R}[+] Install flag detected — user count incremented.{X}")
        input("Tekan Enter untuk melanjutkan...")
    while True:
        draw_interface()
        choice = input(f"{W}└─[ PILIH ]─> {X}").strip()
        if choice in ["1","01"]: menu_spam_otp()
        elif choice in ["2","02"]: menu_spam_report()
        elif choice in ["3","03"]: run_video_downloader()
        elif choice in ["4","04"]: run_camera_tool()
        elif choice in ["5","05"]: open_jailbreak_link()
        elif choice in ["0","00"]:
            print("\n[+] Keluar dari program.")
            sys.exit()
        else:
            print(f"{R}[!] Pilihan tidak valid!{X}")
            input("\nTekan Enter untuk kembali ke menu...")

if __name__ == "__main__":
    main()
