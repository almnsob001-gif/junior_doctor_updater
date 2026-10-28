from kivy.config import Config
Config.set('graphics', 'width', '400')
Config.set('graphics', 'height', '700')
Config.set('graphics', 'resizable', '0')
Config.set('graphics', 'orientation', 'portrait')

import os
import webbrowser
import data_medical
import data_pediatric
import data_obgyn
import data_surgical
import data_drugs
import data_protocols
import data_toxicology
import data_calculators

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
from kivy.graphics import Color, RoundedRectangle, Ellipse, Line
from kivy.core.text import LabelBase
from kivy.clock import Clock

LabelBase.register(name="Roboto", fn_regular="DejaVuSans.ttf")

# ================= دمج البيانات =================
DATA = {}
DATA.update(data_medical.MEDICAL_DATA)
DATA.update(data_pediatric.PEDIATRIC_DATA)
DATA.update(data_obgyn.OBGYN_DATA)
DATA.update(data_surgical.SURGICAL_DATA)
DATA.update(data_drugs.DRUGS_DATA)
DATA.update(data_protocols.PROTOCOLS_DATA)
DATA.update(data_toxicology.TOXICOLOGY_DATA)
DATA.update(data_calculators.CALCULATORS_DATA)

TOPIC_PAGES = {}
TOPIC_PAGES.update(data_medical.MEDICAL_TOPICS)
TOPIC_PAGES.update(data_pediatric.PEDIATRIC_TOPICS)
TOPIC_PAGES.update(data_obgyn.OBGYN_TOPICS)
TOPIC_PAGES.update(data_surgical.SURGICAL_TOPICS)
TOPIC_PAGES.update(data_drugs.DRUGS_TOPICS)
TOPIC_PAGES.update(data_protocols.PROTOCOLS_TOPICS)
TOPIC_PAGES.update(data_toxicology.TOXICOLOGY_TOPICS)

for specialty in list(DATA.keys()):
    if isinstance(DATA[specialty], list):
        DATA[specialty] = {"General": DATA[specialty]}

for specialty, subsystems in DATA.items():
    for subsystem, topics in subsystems.items():
        for topic in topics:
            if (specialty, topic) not in TOPIC_PAGES and specialty != "Clinical Calculators":
                TOPIC_PAGES[(specialty, topic)] = [
                    ("PAGE UNDER DEVELOPMENT", "warning", f"Detailed clinical content for **{topic}** is currently being compiled."),
                    ("SAFETY NOTE", "danger", "Verify doses and protocols against local guidelines.")
                ]

# ================= PREMIUM MEDICAL COLORS =================
NAVY = "#0A1930"       
BLUE = "#2563EB"       
TEAL = "#0D9488"       
WHITE = "#FFFFFF"      
BG_COLOR = "#F4F7FB"   
TEXT = "#1E293B"       
MUTED = "#64748B"      
BORDER = "#E2E8F0"     
RED = "#DC2626"        

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

SPECIALTY_ICONS = {
    "Medical Emergencies": "🚑",
    "Pediatric Emergencies": "👶",
    "Obstetric & Gynecological": "🤰",
    "Surgical & Trauma": "🩺",
    "Emergency & ICU Drugs": "💊",
    "Clinical Protocols": "📋",
    "Toxicology": "☠️",
    "Clinical Calculators": "🧮"
}

APP_NAME = "Junior Doctor"
Window.clearcolor = get_color_from_hex(BG_COLOR)

# ================= UI HELPERS =================
def sp(val):
    from kivy.metrics import sp as kivy_sp
    return kivy_sp(val)

def draw_card_bg(widget, bg_color, radius=24, shadow=True, is_bar=False):
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
    text = text.replace("[color=0000FF]", "[color=#2563EB]").replace("[color=FF0000]", "[color=#DC2626]")
    lab = Label(text=text, font_size=sp(size), color=get_color_from_hex(color), markup=True, halign="left", valign="top", size_hint_y=None, line_height=1.25)
    lab.bind(width=lambda i, w: setattr(lab, 'text_size', (w, None)))
    lab.bind(texture_size=lambda i, s: setattr(lab, 'height', s[1] + dp(10)))
    return lab

def make_wrapped_label(text, size=14, color=TEXT, bold=False):
    lab = Label(text=text, font_size=sp(size), color=get_color_from_hex(color), bold=bold, halign="left", valign="top", size_hint_y=None)
    lab.bind(width=lambda i, w: setattr(lab, 'text_size', (w, None)))
    lab.bind(texture_size=lambda i, s: setattr(lab, 'height', s[1] + dp(6)))
    return lab

class Card(BoxLayout):
    def __init__(self, bg=WHITE, radius=24, padding=20, **kwargs):
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
    def __init__(self, title, subtitle="", bg_color=HEADER_NAVY, title_color=WHITE, subtitle_color="#94A3B8", **kwargs):
        super().__init__(orientation="horizontal", size_hint_y=None, height=dp(90), spacing=dp(15), padding=[dp(20), dp(15), dp(20), dp(15)], **kwargs)
        
        with self.canvas.before:
            Color(*get_color_from_hex(bg_color))
            self._bg = RoundedRectangle(pos=self.pos, size=self.size, radius=[0, 0, dp(30), dp(30)])
        self.bind(pos=lambda i, v: setattr(self._bg, 'pos', v), size=lambda i, v: setattr(self._bg, 'size', v))
            
        title_box = BoxLayout(orientation="vertical", spacing=dp(4), size_hint_y=None)
        title_box.bind(minimum_height=title_box.setter("height"))
        
        t_lbl = make_wrapped_label(title, 20, title_color, bold=True)
        title_box.add_widget(t_lbl)
        
        if subtitle:
            s_lbl = make_wrapped_label(subtitle, 12, subtitle_color, bold=True)
            title_box.add_widget(s_lbl)
            
        title_layout = BoxLayout(size_hint_y=None)
        title_layout.bind(minimum_height=title_layout.setter("height"))
        title_layout.add_widget(title_box)
        self.add_widget(title_layout)
        
        def update_header_height(*_):
            self.height = max(dp(90), title_box.height + dp(30))
        title_box.bind(height=update_header_height)

# ================= APP CLASS =================
class JuniorDoctor(App):
    def build(self):
        # --- إجبار أندرويد على الوضع العمودي ---
        from kivy.utils import platform
        if platform == 'android':
            try:
                from jnius import autoclass
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                PythonActivity.mActivity.setRequestedOrientation(1)
            except Exception:
                pass
        # ---------------------------------------

        Window.bind(on_keyboard=self.on_keyboard)
        self.current_back_action = None 
        
        self.sm = ScreenManager(transition=SlideTransition(duration=0.2))
        for name in ("home", "subsystem", "category", "detail", "search"):
            self.sm.add_widget(Screen(name=name))
        self.build_home()
        return self.sm

    def go(self, name):
        self.sm.current = name

    def on_keyboard(self, window, key, scancode, codepoint, modifier):
        if key == 27: 
            if self.current_back_action is not None:
                self.current_back_action() 
                return True 
            else:
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

    def build_home(self):
        screen = self.sm.get_screen("home")
        screen.clear_widgets()
        main_layout = BoxLayout(orientation="vertical", padding=dp(0), spacing=dp(0))
        
        self.current_back_action = None 
        
        main_layout.add_widget(ModernHeader("Junior Doctor", "CLINICAL REFERENCE", bg_color=HEADER_NAVY))
        
        scroll = ScrollView(do_scroll_x=False)
        content = BoxLayout(orientation="vertical", spacing=dp(20), size_hint_y=None, padding=[dp(20), dp(0), dp(20), dp(40)])
        content.bind(minimum_height=content.setter("height"))

        search_box = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(65), padding=[dp(15), dp(10)])
        draw_card_bg(search_box, WHITE, radius=20, shadow=True)
        search_box.add_widget(Label(text="🔍", font_size=sp(20), size_hint_x=None, width=dp(30)))
        
        search_input = TextInput(
            hint_text="Search topics, drugs, or protocols...", 
            multiline=False, 
            font_size=sp(14),
            background_normal="", background_active="", background_color=(0,0,0,0),
            foreground_color=get_color_from_hex(TEXT), cursor_color=get_color_from_hex(BLUE),
            hint_text_color=get_color_from_hex(MUTED)
        )
        search_input.bind(on_text_validate=lambda i: self.open_search(i.text))
        search_box.add_widget(search_input)
        content.add_widget(search_box)

        hero = BoxLayout(orientation="vertical", size_hint_y=None, height=dp(140))
        draw_card_bg(hero, NAVY, radius=28)
        
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
        hero_text.add_widget(Label(text="WELCOME, DOCTOR", font_size=sp(12), color=get_color_from_hex("#60A5FA"), bold=True, halign="left", text_size=(None, None)))
        hero_text.add_widget(Label(text="Your clinical\ncompanion.", font_size=sp(28), color=WHITE, bold=True, halign="left", valign="top", text_size=(None, None)))
        hero.add_widget(hero_text)
        content.add_widget(hero)

        content.add_widget(Label(text="EXPLORE SPECIALTIES", font_size=sp(14), color=get_color_from_hex(MUTED), bold=True, size_hint_y=None, height=dp(30), halign="left"))

        for specialty, subsystems in DATA.items():
            num_topics = sum(len(topics) for topics in subsystems.values())
            
            cat_card = BoxLayout(orientation="vertical", size_hint_y=None, height=dp(140), padding=dp(15), spacing=dp(10))
            draw_card_bg(cat_card, CARD_BLUE, radius=24)
            
            top_row = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(15))
            
            icon_text = SPECIALTY_ICONS.get(specialty, "🏥")
            icon_box = BoxLayout(size_hint=(None, 1), width=dp(50))
            draw_card_bg(icon_box, WHITE, radius=16, shadow=False)
            icon_box.add_widget(Label(text=icon_text, font_size=sp(24)))
            top_row.add_widget(icon_box)
            
            title_box = BoxLayout(orientation="vertical")
            title_box.add_widget(make_wrapped_label(specialty, 15, NAVY, bold=True))
            title_box.add_widget(make_wrapped_label(f"{num_topics} Topics Available", 12, TEAL, bold=True))
            top_row.add_widget(title_box)
            cat_card.add_widget(top_row)
            
            btn = JDButton("View Section →", bg=BLUE, height=42, font_size=13, radius=12)
            btn.bind(on_release=lambda _, s=specialty: self.open_specialty(s))
            cat_card.add_widget(btn)
            content.add_widget(cat_card)
            
        content.add_widget(BoxLayout(size_hint_y=None, height=dp(10))) 
        contact_btn = JDButton("Contact via WhatsApp 💬", bg=TEAL, height=55, radius=16, font_size=15)
        contact_btn.bind(on_release=lambda *_: self.contact_developer())
        content.add_widget(contact_btn)

        scroll.add_widget(content)
        main_layout.add_widget(scroll)
        screen.add_widget(main_layout)

    def open_search(self, query=""):
        screen = self.sm.get_screen("search")
        screen.clear_widgets()
        main_layout = BoxLayout(orientation="vertical", padding=dp(0), spacing=dp(0))
        
        self.current_back_action = lambda: self.go("home") 
        main_layout.add_widget(ModernHeader("Search", "Find any topic", bg_color=HEADER_NAVY))
        
        search_box = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(65), padding=[dp(15), dp(10)])
        draw_card_bg(search_box, WHITE, radius=20, shadow=True)
        search_box.add_widget(Label(text="🔍", font_size=sp(20), size_hint_x=None, width=dp(30)))
        
        search_input = TextInput(
            text=query,
            hint_text="Type to search...", 
            multiline=False, 
            font_size=sp(14),
            background_normal="", background_active="", background_color=(0,0,0,0),
            foreground_color=get_color_from_hex(TEXT), cursor_color=get_color_from_hex(BLUE),
            hint_text_color=get_color_from_hex(MUTED)
        )
        search_box.add_widget(search_input)
        
        scroll = ScrollView(do_scroll_x=False)
        results = BoxLayout(orientation="vertical", spacing=dp(15), size_hint_y=None, padding=[dp(20), dp(20)])
        results.bind(minimum_height=results.setter("height"))
        scroll.add_widget(results)
        
        main_layout.add_widget(search_box)
        main_layout.add_widget(scroll)
        
        def perform_search(q):
            results.clear_widgets()
            q = q.lower().strip()
            if not q: return
            
            for specialty, subsystems in DATA.items():
                for subsystem, topics in subsystems.items():
                    for topic in topics:
                        if q in topic.lower():
                            card = Card(bg=WHITE, padding=15)
                            card.add_widget(make_wrapped_label(topic, 15, NAVY, bold=True))
                            card.add_widget(make_wrapped_label(f"{specialty}  ›  {subsystem}", 12, TEAL, bold=True))
                            btn = JDButton("Read Topic", bg=INFO_BG, fg=BLUE, height=36, font_size=13)
                            btn.bind(on_release=lambda _, s=specialty, t=topic: self.open_detail(s, t))
                            card.add_widget(btn)
                            results.add_widget(card)
                            
            if len(results.children) == 0:
                results.add_widget(Label(text="No topics found.", font_size=sp(14), color=get_color_from_hex(MUTED), height=dp(50)))

        search_input.bind(text=lambda _, v: perform_search(v))
        if query: perform_search(query)
            
        screen.add_widget(main_layout)
        self.go("search")
        Clock.schedule_once(lambda dt: setattr(search_input, 'focus', True), 0.3)

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
        content = BoxLayout(orientation="vertical", spacing=dp(15), size_hint_y=None, padding=[dp(20), dp(10)])
        content.bind(minimum_height=content.setter("height"))

        for subsystem, topics in subsystems.items():
            card = Card(bg=CARD_GREEN, padding=20) 
            card.add_widget(make_wrapped_label(subsystem, 16, NAVY, bold=True))
            card.add_widget(make_wrapped_label(f"{len(topics)} Topics available", 13, MUTED))
            btn = JDButton("View Topics →", bg=BLUE, height=42)
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
        content = BoxLayout(orientation="vertical", spacing=dp(12), size_hint_y=None, padding=[dp(20), dp(10)])
        content.bind(minimum_height=content.setter("height"))

        for i, topic in enumerate(DATA[specialty][subsystem], start=1):
            card = Card(bg=CARD_PURPLE, padding=15) 
            row = BoxLayout(size_hint_y=None, height=dp(35))
            
            num_badge = Card(bg=WHITE, radius=8, padding=[dp(8), dp(2)], size_hint=(None, None), size=(dp(32), dp(28)))
            num_badge.add_widget(Label(text=str(i).zfill(2), font_size=sp(13), color=get_color_from_hex(BLUE), bold=True))
            row.add_widget(num_badge)
            
            title_box = BoxLayout(padding=[dp(10), 0])
            title_box.add_widget(make_wrapped_label(topic, 15, NAVY, bold=True))
            row.add_widget(title_box)
            card.add_widget(row)
            
            btn = JDButton("Read Topic", bg=WHITE, fg=BLUE, height=38, font_size=13)
            btn.bind(on_release=lambda _, t=topic: self.open_detail(specialty, t))
            card.add_widget(btn)
            content.add_widget(card)

        scroll.add_widget(content)
        main_layout.add_widget(scroll)
        screen.add_widget(main_layout)
        self.go("category")

    def open_detail(self, specialty, topic):
        if specialty == "Clinical Calculators":
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
        
        main_layout.add_widget(ModernHeader(topic, specialty.upper(), bg_color=HEADER_NAVY))
        
        scroll = ScrollView(do_scroll_x=False)
        content = BoxLayout(orientation="vertical", spacing=dp(15), size_hint_y=None, padding=[dp(20), dp(10), dp(20), dp(40)])
        content.bind(minimum_height=content.setter("height"))

        sections = TOPIC_PAGES.get((specialty, topic), [("NOT FOUND", "danger", "Topic not found.")])
        for item in sections:
            heading, scheme, body = item[0], item[1], item[2] if len(item) == 3 else item[1]
            h_upper = heading.upper()
            
            if scheme == "danger" or any(w in h_upper for w in ("WARNING", "DON'T MISS", "CONTRAINDICATION")):
                bg, bar_color, title_color = DANGER_BG, DANGER_BAR, RED
            elif scheme == "success" or any(w in h_upper for w in ("DOSE", "TREATMENT", "MANAGEMENT", "ADMINISTER", "PREPARE", "MONITORING", "IMMEDIATE ACTIONS", "FLUID")):
                bg, bar_color, title_color = SUCCESS_BG, SUCCESS_BAR, TEAL
            else:
                bg, bar_color, title_color = INFO_BG, INFO_BAR, NAVY 
                
            card_container = BoxLayout(orientation="horizontal", size_hint_y=None, spacing=0)
            card_container.bind(minimum_height=card_container.setter("height"))
            
            side_bar = BoxLayout(size_hint_x=None, width=dp(8))
            draw_card_bg(side_bar, bar_color, radius=24, shadow=True, is_bar=True)
            card_container.add_widget(side_bar)
            
            card_body = Card(bg=bg, padding=20, radius=24)
            card_body.add_widget(make_wrapped_label(h_upper, 13, title_color, bold=True))
            card_body.add_widget(make_markup_label(body, 13, TEXT))
            
            card_container.add_widget(card_body)
            content.add_widget(card_container)

        back_btn = JDButton("BACK TO TOPICS", bg=WHITE, fg=NAVY, height=52, radius=16)
        back_btn.bind(on_release=lambda *_: self.current_back_action())
        content.add_widget(back_btn)

        scroll.add_widget(content)
        main_layout.add_widget(scroll)
        screen.add_widget(main_layout)
        self.go("detail")

    def open_calculator(self, specialty, topic):
        import data_calculators
        calc = data_calculators.CALCULATOR_DEFINITIONS.get(topic)
        if not calc:
            return
            
        screen = self.sm.get_screen("detail")
        screen.clear_widgets()
        main_layout = BoxLayout(orientation="vertical", padding=dp(0), spacing=dp(0))
        
        self.current_back_action = lambda: self.open_category(specialty, "General")
        
        main_layout.add_widget(ModernHeader(topic, "CALCULATOR", bg_color=HEADER_NAVY))
        
        scroll = ScrollView(do_scroll_x=False)
        content = BoxLayout(orientation="vertical", spacing=dp(15), size_hint_y=None, padding=[dp(20), dp(10), dp(20), dp(40)])
        content.bind(minimum_height=content.setter("height"))
        
        desc_card = Card(bg=CARD_BLUE, padding=15)
        desc_card.add_widget(make_wrapped_label("Description", 14, NAVY, bold=True))
        desc_card.add_widget(make_wrapped_label(calc["description"], 13, TEXT))
        content.add_widget(desc_card)
        
        formula_card = Card(bg=CARD_PURPLE, padding=15)
        formula_card.add_widget(make_wrapped_label("Formula", 14, NAVY, bold=True))
        formula_card.add_widget(make_wrapped_label(calc["formula_text"], 13, TEXT))
        content.add_widget(formula_card)
        
        fields = {}
        inputs_card = Card(bg=WHITE, padding=15)
        inputs_card.add_widget(make_wrapped_label("Input Values", 14, NAVY, bold=True))
        
        for field_def in calc["fields"]:
            key = field_def["key"]
            field_layout = BoxLayout(orientation="vertical", size_hint_y=None, height=dp(75), spacing=dp(5))
            field_layout.add_widget(make_wrapped_label(field_def["label"], 13, TEXT, bold=True))
            
            input_box = TextInput(
                hint_text=field_def.get("placeholder", ""),
                multiline=False,
                font_size=sp(15),
                size_hint_y=None,
                height=dp(45),
                background_color=get_color_from_hex("#F4F7FB"),
                foreground_color=get_color_from_hex(TEXT),
                cursor_color=get_color_from_hex(BLUE),
                padding=[dp(10), dp(10)]
            )
            field_layout.add_widget(input_box)
            inputs_card.add_widget(field_layout)
            fields[key] = input_box
        
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
                values = {}
                for k, inp in fields.items():
                    values[k] = float(inp.text.strip())
                result = eval(calc["formula"], {"__builtins__": {}}, values)
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
    JuniorDoctor().run()