#!/usr/bin/env python3
"""
Feishu Desktop App Controller
Control the native Feishu desktop application using UI Automation
"""

import sys
import time
from pathlib import Path

try:
    from pywinauto import Application, Desktop
    from pywinauto.findwindows import ElementNotFoundError
    PYWINAUTO_AVAILABLE = True
except ImportError:
    PYWINAUTO_AVAILABLE = False
    print("[ERROR] pywinauto not installed")
    print("Install with: pip install pywinauto")
    sys.exit(1)


class FeishuDesktopController:
    def __init__(self):
        self.app = None
        self.main_window = None
        self.feishu_path = self._find_feishu_path()

    def _find_feishu_path(self):
        """Find Feishu desktop app installation"""
        import os
        username = os.getenv("USERNAME")

        possible_paths = [
            f"C:\\Users\\{username}\\AppData\\Local\\Programs\\Feishu\\Feishu.exe",
            "C:\\Program Files\\Feishu\\Feishu.exe",
            "C:\\Program Files (x86)\\Feishu\\Feishu.exe",
        ]

        for path in possible_paths:
            if Path(path).exists():
                return path

        return None

    def launch(self):
        """Launch Feishu desktop app"""
        if not self.feishu_path:
            print("[ERROR] Feishu desktop app not found")
            print("Please install from: https://www.feishu.cn/download")
            return False

        print(f"[*] Launching Feishu from: {self.feishu_path}")

        try:
            # Launch the application
            self.app = Application(backend="uia").start(self.feishu_path)
            time.sleep(5)  # Wait for app to start

            # Connect to main window
            self.main_window = self.app.window(title_re=".*Feishu.*|.*飞书.*")
            print("[OK] Connected to Feishu desktop app")
            return True

        except Exception as e:
            print(f"[ERROR] Failed to launch: {e}")
            return False

    def connect_existing(self):
        """Connect to already running Feishu app"""
        try:
            self.app = Application(backend="uia").connect(title_re=".*Feishu.*|.*飞书.*")
            self.main_window = self.app.window(title_re=".*Feishu.*|.*飞书.*")
            print("[OK] Connected to running Feishu app")
            return True
        except Exception as e:
            print(f"[ERROR] Could not connect to Feishu: {e}")
            print("[*] Is Feishu running?")
            return False

    def list_chats(self):
        """List visible chats"""
        if not self.main_window:
            print("[ERROR] Not connected to Feishu")
            return []

        try:
            print("[*] Getting chat list...")

            # Get all list items (chats)
            chat_list = self.main_window.descendants(control_type="ListItem")
            chats = []

            for item in chat_list[:20]:  # Limit to first 20
                try:
                    name = item.window_text()
                    if name:
                        chats.append(name)
                except:
                    continue

            print(f"[OK] Found {len(chats)} chats")
            return chats

        except Exception as e:
            print(f"[ERROR] Could not list chats: {e}")
            return []

    def open_chat(self, chat_name):
        """Open a specific chat"""
        if not self.main_window:
            print("[ERROR] Not connected to Feishu")
            return False

        try:
            print(f"[*] Opening chat: {chat_name}")

            # Find the chat in list
            chat_item = self.main_window.child_window(title=chat_name, control_type="ListItem")
            chat_item.click_input()

            time.sleep(1)
            print(f"[OK] Opened chat: {chat_name}")
            return True

        except Exception as e:
            print(f"[ERROR] Could not open chat: {e}")
            return False

    def send_message(self, message):
        """Send a message in the current chat"""
        if not self.main_window:
            print("[ERROR] Not connected to Feishu")
            return False

        try:
            print(f"[*] Sending message: {message[:50]}...")

            # Find the message input box
            # This might need adjustment based on Feishu's UI structure
            input_box = self.main_window.child_window(control_type="Edit", found_index=0)

            # Type the message
            input_box.set_focus()
            time.sleep(0.3)
            input_box.type_keys(message, with_spaces=True)
            time.sleep(0.3)

            # Press Enter to send
            input_box.type_keys("{ENTER}")
            time.sleep(0.5)

            print("[OK] Message sent!")
            return True

        except Exception as e:
            print(f"[ERROR] Could not send message: {e}")
            print("[*] Tip: Make sure a chat is open")
            return False

    def send_to_chat(self, chat_name, message):
        """Send message to specific chat"""
        if self.open_chat(chat_name):
            return self.send_message(message)
        return False

    def get_window_info(self):
        """Get information about Feishu window structure"""
        if not self.main_window:
            print("[ERROR] Not connected to Feishu")
            return

        print("\n[*] Feishu Window Structure:")
        self.main_window.print_control_identifiers()

    def take_screenshot(self, filename="feishu_desktop.png"):
        """Take screenshot of Feishu window"""
        if not self.main_window:
            print("[ERROR] Not connected to Feishu")
            return False

        try:
            self.main_window.capture_as_image().save(filename)
            print(f"[OK] Screenshot saved: {filename}")
            return True
        except Exception as e:
            print(f"[ERROR] Screenshot failed: {e}")
            return False

    def close(self):
        """Close Feishu app"""
        if self.app:
            try:
                self.app.kill()
                print("[OK] Feishu closed")
            except:
                pass


def main():
    if not PYWINAUTO_AVAILABLE:
        return

    if len(sys.argv) < 2:
        print("""
Feishu Desktop App Controller

SETUP:
  pip install pywinauto

COMMANDS:
  launch                        - Launch Feishu app
  connect                       - Connect to running Feishu
  list                          - List chats
  send <chat> <message>         - Send message to chat
  info                          - Show window structure (for debugging)
  screenshot [filename]         - Take screenshot

EXAMPLES:
  python feishu_desktop.py launch
  python feishu_desktop.py connect
  python feishu_desktop.py list
  python feishu_desktop.py send Hany "Hello from desktop app!"
  python feishu_desktop.py screenshot

NOTE: Desktop app control is experimental and may need adjustments
      based on Feishu's UI structure.
""")
        return

    command = sys.argv[1]
    controller = FeishuDesktopController()

    if command == "launch":
        controller.launch()

    elif command == "connect":
        controller.connect_existing()

    elif command == "list":
        if controller.connect_existing():
            chats = controller.list_chats()
            print("\n[*] Your Chats:")
            for chat in chats:
                print(f"  - {chat}")

    elif command == "send":
        if len(sys.argv) < 4:
            print("[ERROR] Usage: send <chat> <message>")
            return

        chat_name = sys.argv[2]
        message = " ".join(sys.argv[3:])

        if controller.connect_existing():
            controller.send_to_chat(chat_name, message)

    elif command == "info":
        if controller.connect_existing():
            controller.get_window_info()

    elif command == "screenshot":
        filename = sys.argv[2] if len(sys.argv) > 2 else "feishu_desktop.png"
        if controller.connect_existing():
            controller.take_screenshot(filename)

    else:
        print(f"[ERROR] Unknown command: {command}")


if __name__ == "__main__":
    main()
