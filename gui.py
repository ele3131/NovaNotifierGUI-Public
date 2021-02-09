import css
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import QPushButton, QSpacerItem, QSizePolicy, QButtonGroup, \
                            QStackedWidget, QLabel, QWidget, QVBoxLayout, QHBoxLayout, \
                            QTableWidgetItem, QTableWidget, QTreeView
from PyQt5.QtGui import QColor, QIcon


class MainWindow(object):
    def ui(self, MainWindow0):
        self.setWindowTitle('Nova Notifier')

        tbl_data = ["TEST" for i in range(13)]
        tbl_data = []
        headers = ['ID', 'NAME', 'REFINE', 'PROP', 'PRICE', 'EA',
                   'SHORT MED', 'LONG MED', 'SM%', 'LM%', 'ALERT', 'LOCATION']
        # time_last = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        # self.notification = ''

        self.item_index = 0
        self.font_color = {"alert": QColor(46, 208, 60), "yes": QColor(43, 126, 35),
                           "no": QColor(148, 33, 24), "default": QColor(255, 255, 255),
                           "gold": QColor(255, 173, 39)}

        """
        Widgets
        """

        self.vertical_spacer = QSpacerItem(60, 20, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.horizontal_spacer = QSpacerItem(60, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.custom_spacer = QSpacerItem(60, 10)

        self.btn_add_item = QPushButton('ADD ITEM')
        self.btn_help = QPushButton('HELP')
        self.btn_start = QPushButton('START')
        self.btn_stop = QPushButton('STOP')
        self.btn_pause = QPushButton('PAUSE')
        self.btn_resume = QPushButton('RESUME')
        self.btn_refresh = QPushButton('REFRESH')

        # Button groups
        self.btn_grp = QButtonGroup()
        self.btn_grp.setExclusive(True)
        self.btn_grp.addButton(self.btn_pause)
        self.btn_grp.addButton(self.btn_resume)
        self.btn_grp.addButton(self.btn_start)
        self.btn_grp.addButton(self.btn_stop)
        self.btn_grp.buttonClicked.connect(self.switch_buttons)

        # Button stacks
        self.stk_pause_resume = QStackedWidget()
        self.stk_pause_resume.setMaximumWidth(self.stk_pause_resume.width() / 2)
        self.stk_pause_resume.addWidget(self.btn_pause)
        self.stk_pause_resume.addWidget(self.btn_resume)
        self.stk_start_stop = QStackedWidget()
        self.stk_start_stop.setMaximumHeight(20)
        self.stk_start_stop.addWidget(self.btn_start)

        # Options buttons
        self.btn_opt = QPushButton()
        self.btn_opt.setIcon(QIcon('Icons/cog.png'))
        self.btn_opt.setIconSize(QSize(24, 24))
        self.btn_opt.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.btn_opt.setFixedWidth(25)
        self.btn_discord = QPushButton()
        self.btn_discord.setIcon(QIcon('Icons/discord.ico'))
        self.btn_discord.setIconSize(QSize(24, 24))
        self.btn_discord.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.btn_discord.setFixedWidth(25)

        self.lbl_refresh = QLabel(' ')
        self.lbl_last_notif = QLabel('Host: Not Hosting!')
        self.lbl_accounts = QLabel('ACCOUNTS: ')
        self.lbl_acc = QLabel(' ')
        self.lbl_acc.setAlignment(Qt.AlignCenter)
        self.lbl_acc.setWordWrap(True)
        self.tbl = QTableWidget(len(tbl_data), len(headers))
        self.tbl.setVerticalScrollMode(QTreeView.ScrollPerPixel)
        self.tbl.setHorizontalHeaderLabels(headers)
        self.tbl.setCornerButtonEnabled(False)
        self.tbl.horizontalHeader().setSectionResizeMode(True)
        self.tbl.verticalHeader().setSectionResizeMode(False)
        self.tbl.verticalHeader().setMinimumSectionSize(70)
        col = 0
        for i, item in enumerate(tbl_data):
            tbl_items = QTableWidgetItem(item)
            tbl_items.setForeground(self.font_color["yes"])
            tbl_items.setFlags(Qt.ItemIsEnabled)
            self.tbl.setItem(i, col, tbl_items)
            col += 1

        """
        Layouts
        """

        self.lyt_top = QHBoxLayout()
        for i in [self.stk_start_stop, self.btn_refresh, self.btn_add_item, self.btn_help]:
            self.lyt_top.addWidget(i)

        self.lyt_items = QVBoxLayout()
        self.lyt_items.addWidget(self.tbl)

        self.container_lyt_accounts = QWidget()
        self.lyt_accounts = QVBoxLayout(self.container_lyt_accounts)
        self.lyt_accounts.addWidget(self.lbl_accounts)
        self.lyt_accounts.addItem(self.custom_spacer)
        self.lyt_accounts.addWidget(self.lbl_acc)
        self.lyt_accounts.addItem(self.vertical_spacer)
        self.lyt_accounts.addWidget(self.btn_opt)
        self.lyt_accounts.addWidget(self.btn_discord)

        self.container_lyt_notif = QWidget()
        self.lyt_notif = QHBoxLayout(self.container_lyt_notif)
        self.lyt_notif.addWidget(self.lbl_last_notif)
        self.lyt_notif.addItem(self.horizontal_spacer)
        self.lyt_notif.addWidget(self.lbl_refresh)

        self.container_lyt_stop_pause = QWidget()
        self.lyt_stop_pause = QHBoxLayout(self.container_lyt_stop_pause)
        self.lyt_stop_pause.setContentsMargins(0, 0, 0, 0)
        self.lyt_stop_pause.addWidget(self.btn_stop)
        self.lyt_stop_pause.addWidget(self.stk_pause_resume)
        self.stk_start_stop.addWidget(self.container_lyt_stop_pause)

        self.lyt_bottom = QHBoxLayout()
        self.lyt_bottom.addWidget(self.container_lyt_accounts)
        self.lyt_bottom.addLayout(self.lyt_items)

        self.lyt_main = QVBoxLayout()
        self.lyt_main.addLayout(self.lyt_top)
        self.lyt_main.addWidget(self.container_lyt_notif)
        self.lyt_main.addLayout(self.lyt_bottom)

        widget = QWidget()
        widget.setLayout(self.lyt_main)
        self.setCentralWidget(widget)
        # self.setFixedSize(1287, 260)
        self.resize(1400, 600)

        """
            Styling
        """

        for i in [self.btn_start, self.btn_stop, self.btn_pause, self.btn_resume,
                  self.btn_refresh, self.btn_help, self.btn_add_item]:
            i.setStyleSheet(css.btn())
        self.btn_opt.setStyleSheet(css.btn_opt())
        self.btn_discord.setStyleSheet(css.btn_opt())

        self.tbl.setStyleSheet(css.tbl())
        self.tbl.horizontalHeader().setStyleSheet(css.header())
        self.tbl.verticalHeader().setStyleSheet(css.header())
        self.tbl.horizontalScrollBar().setStyleSheet(css.scrollbar())
        self.tbl.verticalScrollBar().setStyleSheet(css.scrollbar())

        self.lbl_acc.setStyleSheet(css.lbl_acc())
        self.lbl_accounts.setStyleSheet(css.lbl())
        self.lbl_refresh.setStyleSheet(css.lbl())
        self.lbl_last_notif.setStyleSheet(css.lbl())

        self.container_lyt_notif.setStyleSheet(css.notif())
        self.container_lyt_accounts.setStyleSheet(css.container())

    def switch_buttons(self, btn):
        if btn.text() == "PAUSE":
            self.stk_pause_resume.setCurrentIndex(1)
        if btn.text() == "RESUME":
            self.stk_pause_resume.setCurrentIndex(0)
        if btn.text() == "START":
            self.stk_start_stop.setCurrentIndex(1)
        if btn.text() == "STOP":
            self.stk_start_stop.setCurrentIndex(0)
