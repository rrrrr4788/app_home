from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.behaviors import ButtonBehavior
from kivy.properties import StringProperty, NumericProperty

from kivy.uix.modalview import ModalView
from kivy.garden.circulardatetimepicker import CircularTimePicker as CTP
from kivy.uix.button import Button

from kivy.metrics import sp, dp
from kivy.utils import rgba
from app.storage.db import Database

from datetime import datetime


class NewTask(ModalView):
    def __init__(self, **kw):
        super().__init__(**kw)

    def get_time(self):
        mv = ModalView(size_hint=[.8, .6])
        box = BoxLayout(orientation='vertical', size_hint=[.5, .5])
        mv.add_widget(box)

        cl = CTP(color=[1, 1, 1, 1])
        cl.bind(time=self.set_time)

        submit = Button(text='OK', background_normal='',
                        background_color=rgba('#ffffff'), color=rgba('#0e1574ff'), size_hint_y=.2)

        submit.bind(on_release=lambda x: self.update_time(cl.time, mv))
        box.add_widget(cl)
        box.add_widget(submit)
        mv.open()

    def set_time(self, inst, value):
        print(value)

    def update_time(self, time, mv):
        mv.dismiss()
        self.ids.task_time.text = str(time)


class NewButton(ButtonBehavior, BoxLayout):
    pass


class Task(ButtonBehavior, BoxLayout):
    name = StringProperty('')
    og_name = StringProperty('')
    time = StringProperty('')
    date = StringProperty('')

    def __init__(self, **kw):
        super().__init__(**kw)

        self.bind(on_release=lambda x: self.view_task())

    def view_task(self):
        vt = ViewTask()
        vt.ids.name.text = self.name
        vt.ids.time.text = self.time
        vt.ids.date.text = self.date
        vt.open()


class Upcoming(Task):
    pass


class ViewTask(ModalView):
    pass


class Today(Task):
    pass


class MainWindow (BoxLayout):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.db = Database()

        self.init_view()

    def init_view(self):
        all_tasks = self.db.get_tasks()
        scroll_parent = Window
        tw = self.ids.today_wrapper
        uw = self.ids.upcoming

        for t in all_tasks:
            date, time = t[2].rsplit(' ', 1)

            if self.clean_date(date):
                task = Today()
                task.og_name = t[1]
                task.name = t[1].upper()
                task.time = time
                task.date = date
                task.size_hint = (None, 1)
                task.size = [scroll_parent.width/2.4, 45]

                itask = Today()
                itask.og_name = t[1]
                itask.name = t[1].upper()
                itask.time = time
                itask.date = date
                itask.size_hint = (None, None)
                itask.size = [scroll_parent.width /
                              2.4, round(scroll_parent.height/4)]

                tw.add_widget(task)
                self.ids.all_today.add_widget(itask)

            else:
                task = Upcoming()
                task.name = t[1].upper()
                task.og_name = t[1]
                task.time = ' '.join([date, time])
                task.date = date
                task.size_hint = (1, None)
                task.height = dp(100)

                itask = Upcoming()
                itask.name = t[1].upper()
                itask.og_name = t[1]
                itask.time = ' '.join([date, time])
                itask.date = date
                itask.size_hint = (1, None)
                itask.height = dp(100)

                uw.add_widget(task)
                self.ids.all_upcoming.add_widget(itask)

            # task.size = [100, 200]
        if len(tw.children) > 1:
            for child in tw.children:
                if type(child) == NewButton:
                    tw.remove_widget(child)

    def clean_date(self, date: str):
        today = datetime.today()
        _date = date.split('/')
        if len(_date) < 3:
            _date = date.split('-')
        date_ = [int(x) for x in reversed(_date)]

        task_date = datetime(date_[0], date_[1], date_[2])

        x = abs((today - task_date).days)

        if x == 0:
            return True
        else:
            return False

    def get_update(self, inst):
        nt = NewTask()
        nt.ids.task_name.text = inst.name
        nt.ids.task_time.text = inst.time
        nt.ids.task_date.text = inst.date
        nt.ids.submit_wrapper.clear_widgets()
        submit = Button(text='Update Task', background_normal='',
                        background_color=rgba('#0e5174'))
        submit.bind(on_release=lambda x: self.update_task(nt, inst))
        nt.ids.submit_wrapper.add_widget(submit)
        nt.open()

    def update_task(self, task_data, task):
        error = False
        xtask = [
            task_data.ids.task_name.text,
            task_data.ids.task_date.text,
            task_data.ids.task_time.text
        ]
        for t in xtask:
            if len(t) < 3:
                t.hint_text = 'Field required'
                t.hint.text_color = [1, 0, 0, 1]
                error = True
        if error:
            pass
        else:
            xtask = [xtask[0], ' '.join(xtask[1:]), task.og_name]
            if self.db.update_task(xtask):
                task.name = task_data.ids.task_name.text
                task.date = task_data.ids.task_date.text
                task.time = task_data.ids.task_time.text
            task_data.dismiss()

    def delete_task(self, task: Today):
        name = task.name
        if self.db.delete_task(name):
            task.parent.remove_widget(task)

    def add_new(self):
        nt = NewTask()
        nt.open()

    def add_task(self, mv, xtask: tuple):
        error = False
        scroll_parent = self.ids.scroll_parent
        tw = self.ids.today_wrapper
        uw = self.ids.upcoming

        for t in xtask:
            if len(t.text) < 3:
                t.hint_text = 'Field required'
                t.hint.text_color = [1, 0, 0, 1]
                error = True
        if error:
            pass
        else:
            date = ' '.join([xtask[1].text, xtask[2].text])
            task_ = (xtask[0].text, date)
            if self.clean_date(xtask[1].text):
                task = Today()
                task.og_name = xtask[0].text
                task.name = xtask[0].text.upper()
                task.time = xtask[2].text
                task.date = xtask[1].text
                task.size_hint = (None, None)
                task.size = [scroll_parent.width /
                             2.4, scroll_parent.height * .9]
                if self.db.add_task(task_):
                    tw.add_widget(task)
            else:
                task = Upcoming()
                task.og_name = xtask[0].text
                task.name = xtask[0].text.upper()
                task.time = xtask[2].text
                task.date = xtask[1].text
                task.size_hint = (1, None)
                task.height = dp(100)
                if self.db.add_task(task_):
                    uw.add_widget(task)

            # add task to db

            mv.dismiss()

            # check if we have enough tasks to show
            if len(tw.children) > 1:
                for child in tw.children:
                    if type(child) == NewButton:
                        tw.remove_widget(child)

    def add_user(self, username, password):
        if len(username.text) < 3 or len(password.text) < 6:
            pass
        else:
            user = (username.text, password.text)

            if self.db.add_user(user):
                self.ids.scrn_mngr.current = 'scrn_signin'

    def auth_user(self, username, password):
        uname = username.text
        upass = password.text

        if self.db.auth_user((uname, upass)):

            self.ids.scrn_mngr.current = 'scrn_main'

        username.text = ''
        password.text = ''
