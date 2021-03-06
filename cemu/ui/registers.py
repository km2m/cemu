from typing import Dict

from PyQt5.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QTableWidget,
    QLabel,
    QTableWidgetItem,
    QWidget,
    QDockWidget,
)

from PyQt5.QtGui import(
    QFont,
    QColor
)

from PyQt5.QtCore import (
    Qt,
    pyqtSignal,
    QEvent,
)

from ..utils import format_address


class RegistersWidget(QDockWidget):

    refreshRegisterGridSignal = pyqtSignal()

    def __init__(self, parent, *args, **kwargs):
        super(RegistersWidget, self).__init__("Registers", parent)
        self.root = self.parentWidget()
        self.log = self.root.log
        self.emulator = self.root.emulator
        self.__row_size = 15
        self.__old_register_values = {}
        layout = QVBoxLayout()
        self.__values = QTableWidget(10, 2)
        self.__values.horizontalHeader().setStretchLastSection(True)
        self.__values.setHorizontalHeaderLabels(["Register", "Value"])
        layout.addWidget(self.__values)
        widget = QWidget()
        widget.setLayout(layout)
        self.setWidget(widget)
        self.updateGrid()

        # define signals
        self.refreshRegisterGridSignal.connect(self.onRefreshRegisterGrid)
        self.root.signals["refreshRegisterGrid"] = self.refreshRegisterGridSignal
        return


    def updateGrid(self) -> None:
        """
        Refresh the grid values from the current values of the
        VM CPU registers
        """
        emu = self.emulator
        arch = self.root.arch
        registers = arch.registers
        self.__values.setRowCount(len(registers))
        for i, reg in enumerate(registers):
            self.__values.setRowHeight(i, self.__row_size)
            name = QTableWidgetItem(reg)
            name.setFlags(Qt.NoItemFlags)
            val = emu.get_register_value(reg) if emu.vm else 0
            old_val = self.__old_register_values.get(reg, 0)
            if type(val) in (int, int):
                value = format_address(val, arch)
            else:
                value = str(val)
            value = QTableWidgetItem( value )
            if old_val != val:
                self.__old_register_values[reg] = val
                value.setForeground(QColor(Qt.red))
            value.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable)
            self.__values.setItem(i, 0, name)
            self.__values.setItem(i, 1, value)
        return


    def getRegisterValues(self) -> Dict[str,int]:
        """
        Returns the current values of the registers, as shown by the widget grid
        """
        regs = {}
        arch = self.root.arch
        for i in range(len(arch.registers)):
            name = self.__values.item(i, 0).text()
            value = self.__values.item(i, 1).text()
            regs[name] = int(value, 16)
        return regs


    def onRefreshRegisterGrid(self) -> None:
        self.updateGrid()
        return