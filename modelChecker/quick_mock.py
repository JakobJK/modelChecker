from PySide2 import QtWidgets, QtCore, QtGui
import maya.OpenMayaUI as omui
from shiboken2 import wrapInstance

def maya_main_window():
    """
    Return the Maya main window widget as a Python object
    """
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)

class MyWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=maya_main_window()):
        super(MyWindow, self).__init__(parent)

        mainQWidget = QtWidgets.QWidget(self)
        self.setCentralWidget(mainQWidget)
        mainLayout = QtWidgets.QVBoxLayout(mainQWidget)

        self.table_widget = QtWidgets.QTableWidget()

        # Allow extended selection (like in Windows Explorer)
        self.table_widget.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.table_widget.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)

        self.table_widget.setStyleSheet("""
            QTableWidget::item:selected {
                background-color: #87bdd8;
            }
        """)

        # Configure the table
        self.table_widget.setColumnCount(5)
        self.table_widget.setHorizontalHeaderLabels(['', 'Select', 'Context', 'Tests', 'Status'])
        self.table_widget.verticalHeader().setVisible(False)
        self.table_widget.setColumnWidth(0, 10)
        self.table_widget.setColumnWidth(1, 50)
        self.table_widget.setColumnWidth(2, 200)
        self.table_widget.itemClicked.connect(self.on_item_clicked)

        # Fill the table
        for i in range(10):
            empty_item = QtWidgets.QTableWidgetItem()
            check_item = QtWidgets.QTableWidgetItem()
            check_item.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
            check_item.setCheckState(QtCore.Qt.Unchecked)
            item = QtWidgets.QTableWidgetItem("Item {}".format(i))

            status_item = QtWidgets.QTableWidgetItem()
            status_icon = self.style().standardIcon(
                QtWidgets.QStyle.SP_DialogApplyButton if i % 2 == 0 else QtWidgets.QStyle.SP_DialogCancelButton)
            status_item.setIcon(status_icon)

            self.table_widget.insertRow(i)
            self.table_widget.setItem(i, 0, empty_item)
            self.table_widget.setItem(i, 1, check_item)
            self.table_widget.setItem(i, 2, item)
            self.table_widget.setItem(i, 4, status_item)

            # Set background color for every other row
            color = QtGui.QColor("#000000")
            empty_item.setBackground(color)
            check_item.setBackground(color)
            item.setBackground(color)
            status_item.setBackground(color)

        self.run_button = QtWidgets.QPushButton("Run")
        self.run_button.clicked.connect(self.on_run)

        mainLayout.addWidget(self.table_widget)
        mainLayout.addWidget(self.run_button)

    def on_run(self):
        for index in range(self.table_widget.rowCount()):
            check_item = self.table_widget.item(index, 1)
            if check_item.checkState() == QtCore.Qt.Checked:
                print("You selected: Item", index)
                                
    def on_item_clicked(self, item):
        # Check if any keyboard modifiers are held down
        modifiers = QtWidgets.QApplication.keyboardModifiers()
        if modifiers == QtCore.Qt.NoModifier:
            # This will only print when item is clicked without holding Shift, Ctrl or Alt
            print("You clicked: ", item.text())


# Then you create an instance of your window to show it:
win = MyWindow()
win.show()
