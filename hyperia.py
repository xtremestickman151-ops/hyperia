"""HYPERIA - a creative desktop shell for Windows by EX Inc.
Honest note: HYPERIA is an app running on Windows, not an operating system or kernel.
©2026 EX Inc."""
import json, os, random, re, subprocess, sys, threading, time, urllib.request, webbrowser
import tkinter as tk
from tkinter import messagebox

APP = "HYPERIA"
APP_VERSION = "1.1.16"
COPYRIGHT = "\u00a92026 EX Inc."
UPDATE_URL = "https://raw.githubusercontent.com/xtremestickman151-ops/hyperia/main/latest.json"
NOWIN = 0x08000000
BG, PANEL, CARD, CARD2, BORDER = "#000000", "#0d0d0f", "#1c1c1e", "#2a2a2d", "#3a3a3d"
TXT, MUT, GREEN, GREEN2 = "#f2f2f4", "#9a9aa0", "#afd067", "#7fa83a"
FONT, MONO = "Segoe UI", "Consolas"

# name, icon glyph, colour, url (None = native app)
WEB_APPS = [
    ("EX SAFARIA LITE", "◎", "#4a90d9", "https://www.bing.com"),
    ("YouTube", "▶", "#ff3b30", "https://www.youtube.com"),
    ("Discord", "◉", "#5865f2", "https://discord.com/app"),
    ("Steam", "♨", "#1b2838", "https://store.steampowered.com"),
    ("itch.io", "◆", "#fa5c5c", "https://itch.io"),
    ("Speed Test", "⚡", "#e5a524", "https://fast.com"),
    ("Reddit", "●", "#ff4500", "https://www.reddit.com"),
    ("Wikipedia", "W", "#888888", "https://www.wikipedia.org"),
    ("Twitch", "▣", "#9146ff", "https://www.twitch.tv"),
    ("Weather", "☁", "#3fa9f5", "https://www.bbc.co.uk/weather"),
    ("Sport", "⚽", "#ffd60a", "https://www.bbc.co.uk/sport"),
    ("Amazon", "a", "#ff9900", "https://www.amazon.co.uk"),
    ("Temu", "T", "#fb7701", "https://www.temu.com"),
    ("Xbox", "X", "#107c10", "https://www.xbox.com"),
    ("Cloud Gaming", "☁", "#107c10", "https://www.xbox.com/play"),
    ("Google Earth", "🌍", "#34a853", "https://earth.google.com/web"),
]
NATIVE_APPS = [
    ("HYPERIA Store", "▦", GREEN), ("Files", "▤", "#e5a524"), ("Terminal", ">_", "#3a3a3d"),
    ("Settings", "⚙", "#8e8e93"), ("Clock", "◷", "#5ac8fa"), ("Pong", "▮", "#ffffff"),
    ("Fireout 1997", "🔥", "#ff453a"),
]


def res_path(name):
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, name)



def vtuple(v):
    return tuple(int(x) for x in re.findall(r"\d+", str(v))[:4]) or (0,)


def check_update():
    try:
        req = urllib.request.Request(UPDATE_URL, headers={"User-Agent": APP + "/" + APP_VERSION})
        with urllib.request.urlopen(req, timeout=8) as r:
            m = json.loads(r.read(65536).decode("utf-8"))
        ver = str(m["version"])
    except Exception as e:
        return "error", "Could not check for updates (%s)." % (getattr(e, "reason", None) or e)
    if vtuple(ver) > vtuple(APP_VERSION):
        return "newer", {"version": ver, "notes": str(m.get("notes", "")),
                         "link": str(m.get("installer_url") or m.get("url", ""))}
    return "latest", "You have the latest version (%s)." % APP_VERSION


WEBVIEW2_GUID = "{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}"
WEBVIEW2_MSG = ("Microsoft Edge WebView2 Runtime is required to open web apps in HYPERIA.\n\n"
                "Install it from Microsoft (search \"WebView2 Runtime\" or visit\n"
                "developer.microsoft.com/microsoft-edge/webview2), then try again.")


def webview2_installed():
    if os.name != "nt": return False
    try:
        import winreg
        keys = [(winreg.HKEY_LOCAL_MACHINE, "SOFTWARE\\WOW6432Node\\Microsoft\\EdgeUpdate\\Clients\\" + WEBVIEW2_GUID),
                (winreg.HKEY_LOCAL_MACHINE, "SOFTWARE\\Microsoft\\EdgeUpdate\\Clients\\" + WEBVIEW2_GUID),
                (winreg.HKEY_CURRENT_USER, "Software\\Microsoft\\EdgeUpdate\\Clients\\" + WEBVIEW2_GUID)]
        for root, path in keys:
            try:
                with winreg.OpenKey(root, path) as k:
                    v, _ = winreg.QueryValueEx(k, "pv")
                    if v and v != "0.0.0.0": return True
            except OSError:
                pass
    except Exception:
        pass
    return False


def open_web(url, title):
    """Open URL in its own HYPERIA web window (Edge WebView2 only, no system-browser fallback)."""
    if not webview2_installed():
        messagebox.showerror(APP, WEBVIEW2_MSG); return False
    try:
        if getattr(sys, "frozen", False):
            cmd = [sys.executable, "--web", url, title]
        else:
            cmd = [sys.executable, os.path.abspath(__file__), "--web", url, title]
        subprocess.Popen(cmd, creationflags=NOWIN if os.name == "nt" else 0)
        return True
    except Exception as e:
        messagebox.showerror(APP, "Could not open the HYPERIA web window:\n%s" % e); return False


def web_main(url, title):
    try:
        if not webview2_installed(): raise RuntimeError("WebView2 missing")
        import webview
        webview.create_window("HYPERIA · " + title, url, width=1200, height=800)
        webview.start(gui="edgechromium")
    except Exception as e:
        r = tk.Tk(); r.withdraw()
        messagebox.showerror(APP, WEBVIEW2_MSG + "\n\nDetails: %s" % e); r.destroy()


def rrect(c, x1, y1, x2, y2, r, **kw):
    pts = [x1+r, y1, x2-r, y1, x2, y1, x2, y1+r, x2, y2-r, x2, y2, x2-r, y2, x1+r, y2, x1, y2, x1, y2-r, x1, y1+r, x1, y1]
    return c.create_polygon(pts, smooth=True, **kw)


class Pill(tk.Canvas):
    def __init__(self, master, text, cmd, w=140, h=32, fill=GREEN, fg="#0a1200", bg=CARD):
        super().__init__(master, width=w, height=h, bg=bg, highlightthickness=0, cursor="hand2")
        self.t, self.f, self.fg = text, fill, fg
        self.bind("<Button-1>", lambda e: cmd()); self.bind("<Enter>", lambda e: self.draw(1)); self.bind("<Leave>", lambda e: self.draw())
        self.draw()

    def set_text(self, text):
        self.t = text; self.draw()

    def draw(self, hover=0):
        self.delete("all"); w, h = int(self["width"]), int(self["height"])
        rrect(self, 1, 1, w-1, h-1, h//2, fill=("#c5e080" if hover and self.f == GREEN else "#3a3a3d" if hover else self.f), outline=BORDER)
        self.create_text(w//2, h//2, text=self.t, fill=self.fg, font=(FONT, 10, "bold"))


class Win(tk.Frame):
    """A window living inside the HYPERIA desktop."""
    def __init__(self, shell, title, w=640, h=440, maximizable=False):
        super().__init__(shell.desk, bg=BORDER, bd=0)
        self.shell, self.title = shell, title
        self._maximized = False
        self._norm = None
        self._max_btn = None
        self._place_w, self._place_h = w, h
        bar = tk.Frame(self, bg=CARD2, height=32); bar.pack(fill="x", padx=1, pady=(1, 0))
        tk.Label(bar, text="  " + title, bg=CARD2, fg=TXT, font=(FONT, 10, "bold")).pack(side="left")
        x = tk.Label(bar, text="  ✕  ", bg=CARD2, fg=TXT, font=(FONT, 10), cursor="hand2"); x.pack(side="right")
        x.bind("<Button-1>", lambda e: self.close())
        x.bind("<Enter>", lambda e: x.configure(bg="#c42b1c")); x.bind("<Leave>", lambda e: x.configure(bg=CARD2))
        if maximizable:
            mx = tk.Label(bar, text="  □  ", bg=CARD2, fg=TXT, font=(FONT, 10), cursor="hand2"); mx.pack(side="right")
            mx.bind("<Button-1>", lambda e: self.toggle_maximize())
            mx.bind("<Enter>", lambda e: mx.configure(bg="#3a3a3d")); mx.bind("<Leave>", lambda e: mx.configure(bg=CARD2))
            self._max_btn = mx
        m = tk.Label(bar, text="  —  ", bg=CARD2, fg=TXT, font=(FONT, 10), cursor="hand2"); m.pack(side="right")
        m.bind("<Button-1>", lambda e: self.minimize())
        self.body = tk.Frame(self, bg=PANEL); self.body.pack(fill="both", expand=True, padx=1, pady=(0, 1))
        for wdg in (bar,) + tuple(bar.winfo_children()[:1]):
            wdg.bind("<ButtonPress-1>", self._press); wdg.bind("<B1-Motion>", self._drag)
        self.bind("<Button-1>", lambda e: self.lift_())
        n = len(shell.wins)
        self.place(x=120 + 30 * (n % 8), y=60 + 26 * (n % 8), width=w, height=h)
        shell.add_win(self)

    def _press(self, e):
        self.lift_()
        if self._maximized:
            return
        self._dx, self._dy = e.x_root - self.winfo_x(), e.y_root - self.winfo_y()

    def _drag(self, e):
        if self._maximized:
            return
        self.place(x=e.x_root - self._dx, y=max(0, e.y_root - self._dy))

    def lift_(self):
        self.lift(); self.shell.focus_win(self)

    def toggle_maximize(self):
        if self._maximized:
            x, y, w, h = self._norm
            self.place(x=x, y=y, width=w, height=h)
            self._maximized = False
            if self._max_btn is not None:
                self._max_btn.configure(text="  □  ")
        else:
            self._norm = (self.winfo_x(), self.winfo_y(), self.winfo_width(), self.winfo_height())
            dw = max(self.shell.desk.winfo_width(), 400)
            dh = max(self.shell.desk.winfo_height(), 300)
            self.place(x=0, y=0, width=dw, height=dh)
            self._maximized = True
            if self._max_btn is not None:
                self._max_btn.configure(text="  ❐  ")
        self.lift_()

    def minimize(self):
        self.place_forget(); self.hidden = True; self.shell.refresh_task()

    def restore(self):
        if getattr(self, "hidden", False):
            if self._maximized and self._norm:
                dw = max(self.shell.desk.winfo_width(), 400)
                dh = max(self.shell.desk.winfo_height(), 300)
                self.place(x=0, y=0, width=dw, height=dh)
            elif self._norm:
                x, y, w, h = self._norm
                self.place(x=x, y=y, width=w, height=h)
            else:
                self.place(x=140, y=80, width=self._place_w, height=self._place_h)
            self.hidden = False
        self.lift_()

    def close(self):
        self.on_close(); self.shell.remove_win(self); self.destroy()

    def on_close(self):
        pass


class Files(Win):
    def __init__(self, shell):
        super().__init__(shell, "Files", 680, 460)
        self.cwd = os.path.expanduser("~")
        top = tk.Frame(self.body, bg=PANEL); top.pack(fill="x", padx=8, pady=8)
        for label, path in (("Home", "~"), ("Desktop", "~/Desktop"), ("Documents", "~/Documents"), ("Downloads", "~/Downloads")):
            Pill(top, label, lambda p=path: self.go(os.path.expanduser(p)), w=100, h=28, fill=CARD2, fg=TXT, bg=PANEL).pack(side="left", padx=3)
        Pill(top, "↑ Up", lambda: self.go(os.path.dirname(self.cwd)), w=70, h=28, fill=CARD2, fg=TXT, bg=PANEL).pack(side="left", padx=3)
        self.path = tk.Label(self.body, bg=PANEL, fg=GREEN, font=(MONO, 9), anchor="w"); self.path.pack(fill="x", padx=10)
        self.lb = tk.Listbox(self.body, bg="#0a0a0a", fg=TXT, font=(FONT, 10), selectbackground=CARD2,
                             relief="flat", highlightthickness=0, activestyle="none")
        self.lb.pack(fill="both", expand=True, padx=8, pady=8)
        self.lb.bind("<Double-Button-1>", self.open_sel); self.lb.bind("<Return>", self.open_sel)
        self.go(self.cwd)

    def go(self, p):
        try:
            items = sorted(os.listdir(p), key=lambda n: (not os.path.isdir(os.path.join(p, n)), n.lower()))
        except Exception as e:
            messagebox.showwarning(APP, "Cannot open folder:\n%s" % e); return
        self.cwd = p; self.path.configure(text=p); self.lb.delete(0, "end")
        for n in items:
            if n.startswith("."): continue
            self.lb.insert("end", ("📁  " if os.path.isdir(os.path.join(p, n)) else "📄  ") + n)

    def open_sel(self, e=None):
        s = self.lb.curselection()
        if not s: return
        name = self.lb.get(s[0])[3:]
        full = os.path.join(self.cwd, name)
        if os.path.isdir(full): self.go(full)
        else:
            try: os.startfile(full)
            except Exception as ex: messagebox.showwarning(APP, str(ex))


class Terminal(Win):
    def __init__(self, shell):
        super().__init__(shell, "Terminal", 720, 440)
        self.cwd = os.path.expanduser("~")
        self.out = tk.Text(self.body, bg="#050505", fg="#d8f0b0", font=(MONO, 10), relief="flat",
                           highlightthickness=0, state="disabled", padx=8, pady=6)
        self.out.pack(fill="both", expand=True)
        row = tk.Frame(self.body, bg=CARD); row.pack(fill="x")
        tk.Label(row, text="PS>", bg=CARD, fg=GREEN, font=(MONO, 10, "bold")).pack(side="left", padx=6)
        self.inp = tk.Entry(row, bg=CARD, fg=TXT, insertbackground=TXT, relief="flat", font=(MONO, 10))
        self.inp.pack(side="left", fill="x", expand=True, ipady=5)
        self.inp.bind("<Return>", self.run)
        self.write("HYPERIA Terminal (PowerShell, one command at a time; cd is remembered)\n" + self.cwd + "\n")
        self.inp.focus_set()

    def write(self, t):
        self.out.configure(state="normal"); self.out.insert("end", t); self.out.see("end"); self.out.configure(state="disabled")

    def run(self, e=None):
        cmd = self.inp.get().strip(); self.inp.delete(0, "end")
        if not cmd: return
        self.write("PS %s> %s\n" % (self.cwd, cmd))
        m = re.match(r"^(cd|Set-Location|sl)\s*(.*)$", cmd, re.I)
        if m:
            target = m.group(2).strip().strip('"') or os.path.expanduser("~")
            new = os.path.normpath(os.path.join(self.cwd, os.path.expanduser(target)))
            if os.path.isdir(new): self.cwd = new; self.write(new + "\n")
            else: self.write("Path not found: %s\n" % target)
            return
        if cmd.lower() in ("cls", "clear"):
            self.out.configure(state="normal"); self.out.delete("1.0", "end"); self.out.configure(state="disabled"); return
        def job():
            try:
                si = None
                if os.name == "nt":
                    si = subprocess.STARTUPINFO(); si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                p = subprocess.run(["powershell", "-NoLogo", "-NoProfile", "-Command", cmd], cwd=self.cwd,
                                   capture_output=True, timeout=120, startupinfo=si,
                                   creationflags=NOWIN if os.name == "nt" else 0)
                out = (p.stdout + p.stderr).decode("utf-8", "replace")
            except Exception as ex:
                out = "Error: %s\n" % ex
            self.after(0, lambda: self.write(out if out.endswith("\n") or not out else out + "\n"))
        threading.Thread(target=job, daemon=True).start()


class Clock(Win):
    def __init__(self, shell):
        super().__init__(shell, "Clock", 380, 260)
        self.t = tk.Label(self.body, bg=PANEL, fg=TXT, font=(FONT, 40, "bold")); self.t.pack(pady=(30, 0))
        self.d = tk.Label(self.body, bg=PANEL, fg=GREEN, font=(FONT, 12)); self.d.pack()
        Pill(self.body, "Weather forecast", lambda: open_web("https://www.bbc.co.uk/weather", "Weather"), w=170, bg=PANEL).pack(pady=18)
        self.tick()

    def tick(self):
        if not self.winfo_exists(): return
        self.t.configure(text=time.strftime("%H:%M:%S")); self.d.configure(text=time.strftime("%A %d %B %Y"))
        self.after(500, self.tick)


class Pong(Win):
    W, H = 560, 340

    def __init__(self, shell):
        super().__init__(shell, "Pong", self.W + 2, self.H + 64)
        self.c = tk.Canvas(self.body, width=self.W, height=self.H, bg="#000", highlightthickness=0); self.c.pack()
        tk.Label(self.body, text="W / S or ↑ / ↓ to move · first to 7", bg=PANEL, fg=MUT, font=(FONT, 9)).pack()
        self.keys = set(); self.score = [0, 0]; self.reset(); self.running = True
        self.c.bind("<KeyPress>", lambda e: self.keys.add(e.keysym.lower()))
        self.c.bind("<KeyRelease>", lambda e: self.keys.discard(e.keysym.lower()))
        self.c.bind("<Button-1>", lambda e: self.c.focus_set()); self.c.focus_set()
        self.p1 = self.p2 = self.H / 2; self.loop()

    def reset(self, d=1):
        self.bx, self.by = self.W / 2, self.H / 2
        self.vx, self.vy = 5 * d, random.choice([-3, -2, 2, 3])

    def loop(self):
        if not self.running or not self.winfo_exists(): return
        if {"w", "up"} & self.keys: self.p1 -= 7
        if {"s", "down"} & self.keys: self.p1 += 7
        self.p2 += max(-5, min(5, self.by - self.p2))
        self.p1 = max(35, min(self.H - 35, self.p1)); self.p2 = max(35, min(self.H - 35, self.p2))
        self.bx += self.vx; self.by += self.vy
        if self.by < 6 or self.by > self.H - 6: self.vy = -self.vy
        if self.bx < 24 and abs(self.by - self.p1) < 38: self.vx = abs(self.vx) * 1.05; self.vy += (self.by - self.p1) / 10
        if self.bx > self.W - 24 and abs(self.by - self.p2) < 38: self.vx = -abs(self.vx) * 1.05
        if self.bx < 0: self.score[1] += 1; self.reset(1)
        if self.bx > self.W: self.score[0] += 1; self.reset(-1)
        c = self.c; c.delete("all")
        for y in range(0, self.H, 20): c.create_rectangle(self.W/2 - 1, y, self.W/2 + 1, y + 10, fill="#444", outline="")
        c.create_rectangle(10, self.p1 - 32, 18, self.p1 + 32, fill=GREEN, outline="")
        c.create_rectangle(self.W - 18, self.p2 - 32, self.W - 10, self.p2 + 32, fill="#fff", outline="")
        c.create_rectangle(self.bx - 6, self.by - 6, self.bx + 6, self.by + 6, fill="#fff", outline="")
        c.create_text(self.W/2 - 40, 30, text=str(self.score[0]), fill=GREEN, font=(MONO, 24, "bold"))
        c.create_text(self.W/2 + 40, 30, text=str(self.score[1]), fill="#fff", font=(MONO, 24, "bold"))
        if max(self.score) >= 7:
            c.create_text(self.W/2, self.H/2, text="YOU WIN!" if self.score[0] >= 7 else "CPU WINS", fill=TXT, font=(MONO, 26, "bold"))
            c.create_text(self.W/2, self.H/2 + 34, text="click to play again", fill=MUT, font=(MONO, 11))
            self.c.bind("<Button-1>", lambda e: (setattr(self, "score", [0, 0]), self.c.focus_set(), self.loop()))
            return
        self.after(16, self.loop)

    def on_close(self):
        self.running = False


class Fireout(Win):
    """Fireout 1997 - an original retro top-down racer."""
    W, H = 420, 520
    LANES = 4

    def __init__(self, shell):
        super().__init__(shell, "Fireout 1997", self.W + 2, self.H + 60)
        self.c = tk.Canvas(self.body, width=self.W, height=self.H, bg="#1a1a1a", highlightthickness=0); self.c.pack()
        tk.Label(self.body, text="← / → or A / D to steer · ↑ boost · Space to restart", bg=PANEL, fg=MUT, font=(FONT, 9)).pack()
        self.keys = set(); self.running = True
        self.c.bind("<KeyPress>", self.kd); self.c.bind("<KeyRelease>", lambda e: self.keys.discard(e.keysym.lower()))
        self.c.bind("<Button-1>", lambda e: self.c.focus_set()); self.c.focus_set()
        self.hi = 0; self.new_game(); self.loop()

    def kd(self, e):
        k = e.keysym.lower(); self.keys.add(k)
        if k == "space" and self.dead: self.new_game()
        if k in ("left", "a") and not self.dead: self.lane = max(0, self.lane - 1)
        if k in ("right", "d") and not self.dead: self.lane = min(self.LANES - 1, self.lane + 1)

    def lane_x(self, i):
        road = self.W - 80; return 40 + road / self.LANES * (i + 0.5)

    def new_game(self):
        self.lane = 1; self.px = self.lane_x(1); self.cars = []; self.speed = 6.0; self.dist = 0
        self.stripe = 0; self.dead = False; self.boom = 0; self.spawn = 0

    def car(self, x, y, body, roof):
        c = self.c
        c.create_rectangle(x-16, y-28, x+16, y+28, fill=body, outline="#000", width=2)
        c.create_rectangle(x-12, y-14, x+12, y+8, fill=roof, outline="")
        c.create_rectangle(x-20, y-22, x-16, y-10, fill="#000", outline=""); c.create_rectangle(x+16, y-22, x+20, y-10, fill="#000", outline="")
        c.create_rectangle(x-20, y+10, x-16, y+22, fill="#000", outline=""); c.create_rectangle(x+16, y+10, x+20, y+22, fill="#000", outline="")

    def loop(self):
        if not self.running or not self.winfo_exists(): return
        c = self.c; c.delete("all")
        boost = 1.6 if ({"up", "w"} & self.keys) and not self.dead else 1.0
        sp = 0 if self.dead else self.speed * boost
        self.stripe = (self.stripe + sp) % 40
        # scenery
        c.create_rectangle(0, 0, 40, self.H, fill="#2f5d1e", outline=""); c.create_rectangle(self.W-40, 0, self.W, self.H, fill="#2f5d1e", outline="")
        c.create_rectangle(36, 0, 40, self.H, fill="#e8e8e8", outline=""); c.create_rectangle(self.W-40, 0, self.W-36, self.H, fill="#e8e8e8", outline="")
        road = self.W - 80
        for i in range(1, self.LANES):
            x = 40 + road / self.LANES * i
            for y in range(-40, self.H, 40):
                c.create_rectangle(x-2, y + self.stripe, x+2, y + self.stripe + 20, fill="#d9c84a", outline="")
        # traffic
        if not self.dead:
            self.spawn -= 1
            if self.spawn <= 0:
                lane = random.randrange(self.LANES)
                self.cars.append([lane, -60, random.choice(["#2b6cb0", "#a0aec0", "#d69e2e", "#6b46c1", "#38a169"]), random.uniform(0.3, 0.6)])
                self.spawn = max(14, int(46 - self.speed * 2.2))
        for car in self.cars:
            car[1] += sp * (1 - car[3]) + (0 if self.dead else 1)
        self.cars = [k for k in self.cars if k[1] < self.H + 60]
        for lane, y, col, _ in self.cars:
            self.car(self.lane_x(lane), y, col, "#111")
        # player
        tx = self.lane_x(self.lane); self.px += (tx - self.px) * 0.35
        py = self.H - 80
        self.car(self.px, py, "#e53e3e", "#2d0000")
        if not self.dead:
            for lane, y, _, _ in self.cars:
                if abs(self.lane_x(lane) - self.px) < 30 and abs(y - py) < 54:
                    self.dead = True; self.boom = 0; self.hi = max(self.hi, int(self.dist)); break
            self.dist += sp / 10; self.speed = min(16, 6 + self.dist / 120)
        if self.dead:
            self.boom += 1
            for i in range(14):
                r = random.randint(6, 26) + self.boom % 8
                fx, fy = self.px + random.randint(-22, 22), py + random.randint(-30, 20)
                c.create_oval(fx-r, fy-r, fx+r, fy+r, fill=random.choice(["#ff453a", "#ff9f0a", "#ffd60a"]), outline="")
            c.create_rectangle(60, self.H/2 - 60, self.W - 60, self.H/2 + 60, fill="#000", outline=GREEN, width=2)
            c.create_text(self.W/2, self.H/2 - 26, text="WRECKED!", fill="#ff453a", font=(MONO, 24, "bold"))
            c.create_text(self.W/2, self.H/2 + 8, text="Distance %d m   Best %d m" % (self.dist, self.hi), fill=TXT, font=(MONO, 11))
            c.create_text(self.W/2, self.H/2 + 34, text="SPACE to race again", fill=MUT, font=(MONO, 10))
        # HUD
        c.create_rectangle(0, 0, self.W, 30, fill="#000", outline="")
        c.create_text(10, 15, anchor="w", text="FIREOUT 1997", fill="#ff9f0a", font=(MONO, 12, "bold"))
        c.create_text(self.W - 10, 15, anchor="e", text="%04d m  %3d km/h" % (self.dist, sp * 14), fill=GREEN, font=(MONO, 11, "bold"))
        self.after(16, self.loop)

    def on_close(self):
        self.running = False


class Settings(Win):
    WALLS = [("Midnight", "#000000", "#0f1a08"), ("Graphite", "#1a1a1d", "#2a2a2d"),
             ("Forest", "#0b1f0b", "#24401a"), ("Ocean", "#04121f", "#0b3350")]

    def __init__(self, shell):
        super().__init__(shell, "Settings", 520, 380)
        b = self.body
        tk.Label(b, text="Wallpaper", bg=PANEL, fg=TXT, font=(FONT, 12, "bold")).pack(anchor="w", padx=16, pady=(14, 4))
        row = tk.Frame(b, bg=PANEL); row.pack(anchor="w", padx=16)
        for name, a, z in self.WALLS:
            Pill(row, name, lambda a=a, z=z: shell.set_wall(a, z), w=104, h=30, fill=CARD2, fg=TXT, bg=PANEL).pack(side="left", padx=3)
        tk.Label(b, text="Display", bg=PANEL, fg=TXT, font=(FONT, 12, "bold")).pack(anchor="w", padx=16, pady=(18, 4))
        Pill(b, "Toggle fullscreen (F11)", shell.toggle_full, w=200, fill=CARD2, fg=TXT, bg=PANEL).pack(anchor="w", padx=16)
        tk.Label(b, text="Updates", bg=PANEL, fg=TXT, font=(FONT, 12, "bold")).pack(anchor="w", padx=16, pady=(18, 4))
        Pill(b, "Check for updates", shell.check_updates, w=180, bg=PANEL).pack(anchor="w", padx=16)
        tk.Label(b, text="HYPERIA %s · %s" % (APP_VERSION, COPYRIGHT), bg=PANEL, fg=MUT, font=(FONT, 9)).pack(anchor="w", padx=16, pady=(18, 0))


class Store(Win):
    def __init__(self, shell):
        super().__init__(shell, "HYPERIA Store", 700, 470, maximizable=True)
        tk.Label(self.body, text="All apps", bg=PANEL, fg=TXT, font=(FONT, 14, "bold")).pack(anchor="w", padx=16, pady=(12, 6))
        grid = tk.Frame(self.body, bg=PANEL); grid.pack(fill="both", expand=True, padx=12)
        apps = [(n, g, c) for n, g, c in NATIVE_APPS if n != "HYPERIA Store"] + [(n, g, c) for n, g, c, _ in WEB_APPS]
        for i, (n, g, col) in enumerate(apps):
            f = tk.Frame(grid, bg=CARD, cursor="hand2"); f.grid(row=i // 4, column=i % 4, padx=5, pady=5, sticky="we")
            if n in shell.app_img:
                tk.Label(f, image=shell.app_img[n][1], bg=CARD, width=34).pack(side="left", padx=6, pady=6)
            else:
                tk.Label(f, text=g, bg=col, fg="white", font=(FONT, 11, "bold"), width=3).pack(side="left", padx=6, pady=6)
            tk.Label(f, text=n, bg=CARD, fg=TXT, font=(FONT, 9), width=16, anchor="w").pack(side="left")
            for w in (f,) + tuple(f.winfo_children()):
                w.bind("<Button-1>", lambda e, n=n: shell.launch(n))
        for c in range(4): grid.columnconfigure(c, weight=1)


class Shell(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP); self.configure(bg=BG); self.geometry("1280x760"); self.minsize(1000, 640)
        try: self.iconbitmap(default=res_path("logo.ico"))
        except Exception: pass
        try:
            self.logo_big = tk.PhotoImage(file=res_path("logo256.png")); self.iconphoto(True, self.logo_big)
            self.logo_big = self.logo_big.subsample(2, 2); self.logo_small = tk.PhotoImage(file=res_path("logo48.png")).subsample(2, 2)
        except Exception:
            self.logo_big = self.logo_small = None
        self.app_img = {}
        try:
            self.app_img["EX SAFARIA LITE"] = (tk.PhotoImage(file=res_path("browser48.png")), tk.PhotoImage(file=res_path("browser22.png")))
        except Exception:
            pass
        try: self.state("zoomed")
        except Exception: pass
        self.wins = []; self.full = False; self.wall = ("#000000", "#0f1a08"); self.start_open = False

        self.desk = tk.Canvas(self, bg=BG, highlightthickness=0); self.desk.pack(fill="both", expand=True)
        self.task = tk.Frame(self, bg="#0b0b0c", height=48, highlightthickness=1, highlightbackground=BORDER)
        self.task.pack(fill="x", side="bottom"); self.task.pack_propagate(False)
        self.start_btn = tk.Label(self.task, text="  ◆  HYPERIA  ", bg="#0b0b0c", fg=GREEN, font=(FONT, 11, "bold"), cursor="hand2")
        if self.logo_small: self.start_btn.configure(image=self.logo_small, compound="left", text="  HYPERIA  ")
        self.start_btn.pack(side="left", padx=6, fill="y")
        self.start_btn.bind("<Button-1>", lambda e: self.toggle_start())
        self.tasks = tk.Frame(self.task, bg="#0b0b0c"); self.tasks.pack(side="left", fill="y", padx=8)
        self.clock = tk.Label(self.task, bg="#0b0b0c", fg=TXT, font=(FONT, 10)); self.clock.pack(side="right", padx=14)
        upd = tk.Label(self.task, text=" ⟳ Updates ", bg="#0b0b0c", fg=GREEN, font=(FONT, 9, "bold"), cursor="hand2")
        upd.pack(side="right", padx=4); upd.bind("<Button-1>", lambda e: self.check_updates())
        upd.bind("<Enter>", lambda e: upd.configure(bg=CARD2)); upd.bind("<Leave>", lambda e: upd.configure(bg="#0b0b0c"))
        self.fs_btn = tk.Label(self.task, text=" Full screen ", bg="#0b0b0c", fg=TXT, font=(FONT, 9, "bold"), cursor="hand2")
        self.fs_btn.pack(side="right", padx=4); self.fs_btn.bind("<Button-1>", lambda e: self.toggle_full())
        self.fs_btn.bind("<Enter>", lambda e: self.fs_btn.configure(bg=CARD2)); self.fs_btn.bind("<Leave>", lambda e: self.fs_btn.configure(bg="#0b0b0c"))
        self.fs_pill = None
        tk.Label(self.task, text=COPYRIGHT, bg="#0b0b0c", fg=MUT, font=(FONT, 8)).pack(side="right", padx=8)

        self.desk.bind("<Configure>", lambda e: self.draw_desk())
        self.desk.bind("<Button-1>", lambda e: self.close_start())
        self.bind("<F11>", lambda e: self.toggle_full()); self.bind("<Escape>", lambda e: self.close_start())
        self.bind("<Super_L>", lambda e: self.toggle_start())
        self.startmenu = None; self.sync_full_label(); self.tick()
        if os.environ.get("HYPERIA_DEMO"):  # used only for screenshots
            self.after(1200, lambda: (self.open_start(), self.launch("HYPERIA Store")))

    # ---------- desktop ----------
    def set_wall(self, a, z):
        self.wall = (a, z); self.draw_desk()

    def draw_desk(self):
        d = self.desk; d.delete("wall"); d.delete("icon")
        w, h = max(d.winfo_width(), 400), max(d.winfo_height(), 300)
        a, z = self.wall
        ra, ga, ba = int(a[1:3], 16), int(a[3:5], 16), int(a[5:7], 16)
        rz, gz, bz = int(z[1:3], 16), int(z[3:5], 16), int(z[5:7], 16)
        steps = 40
        for i in range(steps):
            t = i / (steps - 1)
            col = "#%02x%02x%02x" % (int(ra + (rz - ra) * t), int(ga + (gz - ga) * t), int(ba + (bz - ba) * t))
            d.create_rectangle(0, h * i / steps, w, h * (i + 1) / steps + 1, fill=col, outline="", tags="wall")
        if self.logo_big:
            d.create_image(w / 2, h / 2 - 20, image=self.logo_big, tags="wall")
        d.create_text(w / 2, h / 2 + 120, text="HYPERIA", fill=GREEN, font=(FONT, 30, "bold"), tags="wall")
        icons = [(n, g, c) for n, g, c in NATIVE_APPS] + [(n, g, c) for n, g, c, _ in WEB_APPS]
        per_col = max(1, int((h - 20) // 92))
        for i, (n, g, col) in enumerate(icons):
            x = 20 + (i // per_col) * 92; y = 16 + (i % per_col) * 92
            if x > w / 2 - 200 and x < w / 2 + 200: x += 0  # keep simple
            tag = "ic%d" % i
            if n in self.app_img:
                d.create_image(x + 38, y + 24, image=self.app_img[n][0], tags=("icon", tag))
            else:
                rrect(d, x + 14, y, x + 62, y + 48, 12, fill=col, outline="", tags=("icon", tag))
                d.create_text(x + 38, y + 24, text=g, fill="white", font=(FONT, 15, "bold"), tags=("icon", tag))
            d.create_text(x + 38, y + 62, text=n, fill=TXT, font=(FONT, 9), width=86, tags=("icon", tag))
            d.tag_bind(tag, "<Double-Button-1>", lambda e, n=n: self.launch(n))
            d.tag_bind(tag, "<Enter>", lambda e: d.configure(cursor="hand2")); d.tag_bind(tag, "<Leave>", lambda e: d.configure(cursor=""))
        d.tag_lower("wall")

    def tick(self):
        self.clock.configure(text=time.strftime("%H:%M  %d/%m/%Y")); self.after(1000, self.tick)

    # ---------- start menu ----------
    def toggle_start(self):
        if self.startmenu: self.close_start()
        else: self.open_start()

    def close_start(self):
        if self.startmenu: self.startmenu.destroy(); self.startmenu = None; self.fs_pill = None

    def open_start(self):
        m = tk.Frame(self, bg=CARD, highlightthickness=1, highlightbackground=BORDER)
        h = min(560, self.desk.winfo_height() - 20)
        m.place(x=8, y=self.desk.winfo_height() - h - 6, width=440, height=h)
        self.startmenu = m
        head = tk.Frame(m, bg=CARD); head.pack(fill="x", padx=14, pady=(12, 6))
        tk.Label(head, text="HYPERIA", bg=CARD, fg=GREEN, font=(FONT, 15, "bold")).pack(side="left")
        tk.Label(head, text="v" + APP_VERSION, bg=CARD, fg=MUT, font=(FONT, 9)).pack(side="left", padx=8, pady=(6, 0))
        q = tk.StringVar(); e = tk.Entry(m, textvariable=q, bg=CARD2, fg=TXT, insertbackground=TXT, relief="flat", font=(FONT, 10))
        e.pack(fill="x", padx=14, ipady=6); e.insert(0, ""); e.focus_set()
        lst = tk.Frame(m, bg=CARD); lst.pack(fill="both", expand=True, padx=8, pady=8)
        allapps = [(n, g, c) for n, g, c in NATIVE_APPS] + [(n, g, c) for n, g, c, _ in WEB_APPS]

        def fill(*_):
            for w in lst.winfo_children(): w.destroy()
            f = q.get().lower()
            shown = [a for a in allapps if f in a[0].lower()]
            for i, (n, g, col) in enumerate(shown):
                r = tk.Frame(lst, bg=CARD, cursor="hand2"); r.grid(row=i // 2, column=i % 2, sticky="we", padx=3, pady=2)
                if n in self.app_img:
                    tk.Label(r, image=self.app_img[n][1], bg=CARD, width=30).pack(side="left", padx=4, pady=3)
                else:
                    tk.Label(r, text=g, bg=col, fg="white", font=(FONT, 10, "bold"), width=3).pack(side="left", padx=4, pady=3)
                tk.Label(r, text=n, bg=CARD, fg=TXT, font=(FONT, 10), anchor="w", width=16).pack(side="left")
                for w in (r,) + tuple(r.winfo_children()):
                    w.bind("<Button-1>", lambda e, n=n: (self.close_start(), self.launch(n)))
                    w.bind("<Enter>", lambda e, r=r: [x.configure(bg=CARD2) for x in (r, r.winfo_children()[1])])
                    w.bind("<Leave>", lambda e, r=r: [x.configure(bg=CARD) for x in (r, r.winfo_children()[1])])
            lst.columnconfigure(0, weight=1); lst.columnconfigure(1, weight=1)
        q.trace_add("write", fill); fill()
        e.bind("<Return>", lambda ev: (lambda s=[a for a in allapps if q.get().lower() in a[0].lower()]: s and (self.close_start(), self.launch(s[0][0])))())
        foot = tk.Frame(m, bg=CARD); foot.pack(fill="x", padx=14, pady=8)
        Pill(foot, "Settings", lambda: (self.close_start(), self.launch("Settings")), w=100, h=28, fill=CARD2, fg=TXT).pack(side="left")
        Pill(foot, "⟳ Check for updates", lambda: (self.close_start(), self.check_updates()), w=160, h=28, fill=GREEN, fg="#0a1200").pack(side="left", padx=6)
        self.fs_pill = Pill(foot, self.full_btn_text(), lambda: (self.close_start(), self.toggle_full()), w=110, h=28, fill=CARD2, fg=TXT)
        self.fs_pill.pack(side="left", padx=6)

    # ---------- windows ----------
    def launch(self, name):
        for n, g, col, url in WEB_APPS:
            if n == name: return open_web(url, n)
        cls = {"HYPERIA Store": Store, "Files": Files, "Terminal": Terminal, "Settings": Settings, "Clock": Clock,
               "Pong": Pong, "Fireout 1997": Fireout}.get(name)
        if cls: return cls(self)

    def add_win(self, w):
        self.wins.append(w); self.refresh_task(); w.lift_()

    def remove_win(self, w):
        if w in self.wins: self.wins.remove(w)
        self.refresh_task()

    def focus_win(self, w):
        for b in self.tasks.winfo_children():
            b.configure(bg=CARD2 if getattr(b, "win", None) is w else "#0b0b0c")

    def refresh_task(self):
        for b in self.tasks.winfo_children(): b.destroy()
        for w in self.wins:
            b = tk.Label(self.tasks, text="  " + w.title + "  ", bg="#0b0b0c", fg=TXT, font=(FONT, 9), cursor="hand2")
            b.win = w; b.pack(side="left", padx=2, pady=8, fill="y")
            b.bind("<Button-1>", lambda e, w=w: w.restore())

    def full_btn_text(self):
        return "Windowed" if self.full else "Full screen"

    def sync_full_label(self):
        label = self.full_btn_text()
        if getattr(self, "fs_btn", None) is not None:
            self.fs_btn.configure(text=" %s " % label)
        if getattr(self, "fs_pill", None) is not None:
            try:
                self.fs_pill.set_text(label)
            except tk.TclError:
                self.fs_pill = None

    def toggle_full(self):
        self.full = not self.full
        self.attributes("-fullscreen", self.full)
        self.sync_full_label()

    def check_updates(self):
        def job():
            st, d = check_update(); self.after(0, lambda: self.show_update(st, d))
        threading.Thread(target=job, daemon=True).start()

    def show_update(self, st, d):
        if st != "newer":
            (messagebox.showinfo if st == "latest" else messagebox.showwarning)(APP, d); return
        if d["link"].startswith("http") and messagebox.askyesno(APP, "HYPERIA %s is available (you have %s).\n\n%s\n\nOpen the installer download?" % (d["version"], APP_VERSION, d["notes"])):
            webbrowser.open(d["link"])

    def quit_shell(self):
        if messagebox.askyesno(APP, "Exit HYPERIA?"): self.destroy()


if __name__ == "__main__":
    if len(sys.argv) >= 3 and sys.argv[1] == "--web":
        web_main(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else "Web")
    else:
        Shell().mainloop()
