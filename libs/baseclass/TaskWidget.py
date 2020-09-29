from kivy.uix.boxlayout import BoxLayout
from ..baseclass.DragBehaviour import DraggableController, DraggableLayoutBehavior
from kivymd import images_path

drag_controller = DraggableController()


class DraggableBoxLayout(DraggableLayoutBehavior, BoxLayout):

    def compare_pos_to_widget(self, widget, pos):
        if self.orientation == 'vertical':
            return 'before' if pos[1] >= widget.center_y else 'after'
        return 'before' if pos[0] < widget.center_x else 'after'

    def handle_drag_release(self, index, drag_widget):
        self.add_widget(drag_widget, index)


class TaskWidget(BoxLayout):
    def __init__(self, text='', source=f'{images_path}/transparent.png', value=0, identifier=-1, time="00/00/00   00:00:00", **kwargs):
        super(TaskWidget, self).__init__(**kwargs)
        self.text = text
        self.value = value
        self.child_widgets = 0
        self.source = source
        self.identifier = identifier
        self.time = time

    def add_child(self, child):
        self.child_widgets += child

    def get_id(self):
        return self.identifier


class SubTask(BoxLayout):
    def __init__(self, identifier=-1, text="", **kwargs):
        super(SubTask, self).__init__(**kwargs)
        self.identifier = identifier
        self.text = text

    def get_id(self):
        return self.identifier
