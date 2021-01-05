import css
from PyQt5.QtWidgets import QLabel, QWidget, QVBoxLayout, QPushButton, \
                            QLineEdit, QHBoxLayout, QRadioButton, QFormLayout
from PyQt5.QtGui import QIcon, QIntValidator
from PyQt5 import QtCore


class Popup(QWidget):
    def __init__(self):
        super().__init__()
        self.resize(300, 80)
        self.setWindowTitle("Success")
        self.popup_confirmation()
        self.show()

    def popup_confirmation(self):
        self.setStyleSheet(css.popup())
        self.lbl_text3 = QLabel('Item successfully added!')
        self.lbl_text3.setStyleSheet(css.lbl())
        self.lbl_text3.setAlignment(QtCore.Qt.AlignCenter)
        container_lyt_done = QWidget()
        container_lyt_done.setStyleSheet(css.container())
        self.lyt_submain2 = QVBoxLayout(container_lyt_done)
        self.lyt_submain2.addWidget(self.lbl_text3)

        self.lyt_main = QVBoxLayout()
        self.lyt_main.addWidget(container_lyt_done)
        self.setLayout(self.lyt_main)


class Popupdelete(QWidget):
    def __init__(self, msg):
        super().__init__()
        self.setWindowTitle("Confirm")
        self.resize(300, 80)

        self.setStyleSheet(css.popup())
        self.lbl_text3 = QLabel(msg)
        self.lbl_text3.setStyleSheet(css.lbl())
        self.lbl_text3.setAlignment(QtCore.Qt.AlignCenter)
        self.btn_yes = QPushButton("Yes")
        self.btn_yes.setStyleSheet(css.btn())
        self.btn_no = QPushButton("No")
        self.btn_no.setStyleSheet(css.btn())
        container_lyt_done = QWidget()
        container_lyt_done.setStyleSheet(css.container())
        self.lyt_button = QHBoxLayout()
        self.lyt_button.addWidget(self.btn_yes)
        self.lyt_button.addWidget(self.btn_no)
        self.lyt_submain2 = QVBoxLayout(container_lyt_done)
        self.lyt_submain2.addWidget(self.lbl_text3)
        self.lyt_submain2.addLayout(self.lyt_button)

        self.lyt_main = QVBoxLayout()
        self.lyt_main.addWidget(container_lyt_done)
        self.setLayout(self.lyt_main)

        self.show()


class Popuphelp(QWidget):
    def __init__(self):
        super().__init__()
        self.resize(500, 80)
        self.setWindowTitle("Help")
        self.popup_confirmation()
        self.show()

    def popup_confirmation(self):
        self.setStyleSheet(css.popup())
        with open('Files/README.txt', 'r') as f:
            msg = f.read()
        self.lbl_text3 = QLabel(msg)

        self.lbl_text3.setStyleSheet(css.lbl())
        self.lbl_text3.setAlignment(QtCore.Qt.AlignCenter)
        container_lyt_done = QWidget()
        container_lyt_done.setStyleSheet(css.container())
        self.lyt_submain2 = QVBoxLayout(container_lyt_done)
        self.lyt_submain2.addWidget(self.lbl_text3)

        self.lyt_main = QVBoxLayout()
        self.lyt_main.addWidget(container_lyt_done)
        self.setLayout(self.lyt_main)


class PopupDiscord(QWidget):
    def __init__(self):
        super().__init__()
        self.resize(450, 80)
        self.setStyleSheet(css.popup())
        self.setWindowTitle("Discord Integration")
        self.setWindowIcon(QIcon('Icons/discord.ico'))
        self.menu()
        self.show()

    def menu(self):
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


class PopupAll(QWidget):
    def __init__(self, title=None, message=None):
        super().__init__()
        if message is None:
            message = "Error has occured"
        self.resize(450, 80)
        self.setStyleSheet(css.popup())
        self.setWindowTitle(title)
        self.setWindowIcon(QIcon('Icons/discord.ico'))

        self.lbl = QLabel(message)
        self.btn_close = QPushButton("Close")

        self.lyt_main = QVBoxLayout()
        self.lyt_main.addWidget(self.lbl)
        self.lyt_main.addWidget(self.btn_close)

        self.lbl.setStyleSheet(css.lbl())
        self.btn_close.setStyleSheet(css.btn())

        self.setLayout(self.lyt_main)
        self.show()


class PopupSettings(QWidget):
    def __init__(self, config):
        super().__init__()
        self.resize(450, 200)
        self.setStyleSheet(css.popup())
        self.setWindowTitle("Settings")
        self.setWindowIcon(QIcon('Icons/cog.png'))

        self.btn_save = QPushButton("Save")
        self.btn_reset_cache = QPushButton("Reset Median")
        self.btn_reset_discord = QPushButton("Reset Discord")
        self.line_short_median = QLineEdit()
        self.line_short_median.setPlaceholderText(f"Current Short Median: {format(config['SM'], ',d')} days")
        self.line_long_median = QLineEdit()
        self.line_long_median.setPlaceholderText(f"Current Long Median: {format(config['LM'], ',d')} days")
        self.line_median_filter = QLineEdit()
        self.line_median_filter.setPlaceholderText(f"Current Median Filter: {format(config['median_filter'], ',d')}z")
        self.line_sell_filter = QLineEdit()
        self.line_sell_filter.setPlaceholderText(f"Current Minimum Sell Notification: {format(config['sell_filter'], ',d')}z")
        self.line_time_interval = QLineEdit()
        self.line_time_interval.setPlaceholderText(f"Current refresh interval: {config['timer_refresh']} seconds")
        self.lbl_short_median = QLabel("Short Median: ")
        self.lbl_long_median = QLabel("Long Median: ")
        self.lbl_median_filter = QLabel("Median Filter: ")
        self.lbl_sell_filter = QLabel("Sell Filter: ")
        self.lbl_time_interval = QLabel("Refresh Time (seconds): ")

        self.lines = [self.line_short_median, self.line_long_median, self.line_median_filter, self.line_sell_filter, self.line_time_interval]
        self.labels = [self.lbl_short_median, self.lbl_long_median, self.lbl_median_filter, self.lbl_sell_filter, self.lbl_time_interval]

        self.rbtn_chrome = QRadioButton("Chrome", self)
        self.rbtn_firefox = QRadioButton("Firefox", self)
        self.rbtn_none = QRadioButton("None", self)
        self.lbl_browser_cookie = QLabel("Browser Cookie: ")
        if config['browser'] == 'firefox':
            self.rbtn_firefox.setChecked(True)
        elif config['browser'] == 'chrome':
            self.rbtn_chrome.setChecked(True)
        else:
            self.rbtn_none.setChecked(True)

        self.rbtn_chrome.setStyleSheet(css.rbtn())
        self.rbtn_firefox.setStyleSheet(css.rbtn())
        self.rbtn_none.setStyleSheet(css.rbtn())
        self.lbl_browser_cookie.setStyleSheet(css.lbl())
        self.btn_reset_cache.setStyleSheet(css.btn())
        self.btn_reset_discord.setStyleSheet(css.btn())
        self.btn_save.setStyleSheet(css.btn())

        self.lyt_inputs = QFormLayout()
        for line, label in zip(self.lines, self.labels):
            line.setValidator(QIntValidator())
            line.setStyleSheet(css.line_edit())
            label.setStyleSheet(css.lbl())
            self.lyt_inputs.addRow(label, line)

        self.lyt_rbtn = QHBoxLayout()
        self.lyt_rbtn.addWidget(self.rbtn_chrome)
        self.lyt_rbtn.addWidget(self.rbtn_firefox)
        self.lyt_rbtn.addWidget(self.rbtn_none)
        self.lyt_inputs.addRow(self.lbl_browser_cookie, self.lyt_rbtn)
        self.lyt_main = QVBoxLayout()
        self.lyt_main.addLayout(self.lyt_inputs)
        self.lyt_main.addWidget(self.btn_reset_cache)
        self.lyt_main.addWidget(self.btn_reset_discord)
        self.lyt_main.addWidget(self.btn_save)

        self.setLayout(self.lyt_main)
        self.show()


def clear_layout(layout):
    if layout:
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
            elif child.layout():
                clear_layout(child.layout())
