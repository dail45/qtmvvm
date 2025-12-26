import weakref

from qtpy.QtWidgets import QWidget
from qtpy.QtCore import Signal


class BindingState:
    def __init__(
            self,
            widget: QWidget,
            property: str = None,
            signal: Signal = None
    ):
        self.weakRef = weakref.ref(widget)
        self.valueEditing = False
        self.property = property
        self.signal = signal
        self.signal_value = None

    @property
    def widget(self):
        return self.weakRef()

    def __enter__(self):
        self.valueEditing = True

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.valueEditing = False
