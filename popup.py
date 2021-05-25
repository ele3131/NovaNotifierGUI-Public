import css
from PySide2.QtWidgets import QLabel, QWidget, QVBoxLayout, QPushButton, \
                            QLineEdit, QHBoxLayout
from PySide2.QtGui import QIcon
from PySide2 import QtCore


class Popup(QWidget):
    def __init__(self, message=None):
        super().__init__()
        self.resize(300, 80)
        self.message = message

    def info(self):
        self.setWindowTitle("Information")
        self.setStyleSheet(css.popup())
        self.lbl_text = QLabel(self.message)
        self.lbl_text.setStyleSheet(css.lbl())
        self.lbl_text.setAlignment(QtCore.Qt.AlignCenter)

        self.btn_close = QPushButton("Close")
        self.btn_close.setStyleSheet(css.btn())
        self.btn_close.clicked.connect(self.close)

        container_lyt_done = QWidget()
        container_lyt_done.setStyleSheet(css.container())
        self.lyt_submain = QVBoxLayout(container_lyt_done)
        self.lyt_submain.addWidget(self.lbl_text)
        self.lyt_submain.addWidget(self.btn_close)

        self.lyt_main = QVBoxLayout()
        self.lyt_main.addWidget(container_lyt_done)
        self.setLayout(self.lyt_main)
        self.show()

    def question(self):

        self.setWindowTitle("Question")
        self.setStyleSheet(css.popup())
        self.lbl_text = QLabel(self.message)
        self.lbl_text.setStyleSheet(css.lbl())
        self.lbl_text.setAlignment(QtCore.Qt.AlignCenter)
        self.btn_yes = QPushButton("Yes")
        self.btn_yes.setStyleSheet(css.btn())
        self.btn_no = QPushButton("No")
        self.btn_no.setStyleSheet(css.btn())
        container_lyt_done = QWidget()
        container_lyt_done.setStyleSheet(css.container())
        self.lyt_button = QHBoxLayout()
        self.lyt_button.addWidget(self.btn_yes)
        self.lyt_button.addWidget(self.btn_no)
        self.lyt_submain = QVBoxLayout(container_lyt_done)
        self.lyt_submain.addWidget(self.lbl_text)
        self.lyt_submain.addLayout(self.lyt_button)

        self.lyt_main = QVBoxLayout()
        self.lyt_main.addWidget(container_lyt_done)
        self.setLayout(self.lyt_main)

        self.show()

    def help(self):

        self.resize(500, 80)
        self.setWindowTitle("Help")
        self.setStyleSheet(css.popup())

        msg = (
            """
            Nova Notifier can be used with or without Browsers\n

            - LogIn NovaRO Website and Select "Remember Me". (Browser can be closed afterwards)\n

            - If you selected 'None' Browser, take notice that Sell Notifications won't work\n

            Notes:\n

                Property - Copy/Paste Properties from NovaRO Website (separator = ',')\n
                Median - Calculated based on your Refine and Properties\n
                Cheap Column - Amount of Lowest Price Items / Amount of Items Below Median\n

            Important:\n

                - If your refine could not be found, an above refine will be show temporarily\n
                - For Elements, input only the element name (e.g: Water, Fire, Shadow...)\n

            Special Thanks:\n

            Timo#7531 (First User Interface)\n

            Support:\n

            Discord: Michel#3659\n
            Forum: www.novaragnarok.com/forum/topic/11837-novaro-tag-system-program
            """
        )

        self.lbl_text = QLabel(msg)
        self.lbl_text.setStyleSheet(css.lbl())
        self.lbl_text.setAlignment(QtCore.Qt.AlignCenter)
        container_lyt_done = QWidget()
        container_lyt_done.setStyleSheet(css.container())
        self.lyt_submain = QVBoxLayout(container_lyt_done)
        self.lyt_submain.addWidget(self.lbl_text)

        self.lyt_main = QVBoxLayout()
        self.lyt_main.addWidget(container_lyt_done)
        self.setLayout(self.lyt_main)

        self.show()

    def discord(self):
        self.resize(500, 80)
        self.setWindowTitle("Discord")
        self.setStyleSheet(css.popup())
        self.setWindowTitle("Discord Integration")
        self.setWindowIcon(QIcon('Files/Icons/App/discord.svg'))
        self.lbl_integration = QLabel("DM !start to NovaNotifier Bot")
        self.lbl_enter = QLabel("Token: ")
        self.line_tkn = QLineEdit()
        self.line_tkn.setPlaceholderText("Enter Token ID | e.g. e4d2")
        self.btn_submit = QPushButton("Submit")

        # Layouts
        self.lyt_submission = QHBoxLayout()
        self.lyt_submission.addWidget(self.lbl_enter)
        self.lyt_submission.addWidget(self.line_tkn)
        self.lyt_main = QVBoxLayout()
        self.lyt_main.addWidget(self.lbl_integration)
        self.lyt_main.addLayout(self.lyt_submission)
        self.lyt_main.addWidget(self.btn_submit)

        # CSS Style
        self.lbl_integration.setStyleSheet(css.lbl())
        self.lbl_enter.setStyleSheet(css.lbl())
        self.line_tkn.setStyleSheet(css.line_edit())
        self.btn_submit.setStyleSheet(css.btn())

        self.setLayout(self.lyt_main)
        self.show()

        # Connections
        self.btn_submit.clicked.connect(self.submit_token)

    def warning(self):
        self.setStyleSheet(css.popup())
        self.setWindowTitle("Warning")
        # self.setWindowIcon(QMessageBox.warning)

        self.lbl = QLabel(self.message)
        self.lbl.setStyleSheet(css.lbl())
        self.lbl.setAlignment(QtCore.Qt.AlignCenter)

        self.btn_close = QPushButton("Close")
        self.btn_close.setStyleSheet(css.btn())

        container_lyt_done = QWidget()
        container_lyt_done.setStyleSheet(css.container())

        self.lyt_submain = QVBoxLayout(container_lyt_done)
        self.lyt_submain.setContentsMargins(10, 10, 10, 10)
        self.lyt_submain.addWidget(self.lbl)
        self.lyt_submain.addWidget(self.btn_close)

        self.lyt_main = QVBoxLayout()
        self.lyt_main.addWidget(container_lyt_done)

        self.btn_close.clicked.connect(self.close)
        self.setLayout(self.lyt_main)
        self.show()

    def critical(self):
        self.resize(450, 80)
        self.setStyleSheet(css.popup())
        self.setWindowTitle("Critical")
        # self.setWindowIcon(QMessageBox.critical)

        self.lbl = QLabel(self.message)
        self.btn_close = QPushButton("Close")

        self.lyt_main = QVBoxLayout()
        self.lyt_main.addWidget(self.lbl)
        self.lyt_main.addWidget(self.btn_close)

        self.lbl.setStyleSheet(css.lbl())
        self.btn_close.setStyleSheet(css.btn())

        self.btn_close.clicked.connect(self.close)
        self.setLayout(self.lyt_main)
        self.show()
