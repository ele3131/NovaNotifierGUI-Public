import css
from PySide2.QtCore import Qt, QSize, QTimer
from PySide2.QtWidgets import QLabel, QWidget, QPushButton, QTableWidget, \
                            QAbstractScrollArea, QAbstractItemView, QHBoxLayout, \
                            QVBoxLayout, QHeaderView, QGraphicsColorizeEffect
from PySide2.QtGui import QColor, QPixmap


class MainWindow(QWidget):
    def ui(self, MainWindow0):
        self.setWindowTitle('Nova Notifier')

        headers = ['ID', 'NAME', 'REFINE', 'PROP', 'PRICE', 'EA',
                   'SHORT MED', 'LONG MED', 'SM%', 'LM%', 'ALERT', 'LOCATION']

        self.resize_flag = False
        self.font_color = {"alert": QColor(46, 208, 60), "yes": QColor(43, 126, 35),
                           "no": QColor(148, 33, 24), "default": QColor(255, 255, 255),
                           "gold": QColor(255, 173, 39)}

        # Logo
        self.logo = QLabel()
        self.logo_img = QPixmap('Files/Icons/App/main.png')
        self.logo_img = self.logo_img.scaled(142, 85, Qt.KeepAspectRatio)
        self.logo.setPixmap(self.logo_img)
        self.logo.resize(self.logo_img.width()/4, self.logo_img.height()/4)

        # Top Buttons
        btn_names = ["btn_start", "btn_stop", "btn_pause",
                     "btn_refresh", "btn_opt", "btn_add",
                     "btn_discord", "btn_help", "btn_accounts"]

        self.buttons = []

        for button in btn_names:
            button_self = f"self.{button}"
            effect = f"self.{button}_effect"
            setattr(self, button, QPushButton(objectName=button_self))
            setattr(self, button + '_effect', QGraphicsColorizeEffect(self))
            eval(effect).setColor(Qt.white)
            eval(button_self).setGraphicsEffect(eval(effect))
            eval(button_self).setIconSize(QSize(64, 64))
            eval(button_self).installEventFilter(self)
            self.buttons.append(eval(button_self))

        # Timer
        self.resize_timer = QTimer()

        # Accounts
        self.lbl_refresh = QLabel()
        self.lbl_refresh.setAlignment(Qt.AlignCenter)
        self.lbl_accounts = QLabel('Accounts: ')
        self.lbl_acc = QLabel()
        self.lbl_acc.setAlignment(Qt.AlignCenter)
        self.lbl_acc.setWordWrap(True)

        # Table
        self.tbl = QTableWidget(0, len(headers))
        self.tbl.setHorizontalHeaderLabels(headers)
        self.tbl.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.tbl.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tbl.setSelectionMode(QAbstractItemView.NoSelection)
        self.tbl.setFocusPolicy(Qt.NoFocus)

        # Layouts
        self.lyt_top = QHBoxLayout()
        self.lyt_top.addWidget(self.logo)
        self.lyt_top.addStretch()
        self.lyt_top.addWidget(self.btn_stop)
        self.lyt_top.addWidget(self.btn_start)
        self.lyt_top.addWidget(self.btn_pause)
        self.lyt_top.addWidget(self.btn_refresh)
        self.lyt_top.addStretch()
        self.lyt_top.addWidget(self.btn_help)

        self.lyt_bottom = QHBoxLayout()
        self.lyt_bottom.addWidget(self.btn_opt)
        self.lyt_bottom.addStretch()
        self.lyt_bottom.addWidget(self.btn_accounts)
        self.lyt_bottom.addWidget(self.btn_add)
        self.lyt_bottom.addStretch()
        self.lyt_bottom.addWidget(self.btn_discord)

        self.lyt_main = QVBoxLayout()
        self.lyt_main.setContentsMargins(0, 0, 0, 0)
        self.lyt_main.addLayout(self.lyt_top)
        self.lyt_main.addWidget(self.lbl_refresh)
        self.lyt_main.addWidget(self.tbl)
        self.lyt_main.addLayout(self.lyt_bottom)

        widget = QWidget()
        widget.setLayout(self.lyt_main)
        self.setCentralWidget(widget)
        self.resize(self.frameGeometry().width()*1.8, self.frameGeometry().height()*1.1)

        # Styling
        self.btn_start.setStyleSheet(css.btn_start())
        self.btn_stop.setStyleSheet(css.btn_stop())
        self.btn_pause.setStyleSheet(css.btn_pause())
        self.btn_refresh.setStyleSheet(css.btn_refresh())
        self.btn_opt.setStyleSheet(css.btn_opt())
        self.btn_add.setStyleSheet(css.btn_add())
        self.btn_discord.setStyleSheet(css.btn_discord())
        self.btn_help.setStyleSheet(css.btn_help())
        self.btn_accounts.setStyleSheet(css.btn_accounts())

        self.tbl.setStyleSheet(css.tbl())
        self.tbl.horizontalHeader().setStyleSheet(css.header())
        self.tbl.horizontalScrollBar().setStyleSheet(css.scrollbar())
        self.tbl.verticalScrollBar().setStyleSheet(css.scrollbar())

        self.lbl_acc.setStyleSheet(css.lbl_acc())
        self.lbl_accounts.setStyleSheet(css.lbl())
        self.lbl_refresh.setStyleSheet(css.lbl_refresh())

        # Hides
        self.btn_stop.hide()
        self.btn_pause.hide()
        self.btn_refresh.hide()
        self.lbl_refresh.hide()
        self.tbl.verticalHeader().hide()
        self.tbl.horizontalHeader().hide()
        self.btn_accounts.hide()

        # Connects
        self.btn_start.clicked.connect(self.switch_start)
        self.btn_stop.clicked.connect(self.switch_stop)
        self.btn_pause.clicked.connect(self.switch_pause)

        self.resize_flag = True

    def eventFilter(self, source, event):
        num = event.type()
        if num == 127:
            name = source.objectName()
            effect = name + '_effect'
            eval(effect).setColor(QColor(255, 213, 0))
        elif num == 128:
            name = source.objectName()
            effect = name + '_effect'
            eval(effect).setColor(Qt.white)

        return super(MainWindow, self).eventFilter(source, event)

    def resizeEvent(self, event):
        if self.resize_flag:
            self.resize_flag = False
            self.resize_timer.singleShot(1000, self.restore_headers)
            self.tbl.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def restore_headers(self):
        self.resize_flag = True
        self.tbl.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.tbl.horizontalHeader().setSectionResizeMode(11, QHeaderView.Stretch)

    def switch_start(self):
        self.btn_start.hide()
        self.lbl_refresh.show()
        self.btn_pause.show()
        self.btn_refresh.show()
        self.btn_stop.show()

    def switch_stop(self):
        self.btn_stop.hide()
        self.btn_refresh.hide()
        self.btn_pause.hide()
        self.btn_start.show()
        self.not_running = True

    def switch_pause(self):
        self.btn_pause.hide()
        self.btn_start.show()
