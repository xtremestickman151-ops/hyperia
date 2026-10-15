# HYPERIA

A creative **desktop shell** for Windows from EX Inc.: wallpaper, taskbar, Start menu, desktop icons and windows that open inside the shell.

**Honest note:** HYPERIA is an app that runs on Windows. It is **not** a real operating system or kernel. Web apps open the real websites only in a HYPERIA web window (requires the Microsoft Edge WebView2 Runtime, standard on Windows 10/11); HYPERIA does not copy or host their content.

## Apps
- **Built in:** HYPERIA Store, Files, Terminal (PowerShell), Settings (wallpaper, fullscreen, updates), Clock, Pong, **Fireout 1997** (original retro top-down racer).
- **Web:** EX SAFARIA LITE (browser), YouTube, Discord, Steam, itch.io, Speed Test, Reddit, Wikipedia, Twitch, Weather, Sport, Amazon, Temu, Xbox, Cloud Gaming, Google Earth.

Shortcuts: F11 fullscreen, Esc closes the Start menu.

## Install
Download **`HYPERIA Setup <version>.exe`** from [Releases](../../releases/latest) and run it (per-user, no admin). The app is unsigned, so SmartScreen may warn: **More info → Run anyway**.

## Build (Windows)
```
pip install pyinstaller pywebview
pyinstaller --onedir --noconsole --name HYPERIA --icon logo.ico --version-file version.txt --add-data "logo.ico;." --add-data "logo256.png;." --add-data "logo48.png;." --add-data "browser48.png;." --add-data "browser22.png;." --collect-all webview hyperia.py
```
Installer: compile `installer.iss` with Inno Setup 6.

---
©2026 EX Inc.
