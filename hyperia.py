"""HYPERIA — branded VirtualBox front-end for Windows. ©2026 EX Inc.
Honest note: HYPERIA is a launcher/manager for VirtualBox VMs, not a from-scratch OS."""
import ctypes, json, os, queue, re, shutil, subprocess, sys, threading, time, urllib.request, webbrowser
import tkinter as tk
from tkinter import filedialog, messagebox

APP = "HYPERIA"
APP_VERSION = "1.0.0"
COPYRIGHT = "\u00a92026 EX Inc."
UPDATE_URL = "https://raw.githubusercontent.com/xtremestickman151-ops/hyperia/main/latest.json"
VM_NAME = "HYPERIA"
VBOX_DOWNLOAD = "https://www.virtualbox.org/wiki/Downloads"
LUBUNTU_DOWNLOAD = "https://lubuntu.me/downloads/"
NOWIN = 0x08000000
BG, SIDE, CARD, CARD2, BORDER = "#000000", "#0a0a0a", "#1c1c1e", "#2a2a2d", "#3a3a3d"
TXT, MUT, GREEN, GREY = "#f2f2f4", "#9a9aa0", "#afd067", "#3a3a3d"
FONT = "Segoe UI"
_MUTEX = None


def res_path(name):
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, name)


def is_admin():
    try: return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception: return False


def single_instance():
    global _MUTEX
    if os.name != "nt": return True
    try:
        k = ctypes.windll.kernel32
        _MUTEX = k.CreateMutexW(None, False, "Local\\HYPERIA_SingleInstance")
        if k.GetLastError() != 183: return True
        u = ctypes.windll.user32
        for _ in range(10):
            found = []
            def cb(h, l):
                buf = ctypes.create_unicode_buffer(256)
                u.GetWindowTextW(h, buf, 256)
                if buf.value.startswith(APP) and u.IsWindowVisible(h): found.append(h)
                return True
            u.EnumWindows(ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)(cb), 0)
            if found:
                u.ShowWindow(found[0], 9); u.SetForegroundWindow(found[0]); return False
            time.sleep(0.3)
        return True
    except Exception:
        return True


def vtuple(v):
    return tuple(int(x) for x in re.findall(r"\d+", str(v))[:4]) or (0,)


def check_update():
    if not UPDATE_URL.strip():
        return "unconfigured", "Update server not configured yet."
    try:
        req = urllib.request.Request(UPDATE_URL, headers={"User-Agent": APP + "/" + APP_VERSION})
        with urllib.request.urlopen(req, timeout=8) as r:
            m = json.loads(r.read(65536).decode("utf-8"))
        ver = str(m["version"])
    except Exception as e:
        return "error", "Could not check for updates (%s)." % (getattr(e, "reason", None) or e)
    if vtuple(ver) > vtuple(APP_VERSION):
        return "newer", {"version": ver, "url": str(m.get("url", "")), "notes": str(m.get("notes", "")),
                         "full_url": str(m.get("full_url", "")), "installer_url": str(m.get("installer_url", ""))}
    return "latest", "You have the latest version (%s)." % APP_VERSION


def run(cmd, timeout=120):
    try:
        si = None; flags = 0
        if os.name == "nt":
            si = subprocess.STARTUPINFO(); si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            flags = NOWIN
        p = subprocess.run(cmd, capture_output=True, timeout=timeout, startupinfo=si, creationflags=flags)
        out = (p.stdout or b"") + (p.stderr or b"")
        return p.returncode, out.decode("utf-8", "replace")
    except FileNotFoundError:
        return -1, "not found"
    except Exception as e:
        return -1, str(e)


def find_vboxmanage():
    candidates = []
    which = shutil.which("VBoxManage") or shutil.which("VBoxManage.exe")
    if which: candidates.append(which)
    for base in (
        os.environ.get("VBOX_MSI_INSTALL_PATH", ""),
        os.environ.get("VBOX_INSTALL_PATH", ""),
        r"C:\Program Files\Oracle\VirtualBox",
        r"C:\Program Files (x86)\Oracle\VirtualBox",
        os.path.expandvars(r"%ProgramFiles%\Oracle\VirtualBox"),
        os.path.expandvars(r"%ProgramFiles(x86)%\Oracle\VirtualBox"),
    ):
        if not base: continue
        p = os.path.join(base, "VBoxManage.exe")
        if os.path.isfile(p): candidates.append(p)
    for p in candidates:
        rc, out = run([p, "--version"], 15)
        if rc == 0 and out.strip():
            return p, out.strip().splitlines()[0]
    return None, None


def vbox(vb, *args, timeout=180):
    return run([vb, *args], timeout)


def parse_vminfo(text):
    d = {}
    for line in text.splitlines():
        if "=" in line:
            k, _, v = line.partition("=")
            d[k.strip()] = v.strip().strip('"')
    return d


def rrect(c, x1, y1, x2, y2, r, **kw):
    pts = [x1+r, y1, x2-r, y1, x2, y1, x2, y1+r, x2, y2-r, x2, y2, x2-r, y2, x1+r, y2, x1, y2, x1, y2-r, x1, y1+r, x1, y1]
    return c.create_polygon(pts, smooth=True, **kw)


class Card(tk.Canvas):
    def __init__(self, master, title="", height=None, **kw):
        super().__init__(master, bg=BG, highlightthickness=0, height=height or 100, **kw)
        self.title = title
        self.body = tk.Frame(self, bg=CARD)
        self.win = self.create_window(18, 44 if title else 16, window=self.body, anchor="nw")
        self.bind("<Configure>", self._draw)

    def _draw(self, e=None):
        self.delete("bg"); w, h = self.winfo_width(), self.winfo_height()
        rrect(self, 2, 2, w-2, h-2, 18, fill=CARD, outline=BORDER, width=1, tags="bg")
        if self.title:
            self.create_text(18, 22, text=self.title, anchor="w", fill=MUT, font=(FONT, 10, "bold"), tags="bg")
        self.tag_lower("bg"); self.itemconfigure(self.win, width=max(10, w-36))


class PillButton(tk.Canvas):
    def __init__(self, master, text, cmd, w=180, h=36, fill=GREEN, fg="#0a1200", bg=CARD):
        super().__init__(master, width=w, height=h, bg=bg, highlightthickness=0, cursor="hand2")
        self.cmd, self.fill, self.text, self.fg = cmd, fill, text, fg
        self.bind("<Button-1>", lambda e: cmd()); self.bind("<Enter>", lambda e: self.draw(True)); self.bind("<Leave>", lambda e: self.draw())
        self.draw()

    def draw(self, hover=False):
        self.delete("all"); w, h = int(self["width"]), int(self["height"])
        f = self.fill if not hover else ("#c5e080" if self.fill == GREEN else "#3a3a3d")
        rrect(self, 1, 1, w-1, h-1, h//2, fill=f, outline=BORDER)
        self.create_text(w//2, h//2, text=self.text, fill=self.fg, font=(FONT, 10, "bold"))


class NoticeBox(tk.Canvas):
    def __init__(self, master, text, bg, w=160, h=28, size=8):
        super().__init__(master, width=w, height=h, bg=bg, highlightthickness=0)
        rrect(self, 1, 1, w-1, h-1, 9, fill="#1c1c1e", outline="#3a3a3d", width=1)
        self.create_text(w//2, h//2, text=text, fill="#c7c7cc", font=(FONT, size))


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP + ("  [Administrator]" if is_admin() else ""))
        try: self.iconbitmap(default=res_path("logo.ico"))
        except Exception: pass
        try: self._icon = tk.PhotoImage(file=res_path("logo256.png")); self.iconphoto(True, self._icon)
        except Exception: pass
        self.geometry("920x640"); self.minsize(780, 560); self.configure(bg=BG)
        self.q = queue.Queue()
        self.vb = None; self.vb_ver = None; self.iso_path = tk.StringVar(value="")
        self.status = {"vbox": "Checking…", "vm": "—", "state": "—", "os": "—", "ram": "—", "iso": "—"}

        side = tk.Frame(self, bg=SIDE, width=200); side.pack(side="left", fill="y"); side.pack_propagate(False)
        logo = tk.Canvas(side, width=200, height=100, bg=SIDE, highlightthickness=0); logo.pack()
        try:
            self._logo = tk.PhotoImage(file=res_path("logo48.png"))
            logo.create_image(36, 50, image=self._logo)
        except Exception:
            logo.create_oval(18, 32, 54, 68, fill=GREEN, outline="")
        logo.create_text(62, 42, text="HYPERIA", anchor="w", fill=TXT, font=(FONT, 14, "bold"))
        logo.create_text(62, 62, text="VM launcher", anchor="w", fill=GREEN, font=(FONT, 9, "bold"))

        self.navs = {}; self.pages = {}
        main = tk.Frame(self, bg=BG); main.pack(side="left", fill="both", expand=True)
        self.content = tk.Frame(main, bg=BG); self.content.pack(fill="both", expand=True, padx=18, pady=16)
        for name, icon in (("Home", "⌂"), ("About", "ⓘ")):
            l = tk.Label(side, text=f"  {icon}   {name}", anchor="w", bg=SIDE, fg=MUT, font=(FONT, 11),
                         cursor="hand2", padx=14, pady=10)
            l.pack(fill="x", padx=12, pady=2); l.bind("<Button-1>", lambda e, n=name: self.show(n)); self.navs[name] = l
            self.pages[name] = tk.Frame(self.content, bg=BG)
        tk.Frame(side, bg=BORDER, height=1).pack(fill="x", padx=24, pady=8)
        up = tk.Label(side, text="  ⟳   Check for updates", anchor="w", bg=SIDE, fg=MUT, font=(FONT, 11),
                      cursor="hand2", padx=14, pady=10)
        up.pack(fill="x", padx=12, pady=2); up.bind("<Button-1>", lambda e: self.update_click())
        up.bind("<Enter>", lambda e: up.configure(bg=CARD2, fg=TXT)); up.bind("<Leave>", lambda e: up.configure(bg=SIDE, fg=MUT))
        NoticeBox(side, COPYRIGHT, SIDE, w=160, h=28).pack(side="bottom", pady=(4, 14))
        tk.Label(side, text="VirtualBox front-end\n· not a from-scratch OS",
                 bg=SIDE, fg=MUT, font=(FONT, 8), justify="left").pack(side="bottom", padx=20, pady=(4, 2))

        self.build_home(); self.build_about(); self.show("Home")
        self.after(200, self.pump); self.after(100, self.refresh); self.after(4000, self.poll)

    def show(self, name):
        for n, p in self.pages.items():
            p.pack_forget(); self.navs[n].configure(bg=SIDE, fg=MUT)
        self.pages[name].pack(fill="both", expand=True); self.navs[name].configure(bg=CARD2, fg=TXT)

    def build_home(self):
        p = self.pages["Home"]
        # Status card
        c = Card(p, "STATUS", height=200); c.pack(fill="x")
        self.lbl = {}
        for key, title in (("vbox", "VirtualBox"), ("vm", "VM"), ("state", "State"), ("ram", "Memory"), ("iso", "Attached ISO")):
            row = tk.Frame(c.body, bg=CARD); row.pack(fill="x", pady=2)
            tk.Label(row, text=title, bg=CARD, fg=MUT, font=(FONT, 9), width=14, anchor="w").pack(side="left")
            v = tk.StringVar(value="—"); self.lbl[key] = v
            tk.Label(row, textvariable=v, bg=CARD, fg=TXT, font=(FONT, 10, "bold"), anchor="w").pack(side="left", fill="x", expand=True)

        # Actions
        a = Card(p, "ACTIONS", height=280); a.pack(fill="x", pady=14)
        row = tk.Frame(a.body, bg=CARD); row.pack(fill="x", pady=4)
        PillButton(row, "Get VirtualBox", self.open_vbox_dl, w=150, fill=CARD2, fg=TXT).pack(side="left", padx=(0, 8))
        PillButton(row, "Create HYPERIA VM", self.create_vm, w=170).pack(side="left", padx=(0, 8))
        PillButton(row, "Start VM", self.start_vm, w=110).pack(side="left", padx=(0, 8))
        PillButton(row, "Stop VM", self.stop_vm, w=110, fill=CARD2, fg=TXT).pack(side="left")

        tk.Label(a.body, text="Attach a Linux ISO (you download it yourself — HYPERIA never ships OS images):",
                 bg=CARD, fg=MUT, font=(FONT, 9), wraplength=620, justify="left").pack(anchor="w", pady=(12, 4))
        row = tk.Frame(a.body, bg=CARD); row.pack(fill="x")
        tk.Entry(row, textvariable=self.iso_path, bg=CARD2, fg=TXT, insertbackground=TXT, relief="flat",
                 font=(FONT, 9)).pack(side="left", fill="x", expand=True, ipady=6, padx=(0, 8))
        PillButton(row, "Browse…", self.browse_iso, w=100, h=32, fill=CARD2, fg=TXT).pack(side="left", padx=(0, 8))
        PillButton(row, "Attach ISO", self.attach_iso, w=110, h=32).pack(side="left")

        row = tk.Frame(a.body, bg=CARD); row.pack(fill="x", pady=(12, 0))
        PillButton(row, "Download Lubuntu ISO (official site)", self.open_lubuntu, w=280, fill=GREEN).pack(side="left")
        tk.Label(a.body, text="Opens lubuntu.me/downloads — HYPERIA does not host or redistribute ISOs.",
                 bg=CARD, fg=MUT, font=(FONT, 8)).pack(anchor="w", pady=(6, 0))

        self.log = tk.Text(p, height=6, bg="#0d0d0f", fg=TXT, relief="flat", font=("Consolas", 9),
                           state="disabled", highlightthickness=1, highlightbackground=BORDER)
        self.log.pack(fill="x", pady=(8, 0))

    def build_about(self):
        p = self.pages["About"]
        c = Card(p, "ABOUT & UPDATES", height=280); c.pack(fill="x")
        tk.Label(c.body, text="%s  version %s" % (APP, APP_VERSION), bg=CARD, fg=TXT, font=(FONT, 13, "bold")).pack(anchor="w")
        tk.Label(c.body, text="HYPERIA is a branded front-end for Oracle VirtualBox — not a from-scratch operating system.\n"
                 "It helps you create a VM named HYPERIA, attach an ISO you provide, and start or stop that VM.\n"
                 "You must install VirtualBox separately. Linux ISOs are downloaded from their official sites.",
                 bg=CARD, fg=MUT, font=(FONT, 9), justify="left", wraplength=600).pack(anchor="w", pady=8)
        NoticeBox(c.body, COPYRIGHT, CARD, w=170, h=30, size=9).pack(anchor="w", pady=(4, 10))
        row = tk.Frame(c.body, bg=CARD); row.pack(fill="x")
        PillButton(row, "Check for updates", self.update_click, w=180, fill=CARD2, fg=TXT).pack(side="left")
        self.upd = tk.StringVar(value=""); tk.Label(row, textvariable=self.upd, bg=CARD, fg=MUT, font=(FONT, 9)).pack(side="left", padx=12)

    def emit(self, msg):
        self.q.put(("log", time.strftime("%H:%M:%S  ") + msg))

    def pump(self):
        while not self.q.empty():
            kind, v = self.q.get()
            if kind == "status":
                for k, val in v.items():
                    if k in self.lbl: self.lbl[k].set(val)
            elif kind == "log":
                self.log.configure(state="normal"); self.log.insert("end", v + "\n"); self.log.see("end"); self.log.configure(state="disabled")
            elif kind == "upd":
                self.update_result(*v)
        self.after(200, self.pump)

    def bg(self, fn, *a):
        threading.Thread(target=fn, args=a, daemon=True).start()

    def refresh(self):
        self.bg(self._refresh)

    def poll(self):
        self.refresh(); self.after(4000, self.poll)

    def _refresh(self):
        vb, ver = find_vboxmanage()
        self.vb, self.vb_ver = vb, ver
        st = {"vbox": ("Found  " + ver) if vb else "Not installed", "vm": "—", "state": "—", "ram": "—", "iso": "—"}
        if vb:
            rc, out = vbox(vb, "showvminfo", VM_NAME, "--machinereadable")
            if rc == 0:
                info = parse_vminfo(out)
                st["vm"] = VM_NAME
                st["state"] = info.get("VMState", "unknown")
                mem = info.get("memory", "")
                st["ram"] = (mem + " MB") if mem else "—"
                # find DVD
                iso = "—"
                for k, v in info.items():
                    if "dvdimage" in k.lower() or (k.startswith("IDE") and v.lower().endswith(".iso")):
                        iso = os.path.basename(v) if v and v != "none" else "—"
                        if iso != "—": break
                    if "ImageUUID" in k and ".iso" in info.get(k.replace("ImageUUID", "Image"), "").lower():
                        pass
                for k, v in info.items():
                    if v.lower().endswith(".iso"):
                        iso = os.path.basename(v); break
                st["iso"] = iso
            else:
                st["vm"] = "Not created yet"
                st["state"] = "absent"
        self.q.put(("status", st))

    def open_vbox_dl(self):
        webbrowser.open(VBOX_DOWNLOAD)
        self.emit("Opened VirtualBox downloads page.")

    def open_lubuntu(self):
        webbrowser.open(LUBUNTU_DOWNLOAD)
        self.emit("Opened official Lubuntu downloads: " + LUBUNTU_DOWNLOAD)

    def browse_iso(self):
        p = filedialog.askopenfilename(title="Select Linux ISO", filetypes=[("ISO images", "*.iso"), ("All files", "*.*")])
        if p: self.iso_path.set(p)

    def need_vb(self):
        if self.vb: return True
        if messagebox.askyesno(APP, "VirtualBox (VBoxManage) was not found.\n\nOpen the official VirtualBox download page?"):
            self.open_vbox_dl()
        return False

    def create_vm(self):
        if not self.need_vb(): return
        self.bg(self._create_vm)

    def _create_vm(self):
        vb = self.vb
        rc, out = vbox(vb, "showvminfo", VM_NAME)
        if rc == 0:
            self.emit("VM '%s' already exists." % VM_NAME); self._refresh(); return
        self.emit("Creating VM '%s'…" % VM_NAME)
        steps = [
            ["createvm", "--name", VM_NAME, "--ostype", "Ubuntu_64", "--register"],
            ["modifyvm", VM_NAME, "--memory", "2048", "--cpus", "2", "--vram", "128",
             "--nic1", "nat", "--audio-driver", "none", "--firmware", "efi"],
            ["storagectl", VM_NAME, "--name", "SATA", "--add", "sata", "--controller", "IntelAhci"],
            ["createmedium", "disk", "--filename", os.path.join(os.path.expanduser("~"), "VirtualBox VMs", VM_NAME, VM_NAME + ".vdi"),
             "--size", "20480", "--format", "VDI"],
        ]
        for s in steps:
            rc, out = vbox(vb, *s, timeout=300)
            self.emit(("OK" if rc == 0 else "FAIL") + ": " + " ".join(s[:3]) + ((" — " + out.strip()[:120]) if rc else ""))
            if rc != 0 and s[0] != "createmedium":
                # continue where possible
                pass
        # attach disk
        vdi = os.path.join(os.path.expanduser("~"), "VirtualBox VMs", VM_NAME, VM_NAME + ".vdi")
        if not os.path.isfile(vdi):
            # VirtualBox may put it under Documents
            alt = os.path.join(os.path.expandvars(r"%USERPROFILE%"), "VirtualBox VMs", VM_NAME, VM_NAME + ".vdi")
            if os.path.isfile(alt): vdi = alt
        rc, out = vbox(vb, "storageattach", VM_NAME, "--storagectl", "SATA", "--port", "0", "--device", "0",
                       "--type", "hdd", "--medium", vdi)
        self.emit(("Disk attached." if rc == 0 else "Disk attach: ") + ("" if rc == 0 else out.strip()[:150]))
        rc, out = vbox(vb, "storagectl", VM_NAME, "--name", "IDE", "--add", "ide")
        self.emit("IDE controller ready." if rc == 0 else ("IDE: " + out.strip()[:100]))
        self.emit("VM created. Attach an ISO, then Start.")
        self._refresh()

    def attach_iso(self):
        if not self.need_vb(): return
        path = self.iso_path.get().strip()
        if not path or not os.path.isfile(path):
            messagebox.showwarning(APP, "Choose a valid .iso file first."); return
        self.bg(self._attach_iso, path)

    def _attach_iso(self, path):
        vb = self.vb
        # ensure IDE controller
        vbox(vb, "storagectl", VM_NAME, "--name", "IDE", "--add", "ide")
        rc, out = vbox(vb, "storageattach", VM_NAME, "--storagectl", "IDE", "--port", "0", "--device", "0",
                       "--type", "dvddrive", "--medium", path)
        self.emit(("ISO attached: " + os.path.basename(path)) if rc == 0 else ("Attach failed: " + out.strip()[:200]))
        # boot from DVD first
        vbox(vb, "modifyvm", VM_NAME, "--boot1", "dvd", "--boot2", "disk")
        self._refresh()

    def start_vm(self):
        if not self.need_vb(): return
        self.bg(self._start_vm)

    def _start_vm(self):
        rc, out = vbox(self.vb, "startvm", VM_NAME, "--type", "gui", timeout=60)
        self.emit("Starting…" if rc == 0 else ("Start failed: " + out.strip()[:200]))
        time.sleep(1); self._refresh()

    def stop_vm(self):
        if not self.need_vb(): return
        self.bg(self._stop_vm)

    def _stop_vm(self):
        # ACPI power button first; force if needed
        rc, out = vbox(self.vb, "controlvm", VM_NAME, "acpipowerbutton", timeout=30)
        if rc != 0:
            rc, out = vbox(self.vb, "controlvm", VM_NAME, "poweroff", timeout=30)
            self.emit("Force power-off." if rc == 0 else ("Stop failed: " + out.strip()[:150]))
        else:
            self.emit("Sent ACPI power button (graceful shutdown).")
        time.sleep(1); self._refresh()

    def update_click(self):
        self.upd.set("Checking…")
        def job():
            st, d = check_update(); self.q.put(("upd", (st, d)))
        self.bg(job)

    def update_result(self, st, d):
        if st != "newer":
            self.upd.set(d); (messagebox.showinfo if st == "latest" else messagebox.showwarning)(APP, d); return
        self.upd.set("Version %s available" % d["version"])
        msg = "Version %s is available (you have %s).\n\n%s" % (d["version"], APP_VERSION, d["notes"] or "")
        link = d.get("installer_url") or d["url"]
        msg += "\n\nDownload and run the installer (close this app first)."
        if link.lower().startswith(("https://", "http://")):
            if messagebox.askyesno(APP, msg + "\n\nOpen the download in your browser?"):
                webbrowser.open(link)
        else:
            messagebox.showinfo(APP, msg)


if __name__ == "__main__":
    if single_instance():
        App().mainloop()
