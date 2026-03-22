from typing import Generic, TypeVar, Literal, Callable, Any, Union

from qtpy.QtWidgets import QWidget
from qtpy.QtCore import QObject, Signal

from qtmvvm.binding_state import BindingState
from qtmvvm.binding_rules import AbstractBindingRule, PropertyBindingRule
from qtmvvm.binding_mixins import SuperBindingMixin

T = TypeVar("T")


class ObservableProperty(SuperBindingMixin, QObject, Generic[T]):
    """
    Observable property with support for Qt widget bindings.

    Operators:
        >> : 1-way binding to widget (property -> widget)
        @  : 2-way binding to widget (property <-> widget)
        << : 1-way signal binding (signal -> property)
    """
    valueChanged = Signal(object)

    def __init__(self, value: T, parent: Any = None):
        super().__init__(parent)
        self._value = value

    # Signal connecting functions
    def bind(
            self,
            widget: QWidget,
            property: str = None,
            bindingRule: AbstractBindingRule = None,
            mode: Literal["1-way", "2-way"] = "2-way"
    ):
        if bindingRule is None:
            bindingRule = PropertyBindingRule()
        if property is None:
            property = self._get_default_property(widget)

        bindingState = bindingRule.createBindingState(widget, property)

        # property -> widget
        self.valueChanged.connect(lambda: self._onValueChanged(bindingState, bindingRule))
        self._onValueChanged(bindingState, bindingRule)

        # widget -> property
        if mode == "2-way" and bindingState.signal is not None:
            bindingState.signal.connect(self._onSignalBind(bindingState, bindingRule))

        return self

    def bindSignal(
            self,
            signal: Signal,
            modifyFunc: Callable[[Any], Any] = None
    ):
        """
        Bind property to signal (property -> signal).
        When property changes, the signal is emitted with the new value.
        """
        if modifyFunc is not None:
            self.valueChanged.connect(lambda v: signal.emit(modifyFunc(v)))
        else:
            self.valueChanged.connect(signal.emit)
        return self

    def _onValueChanged(self, state: BindingState, bindingRule: AbstractBindingRule):
        if state.valueEditing:
            return
        with state:
            bindingRule.propertyToWidget(self, state)

    def _onSignal(self, state: BindingState, bindingRule: AbstractBindingRule, signal_value):
        if state.valueEditing:
            return
        with state:
            state.signal_value = signal_value
            bindingRule.widgetToProperty(self, state)

    def _onSignalBind(
            self,
            bindingState: BindingState,
            bindingRule: AbstractBindingRule,
            modifyFunc: Callable[[Any], Any] = None
    ):
        def signalBindFunc(*args):
            signal_value = args[0] if len(args) == 1 else None if len(args) == 0 else args
            if modifyFunc is not None:
                signal_value = modifyFunc(signal_value)
            self._onSignal(bindingState, bindingRule, signal_value)
        return signalBindFunc

    # Binding operators
    def __rshift__(self, other: Any) -> "ObservableProperty[T]":
        """
        1-way binding: property >> widget
        property -> widget
        
        If other is QWidget - performs binding.
        Otherwise - returns proxied value operation.
        """
        if isinstance(other, tuple):
            widget, mode = other
        else:
            widget, mode = other, "1-way"

        if isinstance(widget, QWidget):
            self.bindAuto(widget, mode=mode)
            return self
        else:
            # If not a widget, return value (proxy behavior)
            return self._value >> other

    def __matmul__(self, other: Any) -> "ObservableProperty[T]":
        """
        2-way binding: property @ widget
        property <-> widget
        
        If other is QWidget - performs binding.
        Otherwise - returns proxied value operation.
        """
        if isinstance(other, tuple):
            widget, mode = other
        else:
            widget, mode = other, "2-way"

        if isinstance(widget, QWidget):
            self.bindAuto(widget, mode=mode)
            return self
        else:
            # If not a widget, return value (proxy behavior)
            return self._value @ other

    def __lshift__(self, other: Any) -> "ObservableProperty[T]":
        """
        1-way signal binding: signal << property
        signal -> property
        
        If other is Signal - performs binding.
        Otherwise - returns proxied value operation.
        """
        if isinstance(other, Signal):
            self.bindSignal(other)
            return self
        else:
            # If not a signal, return value (proxy behavior)
            return self._value << other

    # Proxy functions
    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value: T):
        self._value = value
        self.valueChanged.emit(value)

    def set(self, value: T):
        self.value = value

    def __call__(self, value: T = None) -> Union[T, None]:
        """
        If value is provided - set it, otherwise return the pure value.
        """
        if value is None:
            return self._value
        self.value = value
        return None

    def __repr__(self):
        return str(self._value)

    def __eq__(self, other):
        return self._value == other

    def __ne__(self, other):
        return self._value != other

    def __add__(self, other):
        return self._value + other

    def __radd__(self, other):
        return other + self._value

    def __iadd__(self, other):
        self._value += other
        self.valueChanged.emit(self._value)
        return self

    def __sub__(self, other):
        return self._value - other

    def __isub__(self, other):
        self._value -= other
        self.valueChanged.emit(self._value)
        return self

    def __rsub__(self, other):
        return other - self._value

    def __mul__(self, other):
        return self._value * other

    def __rmul__(self, other):
        return other * self._value

    def __imul__(self, other):
        self._value *= other
        self.valueChanged.emit(self._value)
        return self

    def __mod__(self, other):
        return self._value % other

    def __rmod__(self, other):
        return other % self._value

    def __imod__(self, other):
        self._value %= other
        self.valueChanged.emit(self._value)
        return self

    def __pow__(self, other):
        return self._value ** other

    def __rpow__(self, other):
        return other ** self._value

    def __ipow__(self, other):
        self._value **= other
        self.valueChanged.emit(self._value)
        return self

    def __truediv__(self, other):
        return self._value / other

    def __floordiv__(self, other):
        return self._value // other

    def __gt__(self, other):
        return self._value > other

    def __lt__(self, other):
        return self._value < other

    def __ge__(self, other):
        return self._value >= other

    def __le__(self, other):
        return self._value <= other

    def __bool__(self):
        return bool(self._value)

    def __neg__(self):
        return -self._value

    def __abs__(self):
        return abs(self._value)

    def __pos__(self):
        return self._value

    def __len__(self):
        return len(self._value)

    def __or__(self, other):
        return self._value | other

    def __and__(self, other):
        return self._value & other

    def __rand__(self, other):
        return other & self._value

    def __iand__(self, other):
        self._value &= other
        self.valueChanged.emit(self._value)
        return self

    def __xor__(self, other):
        return self._value ^ other

    def __rxor__(self, other):
        return other ^ self._value

    def __ixor__(self, other):
        self._value ^= other
        self.valueChanged.emit(self._value)
        return self

    def __lor__(self, other):
        return self._value | other

    def __ior__(self, other):
        self._value |= other
        self.valueChanged.emit(self._value)
        return self

    def __rlshift__(self, other):
        return other << self._value

    def __ilshift__(self, other):
        self._value <<= other
        self.valueChanged.emit(self._value)
        return self

    def __rrshift__(self, other):
        return other >> self._value

    def __irshift__(self, other):
        self._value >>= other
        self.valueChanged.emit(self._value)
        return self

    def __round__(self, n=None):
        return round(self._value, n) if n is not None else round(self._value)

    def __int__(self):
        return int(self._value)

    def __float__(self):
        return float(self._value)

    def __complex__(self):
        return complex(self._value)

    def __index__(self):
        return int(self._value)

    def __invert__(self):
        return ~self._value
