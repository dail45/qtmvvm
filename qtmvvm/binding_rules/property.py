from __future__ import annotations
from typing import TYPE_CHECKING

from qtmvvm.binding_rules import AbstractBindingRule

if TYPE_CHECKING:
    from qtmvvm.observable_property import ObservableProperty, T
    from qtmvvm.binding_state import BindingState


class PropertyBindingRule(AbstractBindingRule):
    def propertyToWidget(
            self,
            observableProperty: ObservableProperty[T],
            state: BindingState
    ):
        state.widget.setProperty(state.property, observableProperty.value)

    def widgetToProperty(
            self,
            observableProperty: ObservableProperty[T],
            state: BindingState
    ):
        observableProperty.value = state.widget.property(state.property)
