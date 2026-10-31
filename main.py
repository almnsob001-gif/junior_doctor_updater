from kivy.config import Config
Config.set('graphics', 'width', '400')
Config.set('graphics', 'height', '700')
Config.set('graphics', 'resizable', '0')
Config.set('graphics', 'orientation', 'portrait')

import os
import json
import webbrowser
import datetime
import re
import data_medical
import data_pediatric
import data_obgyn
import data_surgical
import data_ent
import data_ophthalmology
import data_orthopedics
import data_urology
import data_toxicology
import data_drugs
import data_protocols
import data_calculators
import data_pediatric_calculators
import data_extensions
import data_updater

try:
    import arabic_reshaper
    from bidi.algorithm import get_display
    HAS_ARABIC_SUPPORT = True
except ImportError:
    HAS_ARABIC_SUPPORT = False
    print("Warning: arabic_reshaper or python-bidi not installed.")

from kivy.app import App
from kivy.metrics import dp
from kivy.core.window import Window
from kivy.utils import get_color_from_hex
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.switch import Switch
from kivy.uix.popup import Popup
from kivy.uix.dropdown import DropDown
from kivy.uix.image import AsyncImage
from kivy.graphics import Color, RoundedRectangle, Ellipse
from kivy.core.text import LabelBase
from kivy.core.clipboard import Clipboard
from kivy.clock import Clock

try:
    LabelBase.register(name="Roboto", fn_regular="DejaVuSans.ttf")
except:
    pass

try:
    LabelBase.register(name="ArabicFont", fn_regular="arabic.ttf")
except:
    print("Warning: arabic.ttf not found. Arabic text might not display correctly.")

# ================= دمج البيانات =================
DATA = {}
DATA.update(data_medical.MEDICAL_DATA)
DATA.update(data_pediatric.PEDIATRIC_DATA)
DATA.update(data_obgyn.OBGYN_DATA)
DATA.update(data_surgical.SURGICAL_DATA)
DATA.update(data_ent.ENT_DATA)
DATA.update(data_ophthalmology.OPHTHALMOLOGY_DATA)
DATA.update(data_orthopedics.ORTHOPEDICS_DATA)
DATA.update(data_urology.UROLOGY_DATA)
DATA.update(data_toxicology.TOXICOLOGY_DATA)
DATA.update(data_drugs.DRUGS_DATA)
DATA.update(data_protocols.PROTOCOLS_DATA)
DATA.update(data_calculators.CALCULATORS_DATA)
DATA.update(data_pediatric_calculators.PEDIATRIC_CALCULATORS_DATA)

for spec, subs in data_extensions.EXTENSIONS_DATA.items():
    if spec in DATA:
        for sub, topics in subs.items():
            if sub in DATA[spec]:
                for t in topics:
                    if t not in DATA[spec][sub]:
                        DATA[spec][sub].append(t)
            else:
                DATA[spec][sub] = topics
    else:
        DATA[spec] = subs

TOPIC_PAGES = {}
TOPIC_PAGES.update(data_medical.MEDICAL_TOPICS)
TOPIC_PAGES.update(data_pediatric.PEDIATRIC_TOPICS)
TOPIC_PAGES.update(data_obgyn.OBGYN_TOPICS)
TOPIC_PAGES.update(data_surgical.SURGICAL_TOPICS)
TOPIC_PAGES.update(data_ent.ENT_TOPICS)
TOPIC_PAGES.update(data_ophthalmology.OPHTHALMOLOGY_TOPICS)
TOPIC_PAGES.update(data_orthopedics.ORTHOPEDICS_TOPICS)
TOPIC_PAGES.update(data_urology.UROLOGY_TOPICS)
TOPIC_PAGES.update(data_toxicology.TOXICOLOGY_TOPICS)
TOPIC_PAGES.update(data_drugs.DRUGS_TOPICS)
TOPIC_PAGES.update(data_protocols.PROTOCOLS_TOPICS)

for key, val in data_extensions.EXTENSIONS_TOPICS.items():
    TOPIC_PAGES[key] = val

for specialty in list(DATA.keys()):
    if isinstance(DATA[specialty], list):
        DATA[specialty] = {"General": DATA[specialty]}

for specialty, subsystems in DATA.items():
    for subsystem, topics in subsystems.items():
        for topic in topics:
            if (specialty, topic) not in TOPIC_PAGES and specialty not in ("Clinical Calculators", "Pediatric Calculators"):
                TOPIC_PAGES[(specialty, topic)] = [
                    ("PAGE UNDER DEVELOPMENT", "warning", f"Detailed clinical content for [b]{topic}[/b] is currently being compiled."),
                    ("SAFETY NOTE", "danger", "Verify doses and protocols against local guidelines.")
                ]

# ================= THEME SYSTEM =================
THEME_STATE = {"mode": "light"}

NAVY = "#0A1930"
BLUE = "#2563EB"
TEAL = "#0D9488"
WHITE = "#FFFFFF"
BG_COLOR = "#F4F7FB"
TEXT = "#1E293B"
MUTED = "#64748B"
BORDER = "#E2E8F0"
RED = "#DC2626"
VIOLET = "#8B5CF6"
HEADER_NAVY = "#0F172A"
HEADER_BLUE = "#1E40AF"
CARD_BLUE = "#F0F9FF"
CARD_GREEN = "#F0FDF4"
CARD_PURPLE = "#FAF5FF"
INFO_BG = "#EFF6FF"
INFO_BAR = "#3B82F6"
SUCCESS_BG = "#ECFDF5"
SUCCESS_BAR = "#10B981"
DANGER_BG = "#FEF2F2"
DANGER_BAR = "#EF4444"
HERO_BG = "#0A1930"
SURFACE = "#FFFFFF"
INPUT_BG = "#F4F7FB"

def apply_theme(mode):
    global NAVY, BLUE, TEAL, BG_COLOR, TEXT, MUTED, BORDER, RED, VIOLET
    global HEADER_NAVY, HEADER_BLUE, CARD_BLUE, CARD_GREEN, CARD_PURPLE
    global INFO_BG, INFO_BAR, SUCCESS_BG, SUCCESS_BAR, DANGER_BG, DANGER_BAR
    global HERO_BG, SURFACE, INPUT_BG

    THEME_STATE["mode"] = mode

    if mode == "dark":
        NAVY = "#E2E8F0"; BLUE = "#60A5FA"; TEAL = "#2DD4BF"
        BG_COLOR = "#0F172A"; TEXT = "#E2E8F0"; MUTED = "#94A3B8"
        BORDER = "#334155"; RED = "#F87171"; VIOLET = "#A78BFA"
        HEADER_NAVY = "#020617"; HEADER_BLUE = "#1E3A8A"
        CARD_BLUE = "#1E293B"; CARD_GREEN = "#064E3B"; CARD_PURPLE = "#3B0764"
        INFO_BG = "#1E3A8A"; INFO_BAR = "#3B82F6"
        SUCCESS_BG = "#064E3B"; SUCCESS_BAR = "#10B981"
        DANGER_BG = "#7F1D1D"; DANGER_BAR = "#EF4444"
        HERO_BG = "#020617"; SURFACE = "#1E293B"; INPUT_BG = "#0F172A"
    else:
        NAVY = "#0A1930"; BLUE = "#2563EB"; TEAL = "#0D9488"
        BG_COLOR = "#F4F7FB"; TEXT = "#1E293B"; MUTED = "#64748B"
        BORDER = "#E2E8F0"; RED = "#DC2626"; VIOLET = "#8B5CF6"
        HEADER_NAVY = "#0F172A"; HEADER_BLUE = "#1E40AF"
        CARD_BLUE = "#F0F9FF"; CARD_GREEN = "#F0FDF4"; CARD_PURPLE = "#FAF5FF"
        INFO_BG = "#EFF6FF"; INFO_BAR = "#3B82F6"
        SUCCESS_BG = "#ECFDF5"; SUCCESS_BAR = "#10B981"
        DANGER_BG = "#FEF2F2"; DANGER_BAR = "#EF4444"
        HERO_BG = "#0A1930"; SURFACE = "#FFFFFF"; INPUT_BG = "#F4F7FB"

def is_dark_mode():
    return THEME_STATE["mode"] == "dark"

APP_NAME = "Junior Doctor"
Window.clearcolor = get_color_from_hex(BG_COLOR)

# ================= UI HELPERS =================
def sp(val):
    from kivy.metrics import sp as kivy_sp
    return kivy_sp(val)

def draw_card_bg(widget, bg_color, radius=24, shadow=True, is_bar=False):
    if bg_color == "#FFFFFF":
        bg_color = SURFACE
    with widget.canvas.before:
        if shadow:
            Color(0.1, 0.2, 0.4, 0.06)
            widget._shadow = RoundedRectangle(pos=(widget.x, widget.y - dp(4)), size=widget.size, radius=[dp(radius)])
        Color(*get_color_from_hex(bg_color))
        if is_bar:
            widget._bg_rect = RoundedRectangle(pos=widget.pos, size=widget.size, radius=[dp(radius), 0, 0, dp(radius)])
        else:
            widget._bg_rect = RoundedRectangle(pos=widget.pos, size=widget.size, radius=[dp(radius)])
            
    def update(*_):
        widget._bg_rect.pos = widget.pos
        widget._bg_rect.size = widget.size
        if shadow:
            widget._shadow.pos = (widget.x, widget.y - dp(4))
            widget._shadow.size = widget.size
    widget.bind(pos=update, size=update)

def make_markup_label(text, size=13, color=TEXT):
    if not isinstance(text, str):
        text = str(text)
    blue_hex = BLUE.replace("#", "")
    red_hex = RED.replace("#", "")
    text = text.replace("[color=0000FF]", f"[color={blue_hex}]")
    text = text.replace("[color=FF0000]", f"[color={red_hex}]")
    text = text.replace("[color=#2563EB]", f"[color={blue_hex}]")
    text = text.replace("[color=#DC2626]", f"[color={red_hex}]")
    
    lab = Label(text=text, font_size=sp(size), color=get_color_from_hex(color), markup=True, halign="left", valign="top", size_hint_y=None, line_height=1.25)
    lab.bind(width=lambda i, w: setattr(lab, 'text_size', (w, None)))
    lab.bind(texture_size=lambda i, s: setattr(lab, 'height', s[1] + dp(10)))
    return lab

def make_wrapped_label(text, size=14, color=TEXT, bold=False, halign="left"):
    if not isinstance(text, str):
        text = str(text)
        
    is_arabic = bool(re.search(r'[\u0600-\u06FF]', text))
    
    font_name = "Roboto"
    if is_arabic:
        font_name = "ArabicFont"
        halign = "right"
        if HAS_ARABIC_SUPPORT:
            lines = text.split('\n')
            processed_lines = []
            for line in lines:
                if line.strip():
                    reshaped_line = arabic_reshaper.reshape(line)
                    bidi_line = get_display(reshaped_line)
                    processed_lines.append(bidi_line)
                else:
                    processed_lines.append("")
            text = '\n'.join(processed_lines)

    lab = Label(text=text, font_size=sp(size), color=get_color_from_hex(color), bold=bold, halign=halign, valign="top", size_hint_y=None, font_name=font_name)
    lab.bind(width=lambda i, w: setattr(lab, 'text_size', (w, None)))
    lab.bind(texture_size=lambda i, s: setattr(lab, 'height', s[1] + dp(6)))
    return lab

def highlight_text(text, query):
    if not query:
        return text
    text = re.sub(r'\[color=#([0-9A-Fa-f]{6})\]', r'[color=\1]', str(text))
    parts = re.split(r'(\[[^\]]+\])', text)
    highlighted_parts = []
    red_hex = RED.replace("#", "")
    for part in parts:
        if part.startswith('[') and part.endswith(']'):
            highlighted_parts.append(part)
        else:
            highlighted_part = re.sub(f'(?i)({re.escape(query)})', f'[color={red_hex}][b][u]\\1[/u][/b][/color]', part)
            highlighted_parts.append(highlighted_part)
    return "".join(highlighted_parts)

class Card(BoxLayout):
    def __init__(self, bg=WHITE, radius=24, padding=20, **kwargs):
        if bg == "#FFFFFF":
            bg = SURFACE
        if isinstance(padding, (int, float)):
            pad = dp(padding)
        elif isinstance(padding, (list, tuple)):
            pad = [dp(p) if isinstance(p, (int, float)) else p for p in padding]
        else:
            pad = padding
            
        if 'size_hint' not in kwargs and 'size_hint_y' not in kwargs:
            kwargs['size_hint_y'] = None
            
        super().__init__(orientation="vertical", padding=pad, spacing=dp(8), **kwargs)
        self.bind(minimum_height=self.setter("height"))
        draw_card_bg(self, bg, radius)

class JDButton(Button):
    def __init__(self, text="", bg=BLUE, fg=WHITE, height=52, radius=16, font_size=15, **kwargs):
        halign = kwargs.pop("halign", "center")
        super().__init__(text=text, size_hint_y=None, height=dp(height), font_size=sp(font_size), bold=True,
                         color=get_color_from_hex(fg), background_normal="", background_down="",
                         background_color=(0, 0, 0, 0), halign=halign, valign="middle", **kwargs)
        draw_card_bg(self, bg, radius, shadow=False)
        self.bind(size=lambda i, v: setattr(i, 'text_size', (v[0] - dp(20), None)))

class ModernHeader(BoxLayout):
    def __init__(self, title, subtitle="", bg_color=HEADER_NAVY, title_color=WHITE,
                 subtitle_color="#94A3B8", menu_callback=None,
                 heart_callback=None, is_fav=False, **kwargs):
        super().__init__(orientation="horizontal", size_hint_y=None, height=dp(90),
                         spacing=dp(6), padding=[dp(20), dp(15), dp(15), dp(15)], **kwargs)

        with self.canvas.before:
            Color(*get_color_from_hex(bg_color))
            self._bg = RoundedRectangle(pos=self.pos, size=self.size, radius=[0, 0, dp(30), dp(30)])
        self.bind(pos=lambda i, v: setattr(self._bg, 'pos', v),
                  size=lambda i, v: setattr(self._bg, 'size', v))

        title_box = BoxLayout(orientation="vertical", spacing=dp(4), size_hint_y=None)
        title_box.bind(minimum_height=title_box.setter("height"))
        title_box.add_widget(make_wrapped_label(title, 20, title_color, bold=True))
        if subtitle:
            title_box.add_widget(make_wrapped_label(subtitle, 12, subtitle_color, bold=True))

        title_layout = BoxLayout(size_hint_y=None)
        title_layout.bind(minimum_height=title_layout.setter("height"))
        title_layout.add_widget(title_box)
        self.add_widget(title_layout)

        if heart_callback is not None:
            heart_btn = Button(
                text="\u2665" if is_fav else "\u2661",
                font_size=sp(26),
                size_hint=(None, 1),
                width=dp(45),
                background_normal="",
                background_down="",
                background_color=(0, 0, 0, 0),
                color=get_color_from_hex(RED if is_fav else WHITE),
                bold=True,
            )
            heart_btn.bind(on_release=lambda *_: heart_callback(heart_btn))
            self.add_widget(heart_btn)

        if menu_callback:
            menu_btn = Button(
                text="\u22EE", font_size=sp(24), size_hint=(None, 1), width=dp(40),
                background_normal="", background_down="",
                background_color=(0, 0, 0, 0), color=get_color_from_hex(WHITE), bold=True
            )
            menu_btn.bind(on_release=lambda *_: menu_callback(menu_btn))
            self.add_widget(menu_btn)

        def update_header_height(*_):
            self.height = max(dp(90), title_box.height + dp(30))
        title_box.bind(height=update_header_height)


# ================= APP CLASS =================
class JuniorDoctor(App):
    def build(self):
        from kivy.utils import platform
        if platform == 'android':
            try:
                from jnius import autoclass
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                PythonActivity.mActivity.setRequestedOrientation(1)
            except Exception:
                pass

        self.settings = self.load_settings()
        apply_theme(self.settings.get("theme", "light"))
        Window.clearcolor = get_color_from_hex(BG_COLOR)

        self.update_error_message = None
        downloaded_topics = None
        try:
            data_updater.check_for_updates(self.user_data_dir, current_version=1.0)
            self.update_error_message = data_updater.get_error_message(self.user_data_dir)
            downloaded_topics = data_updater.load_downloaded_data(self.user_data_dir)
        except Exception as e:
            print(f"Updater error: {e}")

        if downloaded_topics:
            for spec_name, subs in downloaded_topics.items():
                if spec_name not in DATA:
                    DATA[spec_name] = {}
                for sub_name, topics in subs.items():
                    if sub_name not in DATA[spec_name]:
                        DATA[spec_name][sub_name] = []
                    for topic_name, topic_content in topics.items():
                        if topic_name not in DATA[spec_name][sub_name]:
                            DATA[spec_name][sub_name].insert(0, topic_name)
                        formatted_content = []
                        for item in topic_content:
                            formatted_content.append(tuple(item) if isinstance(item, list) else item)
                        TOPIC_PAGES[(spec_name, topic_name)] = formatted_content

        Window.bind(on_keyboard=self.on_keyboard)
        self.current_back_action = None

        self.sm = ScreenManager(transition=SlideTransition(duration=0.2))
        for name in ("welcome", "disclaimer", "home", "subsystem", "category", "detail",
                     "search", "topic_search", "notes", "note_edit", "settings", "favorites"):
            self.sm.add_widget(Screen(name=name))

        self.nav_bar = self.build_bottom_nav()

        self.main_container = BoxLayout(orientation="vertical", padding=dp(0), spacing=dp(0))
        self.main_container.add_widget(self.sm)
        self.main_container.add_widget(self.nav_bar)

        self.build_home()
        self.build_welcome()
        self.build_disclaimer()
        self.go("welcome")
        return self.main_container

    def build_bottom_nav(self):
        nav = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(70), spacing=dp(0))
        
        with nav.canvas.before:
            Color(*get_color_from_hex(SURFACE))
            nav._bg = RoundedRectangle(pos=nav.pos, size=nav.size, radius=[dp(25), dp(25), 0, 0])
            Color(0, 0, 0, 0.05)
            nav._shadow = RoundedRectangle(pos=(nav.x, nav.y + dp(2)), size=nav.size, radius=[dp(25), dp(25), 0, 0])
            
        nav.bind(pos=lambda i, v: (setattr(i._bg, 'pos', v), setattr(i._shadow, 'pos', (v[0], v[1] + dp(2)))),
                 size=lambda i, v: (setattr(i._bg, 'size', v), setattr(i._shadow, 'size', v)))

        self.nav_buttons = {}
        tabs = [
            ("home", "Home", lambda *_: self.go("home")),
            ("favorites", "Favorites", lambda *_: self.open_favorites()),
            ("notes", "Notes", lambda *_: self.open_notes()),
            ("settings", "Settings", lambda *_: self.open_settings()),
        ]

        for key, text, callback in tabs:
            btn = Button(text=text, background_normal="", background_down="",
                         background_color=(0, 0, 0, 0),
                         color=get_color_from_hex(MUTED),
                         font_size=sp(14), bold=True)
            btn.bind(on_release=callback)
            nav.add_widget(btn)
            self.nav_buttons[key] = btn

        return nav

    def update_nav_colors(self, active_screen):
        for key, btn in self.nav_buttons.items():
            btn.color = get_color_from_hex(BLUE if key == active_screen else MUTED)

    def go(self, name):
        prev = self.sm.current
        self.sm.current = name
        
        if name in ("home", "favorites", "notes", "settings"):
            self.nav_bar.height = dp(70)
            self.nav_bar.opacity = 1
            self.nav_bar.disabled = False
            self.update_nav_colors(name)
        else:
            self.nav_bar.height = 0
            self.nav_bar.opacity = 0
            self.nav_bar.disabled = True

        if name == "home" and prev != "home":
            Clock.schedule_once(lambda dt: self.check_and_show_updates(), 0.5)
            Clock.schedule_once(lambda dt: self.check_and_show_announcement(), 0.8)

    def on_keyboard(self, window, key, scancode, codepoint, modifier):
        if key == 27:
            if self.current_back_action is not None:
                self.current_back_action()
                return True
            return False
        return False

    def contact_developer(self):
        phone = "967774602007"
        text = "Hello Doctor, I would like to share some feedback on the Junior Doctor App."
        url = f"https://wa.me/{phone}?text={text}"
        try:
            webbrowser.open(url)
        except Exception as e:
            print("Could not open browser:", e)

    # ================= WELCOME SCREEN =================
    def build_welcome(self):
        screen = self.sm.get_screen("welcome")
        screen.clear_widgets()
        self.current_back_action = None

        main = BoxLayout(orientation="vertical", padding=[dp(30), dp(30), dp(30), dp(30)], spacing=dp(15))
        draw_card_bg(main, HERO_BG, radius=0, shadow=False)

        main.add_widget(BoxLayout(size_hint_y=0.15))

        icon_row = BoxLayout(size_hint_y=None, height=dp(180))
        icon_row.add_widget(BoxLayout(size_hint_x=0.2))

        icon_box = BoxLayout(size_hint=(None, 1), width=dp(180))
        draw_card_bg(icon_box, BLUE, radius=90, shadow=False)
        icon_box.add_widget(Label(text="\u2695", font_size=sp(100),
                                  color=get_color_from_hex(WHITE), bold=True,
                                  halign="center", valign="middle"))
        icon_row.add_widget(icon_box)
        icon_row.add_widget(BoxLayout(size_hint_x=0.2))
        main.add_widget(icon_row)

        main.add_widget(Label(
            text="Junior Doctor",
            font_size=sp(38), bold=True,
            color=get_color_from_hex(WHITE),
            size_hint_y=None, height=dp(55),
            halign="center", valign="middle",
            text_size=(Window.width - dp(60), None)
        ))
        main.add_widget(Label(
            text="Your Clinical Companion",
            font_size=sp(14), bold=True,
            color=get_color_from_hex("#60A5FA"),
            size_hint_y=None, height=dp(30),
            halign="center", valign="middle"
        ))

        main.add_widget(BoxLayout(size_hint_y=0.3))

        get_started = JDButton("Get Started", bg=BLUE, height=60, radius=30, font_size=18)
        get_started.bind(on_release=lambda *_: self.go("disclaimer"))
        main.add_widget(get_started)

        main.add_widget(BoxLayout(size_hint_y=0.1))

        screen.add_widget(main)

    # ================= DISCLAIMER SCREEN =================
    def build_disclaimer(self):
        screen = self.sm.get_screen("disclaimer")
        screen.clear_widgets()
        self.current_back_action = lambda: self.go("welcome")

        main = BoxLayout(orientation="vertical", padding=dp(0), spacing=dp(0))
        draw_card_bg(main, BG_COLOR, radius=0, shadow=False)

        main.add_widget(ModernHeader("Medical Disclaimer", "PLEASE READ CAREFULLY", bg_color=HEADER_NAVY))

        scroll = ScrollView(do_scroll_x=False)
        content = BoxLayout(orientation="vertical", spacing=dp(15), size_hint_y=None,
                            padding=[dp(20), dp(15), dp(20), dp(30)])
        content.bind(minimum_height=content.setter("height"))

        title_card = Card(bg=CARD_BLUE, padding=20)
        title_card.add_widget(make_wrapped_label("Important Notice", 18, NAVY, bold=True))
        title_card.add_widget(make_wrapped_label(
            "This application is intended for educational and quick-reference purposes only. "
            "It is designed to support — not replace — the clinical judgment of qualified "
            "healthcare professionals.",
            13, TEXT))
        content.add_widget(title_card)

        points_card = Card(bg=CARD_PURPLE, padding=20)
        points_card.add_widget(make_wrapped_label("Key Points", 15, NAVY, bold=True))
        points = [
            "This app does NOT provide medical diagnosis, treatment, or prescription advice.",
            "Dosing information and clinical protocols may vary by region, institution, and patient context. Always verify against local guidelines and the most recent official references before clinical application.",
            "The developers and contributors accept no liability for any clinical decision, action, or outcome resulting from the use of this application.",
            "By proceeding, you confirm that you are a healthcare professional or a medical trainee under supervision.",
        ]
        for p in points:
            row = BoxLayout(size_hint_y=None, spacing=dp(8))
            row.bind(minimum_height=row.setter("height"))
            row.add_widget(Label(text="•", font_size=sp(20), bold=True,
                                 color=get_color_from_hex(BLUE),
                                 size_hint=(None, None), size=(dp(20), dp(20)),
                                 halign="center", valign="top"))
            row.add_widget(make_wrapped_label(p, 13, TEXT))
            points_card.add_widget(row)
        content.add_widget(points_card)

        agree_btn = JDButton("I Understand & Continue", bg=TEAL, height=60, radius=30, font_size=16)
        agree_btn.bind(on_release=lambda *_: self.go("home"))
        content.add_widget(agree_btn)

        scroll.add_widget(content)
        main.add_widget(scroll)
        screen.add_widget(main)

    # ================= SETTINGS =================
    def get_settings_file(self):
        try:
            d = self.user_data_dir
            if not os.path.exists(d):
                os.makedirs(d)
            return os.path.join(d, "settings.json")
        except Exception:
            return os.path.join(os.path.expanduser("~"), "junior_doctor_settings.json")

    def load_settings(self):
        try:
            with open(self.get_settings_file(), 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {"theme": "light"}

    def save_settings(self, settings):
        try:
            with open(self.get_settings_file(), 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving settings: {e}")

    def toggle_dark_mode(self, instance, value):
        new_mode = "dark" if value else "light"
        apply_theme(new_mode)
        Window.clearcolor = get_color_from_hex(BG_COLOR)
        self.settings = self.load_settings()
        self.settings["theme"] = new_mode
        self.save_settings(self.settings)
        self.refresh_theme_ui()

    def refresh_theme_ui(self):
        cur = self.sm.current
        if cur == "home":
            self.build_home()
        elif cur == "settings":
            self.open_settings()
        elif cur == "notes":
            self.open_notes()
        elif cur == "favorites":
            self.open_favorites()
        elif cur == "search":
            self.open_search("")
        else:
            self.go("home")

    def show_message_popup(self, title, message):
        try:
            content = BoxLayout(orientation="vertical", padding=dp(15), spacing=dp(12))
            content.add_widget(make_wrapped_label(message, 14, TEXT))
            btn = JDButton("OK", bg=BLUE, height=45, radius=12, font_size=14)
            content.add_widget(btn)
            popup = Popup(title=title, content=content, size_hint=(0.9, 0.45),
                          background_color=get_color_from_hex(SURFACE),
                          title_color=get_color_from_hex(NAVY))
            btn.bind(on_release=lambda *_: popup.dismiss())
            popup.open()
        except Exception as e:
            print(f"Popup error: {e}")

    # ================= ANNOUNCEMENTS =================
    def get_announcement_file(self):
        try:
            d = self.user_data_dir
            if not os.path.exists(d):
                os.makedirs(d)
            return os.path.join(d, "last_announcement.txt")
        except Exception:
            return os.path.join(os.path.expanduser("~"), "last_announcement.txt")

    def check_and_show_announcement(self, force=False):
        try:
            if "App Announcements" in DATA and "General" in DATA["App Announcements"]:
                topics = DATA["App Announcements"]["General"]
                if topics:
                    latest_topic = topics[0]
                    pages = TOPIC_PAGES.get(("App Announcements", latest_topic), [])
                    if pages:
                        message = ""
                        image_url = ""
                        for page in pages:
                            if len(page) >= 2 and page[1] == "image":
                                image_url = page[2]
                            else:
                                msg_part = page[2] if len(page) == 3 else page[1]
                                message += msg_part + "\n\n"
                        
                        message = message.strip()
                        ann_file = self.get_announcement_file()
                        last_shown = ""
                        if os.path.exists(ann_file):
                            with open(ann_file, 'r', encoding='utf-8') as f:
                                last_shown = f.read().strip()
                                
                        current_hash = message + image_url
                        if force or last_shown != current_hash:
                            self.show_announcement_popup("App Announcement", message, image_url)
                            with open(ann_file, 'w', encoding='utf-8') as f:
                                f.write(current_hash)
        except Exception as e:
            print(f"Announcement error: {e}")

    def show_announcement_popup(self, title, message, image_url=""):
        try:
            content = BoxLayout(orientation="vertical", padding=dp(15), spacing=dp(10))
            
            content.add_widget(make_wrapped_label(title, 16, "#2DD4BF", bold=True))
            
            scroll = ScrollView()
            list_layout = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(10))
            list_layout.bind(minimum_height=list_layout.setter("height"))
            
            if image_url:
                img = AsyncImage(source=image_url, size_hint_y=None, height=dp(200))
                list_layout.add_widget(img)
                
            if message:
                list_layout.add_widget(make_markup_label(message, 14, "#FFFFFF"))
                
            scroll.add_widget(list_layout)
            content.add_widget(scroll)
            
            btn = JDButton("Got it!", bg=BLUE, height=45, radius=12, font_size=14)
            content.add_widget(btn)
            
            popup = Popup(title="Notice", content=content, size_hint=(0.9, 0.7),
                          background_color=get_color_from_hex("#0F172A"), title_color=get_color_from_hex("#FFFFFF"))
            btn.bind(on_release=lambda *_: popup.dismiss())
            popup.open()
        except Exception as e:
            print(f"Popup error: {e}")

    # ================= WHAT'S NEW POPUP =================
    def check_and_show_updates(self):
        try:
            updates = data_updater.get_latest_updates(self.user_data_dir)
            if updates and updates.get("topics"):
                self.show_whats_new_popup(updates)
                file_path = os.path.join(self.user_data_dir, "latest_updates.json")
                if os.path.exists(file_path):
                    os.remove(file_path)
        except Exception as e:
            print(f"Error checking updates: {e}")

    def _find_topic_location(self, topic_name):
        for spec, subsystems in DATA.items():
            for sub, topics in subsystems.items():
                if topic_name in topics:
                    return (spec, sub)
        return (None, None)

    def show_whats_new_popup(self, updates_data):
        try:
            topics = updates_data.get("topics", [])
            if not topics:
                return

            new_topics = []
            updated_topics = []
            
            for t in topics:
                clean_t = t.replace("✨", "").replace("🔄", "").strip()
                
                if "Current Notice" in clean_t or "App Announcement" in clean_t:
                    continue

                if "NEW:" in clean_t:
                    new_topics.append(clean_t.replace("NEW:", "").strip())
                elif "UPDATED:" in clean_t:
                    updated_topics.append(clean_t.replace("UPDATED:", "").strip())
                else:
                    new_topics.append(clean_t)

            if not new_topics and not updated_topics:
                return

            content = BoxLayout(orientation="vertical", padding=dp(15), spacing=dp(10))
            content.add_widget(make_wrapped_label("New & updated topics", 18, "#2DD4BF", bold=True))
            
            scroll = ScrollView()
            list_layout = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(10))
            list_layout.bind(minimum_height=list_layout.setter("height"))

            popup_holder = {"popup": None}

            def open_topic_and_close(topic_name):
                spec, _ = self._find_topic_location(topic_name)
                if spec:
                    if popup_holder["popup"]:
                        try:
                            popup_holder["popup"].dismiss()
                        except Exception:
                            pass
                    self.open_detail(spec, topic_name)

            def make_topic_row(topic_name, icon):
                row = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(4))
                row.bind(minimum_height=row.setter("height"))
                row.add_widget(make_wrapped_label(f"{icon} {topic_name}", 14, "#FFFFFF"))
                spec, _ = self._find_topic_location(topic_name)
                if spec:
                    view_btn = JDButton("View Topic", bg=TEAL, height=38, radius=10, font_size=13)
                    view_btn.bind(on_release=lambda _, t=topic_name: open_topic_and_close(t))
                    row.add_widget(view_btn)
                return row

            if new_topics:
                list_layout.add_widget(make_wrapped_label("✨ New Topics", 13, "#2DD4BF", bold=True))
                for t in new_topics:
                    list_layout.add_widget(make_topic_row(t, "✨"))

            if updated_topics:
                list_layout.add_widget(make_wrapped_label("🔄 Updated Topics", 13, "#60A5FA", bold=True))
                for t in updated_topics:
                    list_layout.add_widget(make_topic_row(t, "🔄"))
                
            scroll.add_widget(list_layout)
            content.add_widget(scroll)
            
            btn = JDButton("Got it!", bg=BLUE, height=45, radius=12, font_size=14)
            content.add_widget(btn)
            
            popup = Popup(title="Update Alert", content=content, size_hint=(0.9, 0.65),
                          background_color=get_color_from_hex("#0F172A"), title_color=get_color_from_hex("#FFFFFF"))
            popup_holder["popup"] = popup
            btn.bind(on_release=lambda *_: popup.dismiss())
            popup.open()
        except Exception as e:
            print(f"Popup error: {e}")

    def open_settings(self):
        screen = self.sm.get_screen("settings")
        screen.clear_widgets()
        main_layout = BoxLayout(orientation="vertical", padding=dp(0), spacing=dp(0))
        self.current_back_action = lambda: self.go("home")
        main_layout.add_widget(ModernHeader("Settings", "APP SETTINGS", bg_color=HEADER_NAVY))

        scroll = ScrollView(do_scroll_x=False)
        content = BoxLayout(orientation="vertical", spacing=dp(15), size_hint_y=None,
                            padding=[dp(20), dp(10), dp(20), dp(20)])
        content.bind(minimum_height=content.setter("height"))

        theme_card = Card(bg=CARD_BLUE, padding=15)
        theme_row = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
        theme_row.add_widget(make_wrapped_label("Dark Mode", 16, NAVY, bold=True))
        sw = Switch(active=is_dark_mode())
        sw.bind(active=self.toggle_dark_mode)
        theme_row.add_widget(sw)
        theme_card.add_widget(theme_row)
        theme_card.add_widget(make_wrapped_label("Switch between light and dark themes.", 12, MUTED))
        content.add_widget(theme_card)

        ann_card = Card(bg=CARD_PURPLE, padding=15)
        ann_card.add_widget(make_wrapped_label("Latest Announcement", 14, NAVY, bold=True))
        ann_card.add_widget(make_wrapped_label("View the latest medical tip or app announcement.", 12, TEXT))
        ann_btn = JDButton("View Announcement", bg=VIOLET, height=48, radius=12, font_size=14)
        ann_btn.bind(on_release=lambda *_: self.check_and_show_announcement(force=True))
        ann_card.add_widget(ann_btn)
        content.add_widget(ann_card)

        contact_card = Card(bg=CARD_GREEN, padding=15)
        contact_card.add_widget(make_wrapped_label("Feedback & Support", 14, NAVY, bold=True))
        contact_card.add_widget(make_wrapped_label("Have a suggestion or found a bug? Contact us on WhatsApp.", 12, TEXT))
        contact_btn = JDButton("Contact via WhatsApp", bg=TEAL, height=48, radius=12, font_size=14)
        contact_btn.bind(on_release=lambda *_: self.contact_developer())
        contact_card.add_widget(contact_btn)
        content.add_widget(contact_card)

        about_card = Card(bg=CARD_PURPLE, padding=15)
        about_card.add_widget(make_wrapped_label("About", 14, NAVY, bold=True))
        about_card.add_widget(make_wrapped_label("Junior Doctor v1.0", 13, TEXT, bold=True))
        about_card.add_widget(make_wrapped_label("Clinical reference for junior doctors and medical students.", 12, MUTED))
        content.add_widget(about_card)

        clear_btn = JDButton("Clear All Favorites", bg=RED, height=50, radius=14, font_size=14)
        clear_btn.bind(on_release=lambda *_: self.clear_all_favorites())
        content.add_widget(clear_btn)

        scroll.add_widget(content)
        main_layout.add_widget(scroll)
        screen.add_widget(main_layout)
        self.go("settings")

    def clear_all_favorites(self):
        self.save_favorites([])
        self.show_message_popup("Favorites", "All favorites have been cleared.")

    # ================= FAVORITES =================
    def get_favorites_file(self):
        try:
            d = self.user_data_dir
            if not os.path.exists(d):
                os.makedirs(d)
            return os.path.join(d, "favorites.json")
        except Exception:
            return os.path.join(os.path.expanduser("~"), "junior_doctor_favorites.json")

    def load_favorites(self):
        try:
            with open(self.get_favorites_file(), 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return []

    def save_favorites(self, favs):
        try:
            with open(self.get_favorites_file(), 'w', encoding='utf-8') as f:
                json.dump(favs, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving favorites: {e}")

    def is_favorite(self, spec, topic):
        return [spec, topic] in self.load_favorites()

    def toggle_favorite(self, spec, topic):
        favs = self.load_favorites()
        key = [spec, topic]
        if key in favs:
            favs.remove(key)
        else:
            favs.append(key)
        self.save_favorites(favs)

    def toggle_favorite_ui(self, spec, topic):
        self.toggle_favorite(spec, topic)
        self.open_detail(spec, topic)

    def remove_favorite_and_refresh(self, spec, topic):
        self.toggle_favorite(spec, topic)
        self.open_favorites()

    def open_favorites(self):
        screen = self.sm.get_screen("favorites")
        screen.clear_widgets()
        main_layout = BoxLayout(orientation="vertical", padding=dp(0), spacing=dp(0))
        self.current_back_action = lambda: self.go("home")
        main_layout.add_widget(ModernHeader("Favorites", "SAVED TOPICS", bg_color=HEADER_NAVY))

        scroll = ScrollView(do_scroll_x=False)
        content = BoxLayout(orientation="vertical", spacing=dp(12), size_hint_y=None,
                            padding=[dp(20), dp(10), dp(20), dp(20)])
        content.bind(minimum_height=content.setter("height"))

        favs = self.load_favorites()
        if not favs:
            card = Card(bg=CARD_BLUE, padding=20)
            card.add_widget(make_wrapped_label("No favorites yet.", 16, NAVY, bold=True))
            card.add_widget(make_wrapped_label("Tap the heart icon on any topic to add it here.", 13, MUTED))
            content.add_widget(card)
        else:
            for spec, topic in favs:
                card = Card(bg=CARD_GREEN, padding=15)
                card.add_widget(make_wrapped_label(topic, 15, NAVY, bold=True))
                card.add_widget(make_wrapped_label(spec, 12, TEAL, bold=True))
                row = BoxLayout(size_hint_y=None, height=dp(42), spacing=dp(8))
                open_btn = JDButton("Open", bg=BLUE, height=42, radius=12, font_size=13)
                open_btn.bind(on_release=lambda _, s=spec, t=topic: self.open_detail(s, t))
                row.add_widget(open_btn)
                del_btn = JDButton("Remove", bg=RED, height=42, radius=12, font_size=13)
                del_btn.bind(on_release=lambda _, s=spec, t=topic: self.remove_favorite_and_refresh(s, t))
                row.add_widget(del_btn)
                card.add_widget(row)
                content.add_widget(card)

        scroll.add_widget(content)
        main_layout.add_widget(scroll)
        screen.add_widget(main_layout)
        self.go("favorites")

    # ================= NOTES =================
    def get_notes_file(self):
        try:
            d = self.user_data_dir
            if not os.path.exists(d):
                os.makedirs(d)
            return os.path.join(d, "notes.json")
        except Exception:
            return os.path.join(os.path.expanduser("~"), "junior_doctor_notes.json")

    def load_notes(self):
        try:
            with open(self.get_notes_file(), 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return []

    def save_notes(self, notes):
        try:
            with open(self.get_notes_file(), 'w', encoding='utf-8') as f:
                json.dump(notes, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving notes: {e}")

    def delete_note(self, index):
        notes = self.load_notes()
        if 0 <= index < len(notes):
            notes.pop(index)
            self.save_notes(notes)
        self.open_notes()

    def export_notes(self):
        notes = self.load_notes()
        if not notes:
            self.show_message_popup("Export Notes", "No notes to export.")
            return
        lines = ["=" * 50, "JUNIOR DOCTOR — MY NOTES", "=" * 50, ""]
        for i, note in enumerate(notes, 1):
            lines.append(f"--- Note {i} ---")
            lines.append(f"Title: {note.get('title', 'Untitled')}")
            lines.append(f"Date:  {note.get('date', '')}")
            lines.append("")
            lines.append(note.get("content", ""))
            lines.append("")
        text = "\n".join(lines)

        export_path = ""
        try:
            export_path = os.path.join(self.user_data_dir, "notes_export.txt")
            with open(export_path, 'w', encoding='utf-8') as f:
                f.write(text)
        except Exception as e:
            export_path = f"(failed: {e})"

        copied = False
        try:
            Clipboard.copy(text)
            copied = True
        except Exception:
            pass

        msg = "Notes exported."
        if copied:
            msg += "\n\nCopied to clipboard."
        msg += f"\n\nSaved to:\n{export_path}"
        self.show_message_popup("Export Notes", msg)

    def open_notes(self):
        screen = self.sm.get_screen("notes")
        screen.clear_widgets()
        main_layout = BoxLayout(orientation="vertical", padding=dp(0), spacing=dp(0))
        self.current_back_action = lambda: self.go("home")
        main_layout.add_widget(ModernHeader("My Notes", "PERSONAL CLINICAL NOTES", bg_color=HEADER_NAVY))

        scroll = ScrollView(do_scroll_x=False)
        content = BoxLayout(orientation="vertical", spacing=dp(12), size_hint_y=None,
                            padding=[dp(20), dp(10), dp(20), dp(20)])
        content.bind(minimum_height=content.setter("height"))

        add_btn = JDButton("+  Add New Note", bg=TEAL, height=52, radius=16, font_size=15)
        add_btn.bind(on_release=lambda *_: self.open_note_editor(-1))
        content.add_widget(add_btn)

        notes = self.load_notes()
        if notes:
            export_btn = JDButton("Export All Notes", bg=BLUE, height=48, radius=14, font_size=14)
            export_btn.bind(on_release=lambda *_: self.export_notes())
            content.add_widget(export_btn)

        if not notes:
            card = Card(bg=CARD_BLUE, padding=20)
            card.add_widget(make_wrapped_label("No notes yet.", 16, NAVY, bold=True))
            card.add_widget(make_wrapped_label("Tap '+ Add New Note' to create your first note.", 13, MUTED))
            content.add_widget(card)
        else:
            for i, note in enumerate(reversed(notes)):
                idx = len(notes) - 1 - i
                card = Card(bg=CARD_PURPLE, padding=15)
                title = note.get("title", "") or "Untitled Note"
                body = note.get("content", "") or ""
                preview = body[:100] + ("..." if len(body) > 100 else "")
                card.add_widget(make_wrapped_label(title, 15, NAVY, bold=True))
                if preview:
                    card.add_widget(make_wrapped_label(preview, 12, MUTED))
                card.add_widget(make_wrapped_label(note.get("date", ""), 11, MUTED, bold=True))
                row = BoxLayout(size_hint_y=None, height=dp(42), spacing=dp(8))
                edit_btn = JDButton("Edit", bg=BLUE, height=42, radius=12, font_size=13)
                edit_btn.bind(on_release=lambda _, ix=idx: self.open_note_editor(ix))
                row.add_widget(edit_btn)
                del_btn = JDButton("Delete", bg=RED, height=42, radius=12, font_size=13)
                del_btn.bind(on_release=lambda _, ix=idx: self.delete_note(ix))
                row.add_widget(del_btn)
                card.add_widget(row)
                content.add_widget(card)

        scroll.add_widget(content)
        main_layout.add_widget(scroll)
        screen.add_widget(main_layout)
        self.go("notes")

    def open_note_editor(self, note_index):
        screen = self.sm.get_screen("note_edit")
        screen.clear_widgets()
        main_layout = BoxLayout(orientation="vertical", padding=dp(0), spacing=dp(0))
        self.current_back_action = lambda: self.open_notes()
        notes = self.load_notes()
        is_new = (note_index == -1)
        note = {"title": "", "content": "", "date": ""} if is_new else notes[note_index]
        title_text = "New Note" if is_new else "Edit Note"
        main_layout.add_widget(ModernHeader(title_text, "PERSONAL NOTES", bg_color=HEADER_NAVY))

        scroll = ScrollView(do_scroll_x=False)
        content = BoxLayout(orientation="vertical", spacing=dp(15), size_hint_y=None,
                            padding=[dp(20), dp(10), dp(20), dp(20)])
        content.bind(minimum_height=content.setter("height"))

        title_card = Card(bg=CARD_BLUE, padding=15)
        title_card.add_widget(make_wrapped_label("Title", 14, NAVY, bold=True))
        title_input = TextInput(text=note.get("title", ""), hint_text="Note title...",
                                multiline=False, font_size=sp(15), size_hint_y=None, height=dp(45),
                                background_color=get_color_from_hex(INPUT_BG),
                                foreground_color=get_color_from_hex(TEXT),
                                cursor_color=get_color_from_hex(BLUE),
                                padding=[dp(10), dp(10), dp(10), dp(10)])
        title_card.add_widget(title_input)
        content.add_widget(title_card)

        body_card = Card(bg=CARD_PURPLE, padding=15)
        body_card.add_widget(make_wrapped_label("Content", 14, NAVY, bold=True))
        body_input = TextInput(text=note.get("content", ""), hint_text="Write your note here...",
                               multiline=True, font_size=sp(14), size_hint_y=None, height=dp(300),
                               background_color=get_color_from_hex(INPUT_BG),
                               foreground_color=get_color_from_hex(TEXT),
                               cursor_color=get_color_from_hex(BLUE),
                               padding=[dp(10), dp(10), dp(10), dp(10)])
        body_card.add_widget(body_input)
        content.add_widget(body_card)

        def do_save(*_):
            all_notes = self.load_notes()
            new_note = {
                "title": title_input.text.strip() or "Untitled Note",
                "content": body_input.text.strip(),
                "date": datetime.datetime.now().strftime("%Y-%m-%d  %H:%M")
            }
            if is_new:
                all_notes.append(new_note)
            else:
                all_notes[note_index] = new_note
            self.save_notes(all_notes)
            self.open_notes()

        save_btn = JDButton("SAVE NOTE", bg=TEAL, height=52, radius=16, font_size=15)
        save_btn.bind(on_release=do_save)
        content.add_widget(save_btn)

        scroll.add_widget(content)
        main_layout.add_widget(scroll)
        screen.add_widget(main_layout)
        self.go("note_edit")

    # ================= HOME =================
    def build_home(self):
        screen = self.sm.get_screen("home")
        screen.clear_widgets()
        
        main_layout = BoxLayout(orientation="vertical", padding=dp(0), spacing=dp(0))
        self.current_back_action = None
        main_layout.add_widget(ModernHeader("Junior Doctor", "CLINICAL REFERENCE", bg_color=HEADER_NAVY))

        scroll = ScrollView(do_scroll_x=False)
        content = BoxLayout(orientation="vertical", spacing=dp(20), size_hint_y=None,
                            padding=[dp(20), dp(0), dp(20), dp(20)])
        content.bind(minimum_height=content.setter("height"))

        search_box = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(65), padding=[dp(15), dp(10)])
        draw_card_bg(search_box, WHITE, radius=20, shadow=True)
        search_input = TextInput(hint_text="Search topic titles only...", multiline=False,
                                 font_size=sp(14), background_normal="", background_active="",
                                 background_color=(0, 0, 0, 0),
                                 foreground_color=get_color_from_hex(TEXT),
                                 cursor_color=get_color_from_hex(BLUE),
                                 hint_text_color=get_color_from_hex(MUTED),
                                 padding=[dp(10), 0, dp(10), 0])
        search_input.bind(on_text_validate=lambda i: self.open_search(i.text))
        search_box.add_widget(search_input)
        content.add_widget(search_box)

        if hasattr(self, 'update_error_message') and self.update_error_message:
            err_card = Card(bg="#FEF2F2", padding=10, radius=10)
            err_card.add_widget(make_wrapped_label("UPDATE DEBUG INFO:", 12, RED, bold=True))
            err_card.add_widget(make_wrapped_label(self.update_error_message, 11, RED))
            content.add_widget(err_card)

        hero = BoxLayout(orientation="vertical", size_hint_y=None, height=dp(140))
        draw_card_bg(hero, HERO_BG, radius=28)
        with hero.canvas.after:
            Color(1, 1, 1, 0.05)
            hero._circle1 = Ellipse(pos=(hero.x + dp(200), hero.y + dp(20)), size=(dp(150), dp(150)))
            Color(1, 1, 1, 0.03)
            hero._circle2 = Ellipse(pos=(hero.x + dp(250), hero.y - dp(30)), size=(dp(100), dp(100)))
        def update_hero(*_):
            hero._circle1.pos = (hero.x + hero.width - dp(100), hero.y + dp(20))
            hero._circle2.pos = (hero.x + hero.width - dp(50), hero.y - dp(30))
        hero.bind(pos=update_hero, size=update_hero)

        hero_text = BoxLayout(orientation="vertical", padding=[dp(20), dp(20)], spacing=dp(5))
        hero_text.add_widget(Label(text="WELCOME, DOCTOR", font_size=sp(12),
                                   color=get_color_from_hex("#60A5FA"), bold=True,
                                   halign="left", text_size=(None, None)))
        hero_text.add_widget(Label(text="Your clinical\ncompanion.", font_size=sp(28),
                                   color=get_color_from_hex(WHITE), bold=True,
                                   halign="left", valign="top", text_size=(None, None)))
        hero.add_widget(hero_text)
        content.add_widget(hero)

        content.add_widget(Label(text="EXPLORE SPECIALTIES", font_size=sp(14),
                                 color=get_color_from_hex(MUTED), bold=True,
                                 size_hint_y=None, height=dp(30), halign="left"))

        for specialty, subsystems in DATA.items():
            if specialty == "App Announcements":
                continue

            num_topics = sum(len(topics) for topics in subsystems.values())
            cat_card = BoxLayout(orientation="vertical", size_hint_y=None, height=dp(120),
                                 padding=dp(15), spacing=dp(10))
            draw_card_bg(cat_card, CARD_BLUE, radius=24)
            
            title_box = BoxLayout(orientation="vertical")
            title_box.add_widget(make_wrapped_label(specialty, 16, NAVY, bold=True))
            title_box.add_widget(make_wrapped_label(f"{num_topics} Topics Available", 13, TEAL, bold=True))
            cat_card.add_widget(title_box)
            
            btn = JDButton("View Section", bg=BLUE, height=42, font_size=13, radius=12)
            btn.bind(on_release=lambda _, s=specialty: self.open_specialty(s))
            cat_card.add_widget(btn)
            content.add_widget(cat_card)

        scroll.add_widget(content)
        main_layout.add_widget(scroll)
        screen.add_widget(main_layout)
            # ================= SEARCH (Global - Titles Only) =================
    def open_search(self, query=""):
        screen = self.sm.get_screen("search")
        screen.clear_widgets()
        main_layout = BoxLayout(orientation="vertical", padding=dp(0), spacing=dp(0))
        self.current_back_action = lambda: self.go("home")
        main_layout.add_widget(ModernHeader("Search Topics", "GLOBAL SEARCH", bg_color=HEADER_NAVY))

        search_box = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(65), padding=[dp(15), dp(10)])
        draw_card_bg(search_box, WHITE, radius=20, shadow=True)
        search_input = TextInput(text=query, hint_text="Search topic titles...",
                                 multiline=False, font_size=sp(14),
                                 background_normal="", background_active="",
                                 background_color=(0, 0, 0, 0),
                                 foreground_color=get_color_from_hex(TEXT),
                                 cursor_color=get_color_from_hex(BLUE),
                                 hint_text_color=get_color_from_hex(MUTED),
                                 padding=[dp(10), 0, dp(10), 0])
        search_box.add_widget(search_input)

        scroll = ScrollView(do_scroll_x=False)
        results = BoxLayout(orientation="vertical", spacing=dp(12), size_hint_y=None,
                            padding=[dp(20), dp(15)])
        results.bind(minimum_height=results.setter("height"))
        scroll.add_widget(results)

        main_layout.add_widget(search_box)
        main_layout.add_widget(scroll)

        def perform_search(q):
            results.clear_widgets()
            q = q.lower().strip()
            if not q:
                results.add_widget(make_wrapped_label(
                    "Type a topic title to search.",
                    13, MUTED))
                return
            matches = []
            for specialty, subsystems in DATA.items():
                for subsystem, topics in subsystems.items():
                    for topic in topics:
                        if q in topic.lower():
                            matches.append((specialty, subsystem, topic, "Title"))
            
            if not matches:
                results.add_widget(make_wrapped_label(f"No topics found for '{q}'.", 14, RED, bold=True))
                return
            results.add_widget(make_wrapped_label(f"{len(matches)} topic(s) found",
                                                  12, MUTED, bold=True))
            for spec, sub, topic, mtype in matches:
                card = Card(bg=CARD_BLUE, padding=15)
                card.add_widget(make_wrapped_label(topic, 15, NAVY, bold=True))
                card.add_widget(make_wrapped_label(f"{spec} > {sub}", 12, TEAL, bold=True))
                btn = JDButton("Read Topic", bg=BLUE, height=38, radius=10, font_size=13)
                btn.bind(on_release=lambda _, s=spec, t=topic: self.open_detail(s, t))
                card.add_widget(btn)
                results.add_widget(card)

        search_input.bind(text=lambda _, v: perform_search(v))
        if query:
            perform_search(query)
        else:
            perform_search("")

        screen.add_widget(main_layout)
        self.go("search")
        Clock.schedule_once(lambda dt: setattr(search_input, 'focus', True), 0.3)

    # ================= TOPIC SEARCH (Inside a specific topic) =================
    def open_topic_search(self, specialty, topic):
        screen = self.sm.get_screen("topic_search")
        screen.clear_widgets()
        main_layout = BoxLayout(orientation="vertical", padding=dp(0), spacing=dp(0))
        self.current_back_action = lambda: self.open_detail(specialty, topic)

        def on_heart_ts(btn):
            self.toggle_favorite(specialty, topic)
            fav = self.is_favorite(specialty, topic)
            btn.text = "\u2665" if fav else "\u2661"
            btn.color = get_color_from_hex(RED if fav else WHITE)

        main_layout.add_widget(ModernHeader(
            "Search in Topic", topic.upper()[:30],
            bg_color=HEADER_NAVY,
            heart_callback=on_heart_ts,
            is_fav=self.is_favorite(specialty, topic)
        ))

        top_area = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(10), padding=[dp(20), dp(10), dp(20), dp(10)])
        top_area.bind(minimum_height=top_area.setter("height"))

        search_container = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(60), spacing=dp(10))
        
        search_box = BoxLayout(orientation="horizontal", size_hint=(1, 1))
        draw_card_bg(search_box, WHITE, radius=20, shadow=True)
        search_input = TextInput(hint_text="Type to highlight matches...", multiline=False,
                                 font_size=sp(14), background_normal="", background_active="",
                                 background_color=(0, 0, 0, 0),
                                 foreground_color=get_color_from_hex(TEXT),
                                 cursor_color=get_color_from_hex(BLUE),
                                 hint_text_color=get_color_from_hex(MUTED),
                                 padding=[dp(10), 0, dp(10), 0])
        search_box.add_widget(search_input)
        search_container.add_widget(search_box)

        btn_prev = JDButton("▲", bg=INFO_BAR, height=55, radius=12, font_size=16, size_hint=(None, 1), width=dp(50))
        btn_prev.disabled = True
        btn_prev.opacity = 0.5
        search_container.add_widget(btn_prev)

        btn_next = JDButton("▼", bg=INFO_BAR, height=55, radius=12, font_size=16, size_hint=(None, 1), width=dp(50))
        btn_next.disabled = True
        btn_next.opacity = 0.5
        search_container.add_widget(btn_next)

        top_area.add_widget(search_container)

        scroll = ScrollView(do_scroll_x=False)
        results = BoxLayout(orientation="vertical", spacing=dp(12), size_hint_y=None, padding=[dp(20), dp(10), dp(20), dp(20)])
        results.bind(minimum_height=results.setter("height"))
        scroll.add_widget(results)

        main_layout.add_widget(top_area)
        main_layout.add_widget(scroll)

        sections = TOPIC_PAGES.get((specialty, topic), [])
        self.topic_match_widgets = []
        self.current_match_idx = 0

        def render_section(item, q=""):
            heading = item[0]
            scheme = item[1]
            body = item[2] if len(item) == 3 else item[1]
            h_upper = heading.upper()

            if q:
                h_display = highlight_text(h_upper, q)
                b_display = highlight_text(body, q)
            else:
                h_display = h_upper
                b_display = body

            if scheme == "danger" or any(w in h_upper for w in ("WARNING", "DON'T MISS", "CONTRAINDICATION")):
                bg, bar_color, title_color = DANGER_BG, DANGER_BAR, RED
            elif scheme == "success" or any(w in h_upper for w in ("DOSE", "TREATMENT", "MANAGEMENT",
                                                                   "ADMINISTER", "PREPARE", "MONITORING",
                                                                   "IMMEDIATE ACTIONS", "FLUID")):
                bg, bar_color, title_color = SUCCESS_BG, SUCCESS_BAR, TEAL
            else:
                bg, bar_color, title_color = INFO_BG, INFO_BAR, NAVY

            cc = BoxLayout(orientation="horizontal", size_hint_y=None, spacing=0)
            cc.bind(minimum_height=cc.setter("height"))

            side_bar = BoxLayout(size_hint_x=None, width=dp(8))
            draw_card_bg(side_bar, bar_color, radius=24, shadow=True, is_bar=True)
            cc.add_widget(side_bar)

            body_card = Card(bg=bg, padding=20, radius=24)
            body_card.add_widget(make_wrapped_label(h_display, 13, title_color, bold=True))
            body_card.add_widget(make_markup_label(b_display, 13, TEXT))
            cc.add_widget(body_card)
            return cc

        def perform_topic_search(q):
            results.clear_widgets()
            self.topic_match_widgets = []
            self.current_match_idx = 0
            q_lower = q.lower().strip()

            if not q_lower:
                btn_prev.disabled = True
                btn_prev.opacity = 0.5
                btn_next.disabled = True
                btn_next.opacity = 0.5
                for item in sections:
                    results.add_widget(render_section(item, ""))
                return

            match_count = 0
            for item in sections:
                heading = item[0]
                body = item[2] if len(item) == 3 else item[1]
                
                if q_lower in heading.lower() or q_lower in str(body).lower():
                    match_count += 1
                    cc = render_section(item, q_lower)
                    results.add_widget(cc)
                    self.topic_match_widgets.append(cc)

            if match_count == 0:
                results.add_widget(make_wrapped_label(f"No matches for '{q}' in this topic.", 14, RED, bold=True))
                btn_prev.disabled = True
                btn_prev.opacity = 0.5
                btn_next.disabled = True
                btn_next.opacity = 0.5
            else:
                btn_prev.disabled = False
                btn_prev.opacity = 1
                btn_next.disabled = False
                btn_next.opacity = 1
                results.add_widget(make_wrapped_label(f"{match_count} section(s) found.", 12, MUTED, bold=True))

        def go_to_prev_match(*_):
            if not self.topic_match_widgets:
                return
            self.current_match_idx -= 1
            if self.current_match_idx < 0:
                self.current_match_idx = len(self.topic_match_widgets) - 1
            
            target_widget = self.topic_match_widgets[self.current_match_idx]
            Clock.schedule_once(lambda dt: scroll.scroll_to(target_widget, padding=dp(20)), 0.1)

        def go_to_next_match(*_):
            if not self.topic_match_widgets:
                return
            self.current_match_idx += 1
            if self.current_match_idx >= len(self.topic_match_widgets):
                self.current_match_idx = 0
            
            target_widget = self.topic_match_widgets[self.current_match_idx]
            Clock.schedule_once(lambda dt: scroll.scroll_to(target_widget, padding=dp(20)), 0.1)

        btn_prev.bind(on_release=go_to_prev_match)
        btn_next.bind(on_release=go_to_next_match)
        
        search_input.bind(text=lambda _, v: perform_topic_search(v))
        perform_topic_search("")

        screen.add_widget(main_layout)
        self.go("topic_search")
        Clock.schedule_once(lambda dt: setattr(search_input, 'focus', True), 0.3)

    # ================= NAVIGATION =================
    def open_specialty(self, specialty):
        subsystems = DATA[specialty]
        if len(subsystems) == 1 and "General" in subsystems:
            self.open_category(specialty, "General")
            return

        screen = self.sm.get_screen("subsystem")
        screen.clear_widgets()
        main_layout = BoxLayout(orientation="vertical", padding=dp(0), spacing=dp(0))
        self.current_back_action = lambda: self.go("home")
        main_layout.add_widget(ModernHeader(specialty, "Select a Subsystem", bg_color=HEADER_BLUE))

        scroll = ScrollView(do_scroll_x=False)
        content = BoxLayout(orientation="vertical", spacing=dp(15), size_hint_y=None,
                            padding=[dp(20), dp(10)])
        content.bind(minimum_height=content.setter("height"))

        for subsystem, topics in subsystems.items():
            card = Card(bg=CARD_GREEN, padding=20)
            card.add_widget(make_wrapped_label(subsystem, 16, NAVY, bold=True))
            card.add_widget(make_wrapped_label(f"{len(topics)} Topics available", 13, MUTED))
            btn = JDButton("View Topics", bg=BLUE, height=42, radius=12, font_size=14)
            btn.bind(on_release=lambda _, s=specialty, sub=subsystem: self.open_category(s, sub))
            card.add_widget(btn)
            content.add_widget(card)

        scroll.add_widget(content)
        main_layout.add_widget(scroll)
        screen.add_widget(main_layout)
        self.go("subsystem")

    def open_category(self, specialty, subsystem):
        screen = self.sm.get_screen("category")
        screen.clear_widgets()
        main_layout = BoxLayout(orientation="vertical", padding=dp(0), spacing=dp(0))
        if len(DATA[specialty]) > 1:
            self.current_back_action = lambda: self.open_specialty(specialty)
        else:
            self.current_back_action = lambda: self.go("home")

        title_text = subsystem if subsystem != "General" else specialty
        main_layout.add_widget(ModernHeader(title_text, "Select a Topic", bg_color=HEADER_BLUE))

        scroll = ScrollView(do_scroll_x=False)
        content = BoxLayout(orientation="vertical", spacing=dp(12), size_hint_y=None,
                            padding=[dp(20), dp(10)])
        content.bind(minimum_height=content.setter("height"))

        if not DATA[specialty][subsystem]:
            card = Card(bg=CARD_BLUE, padding=20)
            card.add_widget(make_wrapped_label("No topics available yet.", 16, NAVY, bold=True))
            card.add_widget(make_wrapped_label("Please check back later for updates.", 13, MUTED))
            content.add_widget(card)
        else:
            for i, topic in enumerate(DATA[specialty][subsystem], start=1):
                card = Card(bg=CARD_PURPLE, padding=15)
                row = BoxLayout(size_hint_y=None, height=dp(35))
                
                num_badge = Card(bg=WHITE, radius=8, padding=[dp(8), dp(2)],
                                 size_hint=(None, None), size=(dp(32), dp(28)))
                num_badge.add_widget(Label(text=str(i).zfill(2), font_size=sp(13),
                                           color=get_color_from_hex(BLUE), bold=True))
                row.add_widget(num_badge)
                
                title_box = BoxLayout(padding=[dp(10), 0])
                title_box.add_widget(make_wrapped_label(topic, 15, NAVY, bold=True))
                row.add_widget(title_box)
                card.add_widget(row)
                
                btn = JDButton("Read Topic", bg=BLUE, height=38, radius=10, font_size=13)
                btn.bind(on_release=lambda _, t=topic: self.open_detail(specialty, t))
                card.add_widget(btn)
                content.add_widget(card)

        scroll.add_widget(content)
        main_layout.add_widget(scroll)
        screen.add_widget(main_layout)
        self.go("category")

    def open_detail(self, specialty, topic):
        if specialty in ("Clinical Calculators", "Pediatric Calculators"):
            self.open_calculator(specialty, topic)
            return

        screen = self.sm.get_screen("detail")
        screen.clear_widgets()
        main_layout = BoxLayout(orientation="vertical", padding=dp(0), spacing=dp(0))
        subsystem_found = "General"
        for sub, tps in DATA[specialty].items():
            if topic in tps:
                subsystem_found = sub
                break
        self.current_back_action = lambda: self.open_category(specialty, subsystem_found)

        def show_menu(btn):
            dropdown = DropDown()
            dropdown.width = dp(200)
            dropdown.auto_width = False

            btn1 = Button(text="Find in Page", size_hint_y=None, height=dp(45),
                          background_normal="", background_color=get_color_from_hex(SURFACE),
                          color=get_color_from_hex(TEXT), font_size=sp(14), bold=True,
                          halign="left", padding=[dp(15), 0])
            btn1.bind(size=lambda ins, val: setattr(ins, 'text_size', (val[0]-dp(20), val[1])))
            btn1.bind(on_release=lambda *_: (dropdown.dismiss(), self.open_topic_search(specialty, topic)))
            dropdown.add_widget(btn1)

            dropdown.open(btn)

        def on_heart(btn):
            self.toggle_favorite(specialty, topic)
            fav = self.is_favorite(specialty, topic)
            btn.text = "\u2665" if fav else "\u2661"
            btn.color = get_color_from_hex(RED if fav else WHITE)

        main_layout.add_widget(ModernHeader(
            topic, specialty.upper(),
            bg_color=HEADER_NAVY,
            menu_callback=show_menu,
            heart_callback=on_heart,
            is_fav=self.is_favorite(specialty, topic)
        ))

        scroll = ScrollView(do_scroll_x=False)
        content = BoxLayout(orientation="vertical", spacing=dp(15), size_hint_y=None,
                            padding=[dp(20), dp(10), dp(20), dp(40)])
        content.bind(minimum_height=content.setter("height"))

        disclaimer = Card(bg="#FFF3CD", padding=15, radius=15)
        disclaimer.add_widget(make_wrapped_label("MEDICAL DISCLAIMER", 14, "#856404", bold=True))
        disclaimer.add_widget(make_wrapped_label(
            "This app is for educational and quick reference purposes only. "
            "It does not replace clinical judgment or local institutional protocols. "
            "Always verify doses and guidelines before applying.", 12, "#856404"))
        content.add_widget(disclaimer)

        sections = TOPIC_PAGES.get((specialty, topic),
                                   [("NOT FOUND", "danger", "Topic not found.")])
        for item in sections:
            heading = item[0]
            scheme = item[1]
            body = item[2] if len(item) == 3 else item[1]
            h_upper = heading.upper()

            if scheme == "image":
                img = AsyncImage(source=body, size_hint_y=None, height=dp(250))
                content.add_widget(img)
                continue

            if scheme == "danger" or any(w in h_upper for w in ("WARNING", "DON'T MISS", "CONTRAINDICATION")):
                bg, bar_color, title_color = DANGER_BG, DANGER_BAR, RED
            elif scheme == "success" or any(w in h_upper for w in ("DOSE", "TREATMENT", "MANAGEMENT",
                                                                   "ADMINISTER", "PREPARE", "MONITORING",
                                                                   "IMMEDIATE ACTIONS", "FLUID")):
                bg, bar_color, title_color = SUCCESS_BG, SUCCESS_BAR, TEAL
            else:
                bg, bar_color, title_color = INFO_BG, INFO_BAR, NAVY

            cc = BoxLayout(orientation="horizontal", size_hint_y=None, spacing=0)
            cc.bind(minimum_height=cc.setter("height"))

            side_bar = BoxLayout(size_hint_x=None, width=dp(8))
            draw_card_bg(side_bar, bar_color, radius=24, shadow=True, is_bar=True)
            cc.add_widget(side_bar)

            body_card = Card(bg=bg, padding=20, radius=24)
            body_card.add_widget(make_wrapped_label(h_upper, 13, title_color, bold=True))
            body_card.add_widget(make_markup_label(body, 13, TEXT))
            cc.add_widget(body_card)
            content.add_widget(cc)

        back_btn = JDButton("BACK TO TOPICS", bg=WHITE, fg=NAVY, height=52, radius=16, font_size=14)
        back_btn.bind(on_release=lambda *_: self.current_back_action())
        content.add_widget(back_btn)

        scroll.add_widget(content)
        main_layout.add_widget(scroll)
        screen.add_widget(main_layout)
        self.go("detail")

    def open_calculator(self, specialty, topic):
        if specialty == "Pediatric Calculators":
            calc = data_pediatric_calculators.PEDIATRIC_CALCULATOR_DEFINITIONS.get(topic)
        else:
            calc = data_calculators.CALCULATOR_DEFINITIONS.get(topic)

        if not calc:
            self.show_message_popup("Error", f"Calculator '{topic}' not found.")
            return

        subsystem_found = "General"
        for sub, calcs in DATA[specialty].items():
            if topic in calcs:
                subsystem_found = sub
                break

        screen = self.sm.get_screen("detail")
        screen.clear_widgets()
        main_layout = BoxLayout(orientation="vertical", padding=dp(0), spacing=dp(0))
        self.current_back_action = lambda: self.open_category(specialty, subsystem_found)
        main_layout.add_widget(ModernHeader(topic, "CALCULATOR", bg_color=HEADER_NAVY))

        scroll = ScrollView(do_scroll_x=False)
        content = BoxLayout(orientation="vertical", spacing=dp(15), size_hint_y=None,
                            padding=[dp(20), dp(10), dp(20), dp(40)])
        content.bind(minimum_height=content.setter("height"))

        dcard = Card(bg=CARD_BLUE, padding=15)
        dcard.add_widget(make_wrapped_label("Description", 14, NAVY, bold=True))
        dcard.add_widget(make_wrapped_label(calc["description"], 13, TEXT))
        content.add_widget(dcard)

        fcard = Card(bg=CARD_PURPLE, padding=15)
        fcard.add_widget(make_wrapped_label("Formula", 14, NAVY, bold=True))
        fcard.add_widget(make_wrapped_label(calc["formula_text"], 13, TEXT))
        content.add_widget(fcard)

        fields = {}
        inputs_card = Card(bg=WHITE, padding=15)
        inputs_card.add_widget(make_wrapped_label("Input Values", 14, NAVY, bold=True))
        for field_def in calc["fields"]:
            key = field_def["key"]
            fl = BoxLayout(orientation="vertical", size_hint_y=None, height=dp(80), spacing=dp(5))
            fl.add_widget(make_wrapped_label(field_def["label"], 13, TEXT, bold=True))
            inp = TextInput(hint_text=field_def.get("placeholder", ""), multiline=False,
                            font_size=sp(15), size_hint_y=None, height=dp(45),
                            background_color=get_color_from_hex(INPUT_BG),
                            foreground_color=get_color_from_hex(TEXT),
                            cursor_color=get_color_from_hex(BLUE),
                            padding=[dp(10), dp(10), dp(10), dp(10)])
            fl.add_widget(inp)
            inputs_card.add_widget(fl)
            fields[key] = inp
        content.add_widget(inputs_card)

        result_card = Card(bg=SUCCESS_BG, padding=15)
        result_card.add_widget(make_wrapped_label("Result", 14, TEAL, bold=True))
        result_label = make_wrapped_label("Tap 'CALCULATE' to see the result.", 15, TEXT, bold=True)
        result_card.add_widget(result_label)
        content.add_widget(result_card)

        interp_card = Card(bg=INFO_BG, padding=15)
        interp_card.add_widget(make_wrapped_label("Interpretation", 14, NAVY, bold=True))
        interp_card.add_widget(make_wrapped_label(calc["interpretation"], 13, TEXT))
        content.add_widget(interp_card)

        def calculate(*_):
            try:
                values = {k: float(inp.text.strip()) for k, inp in fields.items()}
                result = eval(calc["formula"],
                              {"__builtins__": {"min": min, "max": max, "abs": abs, "round": round}},
                              values)
                result = round(result, 2)
                result_label.text = f"Result: {result} {calc.get('unit', '')}"
                result_label.color = get_color_from_hex(TEAL)
            except ValueError:
                result_label.text = "Invalid input. Enter numbers only."
                result_label.color = get_color_from_hex(RED)
            except ZeroDivisionError:
                result_label.text = "Division by zero error."
                result_label.color = get_color_from_hex(RED)
            except Exception as e:
                result_label.text = f"Error: {str(e)}"
                result_label.color = get_color_from_hex(RED)

        calc_btn = JDButton("CALCULATE", bg=TEAL, height=52, radius=16, font_size=16)
        calc_btn.bind(on_release=calculate)
        content.add_widget(calc_btn)

        ref_card = Card(bg=WHITE, padding=15)
        ref_card.add_widget(make_wrapped_label("Reference", 13, MUTED, bold=True))
        ref_card.add_widget(make_wrapped_label(calc["reference"], 12, MUTED))
        content.add_widget(ref_card)

        scroll.add_widget(content)
        main_layout.add_widget(scroll)
        screen.add_widget(main_layout)
        self.go("detail")


if __name__ == "__main__":
    try:
        JuniorDoctor().run()
    except Exception:
        import traceback
        error_text = traceback.format_exc()
        print(error_text) 
        
        from kivy.app import App
        from kivy.uix.label import Label
        from kivy.uix.scrollview import ScrollView
        from kivy.uix.boxlayout import BoxLayout

        Window.clearcolor = (1, 0.95, 0.95, 1)

        class ErrorApp(App):
            def build(self):
                layout = BoxLayout(orientation="vertical", padding=dp(15), spacing=dp(10))
                layout.add_widget(Label(text="APP ERROR DETECTED\n\n(Screenshot this)",
                                        font_size="16sp", color=(0.7, 0, 0, 1),
                                        size_hint_y=None, height=dp(80), bold=True))
                scroll = ScrollView()
                lbl = Label(text=error_text, font_size="10sp", color=(0, 0, 0, 1),
                            size_hint_y=None, halign="left", valign="top")
                lbl.bind(texture_size=lambda i, s: setattr(i, 'height', s[1] + dp(20)))
                lbl.bind(width=lambda i, w: setattr(i, 'text_size', (w - dp(10), None)))
                scroll.add_widget(lbl)
                layout.add_widget(scroll)
                return layout

        ErrorApp().run()
