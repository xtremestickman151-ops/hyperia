# HYPERIA

A Windows **VirtualBox front-end** from EX Inc.

**Honest note:** HYPERIA is a branded launcher/manager for Oracle VirtualBox — **not** a from-scratch operating system. It helps you create a VM named `HYPERIA`, attach an ISO you provide, and start or stop that VM.

## Features
- Detects VirtualBox (`VBoxManage`); offers the official download page if missing.
- Create a `HYPERIA` VM (2 GB RAM, 20 GB disk, Ubuntu_64 / EFI).
- Browse and attach a Linux ISO; boot order DVD then disk.
- Start / Stop (ACPI power button, then force power-off if needed).
- **Download Lubuntu ISO** opens the official [Lubuntu downloads](https://lubuntu.me/downloads/) page. HYPERIA does **not** host or redistribute OS images.
- Check for updates; ©2026 EX Inc.

## Install
1. Download **`HYPERIA Setup <version>.exe`** from [Releases](../../releases/latest) and run it (per-user, no admin needed for install).
2. Install [Oracle VirtualBox](https://www.virtualbox.org/wiki/Downloads) separately if you do not already have it.
3. SmartScreen may warn (unsigned): **More info → Run anyway**.

## Build (Windows)
```
pip install pyinstaller
pyinstaller --onedir --noconsole --name HYPERIA --icon logo.ico --version-file version.txt --add-data "logo.ico;." --add-data "logo256.png;." --add-data "logo48.png;." hyperia.py
```
Installer: compile `installer.iss` with Inno Setup 6.

---
©2026 EX Inc.
