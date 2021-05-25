import css
from PySide2.QtWidgets import QWidget, QLabel, QPushButton, \
                            QTableWidgetItem, QVBoxLayout, QHBoxLayout, \
                            QRadioButton, QFormLayout
from PySide2.QtGui import QIcon
from PySide2.QtCore import Qt


class Accounts(QWidget):
    def __init__(self, main):
        super().__init__()

        self.main = main

        self.setStyleSheet(css.popup())
        self.setWindowTitle("Accounts")
        self.setWindowIcon(QIcon('Files/Icons/App/people.svg'))

        """
            Widgets
        """

        self.lbl_usernames = QLabel('Accounts:')
        self.lbl_characters_zeny = QLabel('Character Zeny:')
        self.lbl_total_zeny = QLabel('Total Zeny:')

        self.lbl_total_result = QLabel('')
        self.lbl_characters_result = QLabel('')

        self.radio_buttons = []
        for username in self.main.nova_notifier.usernames:
            btn = QRadioButton(username, self)
            btn.setStyleSheet(css.rbtn())
            btn.clicked.connect(self.account_change)
            self.radio_buttons.append(btn)

        if self.radio_buttons:
            self.radio_buttons[0].setChecked(True)

        self.btn_reload = QPushButton("Reload")

        """
            Stylesheets
        """

        self.lbl_usernames.setStyleSheet(css.lbl())
        self.lbl_characters_zeny.setStyleSheet(css.lbl())
        self.lbl_total_zeny.setStyleSheet(css.lbl())
        self.lbl_characters_result.setStyleSheet(css.lbl())
        self.lbl_total_result.setStyleSheet(css.lbl())
        self.btn_reload.setStyleSheet(css.btn())

        """
            Layouts
        """

        self.lyt_info = QFormLayout()

        self.lyt_rbtn = QHBoxLayout()
        for button in self.radio_buttons:
            self.lyt_rbtn.addWidget(button)

        self.lyt_info.addRow(self.lbl_usernames, self.lyt_rbtn)
        self.lyt_info.addRow(self.lbl_characters_zeny, self.lbl_characters_result)
        self.lyt_info.addRow(self.lbl_total_zeny, self.lbl_total_result)

        self.lyt_main = QVBoxLayout()
        self.lyt_main.setSpacing(6)
        self.lyt_main.addStretch()
        self.lyt_main.addLayout(self.lyt_info)
        self.lyt_main.addWidget(self.btn_reload)
        self.lyt_main.addStretch()

        self.lyt_main2 = QHBoxLayout()
        self.lyt_main2.addStretch()
        self.lyt_main2.addLayout(self.lyt_main)
        self.lyt_main2.addStretch()

        self.btn_reload.clicked.connect(self.main.nova_notifier.account_data)

        self.setLayout(self.lyt_main2)
        self.account_change()
        self.show()

    def show_table(self):
        table = []
        self.tbl.setRowCount(0)
        for each in self.items.values():
            table = [each['id'], each['name'], '+' + str(each['refine']), ', '.join(each['property']), format(each['alert'], ',d') + 'z']
            row = self.tbl.rowCount()
            self.tbl.setRowCount(row + 1)
            col = 0
            for item in table:
                cell = QTableWidgetItem(item)
                cell.setTextAlignment(Qt.AlignCenter)
                # cell.setFlags(Qt.ItemIsEnabled)
                self.tbl.setItem(row, col, cell)
                col += 1

    def account_change(self):
        for btn in self.radio_buttons:
            if btn.isChecked():
                username = btn.text()
                characters = self.main.nova_notifier.accounts[username]['characters']
                characters_zeny = self.main.nova_notifier.accounts[username]['characters_zeny']
                total_zeny = f"<font color=\"#2ED03C\">{self.main.nova_notifier.accounts[username]['total_zeny']}</font>"

                txt = ''
                for i, character in enumerate(characters):
                    if i == 0:
                        txt = txt + f"{character} - <font color=\"#2ED03C\">{characters_zeny[i]}</font>"
                    else:
                        txt = txt + f"<br><br>{character} - <font color=\"#2ED03C\">{characters_zeny[i]}</font>"

                self.lbl_characters_result.setText(txt)
                self.lbl_total_result.setText(total_zeny)
