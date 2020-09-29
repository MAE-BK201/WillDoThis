from kivymd.theming import ThemableBehavior
from kivy.uix.textinput import TextInput
from kivy.properties import StringProperty, ListProperty
from kivymd.uix.label import MDIcon


class CustomField(ThemableBehavior, TextInput):
    icon_left = StringProperty()
    """Left icon.

    :attr:`icon_left` is an :class:`~kivy.properties.StringProperty`
    and defaults to `''`.
    """

    icon_left_color = ListProperty([0, 0, 0, 1])
    """Color of left icon in ``rgba`` format.

    :attr:`icon_left_color` is an :class:`~kivy.properties.ListProperty`
    and defaults to `[0, 0, 0, 1]`.
    """

    icon_right = StringProperty()
    """Right icon.

    :attr:`icon_right` is an :class:`~kivy.properties.StringProperty`
    and defaults to `''`.
    """

    icon_right_color = ListProperty([0, 0, 0, 1])
    """Color of right icon.

    :attr:`icon_right_color` is an :class:`~kivy.properties.ListProperty`
    and defaults to `[0, 0, 0, 1]`.
    """

    line_color = ListProperty()
    """Field line color.

    :attr:`line_color` is an :class:`~kivy.properties.ListProperty`
    and defaults to `[]`.
    """

    normal_color = ListProperty()
    """Field color if `focus` is `False`.

    :attr:`normal_color` is an :class:`~kivy.properties.ListProperty`
    and defaults to `[]`.
    """

    color_active = ListProperty()
    """Field color if `focus` is `True`.

    :attr:`color_active` is an :class:`~kivy.properties.ListProperty`
    and defaults to `[]`.
    """

    _color_active = ListProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._lbl_icon_left = MDIcon(theme_text_color="Custom")
        self._lbl_icon_right = MDIcon(theme_text_color="Custom")
        self.cursor_color = self.theme_cls.primary_color

        if not self.normal_color:
            self.normal_color = self.theme_cls.primary_light
        if not self.line_color:
            self.line_color = self.theme_cls.primary_dark
        if not self.color_active:
            self._color_active = [0, 0, 0, 0.5]

    def on_focus(self, instance, value):
        if value:
            self.icon_left_color = self.theme_cls.primary_color
            self.icon_right_color = self.theme_cls.primary_color
        else:
            self.icon_left_color = self.theme_cls.text_color
            self.icon_right_color = self.theme_cls.text_color

    def on_icon_left(self, instance, value):
        self._lbl_icon_left.icon = value

    def on_icon_left_color(self, instance, value):
        self._lbl_icon_left.text_color = value

    def on_icon_right(self, instance, value):
        self._lbl_icon_right.icon = value

    def on_icon_right_color(self, instance, value):
        self._lbl_icon_right.text_color = value

    def on_color_active(self, instance, value):
        if value != [0, 0, 0, 0.5]:
            self._color_active = value
            self._color_active[-1] = 0.5
        else:
            self._color_active = value
