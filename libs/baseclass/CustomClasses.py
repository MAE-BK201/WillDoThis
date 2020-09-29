from ..baseclass.DragBehaviour import DraggableObjectBehavior, DraggableController
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Color, Line
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.behaviors import ToggleButtonBehavior
from kivymd.toast import toast
from kivy.lang import Builder
from kivymd.uix.list import OneLineAvatarListItem

from kivy.properties import ListProperty
from kivy.utils import get_color_from_hex

from kivymd.theming import ThemableBehavior
from kivymd.color_definitions import palette, colors
from kivy.uix.modalview import ModalView
from kivy.uix.widget import Widget
from kivymd.uix.list import ILeftBody

drag_controller = DraggableController()
design = Builder.load_string("""
#: import toast kivymd.toast.toast
<RadioButton>
    background_normal: 'assets/Images/states/color_button_normal.png'
    background_down: 'assets/Images/states/color_button_down.png'
    border: (3, 3, 3, 3)

<ColorButton@RadioButton>:
    group: 'color'

<LineWidthButton@RadioButton>:
    group: 'line_width'
    color: C('#2c3e50')
    background_color: C('#ecf0f1')

<CustomBox>:
    height:self.minimum_height


<PaintWindow>:
    size_hint:1,1
    canvas.before:
        Color:
            rgba:1,0,0,0#get_color_from_hex("#FFFFF")
        Rectangle:
            pos:self.pos
            size:self.size


<About>:
    secondary_text:''
    text:''
    size_hint_y: None
    height: self.minimum_height
    TwoLineIconListItem:
        text:self.parent.text
        secondary_text:self.parent.secondary_text

        IconLeftWidget:
            icon:'information'
            on_press:toast(root.secondary_text, duration=4)
            

<TipButton@MDIconButton+MDTooltip>

<DialogContent>:
    orientation:"vertical"
    spacing:dp(15)
    text:''

    MDLabel:
        id:clock
        text:"00/00/00  00:00:00"
        font_size:25
        halign:"center"
        theme_text_color:"Custom"
        text_color:1,0.3,0.3,0.8

    MDSeparator:    
        color:1,0,0,1

    BoxLayout:
        size_hint_y:None
        height:self.minimum_height + 20

        TipButton:
            icon:"timetable"
            tooltip_text:"Pick deadline for task"


        MDTextField:
            fill_color:(0,0,0,.4)
            mode:'fill'
            icon_right:"alpha-w-circle"
            text:root.text

        TipButton:
            icon:'check'
            tooltip_text:"Mark task as completed"
            


<CustomOneLineAvatarListItem>:
    on_release: app.theme_cls.primary_palette = root.text
    LeftWidget:
        canvas.before:
            Color:
                rgba: root.color
            Ellipse:
                pos: self.pos
                size: self.size
                

<ThemePicker>:
    size_hint: None, None
    height: Window.height * 80 / 100
    width: Window.width * 80 / 100
    canvas:
        Color:
            rgba:(1, 1, 1, 1) if app.theme_cls.theme_style == "Light" else (.2, .2, .2, 1)
        Rectangle:
            pos:self.pos
            size:self.width, self.height

    BoxLayout:
        orientation: "vertical"

        BoxLayout:
            id: box
            padding: "10dp"
            spacing: "10dp"
            size_hint_y: .35

            Image:
                source: "assets/palette.png"
                size_hint: None, None
                size: box.height, box.height + dp(40)

            MDLabel:
                theme_text_color: "Primary"
                text: "Change Theme"
                font_style: "Button"

        RecycleView:
            id: rv
            key_viewclass: 'viewclass'
            key_size: 'height'
            md_bg_color:[1,1,1,1]

            RecycleBoxLayout:
                default_size: None, dp(48)
                default_size_hint: 1, None
                size_hint_y: None
                height: self.minimum_height
                orientation: 'vertical'

""")


class LeftWidget(ILeftBody, Widget):
    pass


class CustomOneLineAvatarListItem(OneLineAvatarListItem):
    color = ListProperty()


class RadioButton(ToggleButton):
    def _do_press(self):
        if self.state == 'normal':
            ToggleButtonBehavior._do_press(self)


class CustomBox(DraggableObjectBehavior, BoxLayout):
    def __init__(self, **kwargs):
        super(CustomBox, self).__init__(**kwargs, drag_controller=drag_controller)

    def initiate_drag(self):
        # during a drag, we remove the widget from the original location
        self.parent.remove_widget(self)


class ThemePicker(ThemableBehavior, ModalView):
    def set_list_colors_themes(self):
        for name_theme in palette:
            self.ids.rv.data.append(
                {
                    "viewclass": "CustomOneLineAvatarListItem",
                    "color": get_color_from_hex(colors[name_theme]["500"]),
                    "text": name_theme,
                }
            )


class PaintWindow(Widget):
    line_width = 2
    line = False
    count = 0

    def on_touch_down(self, touch):
        if Widget.on_touch_down(self, touch):
            return
        if self.collide_point(*touch.pos):
            self.line = True

            with self.canvas:
                touch.ud['current_line'] = Line(
                    points=(touch.x, touch.y),
                    width=self.line_width)

    def on_touch_move(self, touch):
        if self.collide_point(*touch.pos) and self.line:
            if 'current_line' in touch.ud:
                touch.ud['current_line'].points += (touch.x, touch.y)

    def on_touch_up(self, touch):
        self.line = False

    def set_color(self, new_color):
        self.last_color = new_color
        self.canvas.add(Color(*new_color))

    def set_line_width(self, line_width='Normal'):
        self.line_width = {
            'Thin': 1, 'Normal': 2, 'Thick': 4
        }[line_width]

    def save(self):
        toast("Painting saved...")
        self.export_to_png(f"paint_{self.count}.png")
        self.count += 1

    def clear_canvas(self):
        saved = self.children[:]
        self.clear_widgets()
        self.canvas.clear()
        for widget in saved:
            self.add_widget(widget)
        self.set_color(self.last_color)


class About(BoxLayout):
    def __init__(self, text='', secondary_text='', **kwargs):
        super(About, self).__init__(**kwargs)
        self.text = text
        self.secondary_text = secondary_text


class DialogContent(BoxLayout):
    def __init__(self, text='', **kwargs):
        super(DialogContent, self).__init__(**kwargs)
        self.text = text
