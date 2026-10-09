# tool_gen_code_app.py — License Code Generator (English UI)
# ⭐ البصمة الجديدة = SHA256(ANDROID_ID|MANUFACTURER|MODEL)[:16].upper()
#     البصمة القديمة = SHA256(FINGERPRINT|MANUFACTURER|MODEL|BOARD|HARDWARE|DEVICE)[:16].upper()
#     كلاهما يُوقّع بنفس الصيغة: sign(device_id + "|" + hw_fp)

import os
import base64

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
# UI
# =====================================================================
KV = '''
MDScreen:
    md_bg_color: 0.95, 0.96, 0.98, 1
    MDBoxLayout:
        orientation: "vertical"

        MDBoxLayout:
            orientation: "vertical"
            size_hint_y: None
            height: "80dp"
            padding: "14dp", "10dp"
            md_bg_color: 0.08, 0.20, 0.45, 1
            MDLabel:
                text: "License Code Generator"
                font_size: "20sp"
                bold: True
                color: 1, 1, 1, 1
                halign: "center"
                valign: "middle"
                text_size: self.width, None
            MDLabel:
                text: "Samir Pyth_DZ  —  Activation Tool"
                font_size: "11sp"
                color: 1, 1, 1, 0.75
                halign: "center"
                valign: "middle"
                size_hint_y: None
                height: "16dp"
                text_size: self.width, None

        ScrollView:
            MDBoxLayout:
                orientation: "vertical"
                size_hint_y: None
                height: self.minimum_height
                padding: "16dp"
                spacing: "12dp"

                MDCard:
                    orientation: "vertical"
                    size_hint_y: None
                    height: "110dp"
                    padding: "12dp"
                    spacing: "6dp"
                    radius: [12]
                    elevation: 1
                    md_bg_color: app.key_status_color
                    MDLabel:
                        text: app.key_status_text
                        bold: True
                        font_size: "13sp"
                        halign: "center"
                        valign: "middle"
                        theme_text_color: "Custom"
                        text_color: 1, 1, 1, 1
                        size_hint_y: None
                        height: "32dp"
                        text_size: self.width, None
                    MDFlatButton:
                        text: "Import Key (paste PEM)"
                        theme_text_color: "Custom"
                        text_color: 1, 1, 1, 1
                        pos_hint: {"center_x": 0.5}
                        on_release: app.import_key()

                MDCard:
                    orientation: "vertical"
                    size_hint_y: None
                    height: "200dp"
                    padding: "14dp"
                    spacing: "10dp"
                    radius: [16]
                    elevation: 2
                    md_bg_color: 1, 1, 1, 1
                    MDLabel:
                        text: "Device ID"
                        bold: True
                        font_size: "15sp"
                        theme_text_color: "Custom"
                        text_color: 0.08, 0.45, 0.75, 1
                        size_hint_y: None
                        height: "24dp"
                    MDTextField:
                        id: device_field
                        mode: "rectangle"
                        hint_text: "e.g. F08D87722C4B4DC3"
                        icon_left: "identifier"
                        font_size: "16sp"
                        halign: "center"
                    MDBoxLayout:
                        orientation: "horizontal"
                        size_hint_y: None
                        height: "44dp"
                        spacing: "8dp"
                        MDFlatButton:
                            text: "Paste"
                            on_release: app.paste_device()
                        MDFlatButton:
                            text: "Clear"
                            on_release: app.clear_device()

                MDCard:
                    orientation: "vertical"
                    size_hint_y: None
                    height: "200dp"
                    padding: "14dp"
                    spacing: "10dp"
                    radius: [16]
                    elevation: 2
                    md_bg_color: 1, 1, 1, 1
                    MDLabel:
                        text: "HW Fingerprint (recommended)"
                        bold: True
                        font_size: "15sp"
                        theme_text_color: "Custom"
                        text_color: 0.55, 0.27, 0.68, 1
                        size_hint_y: None
                        height: "24dp"
                    MDTextField:
                        id: hwfp_field
                        mode: "rectangle"
                        hint_text: "e.g. 4A1B2C3D4E5F6789"
                        icon_left: "fingerprint"
                        font_size: "16sp"
                        halign: "center"
                    MDBoxLayout:
                        orientation: "horizontal"
                        size_hint_y: None
                        height: "44dp"
                        spacing: "8dp"
                        MDFlatButton:
                            text: "Paste"
                            on_release: app.paste_hwfp()
                        MDFlatButton:
                            text: "Clear"
                            on_release: app.clear_hwfp()

                MDRaisedButton:
                    text: "Generate Code"
                    md_bg_color: 0.08, 0.45, 0.75, 1
                    size_hint_y: None
                    height: "56dp"
                    pos_hint: {"center_x": 0.5}
                    on_release: app.generate()

                MDCard:
                    orientation: "vertical"
                    size_hint_y: None
                    height: "320dp"
                    padding: "14dp"
                    spacing: "10dp"
                    radius: [16]
                    elevation: 2
                    md_bg_color: 1, 1, 1, 1
                    MDLabel:
                        text: "Activation Code"
                        bold: True
                        font_size: "15sp"
                        theme_text_color: "Custom"
                        text_color: 0.15, 0.55, 0.32, 1
                        size_hint_y: None
                        height: "24dp"
                    MDTextField:
                        id: code_field
                        mode: "rectangle"
                        readonly: True
                        multiline: True
                        font_size: "11sp"
                        size_hint_y: None
                        height: "180dp"
                        hint_text: "The code will appear here..."
                    MDBoxLayout:
                        orientation: "horizontal"
                        size_hint_y: None
                        height: "52dp"
                        spacing: "8dp"
                        MDRaisedButton:
                            text: "Copy"
                            md_bg_color: 0.15, 0.55, 0.32, 1
                            size_hint_x: 0.5
                            on_release: app.copy_code()
                        MDRaisedButton:
                            text: "Share"
                            md_bg_color: 0.25, 0.65, 0.85, 1
                            size_hint_x: 0.5
                            on_release: app.share_code()

                Widget:
                    size_hint_y: None
                    height: "20dp"
'''


class CodeGenApp(MDApp):
    key_status_text = StringProperty("")
    key_status_color = ListProperty([0.75, 0.22, 0.17, 1])

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
                toast("Code generated (strong)")
            else:
                toast("Code generated (weak — no HW FP)")
        except Exception as e:
            toast(f"Error: {str(e)[:50]}")

    def copy_code(self):
        code = self.root.ids.code_field.text.strip()
        if not code:
            toast("No code to copy")
            return
        try:
            Clipboard.copy(code)
            toast("Code copied to clipboard")
        except Exception as e:
            toast(f"Error: {str(e)[:40]}")

    def share_code(self):
        code = self.root.ids.code_field.text.strip()
        if not code:
            toast("No code to share")
            return
        device = self.root.ids.device_field.text.strip()
        hwfp = self.root.ids.hwfp_field.text.strip()
        message = (
            f"Samir Pyth_DZ — Activation Code\n"
            f"Device ID: {device}\n"
        )
        if hwfp:
            message += f"HW Fingerprint: {hwfp}\n"
        message += f"\n{code}"

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
                        cast('java.lang.CharSequence', String("Share Code")))
                    PythonActivity.mActivity.startActivity(chooser)
            else:
                Clipboard.copy(message)
                toast("Copied to clipboard (desktop)")
        except Exception as e:
            toast(f"Share failed: {str(e)[:50]}")


if __name__ == "__main__":
    CodeGenApp().run()