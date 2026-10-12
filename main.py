# tool_gen_code_app.py — License & Recovery Code Generator (English UI)
# ⭐ البصمة الجديدة = SHA256(ANDROID_ID|MANUFACTURER|MODEL)[:16].upper()
#     البصمة القديمة = SHA256(FINGERPRINT|MANUFACTURER|MODEL|BOARD|HARDWARE|DEVICE)[:16].upper()
#     كلاهما يُوقّع بنفس الصيغة: sign(device_id + "|" + hw_fp)
#
# ⚠️ أداة إدارية — تحتوي على المفتاح الخاص. لا تُنشر ولا تُشارك.

import os
import base64
import hashlib

from kivy.lang import Builder
from kivy.metrics import dp
from kivy.core.clipboard import Clipboard
from kivy.properties import StringProperty, ListProperty
from kivymd.app import MDApp
from kivymd.toast import toast
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.card import MDCard

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend

# =====================================================================
# Private key loading
# =====================================================================
PRIVATE_KEY = None


def find_private_key(extra_dir=None):
    candidates = []
    if extra_dir:
        candidates.append(os.path.join(extra_dir, "private_key.pem"))
    candidates += [
        "private_key.pem",
        os.path.join(os.path.dirname(__file__), "private_key.pem"),
        os.path.join(os.getcwd(), "private_key.pem"),
        os.path.join(os.path.expanduser("~"), "private_key.pem"),
        "/storage/emulated/0/private_key.pem",
        "/storage/emulated/0/Documents/private_key.pem",
        "/storage/emulated/0/Documents/SamirPythDZ/private_key.pem",
    ]
    for path in candidates:
        if os.path.exists(path):
            return path
    return None


def load_private_key(extra_dir=None):
    global PRIVATE_KEY
    path = find_private_key(extra_dir)
    if not path:
        return False, "private_key.pem not found"
    try:
        with open(path, "rb") as f:
            PRIVATE_KEY = serialization.load_pem_private_key(
                f.read(), password=None, backend=default_backend())
        return True, path
    except Exception as e:
        return False, f"Key error: {str(e)[:60]}"


def generate_license(device_id: str, hw_fp: str = "") -> str:
    """
    Generate a license code.
    The signed message MUST match EXACTLY what the app verifies:
      - If hw_fp provided: sign(device_id|hw_fp)
      - Else: sign(device_id)
    """
    if not device_id or not device_id.strip():
        raise ValueError("Device ID is empty")

    did = device_id.strip().upper()
    fp = (hw_fp or "").strip().upper()

    if fp:
        message = (did + "|" + fp).encode("utf-8")
    else:
        message = did.encode("utf-8")

    signature = PRIVATE_KEY.sign(
        message,
        padding.PSS(mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH),
        hashes.SHA256(),
    )
    return base64.urlsafe_b64encode(signature).decode("ascii")


# =====================================================================
# Recovery code (must match the app's generate_recovery_code)
# =====================================================================
RECOVERY_SECRET = "SamirPythDZ_recovery_2025_v1"


def generate_recovery_code(device_id):
    """نفس الدالة الموجودة داخل التطبيق.
    SHA256(device_id + "|" + RECOVERY_SECRET).hexdigest()[:8].upper()
    """
    if not device_id:
        return ""
    h = hashlib.sha256(
        (device_id.strip().upper() + "|" + RECOVERY_SECRET).encode("utf-8")
    ).hexdigest()
    return h[:8].upper()


# =====================================================================
# UI
# =====================================================================
KV = '''
#:import NoTransition kivy.uix.screenmanager.NoTransition
MDScreen:
    md_bg_color: 0.95, 0.96, 0.98, 1
    MDBoxLayout:
        orientation: "vertical"

        # ============ Header ============
        MDBoxLayout:
            orientation: "vertical"
            size_hint_y: None
            height: "68dp"
            padding: "14dp", "8dp"
            md_bg_color: 0.08, 0.20, 0.45, 1
            MDLabel:
                text: "License & Recovery Tool"
                font_size: "18sp"
                bold: True
                color: 1, 1, 1, 1
                halign: "center"
                valign: "middle"
                text_size: self.width, None
            MDLabel:
                text: "Samir Pyth_DZ  —  Admin Utility"
                font_size: "10sp"
                color: 1, 1, 1, 0.75
                halign: "center"
                valign: "middle"
                size_hint_y: None
                height: "14dp"
                text_size: self.width, None

        # ============ Tab switcher ============
        MDBoxLayout:
            orientation: "horizontal"
            size_hint_y: None
            height: "46dp"
            padding: "8dp", "4dp"
            spacing: "6dp"
            MDCard:
                size_hint_x: 0.5
                radius: [10]
                elevation: 0
                md_bg_color: app.tab_license_color
                ripple_behavior: True
                on_release: app.switch_tab("license")
                MDLabel:
                    text: "Activation Code"
                    halign: "center"
                    valign: "middle"
                    bold: True
                    font_size: "13sp"
                    theme_text_color: "Custom"
                    text_color: 1, 1, 1, 1
            MDCard:
                size_hint_x: 0.5
                radius: [10]
                elevation: 0
                md_bg_color: app.tab_recovery_color
                ripple_behavior: True
                on_release: app.switch_tab("recovery")
                MDLabel:
                    text: "PIN Recovery"
                    halign: "center"
                    valign: "middle"
                    bold: True
                    font_size: "13sp"
                    theme_text_color: "Custom"
                    text_color: 1, 1, 1, 1

        # ============ Screens ============
        ScreenManager:
            id: tab_sm
            transition: NoTransition()

            MDScreen:
                name: "license"
                MDBoxLayout:
                    orientation: "vertical"
                    padding: "10dp"
                    spacing: "6dp"

                    # Key status + import button
                    MDBoxLayout:
                        orientation: "horizontal"
                        size_hint_y: None
                        height: "40dp"
                        spacing: "6dp"
                        MDCard:
                            size_hint_x: 0.65
                            radius: [10]
                            elevation: 0
                            md_bg_color: app.key_status_color
                            padding: "6dp", 0
                            MDLabel:
                                text: app.key_status_text
                                bold: True
                                font_size: "11sp"
                                halign: "center"
                                valign: "middle"
                                theme_text_color: "Custom"
                                text_color: 1, 1, 1, 1
                                text_size: self.width, None
                        MDFlatButton:
                            text: "Import Key"
                            size_hint_x: 0.35
                            font_size: "12sp"
                            theme_text_color: "Custom"
                            text_color: 0.08, 0.45, 0.75, 1
                            on_release: app.import_key()

                    # Device ID
                    MDLabel:
                        text: "Device ID"
                        bold: True
                        font_size: "13sp"
                        size_hint_y: None
                        height: "20dp"
                        theme_text_color: "Custom"
                        text_color: 0.08, 0.45, 0.75, 1
                    MDTextField:
                        id: device_field
                        mode: "rectangle"
                        hint_text: "e.g. F08D87722C4B4DC3"
                        font_size: "14sp"
                        size_hint_y: None
                        height: "48dp"
                        halign: "center"
                    MDBoxLayout:
                        orientation: "horizontal"
                        size_hint_y: None
                        height: "34dp"
                        spacing: "6dp"
                        MDFlatButton:
                            text: "Paste"
                            font_size: "12sp"
                            on_release: app.paste_device()
                        MDFlatButton:
                            text: "Clear"
                            font_size: "12sp"
                            on_release: app.clear_device()

                    # HW Fingerprint
                    MDLabel:
                        text: "HW Fingerprint (recommended)"
                        bold: True
                        font_size: "13sp"
                        size_hint_y: None
                        height: "20dp"
                        theme_text_color: "Custom"
                        text_color: 0.55, 0.27, 0.68, 1
                    MDTextField:
                        id: hwfp_field
                        mode: "rectangle"
                        hint_text: "e.g. 4A1B2C3D4E5F6789"
                        font_size: "14sp"
                        size_hint_y: None
                        height: "48dp"
                        halign: "center"
                    MDBoxLayout:
                        orientation: "horizontal"
                        size_hint_y: None
                        height: "34dp"
                        spacing: "6dp"
                        MDFlatButton:
                            text: "Paste"
                            font_size: "12sp"
                            on_release: app.paste_hwfp()
                        MDFlatButton:
                            text: "Clear"
                            font_size: "12sp"
                            on_release: app.clear_hwfp()

                    # Generate button
                    MDRaisedButton:
                        text: "Generate Activation Code"
                        md_bg_color: 0.08, 0.45, 0.75, 1
                        font_size: "14sp"
                        size_hint_y: None
                        height: "46dp"
                        pos_hint: {"center_x": 0.5}
                        on_release: app.generate()

                    # Code output
                    MDLabel:
                        text: "Activation Code"
                        bold: True
                        font_size: "13sp"
                        size_hint_y: None
                        height: "20dp"
                        theme_text_color: "Custom"
                        text_color: 0.15, 0.55, 0.32, 1
                    MDTextField:
                        id: code_field
                        mode: "rectangle"
                        readonly: True
                        multiline: True
                        font_size: "10sp"
                        size_hint_y: None
                        height: "110dp"
                        hint_text: "The code will appear here..."

                    # Copy/Share
                    MDBoxLayout:
                        orientation: "horizontal"
                        size_hint_y: None
                        height: "42dp"
                        spacing: "6dp"
                        MDRaisedButton:
                            text: "Copy"
                            md_bg_color: 0.15, 0.55, 0.32, 1
                            font_size: "13sp"
                            size_hint_x: 0.5
                            on_release: app.copy_license_code()
                        MDRaisedButton:
                            text: "Share"
                            md_bg_color: 0.25, 0.65, 0.85, 1
                            font_size: "13sp"
                            size_hint_x: 0.5
                            on_release: app.share_license_code()

            MDScreen:
                name: "recovery"
                MDBoxLayout:
                    orientation: "vertical"
                    padding: "10dp"
                    spacing: "8dp"

                    # Info card (compact)
                    MDCard:
                        orientation: "vertical"
                        size_hint_y: None
                        height: "110dp"
                        padding: "10dp"
                        spacing: "4dp"
                        radius: [12]
                        elevation: 0
                        md_bg_color: 0.98, 0.95, 0.88, 1
                        MDLabel:
                            text: "What is this code?"
                            bold: True
                            font_size: "13sp"
                            size_hint_y: None
                            height: "20dp"
                            theme_text_color: "Custom"
                            text_color: 0.75, 0.22, 0.17, 1
                        MDLabel:
                            text: "A recovery code lets a customer who forgot their PIN reset it without losing data. Give it only to the verified device owner."
                            font_size: "11sp"
                            theme_text_color: "Custom"
                            text_color: 0.15, 0.15, 0.20, 1
                            text_size: self.width, None
                        MDLabel:
                            text: "SHA256(DEVICE_ID | secret)[:8]"
                            size_hint_y: None
                            height: "14dp"
                            font_size: "9sp"
                            theme_text_color: "Secondary"

                    # Device ID
                    MDLabel:
                        text: "Device ID"
                        bold: True
                        font_size: "13sp"
                        size_hint_y: None
                        height: "20dp"
                        theme_text_color: "Custom"
                        text_color: 0.08, 0.45, 0.75, 1
                    MDTextField:
                        id: rec_device_field
                        mode: "rectangle"
                        hint_text: "e.g. F08D87722C4B4DC3"
                        font_size: "14sp"
                        size_hint_y: None
                        height: "48dp"
                        halign: "center"
                    MDBoxLayout:
                        orientation: "horizontal"
                        size_hint_y: None
                        height: "34dp"
                        spacing: "6dp"
                        MDFlatButton:
                            text: "Paste"
                            font_size: "12sp"
                            on_release: app.paste_rec_device()
                        MDFlatButton:
                            text: "Clear"
                            font_size: "12sp"
                            on_release: app.clear_rec_device()

                    # Generate button
                    MDRaisedButton:
                        text: "Generate Recovery Code"
                        md_bg_color: 0.55, 0.27, 0.68, 1
                        font_size: "14sp"
                        size_hint_y: None
                        height: "46dp"
                        pos_hint: {"center_x": 0.5}
                        on_release: app.generate_recovery()

                    # Recovery code output
                    MDLabel:
                        text: "Recovery Code (8 characters)"
                        bold: True
                        font_size: "13sp"
                        size_hint_y: None
                        height: "20dp"
                        theme_text_color: "Custom"
                        text_color: 0.55, 0.27, 0.68, 1
                    MDTextField:
                        id: rec_code_field
                        mode: "rectangle"
                        readonly: True
                        font_size: "28sp"
                        bold: True
                        halign: "center"
                        size_hint_y: None
                        height: "70dp"
                        hint_text: "- - - - - - - -"

                    # Copy/Share
                    MDBoxLayout:
                        orientation: "horizontal"
                        size_hint_y: None
                        height: "42dp"
                        spacing: "6dp"
                        MDRaisedButton:
                            text: "Copy"
                            md_bg_color: 0.15, 0.55, 0.32, 1
                            font_size: "13sp"
                            size_hint_x: 0.5
                            on_release: app.copy_recovery_code()
                        MDRaisedButton:
                            text: "Share"
                            md_bg_color: 0.25, 0.65, 0.85, 1
                            font_size: "13sp"
                            size_hint_x: 0.5
                            on_release: app.share_recovery_code()

                    Widget:
'''


class CodeGenApp(MDApp):
    key_status_text = StringProperty("")
    key_status_color = ListProperty([0.75, 0.22, 0.17, 1])
    tab_license_color = ListProperty([0.08, 0.45, 0.75, 1])
    tab_recovery_color = ListProperty([0.75, 0.75, 0.75, 1])
    current_tab = StringProperty("license")

    def build(self):
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Blue"
        return Builder.load_string(KV)

    def on_start(self):
        ok, info = load_private_key(self.user_data_dir)
        if ok:
            self.key_status_text = "Private key loaded successfully"
            self.key_status_color = [0.15, 0.55, 0.32, 1]
        else:
            self.key_status_text = info
            self.key_status_color = [0.75, 0.22, 0.17, 1]

    # ---------------- Tab switcher ----------------
    def switch_tab(self, tab):
        if tab == self.current_tab:
            return
        self.current_tab = tab
        if tab == "license":
            self.tab_license_color = [0.08, 0.45, 0.75, 1]
            self.tab_recovery_color = [0.75, 0.75, 0.75, 1]
        else:
            self.tab_license_color = [0.75, 0.75, 0.75, 1]
            self.tab_recovery_color = [0.55, 0.27, 0.68, 1]
        try:
            self.root.ids.tab_sm.current = tab
        except Exception as e:
            print("switch_tab error:", e)

    # ---------------- Import private key ----------------
    def import_key(self):
        global PRIVATE_KEY
        try:
            pem = (Clipboard.paste() or "").strip()
            if "PRIVATE KEY" not in pem:
                toast("Clipboard has no private key")
                return
            key = serialization.load_pem_private_key(
                pem.encode("utf-8"), password=None, backend=default_backend())
            os.makedirs(self.user_data_dir, exist_ok=True)
            path = os.path.join(self.user_data_dir, "private_key.pem")
            with open(path, "wb") as f:
                f.write(pem.encode("utf-8") + b"\n")
            PRIVATE_KEY = key
            self.key_status_text = "Private key loaded successfully"
            self.key_status_color = [0.15, 0.55, 0.32, 1]
            try:
                Clipboard.copy("")
            except Exception:
                pass
            toast("Key imported")
        except Exception as e:
            toast(f"Key error: {str(e)[:40]}")

    # ---------------- License tab ----------------
    def paste_device(self):
        try:
            self.root.ids.device_field.text = (Clipboard.paste() or "").strip().upper()
        except Exception as e:
            toast(f"Error: {str(e)[:40]}")

    def paste_hwfp(self):
        try:
            self.root.ids.hwfp_field.text = (Clipboard.paste() or "").strip().upper()
        except Exception as e:
            toast(f"Error: {str(e)[:40]}")

    def clear_device(self):
        self.root.ids.device_field.text = ""
        self.root.ids.code_field.text = ""

    def clear_hwfp(self):
        self.root.ids.hwfp_field.text = ""
        self.root.ids.code_field.text = ""

    def generate(self):
        if PRIVATE_KEY is None:
            toast("Private key not loaded")
            return
        device = (self.root.ids.device_field.text or "").strip().upper()
        hwfp = (self.root.ids.hwfp_field.text or "").strip().upper()
        if not device:
            toast("Please enter a device ID")
            return
        if not hwfp:
            toast("Warning: no HW Fingerprint — weak protection")
        try:
            code = generate_license(device, hwfp)
            self.root.ids.code_field.text = code
            if hwfp:
                toast("Activation code generated (strong)")
            else:
                toast("Activation code generated (weak)")
        except Exception as e:
            toast(f"Error: {str(e)[:50]}")

    def copy_license_code(self):
        code = (self.root.ids.code_field.text or "").strip()
        if not code:
            toast("No code to copy")
            return
        try:
            Clipboard.copy(code)
            toast("Activation code copied")
        except Exception as e:
            toast(f"Error: {str(e)[:40]}")

    def share_license_code(self):
        code = (self.root.ids.code_field.text or "").strip()
        if not code:
            toast("No code to share")
            return
        device = (self.root.ids.device_field.text or "").strip()
        hwfp = (self.root.ids.hwfp_field.text or "").strip()
        msg = (
            "Samir Pyth_DZ — Activation Code\n"
            f"Device ID: {device}\n"
        )
        if hwfp:
            msg += f"HW Fingerprint: {hwfp}\n"
        msg += f"\n{code}"
        self._share_text(msg)

    # ---------------- Recovery tab ----------------
    def paste_rec_device(self):
        try:
            self.root.ids.rec_device_field.text = (Clipboard.paste() or "").strip().upper()
        except Exception as e:
            toast(f"Error: {str(e)[:40]}")

    def clear_rec_device(self):
        self.root.ids.rec_device_field.text = ""
        self.root.ids.rec_code_field.text = ""

    def generate_recovery(self):
        device = (self.root.ids.rec_device_field.text or "").strip().upper()
        if not device:
            toast("Please enter a device ID")
            return
        try:
            code = generate_recovery_code(device)
            self.root.ids.rec_code_field.text = code
            toast(f"Recovery code ready: {code}")
        except Exception as e:
            toast(f"Error: {str(e)[:50]}")

    def copy_recovery_code(self):
        code = (self.root.ids.rec_code_field.text or "").strip()
        if not code:
            toast("No code to copy")
            return
        try:
            Clipboard.copy(code)
            toast("Recovery code copied")
        except Exception as e:
            toast(f"Error: {str(e)[:40]}")

    def share_recovery_code(self):
        code = (self.root.ids.rec_code_field.text or "").strip()
        if not code:
            toast("No code to share")
            return
        device = (self.root.ids.rec_device_field.text or "").strip()
        msg = (
            "Samir Pyth_DZ — PIN Recovery Code\n"
            f"Device ID: {device}\n\n"
            f"Recovery Code: {code}\n\n"
            "Enter this code in the app under 'Forgot PIN?'"
        )
        self._share_text(msg)

    # ---------------- Shared share helper ----------------
    def _share_text(self, message):
        try:
            from kivy.utils import platform
            if platform == "android":
                from jnius import autoclass, cast
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                Intent = autoclass('android.content.Intent')
                String = autoclass('java.lang.String')

                intent = Intent(Intent.ACTION_SEND)
                intent.setType("text/plain")
                intent.putExtra(Intent.EXTRA_TEXT,
                                cast('java.lang.CharSequence', String(message)))

                try:
                    wa_intent = Intent(Intent.ACTION_SEND)
                    wa_intent.setType("text/plain")
                    wa_intent.putExtra(Intent.EXTRA_TEXT,
                                       cast('java.lang.CharSequence', String(message)))
                    wa_intent.setPackage("com.whatsapp")
                    PythonActivity.mActivity.startActivity(wa_intent)
                except Exception:
                    chooser = Intent.createChooser(
                        intent,
                        cast('java.lang.CharSequence', String("Share")))
                    PythonActivity.mActivity.startActivity(chooser)
            else:
                Clipboard.copy(message)
                toast("Copied to clipboard (desktop)")
        except Exception as e:
            toast(f"Share failed: {str(e)[:50]}")


if __name__ == "__main__":
    CodeGenApp().run()