import css
from PySide2.QtWidgets import QWidget, QTableWidget, QLineEdit, \
                            QPushButton, QTableWidgetItem, QVBoxLayout, \
                            QMenu, QAbstractScrollArea, QHeaderView, \
                            QAbstractItemView
from PySide2.QtGui import QIcon, QIntValidator
from PySide2.QtCore import Qt, QEvent, QTimer
from popup import Popup
import copy


class AddItem(QWidget):
    def __init__(self, main):
        super().__init__()

        self.resize_flag = False
        self.main = main

        if not self.main.nova_notifier.items:
            self.main.nova_notifier.read_item()

        self.items = copy.deepcopy(self.main.nova_notifier.items)
        self.names = self.main.nova_notifier.names

        self.setStyleSheet(css.popup())
        self.setWindowTitle("Add Items")
        self.setWindowIcon(QIcon('Files/Icons/App/add-file.svg'))
        self.UI()

        self.tbl.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.tbl.setSelectionBehavior(QTableWidget.SelectRows)
        self.tbl.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.resize_flag = True
        self.show_table()
        self.show()

    def resizeEvent(self, event):
        if self.resize_flag:
            self.resize_flag = False
            self.timer.singleShot(1000, self.restore_headers)
            self.tbl.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def restore_headers(self):
        self.resize_flag = True
        self.tbl.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.tbl.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)

    def UI(self):
        """
            Widgets
        """

        headers = ["ID", "Name", "Refine", "Properties", "Alert"]

        self.timer = QTimer()

        self.tbl = QTableWidget(0, len(headers))
        self.tbl.setHorizontalHeaderLabels(headers)
        self.tbl.verticalHeader().hide()
        self.tbl.setFocusPolicy(Qt.NoFocus)
        self.tbl.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tbl.viewport().installEventFilter(self)

        self.line_id = QLineEdit()
        self.line_id.setValidator(QIntValidator(0, 1_000_000_000))
        self.line_id.setPlaceholderText("Enter ID")
        self.line_id.setToolTip("Example: 32641")
        self.line_id.setAlignment(Qt.AlignHCenter)

        self.line_refine = QLineEdit()
        self.line_refine.setValidator(QIntValidator(0, 100))
        self.line_refine.setPlaceholderText("Enter Refine")
        self.line_refine.setToolTip("Example: 10 \nDefault: 0")
        self.line_refine.setAlignment(Qt.AlignHCenter)

        self.line_property = QLineEdit()
        self.line_property.setPlaceholderText("Enter Properties")
        self.line_property.setToolTip("Example: Fire, Fighting Spirit, Any \nDefault: None\nOptional: Any")
        self.line_property.setAlignment(Qt.AlignHCenter)

        self.line_alert_price = QLineEdit()
        self.line_alert_price.setValidator(QIntValidator())
        self.line_alert_price.setPlaceholderText("Enter Alert Price")
        self.line_alert_price.setToolTip("Example: 20.000.000 \nDefault: 0")
        self.line_alert_price.setAlignment(Qt.AlignHCenter)

        self.btn_submit = QPushButton("Add")
        self.btn_save = QPushButton("Save")

        """
            Layouts
        """

        width = self.frameGeometry().width()/6
        self.lyt_top = QVBoxLayout()

        self.lyt_top.addWidget(self.tbl)

        self.lyt_mid = QVBoxLayout()
        self.lyt_mid.setContentsMargins(width, 10, width, 10)
        self.lyt_mid.addWidget(self.line_id)
        self.lyt_mid.addWidget(self.line_refine)
        self.lyt_mid.addWidget(self.line_property)
        self.lyt_mid.addWidget(self.line_alert_price)

        self.lyt_bottom = QVBoxLayout()
        self.lyt_bottom.addWidget(self.btn_submit)
        self.lyt_bottom.addWidget(self.btn_save)
        self.lyt_bottom.setContentsMargins(width, 10, width, 10)

        self.lyt_main = QVBoxLayout()
        self.lyt_main.addLayout(self.lyt_top)
        self.lyt_main.addLayout(self.lyt_mid)
        self.lyt_main.addLayout(self.lyt_bottom)

        self.setLayout(self.lyt_main)

        """
            Connects
        """
        self.tbl.customContextMenuRequested.connect(self.generateMenu)
        self.btn_submit.clicked.connect(self.submit_items)
        self.btn_save.clicked.connect(self.save_data)
        self.btn_save.clicked.connect(self.stop_notifier)
        self.btn_save.clicked.connect(self.close)

        """
            Styling
        """

        self.tbl.setStyleSheet(css.tbl())
        self.tbl.horizontalHeader().setStyleSheet(css.header())
        self.tbl.verticalHeader().setStyleSheet(css.header())
        self.tbl.verticalScrollBar().setStyleSheet(css.scrollbar())
        self.tbl.horizontalScrollBar().setStyleSheet(css.scrollbar())

        self.line_id.setStyleSheet(css.line_edit())
        self.line_refine.setStyleSheet(css.line_edit())
        self.line_property.setStyleSheet(css.line_edit())
        self.line_alert_price.setStyleSheet(css.line_edit())

        self.btn_submit.setStyleSheet(css.btn())
        self.btn_save.setStyleSheet(css.btn())

    def eventFilter(self, source, event):
        if(event.type() == QEvent.MouseButtonPress and
           event.buttons() == Qt.RightButton and
           source is self.tbl.viewport()):

            self.edit_item = self.tbl.itemAt(event.pos())
            if self.edit_item is not None:
                # print('Table Item:', self.edit_item.row(), self.edit_item.column())
                self.menu = QMenu(self)
                self.menu.setStyleSheet(css.menu())
                self.edit = self.menu.addAction('Edit')
                self.remove = self.menu.addAction('Remove')

        return super(AddItem, self).eventFilter(source, event)

    def generateMenu(self, pos):
        try:
            click = self.menu.exec_(self.tbl.mapToGlobal(pos))
        except Exception:
            return

        if click == self.edit:
            lines = [self.line_id, None, self.line_refine, self.line_property, self.line_alert_price]
            for i, line in enumerate(lines):
                if i == 1:
                    continue
                elif i == 2:
                    line.setText(self.tbl.item(self.edit_item.row(), i).text().replace('+', ''))
                elif i == 4:
                    line.setText(self.tbl.item(self.edit_item.row(), i).text().replace('z', '').replace(',', '.'))
                else:
                    line.setText(self.tbl.item(self.edit_item.row(), i).text())
        if click == self.remove:
            self.delete_confirmation()

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

    def delete_confirmation(self):
        self.popup = Popup('Remove from the List?')
        self.popup.question()
        self.popup.btn_yes.clicked.connect(self.delete_item)
        self.popup.btn_yes.clicked.connect(self.popup.close)
        self.popup.btn_no.clicked.connect(self.popup.close)

    def delete_item(self):
        current_cell = self.tbl.currentRow()
        i = 0
        for key in self.items.keys():
            if i == current_cell:
                del(self.items[key])
                break
            i += 1
        self.show_table()

    def submit_items(self):
        new_item = self.filter_inputs()
        if not new_item:
            return
        self.add_data(new_item)
        self.show_table()
        self.popup = Popup("Item Added!")
        self.popup.info()
        self.line_id.setText("")
        self.line_refine.setText("")
        self.line_property.setText("")
        self.line_alert_price.setText("")

    def filter_inputs(self):
        new_item = []

        if line := (self.line_id.text()).replace('.', ''):
            new_item.append(line)
        else:
            self.popup = Popup('ID Empty!')
            self.popup.warning()
            return

        if line := (self.line_refine.text()).replace('.', ''):
            new_item.append(line)
        else:
            new_item.append('0')

        if line := self.line_property.text().strip():
            new_item.append(line)
        else:
            new_item.append('None')

        if line := (self.line_alert_price.text()).replace('.', ''):
            new_item.append(line)
        else:
            new_item.append(0)

        return new_item

    def add_data(self, new_item):
        prop = [item.strip() for item in new_item[2].split(',')]
        prop_key = ', '.join(prop)
        self.items[str((new_item[0], new_item[1], prop_key))] = {'id': new_item[0],
                                                                 'name': self.names[new_item[0]] if new_item[0] in self.names else 'Unknown',
                                                                 'refine': int(new_item[1]),
                                                                 'property': prop,
                                                                 'alert': int(new_item[3]),
                                                                 'short_med': None,
                                                                 'long_med': None}

    def save_data(self, items):
        self.main.nova_notifier.save_data(self.items)

    def stop_notifier(self, items):
        self.main.btn_stop.click()

    def closeEvent(self, event):
        event.accept()
