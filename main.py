from kivymd.app import MDApp
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy.animation import Animation
from libs.baseclass.TaskWidget import TaskWidget, DraggableController
from libs.baseclass.CustomClasses import About, CustomBox, DialogContent, ThemePicker
from libs.baseclass.Dialog import Dialog
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivy.factory import Factory
from kivymd.uix.textfield import MDTextField
from kivymd.toast import toast
from kivymd.uix.snackbar import Snackbar
from kivymd.uix.expansionpanel import MDExpansionPanel, MDExpansionPanelOneLine
from kivy.metrics import dp
from kivy.clock import Clock
from kivymd import images_path
from kivy.core.window import Window
from kivy.utils import get_color_from_hex
from kivymd.uix.dialog import MDDialog

from functools import partial
from datetime import datetime as dt
from os.path import join, dirname, realpath

from plyer import notification
from plyer.utils import platform

import os
import gc
import json
import random


Window.size = (500, 700)
design = Builder.load_file('design.kv')
drag_controller = DraggableController()
complete_show_anim, ongoing_show_anim, task_not_started_anim, no_indicator = True, True, True, True

'''
            Things ToDo
1) Make the Parent Widget Image change based on the subtask progress (In progress)
2) Make each subtask have progress of their own without interference (Completed)
3) Make the paint canvas (Complete)
4) Change the color palette through options (Completed)
5) Save tasks content to a file and read file on start (Completed.... Need to save sub tasks)
6) Implement time management for each task (Completed-ish)
7) Add quotes to paint screen (Completed)
8) More painting options like drawing a line, undo, etc (Not started)
9) Add fonts (Complete)
'''


class WillDoThis(BoxLayout):
    def __init__(self, **kwargs):
        super(WillDoThis, self).__init__(**kwargs)
        self.orientation = 'vertical'
        self.note = ''
        self.task_count = 0
        self.identity = []
        self.dynamic_widgets = []
        self.anim_counter = 0
        self.notif_count = 0
        self.padding = [0, 10, 0, 0]
        self.subtaskcount = -1
        self.sub_task_identity = []
        self.view_count = 2
        self.dummy_text = ""
        self.linker = {}
        self.undo = []
        self.anim_images = ['chevron-down', 'chevron-right', 'chevron-up']
        self.load_data()
        Clock.schedule_interval(self.check_progress, 0)
        Clock.schedule_interval(self.save_data, 0.5)
        self.smart_theme = False

    def load_data(self):  # ToDo needs more work

        try:
            config_dir = open("assets/Settings/config.ini", "r")
            config_settings = json.load(config_dir)
            app = MDApp.get_running_app()
            app.theme_cls.primary_palette = config_settings[0]
            app.theme_cls.theme_style = config_settings[1]
            self.ids.active_theme.active = config_settings[2]

            self.ids.backdrop.ids._front_layer.md_bg_color = [0, 0, 0, 0]

            f = open('assets/Database/database.json', 'r')
            tasks = json.load(f)
            for task in tasks.values():
                box = CustomBox(
                    orientation='vertical', size_hint_y=None, pos_hint={'center_x': 0.5},
                    size_hint_x=0.95, drag_cls='box', spacing=dp(10)
                )
                new_task = TaskWidget(  # Creation of a TaskWidget Instance
                    text=task[0], size_hint_y=None, height=dp(75), identifier=task[2], time=task[1],
                    size_hint_x=0.95, pos_hint={'center_x': 0.5}, value=task[3], source=task[4]
                )
                self.dynamic_widgets.append(new_task)
                self.identity.append([new_task, new_task.get_id()])
                box.add_widget(new_task)
                self.ids.scroll_area.add_widget(box)
                self.task_count += 1
        except:
            pass

    def save_data(self, *ignore):  # Task overwriting
        app = MDApp.get_running_app()
        if self.ids.active_theme.active:  # Enabling auto theme based on the time of the day
            self.ids.disabled_controller.disabled = True
            if dt.now().hour >= 17 or dt.now().hour <= 5:
                app.theme_cls.theme_style = "Dark"
            else:
                app.theme_cls.theme_style = "Light"
        else:
            self.ids.disabled_controller.disabled = False

        data = {}
        config_settings = [app.theme_cls.primary_palette, app.theme_cls.theme_style, self.ids.active_theme.active]

        database = open("assets/Database/database.json", "w")
        config_dir = open("assets/Settings/config.ini", "w")

        for task in self.dynamic_widgets:
            data['task'+str(task.get_id())] = [task.text, task.time, task.get_id(), task.value, task.source]

        json.dump(config_settings, config_dir)
        json.dump(data, database)

    def add_task(self):  # Dynamically adding tasks
        text = self.ids.note.text
        if len(text.strip()) < 1 or not text:  # Ignore blank spaces in text, no empty text
            toast('Cannot add Empty Task')
        else:

            box = CustomBox(
                orientation='vertical', size_hint_y=None, pos_hint={'center_x': 0.5},
                size_hint_x=0.95, drag_cls='box', spacing=dp(10)
            )
            task = TaskWidget(  # Creation of a TaskWidget Instance
                text=text, size_hint_y=None, height=dp(75), identifier=self.task_count,
                size_hint_x=0.95, pos_hint={'center_x': 0.5}, value=0
            )
            box.add_widget(task)  # Adding task to the boxlayout
            self.note = text  # Saving text to pass to the dialog class
            self.dynamic_widgets.append(task)  # task that are dynamically created are referenced
            self.identity.append([task, self.task_count])  # Appending a task with a unique identifier
            self.ids.scroll_area.add_widget(box)  # Adds widget to the ScrollView
            self.ids.note.text = ''  # Resets the text box to empty
            self.task_count += 1

        # Tasks are only able to be dragged once scrolling is possible
        total_widget_height = 0
        for widget in self.ids.scroll_view.children[0].children[0].children:
            total_widget_height += widget.height

        if total_widget_height >= self.ids.scroll_view.height - (self.ids.scroll_view.height / 4):
            print('Drag enabled')

    def up_anim(self, *args):
        if self.anim_counter <= 2:
            args[0].icon = self.anim_images[self.anim_counter]
            self.anim_counter += 1
            Clock.schedule_once(partial(self.up_anim, args[0]), 0.05)
        else:
            self.anim_counter = 0
            self.anim_images.reverse()
            self.reveal_task(args[0].parent.parent)

    # may need to revamp and compile it in the rotate_anim function
    def anim(self, *args):
        if self.anim_counter <= 2:
            args[0].icon = self.anim_images[self.anim_counter]
            self.anim_counter += 1
            Clock.schedule_once(partial(self.up_anim, args[0]), 1)
        else:
            self.anim_counter = 0
            self.anim_images.reverse()
            self.reveal_task(args[0].parent.parent)

    def rotate_anim(self, *args):
        self.up_anim(args[0].children[1].children[3])  # passing the button of the task as parameter

    def check_progress(self, *args):  # Bind the main task id as a dictionary key and sub tasks as values
        self.linker = {}
        global complete_show_anim, ongoing_show_anim, task_not_started_anim, no_indicator
        selected_count = 0
        percentage = []
        date, time = [], []
        count = 0

        for task in self.dynamic_widgets:
            self.linker[task.get_id()] = task.parent.children[0:len(task.parent.children)-1]
            if task.children[1].children[2].texture_size[1] >= 57 and task.children[1].children[2].texture_size[0] >= 170:
                self.dummy_text = task.text
                task.text = task.text[0:len(task.text) - 6] + "..."
            else:
                pass
            if len(task.parent.children) - 1 <= 0:
                task.value = 0
                task.source = f"{images_path}/transparent.png"

        for subtasklist in self.linker.values():
            selected_count = 0
            for subtask in subtasklist:
                if not subtask:
                   pass
                else:
                    if subtask.children[0].children[1].active:
                        selected_count += 1
                    if not subtask.children[0].children[1].active:
                        if selected_count - 1 <= 0:
                            pass
                        else:
                            selected_count -= 1

            percentage.append(selected_count)

        today = dt.today().strftime("%Y/%m/%d   %H:%M:%S")  # Getting the current date
        date_now = today.split("   ")[0]  # Current date
        time_now = today.split("   ")[1]  # Current time
        try:
            for item in self.dynamic_widgets:
                datetime = item.time.split("   ")  # Separating date from time
                date.append(datetime[0])  # Adding each tasks date to list
                time.append(datetime[1])  # Adding each tasks time to list
        except:
            pass

        for item in self.dynamic_widgets:
            try:
                item.value = 100 * (percentage[count] / (len(item.parent.children) - 1))
            except Exception as err:
                pass

            if item.value == 100:
                task_not_started_anim = True
                ongoing_show_anim = True
                if complete_show_anim:
                    item.transition_width = 0
                    Animation.stop_all(item)
                    Animation(transition_width=55, d=0.1, t="out_quad").start(item)
                    item.source = "assets/Images/status/Completed Task (on-time).png"
                    complete_show_anim = False
                else:
                    item.source = "assets/Images/status/Completed Task (on-time).png"

            elif len(item.parent.children) - 1 > 0:
                if item.value == 0:
                    complete_show_anim = True
                    ongoing_show_anim = True
                    if task_not_started_anim:
                        item.transition_width = 0
                        Animation.stop_all(item)
                        Animation(transition_width=55, d=0.1, t="out_quad").start(item)
                        item.source = "assets/Images/status/Task Not Started.png"
                        task_not_started_anim = False
                    else:
                        item.source = "assets/Images/status/Task Not Started.png"
                else:
                    complete_show_anim = True
                    task_not_started_anim = True
                    if ongoing_show_anim:
                        item.transition_width = 0
                        Animation.stop_all(item)
                        Animation(transition_width=55, d=0.1, t="out_quad").start(item)
                        item.source = "assets/Images/status/Ongoing Task.png"
                        ongoing_show_anim = False
                    else:
                        item.source = "assets/Images/status/Ongoing Task.png"

            else:
                item.source = f"{images_path}/transparent.png"

            if date_now.split("/")[0] == date[count].split('/')[0] and date_now.split("/")[1] == date[count].split('/')[
                1]:
                if int(date[count].split('/')[2]) - int(date_now.split("/")[2]) < 3:
                    item.source = 'assets/Images/status/Over Schedule Task.png'
                    if self.notif_count == 0:
                        self.do_notify(mode='fancy')
                    self.notif_count += 1
                elif int(date[count].split('/')[2]) - int(date_now.split("/")[2]) == 3:
                    if time_now == time[count]:
                        pass
                else:
                    item.source = f"{images_path}/transparent.png"

    def add_sub_task(self, *args):
        task = Factory.SubTask(  # Creation of a SubTaskWidget Instance
            identifier=self.subtaskcount, size_hint_y=None, height=dp(-10), size_hint_x=0.9,
            text=" Enter Sub Task Description", pos_hint={'center_x': 0.53}, opacity=0, disabled=True
        )
        hidden_task = Factory.SubTask(  # Creation of a Hidden SubTaskWidget Instance
            identifier=self.subtaskcount, size_hint_y=None, height=dp(75), size_hint_x=0.9,
            text=" Enter Sub Task Description", pos_hint={'center_x': 0.53}, opacity=1, disabled=False
        )
        for item in self.identity:
            if item[1] == args[0]:
                if item[0].children[1].children[3].icon == 'chevron-down':
                    self.sub_task_identity.append([task, self.subtaskcount])
                    item[0].parent.add_widget(task)
                else:
                    self.sub_task_identity.append([hidden_task, self.subtaskcount])
                    item[0].parent.add_widget(hidden_task)
                break
        self.subtaskcount -= 1

    def mark_as_complete(self, identifier):
        for item in self.identity:
            if item[1] == identifier:
                item[0].source = 'assets/Images/status/Completed Task (on-time).png'
                break

    def do_notify(self, mode='normal'):
        title = "WeChat"
        message = "Overschedule"
        ticker = "No Idea"
        kwargs = {'title': title, 'message': message, 'ticker': ticker}

        if mode == 'fancy':
            kwargs['app_name'] = "Plyer Notification Example"
            if platform == "win":
                kwargs['app_icon'] = join(dirname(realpath(__file__)),
                                            'plyer-icon.ico')
                kwargs['timeout'] = 4
            else:
                kwargs['app_icon'] = join(dirname(realpath(__file__)),
                                            'plyer-icon.png')
        elif mode == 'toast':
            kwargs['toast'] = True
        notification.notify(**kwargs)
        
# ToDo need to bind the datetime to the task and dialogue
    def change(self, text, identifier, time):
        if int(identifier) >= 0:
            for item in self.identity:
                if item[1] == int(identifier):
                    item[0].text = text
                    item[0].time = time
        else:
            for item in self.sub_task_identity:
                if item[1] == int(identifier):
                    item[0].text = text

    def reveal_task(self, *args):
        if self.view_count % 2 == 0:  # If reveal
            for task in args[0].parent.children:
                task.disabled = False
                Animation(height=dp(75), opacity=1, duration=0.1).start(task)
        else:   # Else hide
            for task in args[0].parent.children[:len(args[0].parent.children) - 1]:
                task.disabled = True
                Animation(height=dp(-10), opacity=0, d=0.1).start(task)

        self.view_count += 1

    def delete_anim(self, *args):
        def delete(*arg):  # Delete a task
            count = 0
            for item in self.dynamic_widgets:  # removing the deleted task from the list
                if item == arg[1]:
                    self.dynamic_widgets.remove(item)
                count += 1

            self.ids.scroll_area.remove_widget(arg[1].parent)
            self.undo.append(arg[1])
            arg[1].parent.remove_widget(arg[1])
            Snackbar(text="Undo deleted task", button_text="Undo", button_callback=self.undo_delete).show()
            gc.collect()  # garbage collector to collect freed memory

        Animation.stop_all(args[0])  # Delete animation
        anim = (
                Animation(height=120, size_hint_x=1, d=0.3, t='out_quad') +
                Animation(opacity=0, height=0, size_hint_x=0, d=0.2, t='out_quad')
            )
        anim.bind(on_complete=delete)
        anim.start(args[0])
        
    def undo_delete(self, *ignore):  # Adds deleted task back to the layout
        if not self.undo:
            toast("Cannot undo any further")
        else:
            task = self.undo.pop()
            task.source = f"{images_path}/transparent.png"

            box = CustomBox(
                orientation='vertical', size_hint_y=None, pos_hint={'center_x': 0.5},
                size_hint_x=0.95, drag_cls='box', spacing=dp(10)
            )
            box.add_widget(task)
            self.dynamic_widgets.append(task)
            self.ids.scroll_area.add_widget(box)
            Animation.stop_all(task)
            Animation(height=dp(75), opacity=1, size_hint_x=0.95, d=0.3, t='out_quad').start(task)
            toast("Task restored")

    def sub_delete_anim(self, *args):
        def del_sub(*arg):
            for item in self.dynamic_widgets:
                for sub_item in item.parent.children:
                    if sub_item == arg[1]:
                        sub_item.parent.remove_widget(arg[1])
                        gc.collect()

        Animation.stop_all(args[0])
        anim = (Animation(x=40, d=0.5, t='out_quad') + Animation(x=Window.width, d=0.1))
        anim.bind(on_complete=del_sub)
        anim.start(args[0])

    def show_dialog(self, *args):  # Opens Dialog unique to task selected
        # need to find a way to find weak reference to dialogs
        save = MDRaisedButton(text="SAVE", size_hint_x=0.2)
        cancel = MDRaisedButton(text="CANCEL", size_hint_x=0.2)
        add_task = MDRaisedButton(text="ADD SUB-TASK", size_hint_x=0.2)
        print(args[0].texture_size)
        print(args[0].width, args[0].height)
        x = Dialog(
            identifier=args[1].get_id(), type='custom', title='Main Task ' + str(args[1].get_id()), time=args[1].time,
            content_cls=DialogContent(text=args[0].text), buttons=[add_task, save, cancel], auto_dismiss=False
        ).open()

    def show_sub_dialog(self, *args):
        save = MDRaisedButton(text="SAVE")
        cancel = MDFlatButton(text="CANCEL")

        textfield = MDTextField(
            text=args[0].text, size_hint_y=None, height=dp(50), font_size=20, hint_text="Enter Description",
            mode="fill", fill_color=(0, 0, 0, .2)
        )

        x = Dialog(
            identifier=args[1].get_id(), type='custom', title='Sub Task ',
            content_cls=textfield, buttons=[save, cancel], auto_dismiss=False
        ).open()


class MainApp(MDApp):
    drag_controller = drag_controller
    dialog_change_theme = None

    def build(self):
        self.title = 'WillDoThis (Android Build)'
        self.icon = 'assets/Images/icon.png'
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.accent_palette = 'Pink'
        self.root = WillDoThis()
        return design

    def on_start(self):
        self.fps_monitor_start()
        self.init_quotes()
        self.init_information()
        self.root.ids.paint.set_color(get_color_from_hex('#2980b9'))

    def init_information(self):
        counter = 0
        path = r'assets/Images/status'
        images = sorted(os.listdir(path))
        labels = images

        with open('assets/Database/description.txt', 'r') as source:
            description = source.readlines()

        for i in range(6):  # creating the help page for users
            self.root.ids["about"].add_widget(
                MDExpansionPanel(
                    icon=os.path.join(path, images[counter]),
                    content=About(text='About Status Indicator', secondary_text=description[counter].strip('\n')),
                    panel_cls=MDExpansionPanelOneLine(
                        text=labels[counter].strip('.png')
                    )
                )
            )
            counter += 1

    def on_pause(self):
        self.root.save_data()
        return

    def show_license(self):
        with open('LICENSE', 'r') as source:
            text = source.read()

        MDDialog(text=text).open()

    def show_dialog_change_theme(self):
        if not self.dialog_change_theme:
            self.dialog_change_theme = ThemePicker()
            self.dialog_change_theme.set_list_colors_themes()
        self.dialog_change_theme.open()

    def init_quotes(self):
        quote = self.root.ids.quote
        author = self.root.ids.author
        rand_int = random.randint(0, 5000)

        with open("assets/Quotes_Database/quotes.json", 'r', encoding='utf-8', errors='ignore') as source:
            content = json.load(source)
        quote.text = "\"" + content[rand_int]['quoteText'] + "\""
        author.text = "~" + content[rand_int]['quoteAuthor'] + "  "


if __name__ == '__main__':
    MainApp().run()
