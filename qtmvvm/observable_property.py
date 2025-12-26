import weakref
from typing import Generic, TypeVar, Literal

from qtpy.QtWidgets import QWidget
from qtpy.QtCore import QObject, Signal

from qtmvvm.binding_state import BindingState
from qtmvvm.binding_rules import AbstractBindingRule, PropertyBindingRule, SignalBindingRule

T = TypeVar("T")

class ObservableProperty(QObject, Generic[T]):
    valueChanged = Signal()

    def __init__(self, value: T):
        super().__init__()
        self._value = value

    # Signal connecting functions
    def bind(
            self,
            widget: QWidget,
            property: str,
            *,
            bindingRule: AbstractBindingRule = PropertyBindingRule(),
            mode: Literal["1-way", "2-way"] = "2-way"
    ):
        bindingState = bindingRule.createBindingState(widget, property)

        # property -> widget
        self.valueChanged.connect(lambda: self._onValueChanged(bindingState, bindingRule))
        self._onValueChanged(bindingState, bindingRule)

        # widget -> property
        if mode != "2-way":
            return
        if bindingState.signal is not None:
            bindingState.signal.connect(lambda *args: self._onSignal(bindingState, bindingRule, *args))

    def _onValueChanged(self, state: BindingState, bindingRule: AbstractBindingRule):
        if state.valueEditing:
            return
        with state:
            bindingRule.propertyToWidget(self, state)

    def _onSignal(self, state: BindingState, bindingRule: AbstractBindingRule, *args):
        if state.valueEditing:
            return
        with state:
            state.signal_value = args[0] if len(args) == 1 else None if len(args) == 0 else args
            bindingRule.widgetToProperty(self, state)

    # Proxy functions
    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value: T):
        self._value = value
        self.valueChanged.emit()

    def set(self, value: T):
        self.value = value

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
