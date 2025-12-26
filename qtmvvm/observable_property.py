import weakref
from typing import Generic, TypeVar, Any, Literal, Callable

from PyQt6.QtWidgets import QWidget
from qtpy.QtCore import QObject, Signal

T = TypeVar("T")

class ObservableProperty(QObject, Generic[T]):
    valueChanged = Signal()

    def __init__(self, value: T):
        super().__init__()
        self._value = value
        self._type = type(value)

    # Signal connecting functions
    def bind(
            self,
            widget: QWidget,
            property: str,
            *,
            mode: Literal["1-way", "2-way"] = "2-way",
            propertyToWidget: Callable[["ObservableProperty[T]", QWidget, str], None] = None,
            widgetToProperty: Callable[["ObservableProperty[T]", QWidget, str], None] = None,
    ):
        if propertyToWidget is None:
            propertyToWidget = self._propertyToWidget
        if widgetToProperty is None:
            widgetToProperty = self._widgetToProperty

        metaObject = widget.metaObject()
        propertyIndex = metaObject.indexOfProperty(property)

        if propertyIndex == -1:
            return

        weakWidget = weakref.ref(widget)
        valueEditing = False

        # property -> widget
        def onValueChanged():
            nonlocal valueEditing

            if valueEditing:
                return
            widgetInstance = weakWidget()
            if widgetInstance is not None:
                valueEditing = True
                propertyToWidget(self, widgetInstance, property)
                # widgetInstance.setProperty(property, self._value)
                valueEditing = False

        self.valueChanged.connect(onValueChanged)

        # widget -> property
        if mode != "2-way":
            return
        metaProperty = metaObject.property(propertyIndex)

        if not metaProperty.hasNotifySignal():
            return

        def onSignal():
            nonlocal valueEditing

            if valueEditing:
                return
            widgetInstance = weakWidget()
            if widgetInstance is not None:
                valueEditing = True
                widgetToProperty(self, widgetInstance, property)
                # self.value = widgetInstance.property(property)
                valueEditing = False

        metaSignal = metaProperty.notifySignal()
        signal = getattr(widget, metaSignal.name().data().decode("utf-8"))
        signal.connect(onSignal)

    def _propertyToWidget(
            self,
            observableProperty: "ObservableProperty[T]",
            widget: QWidget,
            property: str
    ):
        widget.setProperty(property, observableProperty.value)

    def _widgetToProperty(
            self,
            observableProperty: "ObservableProperty[T]",
            widget: QWidget,
            property: str
    ):
        observableProperty.value = widget.property(property)


    # Proxy functions
    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value: T):
        self._value = value
        self.valueChanged.emit()

    def __repr__(self):
        return str(self.value)

    def __eq__(self, other):
        return self.value == other

    def __ne__(self, other):
        return self.value != other

    def __add__(self, other):
        return self.value + other

    def __radd__(self, other):
        return self + other

    def __iadd__(self, other):
        self.value += other
        return self

    def __sub__(self, other):
        return self.value - other

    def __isub__(self, other):
        self.value -= other
        return self

    def __rsub__(self, other):
        return other - self.value

    def __mul__(self, other):
        return self.value * other

    def __rmul__(self, other):
        return other * self.value

    def __imul__(self, other):
        self.value *= other
        return self

    def __mod__(self, other):
        return self.value % other

    def __rmod__(self, other):
        return other % self.value

    def __imod__(self, other):
        self.value %= other
        return self

    def __pow__(self, other):
        return self.value ** other

    def __rpow__(self, other):
        return other ** self.value

    def __ipow__(self, other):
        self.value **= other
        return self

    def __truediv__(self, other):
        return self.value / other

    def __floordiv__(self, other):
        return self.value // other

    def __gt__(self, other):
        return self.value > other

    def __lt__(self, other):
        return self.value < other

    def __ge__(self, other):
        return self.value >= other

    def __le__(self, other):
        return self.value <= other

    def __bool__(self):
        return bool(self.value)

    def __neg__(self):
        return -self.value

    def __abs__(self):
        return abs(self.value)

    def __pos__(self):
        return self.value

    def __len__(self):
        return len(self.value)

    def __or__(self, other):
        return self.value | other

    def __and__(self, other):
        return self.value & other

    def __rand__(self, other):
        return other & self.value

    def __iand__(self, other):
        self.value &= other
        return self

    def __xor__(self, other):
        return self.value ^ other

    def __rxor__(self, other):
        return other ^ self.value

    def __ixor__(self, other):
        self.value ^= other
        return self

    def __ror__(self, other):
        return other | self.value

    def __ior__(self, other):
        self.value |= other
        return self

    def __lshift__(self, other):
        return self.value << other

    def __rlshift__(self, other):
        return other << self.value

    def __ilshift__(self, other):
        self.value <<= other
        return self

    def __rshift__(self, other):
        return self.value >> other

    def __rrshift__(self, other):
        return other >> self.value

    def __irshift__(self, other):
        self.value >>= other
        return self

    def __round__(self, n=None):
        return round(self.value, n) if n is not None else round(self.value)

    def __int__(self):
        return int(self.value)

    def __float__(self):
        return float(self.value)

    def __complex__(self):
        return complex(self.value)

    def __index__(self):
        return int(self.value)

    def __invert__(self):
        return ~self.value
