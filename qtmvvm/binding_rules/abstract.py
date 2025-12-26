from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from qtpy.QtWidgets import QWidget
from qtpy.QtCore import Signal

from qtmvvm.binding_state import BindingState

if TYPE_CHECKING:
    from qtmvvm.observable_property import ObservableProperty, T


class AbstractBindingRule(ABC):
    def __init__(self, initial_signal: Signal = None):
        self._initial_signal = initial_signal

    @abstractmethod
    def propertyToWidget(
            self,
            observableProperty: ObservableProperty[T],
            state: BindingState
    ) -> None:
        ...

    @abstractmethod
    def widgetToProperty(
            self,
            observableProperty: ObservableProperty[T],
            state: BindingState
    ) -> None:
        ...

    def createBindingState(self, widget: QWidget, property: str):
        bindingState = BindingState(widget, property, self._initial_signal)

        metaObject = widget.metaObject()
        propertyIndex = metaObject.indexOfProperty(property)
        if propertyIndex == -1:
            return bindingState
        metaProperty = metaObject.property(propertyIndex)
        if not metaProperty.hasNotifySignal() or self._initial_signal is not None:
            return bindingState
        metaSignal = metaProperty.notifySignal()
        bindingState.signal = getattr(widget, metaSignal.name().data().decode("utf-8"))
        return bindingState
