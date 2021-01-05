def gui_background():
    return """
    QMainWindow{
    background-color: #000000;
    }
    """


def window():
    return """
    QApplication{
    background-color: #000000;
    }
    """


def btn_start():
    return """
    QPushButton{
    background-color: #141414;
    border-style:outset;
    border-width:2px;
    border-radius:10px;
    border-color:#F09E20;
    color:#E1AD27;
    font:11px;
    padding:3px;
    min-width:6em;
    }
    
    QPushButton::hover{
    background-color: #343436;
    }
    
    QPushButton::pressed{
    background-color: #1A1A20;
    }
    
    """


def btn():
    return """
    QPushButton{
    background-color: #E1AD27;
    border-style:outset;
    border-width:2px;
    border-radius:10px;
    border-color:#F09E20;
    color:#000000;
    font:11px;
    font-weight:bold;
    padding:3px;
    min-width:6em;
    }
    
    QPushButton::hover{
    background-color: #FFD500;
    }
    
    QPushButton::pressed{
    background-color: #F09E20;
    }
    """


def btn_opt():
    return """
    QPushButton{
    background-color: #E1AD27;
    border-style:outset;
    border-width:2px;
    border-radius:10px;
    border-color:#F09E20;
    width: 10px;
    color:#000000;
    font:11px;
    font-weight:bold;
    padding:3px;
    min-width:6em;
    }
    
    QPushButton::hover{
    background-color: #FFD500;
    }
    
    QPushButton::pressed{
    background-color: #F09E20;
    }
    """


def tbl():
    return """
    QTableView{
    background-color: #1E1E1E;
    border-style:outset;
    border-width:2px;
    border-radius:10px;
    border-color:#F09E20;
    color:#E0DEDE;
    font:11px;
    padding:3px;
    min-width:6em;
    }

    QTableCornerButton::section{
    background-color: #fff;
    }

    QTableWidget::item{
    border-left:4px solid #161616;
    border-radius:2px;
    }
    """


"""
add
margin: 0px 20px 0px 20px;
under background-color if you want to remove the scrollbar
"""


def scrollbar():
    return """

    QScrollBar:vertical {
        background-color: #1E1E1E;
    }

    QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical{
        background-color: #1E1E1E;
    }

    QScrollBar::handle:vertical{
        background-color: #141414;
    }
    """


def lbl():
    return """
        QLabel{
        font:11px;
        color:#E1AD27;
        border-width:0px;
        border-radius:0px;
        }
        """


def lbl_white():
    return """
        QLabel{
        font:11px;
        color:#EBFFFF;
        border-width:0px;
        border-radius:0px;
        }
        """


def lbl_title():
    return """
    QLabel{
    font:16px;
    color:#E1AD27;
    border-width:0px;
    border-radius:0px;
    }
    """


def lbl_acc():
    return """
    QLabel{
    font:11px;
    color:#2ED03C;
    border-width:0px;
    border-radius:0px;
    }
    """


def lbl_refresh():
    return """
    QLabel{
    font:11px;
    color:#29D03C;
    border-width:0px;
    border-radius:0px;
    }
    """


def notif():
    return """
    background-color:#141414;
    font:11px;
    color:#E1AD27;
    border-style:outset;
    border-width:2px;
    border-radius:10px;
    padding:3px;
    border-color:#F09E20;
    """


def header():
    return """
    QHeaderView{
    background-color:#141414;
    }

    QHeaderView::section{
    background-color:#141414;
    color:#E1AD27;
    font:11px;
    }
    
    QHeaderView{
    background-color:#141414;
    }
    """


def container():
    return """
    background-color:#141414;
    border-style:outset;
    border-width:2px;
    border-radius:10px;
    border-color:#F09E20;
    """


"""
    Add Item Popup
"""



def popup():
    return """
    QWidget{
    background-color: #141414;
    }
    """


def line_edit():
    return """
    QLineEdit{
    background-color: #1E1E1E;
    color: #E1AD21;
    border-style:outset;
    border-width:2px;
    border-radius:10px;
    padding:3px;
    border-color:#F09E20;
    }
    """


def lbl_popup():
    return """
    QLabel{
    font:11px;
    color:#E1AD27;
    border-width:0px;
    border-radius:0px;
    }
    """


def del_btn():
    return """
    QPushButton{
    background-color: #141414;
    color: #E0DEDE;
    font:11px;
    font-weight:bold;
    padding:3px;
    min-width:6em;
    }
    
    QPushButton::hover{
    background-color: #1E1E1E;
    }
    
    QPushButton::pressed{
    background-color: #161616;
    }
    """


def rbtn():
    return """
    QRadioButton{
    background-color: #141414;
    color: #E1AD27;
    }
    
    QRadioButton::indicator::unchecked{
    border: 1px solid #E1AD27;
    background-color: #1E1E1E;
    }
    
    QRadioButton::indicator::checked{
    border: 1px solid #E1AD27;
    background-color: #F09E20;
    }
    """

# #2D2D2D #161616
