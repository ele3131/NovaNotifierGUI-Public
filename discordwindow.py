import css
from asyncio import create_task
from popup import Popup
from PySide2.QtCore import Qt
from PySide2.QtWidgets import QLabel, QWidget, QVBoxLayout, QPushButton, \
                              QLineEdit
from PySide2.QtGui import QIcon
from qasync import asyncSlot


class Discord_window(QWidget):
    def __init__(self, main):
        super().__init__()
        self.main = main
        self.main.nova_notifier.read_settings()

        self.show_window()
        create_task(self.loading_label())

    def show_window(self):

        self.setWindowTitle("Discord")
        self.setWindowIcon(QIcon('Files/Icons/App/discord.svg'))

        # Widgets

        self.lbl0 = QLabel("\n<font color=\"#d9d9d9\">Loading...</font>")
        self.lbl0.setAlignment(Qt.AlignCenter)

        self.lbl1 = QLabel("1 - Join The Server: " +
                           "<a href=\'https://discord.com/invite/r8qnHkQ'>" +
                           "<font size=4 color=#7289da>Link</a>")

        self.lbl1.setOpenExternalLinks(True)
        self.lbl1.setAlignment(Qt.AlignCenter)

        self.lbl2 = QLabel("2 - Send !start to: " +
                           "<a href=\'https://discord.com/channels/@me/744726126114373682'>" +
                           "<font size=4 color=#7289da>Link</a>")

        self.lbl2.setOpenExternalLinks(True)
        self.lbl2.setAlignment(Qt.AlignCenter)

        self.lbl3 = QLabel("3 - Enter Token: ")
        self.lbl3.setAlignment(Qt.AlignCenter)

        self.line_tkn = QLineEdit()
        self.line_tkn.setPlaceholderText("Token")
        self.line_tkn.setAlignment(Qt.AlignCenter)
        self.btn_submit = QPushButton("Submit")
        self.btn_discord = QPushButton("Reset Discord")

        # CSS Style
        self.setStyleSheet(css.popup())
        self.lbl0.setStyleSheet(css.lbl())
        self.lbl1.setStyleSheet(css.lbl())
        self.lbl2.setStyleSheet(css.lbl())
        self.lbl3.setStyleSheet(css.lbl())
        self.line_tkn.setStyleSheet(css.line_edit())
        self.btn_submit.setStyleSheet(css.btn())
        self.btn_discord.setStyleSheet(css.btn())

        # Layouts
        self.lyt_main = QVBoxLayout()
        self.lyt_main.addWidget(self.lbl0)
        self.lyt_main.addWidget(self.lbl1)
        self.lyt_main.addWidget(self.lbl2)
        self.lyt_main.addWidget(self.lbl3)
        self.lyt_main.addWidget(self.line_tkn)
        self.lyt_main.addWidget(self.btn_submit)
        self.lyt_main.addWidget(self.btn_discord)

        self.setLayout(self.lyt_main)

        self.show()
        self.resize(self.frameGeometry().width()*2, self.frameGeometry().height())

        # Connections
        self.btn_submit.clicked.connect(self.submit_token)
        self.btn_discord.clicked.connect(self.discord_reset)

    async def loading_label(self):
        await self.main.tasks['discord_check']
        if self.main.discord_channel:
            self.lbl0.setText(f"\n<font color=\"#2ED03C\">Online: {self.main.discord_name}</font>")
        else:
            self.lbl0.setText("\n<font color=\"#e32037\">Offline</font>")

    @asyncSlot()
    async def submit_token(self):
        token = self.line_tkn.text()
        if data := await self.main.db.nova.users.find_one({"token": token}):
            self.main.nova_notifier.settings['token'] = token
            self.main.nova_notifier.write_settings()
            self.main.discord_channel = data['channel']
            self.main.discord_name = data['discord']

            self.lbl0.setText(f"\n<font color=\"#2ED03C\">Online: {data['discord']}</font>")
            self.popup = Popup('Token Accepted!')
            self.popup.info()
            self.close()
        else:
            self.popup = Popup('Token Invalid!')
            self.popup.info()

    def discord_reset(self):
        self.popup = Popup('Reset discord?')
        self.popup.question()
        self.popup.btn_yes.clicked.connect(self.discord_reset_confirm)
        self.popup.btn_yes.clicked.connect(self.popup.close)
        self.popup.btn_no.clicked.connect(self.popup.close)

    def discord_reset_confirm(self):
        self.main.discord_channel = None
        self.main.nova_notifier.settings['token'] = None
        self.main.nova_notifier.write_settings()
        self.lbl0.setText("\n<font color=\"#e32037\">Offline</font>")
