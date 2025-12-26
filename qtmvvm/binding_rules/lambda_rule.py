from __future__ import annotations
from typing import TYPE_CHECKING, Callable

from qtpy.QtCore import Signal
from qtmvvm.binding_rules import PropertyBindingRule


if TYPE_CHECKING:
    from qtmvvm.observable_property import ObservableProperty, T
    from qtmvvm.binding_state import BindingState


class LambdaBindingRule(PropertyBindingRule):
    def __init__(
            self,
            signal: Signal = None,
            propertyToWidget: Callable[[ObservableProperty[T], BindingState], None] = None,
            widgetToProperty: Callable[[ObservableProperty[T], BindingState], None] = None
    ):
        super().__init__(signal)
        self._propertyToWidget = propertyToWidget
        self._widgetToProperty = widgetToProperty

    def propertyToWidget(
            self,
            observableProperty: ObservableProperty[T],
            state: BindingState
    ):
        if self._propertyToWidget is not None:
            self._propertyToWidget(observableProperty, state)

    def widgetToProperty(
            self,
            observableProperty: ObservableProperty[T],
            state: BindingState
    ):
        if self._widgetToProperty is not None:
            self._widgetToProperty(observableProperty, state)
