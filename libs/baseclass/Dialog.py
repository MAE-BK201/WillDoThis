from kivymd.uix.dialog import MDDialog
from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.picker import MDTimePicker, MDDatePicker

kv = Builder.load_string('''
<Dialog@MDDialog>:
    radius:[20,7,20,7]
''')


class Dialog(MDDialog):
    def __init__(self, title='default', identifier=-1, time="00/00/00   00:00:00", **kwargs):
        super(Dialog, self).__init__(**kwargs)
        self.title = title
        self.identifier = identifier
        self.size_hint = (0.85, 0.5)
        self.date = ""

        if identifier >= 0:  # Dialog for main task
            self.content_cls.children[2].text = time
            list(kwargs['buttons'])[1].bind(on_release=self.save)
            list(kwargs['buttons'])[2].bind(on_release=self.cancel)
            list(kwargs['buttons'])[0].bind(on_release=self.add)
            print(self.content_cls.children[0].children[0])
            self.content_cls.children[0].children[0].bind(on_press=self.mark_as_complete)
            self.content_cls.children[0].children[2].bind(on_press=self.open_picker)
        else:  # Dialog for main task
            list(kwargs['buttons'])[0].bind(on_release=self.sub_save)
            list(kwargs['buttons'])[1].bind(on_release=self.cancel)

    def save(self, *args):
        app = MDApp.get_running_app()
        print("Content: ", self.content_cls.children[2].text)

        app.root.change(
            self.content_cls.children[0].children[1].text, self.identifier, self.content_cls.children[2].text
        )  # Todo send the text of the time

        self.dismiss()

    def mark_as_complete(self, *instance):
        app = MDApp.get_running_app()
        print("changing source")
        app.root.mark_as_complete(self.identifier)
        self.dismiss()

    def sub_save(self, *ignore):
        app = MDApp.get_running_app()
        app.root.change(self.content_cls.text, self.identifier, "")
        self.dismiss()

    def open_picker(self, *ignore):
        date = MDDatePicker(callback=self.get_date)
        date.open()

    def get_date(self, date):
        self.date = date
        time = MDTimePicker()
        time.bind(time=self.get_time)
        time.open()

    def get_time(self, *args):
        self.content_cls.children[2].text = self.date.strftime("%Y/%m/%d") + "   " + args[1].strftime("%H:%M:%S")

    def cancel(self, *args):
        print('Cancel: ', args)
        self.dismiss()

    def add(self, *args):
        from kivymd.toast import toast
        app = MDApp.get_running_app()
        app.root.add_sub_task(self.identifier)
        toast('SubTask Successfully Added')
        self.dismiss()
