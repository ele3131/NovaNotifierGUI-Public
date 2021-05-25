import css
from sys import argv
from asyncio import sleep, create_task, set_event_loop, Event, \
                    CancelledError
from qasync import QEventLoop, asyncSlot
from PySide2 import QtCore
from PySide2.QtWidgets import QMainWindow, QWidget, QTableWidgetItem, \
                            QLabel, QVBoxLayout, QApplication
from PySide2.QtGui import QIcon, QPixmap
from motor.motor_asyncio import AsyncIOMotorClient
from additem import AddItem
from gui import MainWindow
from traceback import format_exc
from datetime import datetime
from json import load
from NovaNotifier import NovaNotifier
from discordwindow import Discord_window
from popup import Popup
from settings import Settings
from accounts import Accounts


class MainWindow0(QMainWindow, MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        try:
            self.not_running = True
            self.discord_channel = None
            self.discord_name = None
            self.tasks = {}

            with open('Files/TOKEN.json', 'r') as f:
                mongo_token = (load(f))["mongo_token"]

            if not mongo_token:
                raise ValueError("Missing mongo_token")

            self.db = AsyncIOMotorClient(mongo_token)
            self.nova_notifier = NovaNotifier(self)
            self.nova_notifier.read_settings()

            self.tasks['discord_check'] = create_task(self.discord_check())

            self.pause_event = Event()
            self.pause_retrieve = Event()

            self.setStyleSheet(css.gui_background())
            self.ui(self)

            self.btn_start.clicked.connect(self.start_program)
            self.btn_stop.clicked.connect(self.stop_notifier)
            self.btn_pause.clicked.connect(self.timer_pause)
            self.btn_opt.clicked.connect(self.open_settings)
            self.btn_discord.clicked.connect(self.discord_open)
            self.btn_refresh.clicked.connect(self.refresh_notifier)
            self.btn_add.clicked.connect(self.add_open)
            self.btn_accounts.clicked.connect(self.accounts_open)
            self.btn_help.clicked.connect(self.popup_help)
        except Exception:
            self.popup = Popup(format_exc())
            self.popup.critical()
            return

    def exception(self):
        self.popup = Popup(format_exc())
        self.popup.critical()
        self.btn_stop.click()

    @asyncSlot()
    async def open_settings(self):
        self.popup_settings = Settings(self)

    @asyncSlot()
    async def discord_open(self):
        self.popup_discord = Discord_window(self)

    async def discord_check(self):
        try:
            if data := await self.db.nova.users.find_one({"token": self.nova_notifier.settings['token']}):
                self.discord_channel = data['channel']
                self.discord_name = data['discord']
                await self.db.nova.users.update_one({'discord': self.discord_name}, {'$set': {'date': datetime.now()}})
        except Exception:
            self.exception()

    @asyncSlot()
    async def start_program(self):
        if self.not_running:
            self.tasks['start'] = create_task(self.start_routine())
            self.not_running = False
        else:
            self.timer_resume()

    async def start_routine(self):
        try:
            await self.tasks['discord_check']
            await self.nova_notifier.start()
            self.tasks["sold_notification"] = create_task(self.nova_notifier.sold_notification())
            self.tasks['timer'] = create_task(self.timer())
            await self.add_items()
            self.btn_accounts.show()
        except Exception:
            self.exception()
            return

        self.lbl_refresh.show()

    @asyncSlot()
    async def refresh_notifier(self):
        try:
            if self.tasks['timer']._state == 'PENDING':
                self.lbl_refresh.setText("Refreshing")
                self.tasks['refresh'] = await self.refresh_routine()
        except Exception:
            pass

    async def refresh_routine(self):
        try:
            self.timer_pause()
            self.pause_retrieve.set()
            await self.nova_notifier.refresh()
            await self.add_items()
            self.pause_retrieve.clear()
            self.refresh_timer = self.nova_notifier.settings['timer_refresh']
            self.timer_resume()
        except CancelledError:
            pass
        except Exception:
            self.exception()
            return

    def stop_notifier(self):
        try:
            for task in self.tasks.values():
                task.cancel()
        except Exception:
            pass

        self.pause_event.clear()

        self.tbl.setRowCount(0)
        self.tbl.horizontalHeader().hide()
        self.lbl_refresh.hide()
        self.lbl_acc.setText("")
        self.lbl_refresh.setText("")

        temp = self.nova_notifier.settings
        self.nova_notifier = NovaNotifier(self)
        self.nova_notifier.settings = temp

    @asyncSlot()
    async def add_open(self):
        self.popup_window = AddItem(self)

    @asyncSlot()
    async def accounts_open(self):
        self.accounts = Accounts(self)

    def popup_help(self):
        self.popup = Popup()
        self.popup.help()

    async def timer(self):
        try:
            self.pause_event.set()
            if self.nova_notifier.settings['timer_refresh'] > 60:
                self.refresh_timer = self.nova_notifier.settings['timer_refresh']
            else:
                self.refresh_timer = self.nova_notifier.settings['timer_refresh'] = 60
            while True:
                await self.pause_event.wait()
                if self.refresh_timer > 0:
                    self.refresh_timer -= 1
                    self.lbl_refresh.setText(f"Next Refresh: {self.refresh_timer}")
                    await sleep(1)
                else:
                    await self.refresh_notifier()
        except Exception:
            self.exception()

    def timer_pause(self):
        self.pause_event.clear()

    def timer_resume(self):
        self.pause_event.set()

    async def show_usernames(self, username_zeny):
        txt = ''
        for username, zeny in username_zeny.items():
            txt += f"\n<font color=\"#d9d9d9\">{username}</font><br><font color=\"#2ED03C\">{zeny}</font><br><br>"
        self.lbl_acc.setText(txt)

    async def show_notification(self, txt):
        self.lbl_last_notif.setText(txt)
        self.lbl_last_notif.setStyleSheet(css.lbl())

    async def add_items(self):
        self.tbl.setRowCount(0)
        self.tbl.horizontalHeader().show()

        for table_row in self.nova_notifier.result:
            row = self.tbl.rowCount()
            self.tbl.setRowCount(row + 1)
            for col, att in enumerate(table_row):
                if not col:
                    # Label Image
                    icon = QLabel()
                    icon.setAlignment(QtCore.Qt.AlignCenter)
                    icon.setPixmap(QPixmap(f"Files/Icons/Item/{table_row[0]}.png"))
                    # ID text
                    txt = QLabel(table_row[0])  # ID
                    txt.setStyleSheet("QLabel{ color:white; }")
                    txt.setAlignment(QtCore.Qt.AlignCenter)
                    # Add Everything to a layout
                    layout = QVBoxLayout()
                    layout.addWidget(icon)
                    layout.addWidget(txt)
                    # Make the widget
                    cellWidget = QWidget()
                    cellWidget.setLayout(layout)
                    self.tbl.setCellWidget(row, col, cellWidget)
                else:
                    cell = QTableWidgetItem(att)
                    cell.setTextAlignment(QtCore.Qt.AlignCenter)

                    if table_row[col] == '-':
                        cell.setForeground(self.font_color["gold"])

                    elif table_row[4] != '-' and col == 0 or col == 4 or col == 11:
                        if table_row[12] in self.nova_notifier.notify:  # Alert
                            cell.setForeground(self.font_color["alert"])
                            txt.setStyleSheet("QLabel { color: #2BD032; }")

                    elif col == 8:
                        if "+" in table_row[8]:  # Short med
                            cell.setForeground(self.font_color["no"])
                        else:
                            cell.setForeground(self.font_color["yes"])

                    elif col == 9:
                        if "+" in table_row[9]:  # Long med
                            cell.setForeground(self.font_color["no"])
                        else:
                            cell.setForeground(self.font_color["yes"])

                    self.tbl.setItem(row, col, cell)
        self.tbl.resizeRowsToContents()


def windowLauncher():
    app = QApplication(argv)
    app.setWindowIcon(QIcon('Files/Icons/App/main2.ico'))
    app.setStyleSheet(css.window())

    loop = QEventLoop(app)
    set_event_loop(loop)

    w = MainWindow0()
    w.show()
    loop.run_forever()


if __name__ == "__main__":
    windowLauncher()
