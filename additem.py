import css
from PyQt5.QtWidgets import QWidget, QLabel, QTableWidget, QLineEdit, \
                            QPushButton, QFormLayout, QTableWidgetItem, \
                            QVBoxLayout, QFrame
from PyQt5.QtGui import QIcon, QIntValidator
from PyQt5.QtCore import Qt
from popup import Popup, Popupdelete, PopupAll
from NovaNotifier import NovaNotifier


class AddItem(QWidget):
    def __init__(self):
        super().__init__()

    def gui_init(self, items, pause_event):
        self.nova_notifier = NovaNotifier()
        self.pause_event = pause_event
        self.items = items
        self.setStyleSheet(css.popup())
        self.setWindowTitle("Add Items")
        self.setWindowIcon(QIcon('Icons/icon.ico'))
        self.resize(950, 550)
        self.UI()
        self.display_item()
        self.show()

    def UI(self):

        tbl_data = []
        headers = ["ID", "Name", "Refine", "Properties", "Alert"]

        self.titleText = QLabel("Add Item")
        self.titleText.setAlignment(Qt.AlignCenter)

        self.tbl = QTableWidget(len(tbl_data), len(headers))
        self.tbl.setHorizontalHeaderLabels(headers)
        self.tbl.setCornerButtonEnabled(False)
        self.tbl.horizontalHeader().setSectionResizeMode(True)
        self.tbl.cellDoubleClicked.connect(self.delete_confirmation)

        self.lbl_tbl_title = QLabel("List of searched items / # Delete = Double Click Row")
        self.lbl_tbl_title.setAlignment(Qt.AlignCenter)
        self.lbl_id = QLabel("ID: ")
        self.lbl_refine = QLabel("Refine: ")
        self.lbl_property = QLabel("Property: ")
        self.lbl_alert = QLabel("Alert price: ")
        self.lbl_submit = QLabel("")

        self.line_id = QLineEdit()
        self.line_id.setValidator(QIntValidator())
        self.line_id.setPlaceholderText("Enter item ID | e.g. 32641")
        self.line_refine = QLineEdit()
        self.line_refine.setValidator(QIntValidator())
        self.line_refine.setPlaceholderText("Enter refine of item | e.g. 0 or 15 | Default: 0")
        self.line_property = QLineEdit()
        self.line_property.setPlaceholderText("Enter item property | e.g. Int Blessing, Runaway Magic | Default: None")
        self.line_alert_price = QLineEdit()
        self.line_alert_price.setPlaceholderText("Enter alert price | e.g. 20,000 | Default: 0")
        self.btn_submit = QPushButton("Add")
        self.btn_submit.clicked.connect(self.submit_items)
        self.btn_back = QPushButton("Save")
        self.btn_back.clicked.connect(lambda: self.save_data(self.items))
        # self.btn_test = QPushButton("Test")
        # self.btn_test.clicked.connect(self.display_item)

        """
            Layouts
        """

        self.mainLayout = QVBoxLayout()
        self.topLayout = QVBoxLayout()
        self.bottomLayout = QFormLayout()
        self.bottomButtonLayout = QFormLayout()
        self.bottomFrame = QFrame()

        self.topLayout.addWidget(self.lbl_tbl_title)
        self.topLayout.addWidget(self.tbl)
        self.bottomLayout.addRow(self.lbl_id, self.line_id)
        self.bottomLayout.addRow(self.lbl_refine, self.line_refine)
        self.bottomLayout.addRow(self.lbl_property, self.line_property)
        self.bottomLayout.addRow(self.lbl_alert, self.line_alert_price)
        # self.bottomLayout.addRow(self.btn_test)
        self.bottomFrame.setLayout(self.bottomLayout)
        self.bottomButtonLayout.addWidget(self.btn_submit)
        self.bottomButtonLayout.addWidget(self.btn_back)

        self.mainLayout.addLayout(self.topLayout)
        self.mainLayout.addWidget(self.bottomFrame)
        self.mainLayout.addLayout(self.bottomButtonLayout)

        self.setLayout(self.mainLayout)

        """
            Styling
        """

        self.tbl.setStyleSheet(css.tbl())
        self.tbl.horizontalHeader().setStyleSheet(css.header())
        self.tbl.verticalHeader().setStyleSheet(css.header())
        self.tbl.verticalScrollBar().setStyleSheet(css.scrollbar())

        self.lbl_tbl_title.setStyleSheet(css.notif())
        self.lbl_id.setStyleSheet(css.lbl_popup())
        self.lbl_refine.setStyleSheet(css.lbl_popup())
        self.lbl_property.setStyleSheet(css.lbl_popup())
        self.lbl_alert.setStyleSheet(css.lbl_popup())
        self.lbl_submit.setStyleSheet(css.lbl_popup())

        self.line_id.setStyleSheet(css.line_edit())
        self.line_refine.setStyleSheet(css.line_edit())
        self.line_property.setStyleSheet(css.line_edit())
        self.line_alert_price.setStyleSheet(css.line_edit())

        self.btn_submit.setStyleSheet(css.btn())
        self.btn_back.setStyleSheet(css.btn())

    def display_item(self):
        table = []
        self.tbl.setRowCount(0)
        for each in self.items.values():
            table = [each['id'], each['name'], '+' + str(each['refine']), ', '.join(each['property']), format(each['alert'], ',d') + 'z']
            row = self.tbl.rowCount()
            self.tbl.setRowCount(row + 1)
            col = 0
            for item in table:
                cell = QTableWidgetItem(item)
                cell.setFlags(Qt.ItemIsEnabled)
                cell.setTextAlignment(Qt.AlignCenter)
                self.tbl.setItem(row, col, cell)
                col += 1

    def delete_confirmation(self):
        self.popup_confirm = Popupdelete('Do you want to remove this item from the list?')
        self.popup_confirm.btn_yes.clicked.connect(self.delete_item)
        self.popup_confirm.btn_yes.clicked.connect(self.popup_confirm.close)
        self.popup_confirm.btn_no.clicked.connect(self.popup_confirm.close)

    def delete_item(self):
        current_cell = self.tbl.currentRow()
        i = 0
        for key in self.items.keys():
            if i == current_cell:
                del(self.items[key])
                break
            i += 1
        self.display_item()

    def submit_items(self):
        new_item = self.filter_inputs()
        if not new_item:
            return
        self.add_data(new_item)
        self.display_item()
        self.popup_window = Popup()
        self.line_id.setText("")
        self.line_refine.setText("")
        self.line_property.setText("")
        self.line_alert_price.setText("")

    def filter_inputs(self):
        new_item = []

        if line := self.line_id.text().strip():
            new_item.append(line)
        else:
            self.popup_all = PopupAll(title='Error', message='ID Empty')
            self.popup_all.btn_close.clicked.connect(self.popup_all.close)
            return

        if line := self.line_refine.text().strip():
            new_item.append(line)
        else:
            new_item.append('0')

        if line := self.line_property.text().strip():
            new_item.append(line)
        else:
            new_item.append('None')

        if line := self.line_alert_price.text().strip():
            try:
                new_item.append(int(line.replace(',', '').replace('.', '').replace(' ', '')))
            except:
                self.popup_all = PopupAll(title='Error', message='Alert Invalid')
                self.popup_all.btn_close.clicked.connect(self.popup_all.close)
                return
        else:
            new_item.append(0)

        return new_item

    def add_data(self, new_item):
        prop = sorted([item.strip() for item in new_item[2].split(',')])
        prop_key = ', '.join(prop)
        self.items[str((new_item[0], new_item[1], prop_key))] = {'id': new_item[0],
                                                                 'name': 'Unknown',
                                                                 'refine': int(new_item[1]),
                                                                 'property': prop,
                                                                 'alert': int(new_item[3]),
                                                                 'short_med': None,
                                                                 'long_med': None}

    def save_data(self, items):
        self.nova_notifier.save_data(items)

    def closeEvent(self, event):
        self.pause_event.set()
        # self.save_data(self.items)
        event.accept()
