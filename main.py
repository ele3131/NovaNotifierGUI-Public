import css
from sys import argv
from asyncio import sleep, create_task, set_event_loop, Event, \
                    CancelledError
from asyncqt import QEventLoop, asyncSlot
from PyQt5.QtWidgets import QMainWindow, QWidget, QTableWidgetItem, \
                            QLabel, QVBoxLayout, QApplication
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5 import QtCore
from motor.motor_asyncio import AsyncIOMotorClient
from additem import AddItem
from gui import MainWindow
from popup import Popuphelp, Popupdelete, PopupDiscord, PopupAll, PopupSettings
from datetime import datetime
from traceback import format_exc
from NovaNotifier import NovaNotifier


# Tokens / Sensitive information should be hidden with .env file (Environment Variables)
TKN_MONGOdb = 'Insert Here Your MongoDB Token'


class MainWindow0(QMainWindow, MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Discord bot & Mongodb
        self.db = AsyncIOMotorClient(TKN_MONGOdb)
        self.nova_notifier = NovaNotifier()
        self.nova_notifier.read_settings()
        self.channel = None
        create_task(self.get_host())

        self.pause_event = Event()
        self.pause_retrieve = Event()

        self.setStyleSheet(css.gui_background())
        self.ui(self)

        self.btn_start.clicked.connect(self.start_program)
        self.btn_stop.clicked.connect(self.stop_notifier)
        self.btn_pause.clicked.connect(self.timer_pause)
        self.btn_resume.clicked.connect(self.timer_resume)
        self.btn_opt.clicked.connect(self.open_settings)
        self.btn_discord.clicked.connect(self.discord_integration)
        self.btn_refresh.clicked.connect(self.refresh_notifier)
        self.btn_add_item.clicked.connect(self.add_popup)
        self.btn_help.clicked.connect(self.popup_help)

    async def check_bot(self):
        time_last = (await self.db.nova.notifier.find_one({'name': 'session'}))['last_update']
        time_since = datetime.utcnow() - time_last
        seconds_since = int(time_since.total_seconds())
        return seconds_since if seconds_since > 25 else False

    async def get_host(self):
        bot_on = False
        if channel := await self.db.nova.users.find_one({"token": self.nova_notifier.settings['token']}):
            self.channel = channel['channel']
            self.nova_notifier.channel = self.channel
            await self.db.nova.users.update_one({'channel': channel['channel']}, {"$set": {'date': datetime.utcnow()}})

        while True:
            if not bot_on and await self.check_bot():
                from discordbot import NovaBot
                NovaBot(self.db, self.channel, self.lbl_last_notif)
                bot_on = True
            if bot_on:
                pass
                #self.lbl_last_notif.setText("<font color=\"#2ED03C\">Host: Hosting!")
            else:
                pass
                #self.lbl_last_notif.setText("Host: Not Hosting!")

            await sleep(15)

    @asyncSlot()
    async def open_settings(self):
        self.nova_notifier.read_settings()
        self.popup_settings = PopupSettings(self.nova_notifier.settings)
        self.popup_settings.btn_save.clicked.connect(self.submit_settings)
        self.popup_settings.btn_reset_cache.clicked.connect(self.reset_cache)
        self.popup_settings.btn_reset_discord.clicked.connect(self.reset_discord)
        self.popup_settings.show()

    @asyncSlot()
    async def submit_settings(self):
        key = ['SM', 'LM', 'median_filter', 'sell_filter', 'timer_refresh']
        for no, i in enumerate(self.popup_settings.lines):
            if i.text():
                self.nova_notifier.settings[key[no]] = int(i.text())
            i.setText("")
        if self.popup_settings.rbtn_firefox.isChecked():
            self.nova_notifier.settings['browser'] = 'firefox'
        elif self.popup_settings.rbtn_chrome.isChecked():
            self.nova_notifier.settings['browser'] = 'chrome'
        else:
            self.nova_notifier.settings['browser'] = 'none'

        if self.nova_notifier.settings['timer_refresh'] < 60:
             self.nova_notifier.settings['timer_refresh'] = 60

        self.popup_settings.close()
        self.nova_notifier.write_settings()

    @asyncSlot()
    async def reset_cache(self):
        msg = 'Do you want to reset medians?'
        self.popup_confirm = Popupdelete(msg)
        self.popup_confirm.btn_yes.clicked.connect(self.nova_notifier.medians_reset)
        self.popup_confirm.btn_yes.clicked.connect(self.btn_stop.click)
        self.popup_confirm.btn_yes.clicked.connect(self.popup_confirm.close)
        self.popup_confirm.btn_no.clicked.connect(self.popup_confirm.close)

    @asyncSlot()
    async def reset_discord(self):
        self.channel = None
        self.nova_notifier.channel = self.channel
        self.nova_notifier.settings['token'] = None
        self.nova_notifier.write_settings()

        # msg = 'Do you want to reset discord?'
        # self.popup_confirm = Popupdelete(msg)
        # self.popup_confirm.btn_yes.clicked.connect(self.nova_notifier.discord_reset)
        # self.popup_confirm.btn_yes.clicked.connect(self.popup_confirm.close)
        # self.popup_confirm.btn_no.clicked.connect(self.popup_confirm.close)

    @asyncSlot()
    async def discord_integration(self):
        self.nova_notifier.read_settings()

        if not self.channel:
            self.popup_discord = PopupDiscord()
            self.popup_discord.btn_submit.clicked.connect(self.submit_token)
        else:
            self.create_popup(title='Discord', message='Discord is Running')

    @asyncSlot()
    async def submit_token(self):
        token = self.popup_discord.line_tkn.text()
        if data := await self.db.nova.users.find_one({"token": token}):
            self.nova_notifier.settings['token'] = token
            self.nova_notifier.write_settings()
            self.channel = data['channel']
            self.nova_notifier.channel = self.channel
            self.create_popup(title='Success', message="Token Confirmed!")
            self.popup_discord.close()
        else:
            self.create_popup(title='Error', message='Token Invalid')

    @asyncSlot()
    async def start_program(self):
        self.tasks = {}
        self.nova_notifier.db = self.db
        self.nova_notifier.tasks = self.tasks
        self.tasks['retrieving'] = create_task(self.retrieving())
        self.tasks['start'] = create_task(self.start_routine())

    async def start_routine(self):
        try:
            self.pause_retrieve.set()
            self.nova_notifier.channel = self.channel
            await self.nova_notifier.start()
            # await self.show_usernames()
            await self.add_items()
            self.pause_retrieve.clear()
            self.tasks['timer'] = create_task(self.timer())
            if self.nova_notifier.settings['browser'] != 'none':
                self.tasks["Sold Notification"] = create_task(self.nova_notifier.sold_notification(
                                                              self.nova_notifier.username_cookie, self.show_usernames, 
                                                              self.show_notification, self.pause_event))
            await self.nova_notifier.price_notification()
        except CancelledError:
            return
        except:
            self.create_popup(title='Error', message=format_exc())
            self.btn_stop.click()
            return

    @asyncSlot()
    async def refresh_notifier(self):
        try:
            if self.tasks['timer']._state == 'PENDING':
                self.tasks['refresh'] = create_task(self.refresh_routine())
        except:
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
            await self.nova_notifier.price_notification()
        except CancelledError:
            pass
        except:
            self.create_popup(title='Error', message=format_exc())
            self.btn_stop.click()
            return

    def stop_notifier(self):
        try:
            for task in self.tasks.values():
                task.cancel()
        except:
            pass

        self.pause_event.clear()

        self.tbl.setRowCount(0)
        self.lbl_refresh.setText("")
        self.lbl_acc.setText("")

        temp = self.nova_notifier.settings
        self.nova_notifier = NovaNotifier()
        self.nova_notifier.settings = temp

    @asyncSlot()
    async def add_popup(self):
        self.pause_event.clear()

        if not self.nova_notifier.items:
            self.nova_notifier.read_item()

        self.popup_window = AddItem()
        self.popup_window.gui_init(self.nova_notifier.items, self.pause_event)
        self.popup_window.btn_back.clicked.connect(self.popup_window.close)
        self.popup_window.btn_back.clicked.connect(self.pause_event.set)
        self.popup_window.btn_back.clicked.connect(self.refresh_notifier)

    def create_popup(self, title=None, message=None):
        self.new_popup = PopupAll(title=title, message=message)
        self.new_popup.btn_close.clicked.connect(self.new_popup.close)

    def popup_help(self):
        self.popup_help = Popuphelp()

    async def timer(self):
        self.pause_event.set()
        if self.nova_notifier.settings['timer_refresh'] > 60:
            self.refresh_timer = self.nova_notifier.settings['timer_refresh'] 
        else:
            self.nova_notifier.settings['timer_refresh'] = 60
            self.refresh_timer = self.nova_notifier.settings['timer_refresh']
        while True:
            await self.pause_event.wait()
            if self.refresh_timer > 0:
                self.refresh_timer -= 1
                self.lbl_refresh.setText("Next Refresh: %d" % self.refresh_timer)
                self.lbl_refresh.setStyleSheet(css.lbl())
                await sleep(1)
            else:
                await self.refresh_notifier()

    def timer_pause(self):
        self.pause_event.clear()

    def timer_resume(self):
        self.pause_event.set()

    async def show_usernames(self):
        txt = ''
        for username, zeny in self.nova_notifier.username_zeny.items():
            txt += f"\n<font color=\"#ffc100\">{username}</font><br><font color=\"#2ED03C\">{zeny}</font><br><br>"
        self.lbl_acc.setText(txt)

    async def show_notification(self, item):
        time = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        self.lbl_last_notif.setText(f"<font color=\"#2ED03C\">Last Sell: {time} - {item}")
        #self.lbl_refresh.setStyleSheet(css.lbl())

    async def retrieving(self):
        i = 0
        dots = ['', '.', '..', '...']

        while True:
            await self.pause_retrieve.wait()
            self.lbl_refresh.setText(f"{self.nova_notifier.status_lbl}{dots[i]}")
            self.lbl_refresh.setStyleSheet(css.lbl_refresh())
            i += 1
            if i == 4:
                i = 0
            await sleep(0.5)

    async def add_items(self):
        self.tbl.setRowCount(0)
        for table_row in self.nova_notifier.result:
            row = self.tbl.rowCount()
            self.tbl.setRowCount(row + 1)
            for col, att in enumerate(table_row):
                if col == 0:  
                    # Create Label Image 
                    lbl = QLabel()
                    lbl.setAlignment(QtCore.Qt.AlignCenter)
                    lbl.setPixmap(QPixmap(f"Icons/{table_row[0]}.png"))
                    # Create ID text
                    txt = QLabel(table_row[0]) # ID
                    txt.setStyleSheet("QLabel { color: #fff; }")
                    txt.setAlignment(QtCore.Qt.AlignCenter)
                    # Add Everything to a layout
                    layout = QVBoxLayout()
                    layout.addWidget(lbl)
                    layout.addWidget(txt)
                    # Make the widget 
                    cellWidget = QWidget()
                    cellWidget.setLayout(layout)
                    self.tbl.setCellWidget(row, col, cellWidget)
                cell = QTableWidgetItem(str(att))
                cell.setFlags(QtCore.Qt.ItemIsEnabled)
                cell.setTextAlignment(QtCore.Qt.AlignCenter)

                if table_row[col] == '-':
                    cell.setForeground(self.font_color["gold"])

                elif table_row[4] != '-' and col == 0 or col == 4 or col == 11:
                    if table_row[12] in self.nova_notifier.notify: # Alert
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

                if not col:
                    self.tbl.setCellWidget(row, col, cellWidget)
                else:
                    self.tbl.setItem(row, col, cell)

        msg = 'Do you want to remove this item from the list?'
        self.tbl.cellDoubleClicked.connect(lambda: self.delete_confirmation(msg))

    @asyncSlot()
    async def delete_confirmation(self, msg):
        self.popup_confirm = Popupdelete(msg)
        self.popup_confirm.btn_yes.clicked.connect(self.delete_item)
        self.popup_confirm.btn_yes.clicked.connect(self.popup_confirm.close)
        self.popup_confirm.btn_no.clicked.connect(self.popup_confirm.close)

    @asyncSlot()
    async def delete_item(self):
        current_cell = self.tbl.currentRow()
        del self.nova_notifier.items[current_cell]
        del self.nova_notifier.result[current_cell]
        AddItem().save_data(self.nova_notifier.items)
        await self.add_items()


def windowLauncher():
    app = QApplication(argv)
    app.setWindowIcon(QIcon('Icons/icon.ico'))
    app.setStyleSheet(css.window())

    loop = QEventLoop(app)
    set_event_loop(loop)

    w = MainWindow0()
    w.show()
    loop.run_forever()


if __name__ == "__main__":
    windowLauncher()
