from typing import Literal

from qtpy.QtWidgets import (
    QWidget,
    QLabel, QLineEdit, QTextEdit, QPlainTextEdit,
    QCheckBox, QRadioButton, QDoubleSpinBox,
    QSlider, QProgressBar, QComboBox, QDateEdit, QTimeEdit, QDateTimeEdit,
    QDial, QScrollBar, QSpinBox,
    QListWidget, QTableWidget, QTextBrowser,
)

from qtmvvm.binding_rules import AbstractBindingRule, PropertyBindingRule


class BindingMixin:
    """Base mixin for widget binding"""

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
        return super().bind(widget, property, bindingRule, mode)

    def _get_default_property(self, widget: QWidget) -> str:
        """Returns default property for widget"""
        return "value"


class TextBindingMixin(BindingMixin):
    """Mixin for binding text widgets"""

    def bindText(self, widget: QWidget, mode: Literal["1-way", "2-way"] = "2-way"):
        """Binding to text content of widget"""
        if isinstance(widget, (QLineEdit, QTextEdit, QPlainTextEdit, QLabel, QTextBrowser)):
            return self.bind(widget, "text", mode=mode)
        raise TypeError(f"Widget {type(widget).__name__} does not support text binding")


class ValueBindingMixin(BindingMixin):
    """Mixin for binding numeric widgets"""

    def bindValue(self, widget: QWidget, mode: Literal["1-way", "2-way"] = "2-way"):
        """Binding to numeric value of widget"""
        if isinstance(widget, (QSpinBox, QDoubleSpinBox, QSlider, QProgressBar, QDial, QScrollBar)):
            return self.bind(widget, "value", mode=mode)
        raise TypeError(f"Widget {type(widget).__name__} does not support value binding")


class CheckBindingMixin(BindingMixin):
    """Mixin for binding widgets with checked state"""

    def bindChecked(self, widget: QWidget, mode: Literal["1-way", "2-way"] = "2-way"):
        """Binding to checked state"""
        if isinstance(widget, (QCheckBox, QRadioButton)):
            return self.bind(widget, "checked", mode=mode)
        raise TypeError(f"Widget {type(widget).__name__} does not support checked binding")


class CurrentIndexBindingMixin(BindingMixin):
    """Mixin for binding widgets with current index"""

    def bindCurrentIndex(self, widget: QWidget, mode: Literal["1-way", "2-way"] = "2-way"):
        """Binding to current index"""
        if isinstance(widget, (QComboBox, QListWidget, QTableWidget)):
            return self.bind(widget, "currentIndex", mode=mode)
        raise TypeError(f"Widget {type(widget).__name__} does not support currentIndex binding")


class CurrentTextBindingMixin(BindingMixin):
    """Mixin for binding current text in combobox"""

    def bindCurrentText(self, widget: QWidget, mode: Literal["1-way", "2-way"] = "2-way"):
        """Binding to current text"""
        if isinstance(widget, QComboBox):
            return self.bind(widget, "currentText", mode=mode)
        raise TypeError(f"Widget {type(widget).__name__} does not support currentText binding")


class DateTimeBindingMixin(BindingMixin):
    """Mixin for binding date/time widgets"""

    def bindDateTime(self, widget: QWidget, mode: Literal["1-way", "2-way"] = "2-way"):
        """Binding to date/time"""
        if isinstance(widget, (QDateEdit, QTimeEdit, QDateTimeEdit)):
            return self.bind(widget, "dateTime", mode=mode)
        raise TypeError(f"Widget {type(widget).__name__} does not support dateTime binding")

    def bindDate(self, widget: QWidget, mode: Literal["1-way", "2-way"] = "2-way"):
        """Binding to date"""
        if isinstance(widget, QDateEdit):
            return self.bind(widget, "date", mode=mode)
        raise TypeError(f"Widget {type(widget).__name__} does not support date binding")

    def bindTime(self, widget: QWidget, mode: Literal["1-way", "2-way"] = "2-way"):
        """Binding to time"""
        if isinstance(widget, QTimeEdit):
            return self.bind(widget, "time", mode=mode)
        raise TypeError(f"Widget {type(widget).__name__} does not support time binding")


class SuperBindingMixin(
    TextBindingMixin,
    ValueBindingMixin,
    CheckBindingMixin,
    CurrentIndexBindingMixin,
    CurrentTextBindingMixin,
    DateTimeBindingMixin
):
    """
    Super mixin combining all binding methods.
    Provides universal bindAuto method for automatic binding.
    """

    def bindAuto(self, widget: QWidget, mode: Literal["1-way", "2-way"] = "2-way"):
        """
        Automatic binding based on widget type.
        Automatically determines appropriate property and binding method.
        Raises ValueError if auto-binding is not supported for the widget type.
        """
        # Text widgets
        if isinstance(widget, (QLineEdit, QTextEdit, QPlainTextEdit, QTextBrowser)):
            return self.bindText(widget, mode=mode)
        # QLabel - only 1-way
        if isinstance(widget, QLabel):
            return self.bindText(widget, mode="1-way")
        # Numeric widgets
        if isinstance(widget, (QSpinBox, QDoubleSpinBox, QSlider, QProgressBar, QDial, QScrollBar)):
            return self.bindValue(widget, mode=mode)
        # Checkboxes and radio buttons
        if isinstance(widget, (QCheckBox, QRadioButton)):
            return self.bindChecked(widget, mode=mode)
        # ComboBox
        if isinstance(widget, QComboBox):
            return self.bindCurrentText(widget, mode=mode)
        # Date/time
        if isinstance(widget, QDateTimeEdit):
            return self.bindDateTime(widget, mode=mode)
        if isinstance(widget, QDateEdit):
            return self.bindDate(widget, mode=mode)
        if isinstance(widget, QTimeEdit):
            return self.bindTime(widget, mode=mode)
        # Lists and tables
        if isinstance(widget, QListWidget):
            return self.bindCurrentIndex(widget, mode=mode)
        if isinstance(widget, QTableWidget):
            return self.bindCurrentIndex(widget, mode=mode)

        # Auto-binding is not supported for this widget type
        raise ValueError(
            f"Auto-binding is not supported for widget type {type(widget).__name__}. "
            f"Use explicit bind() method with property name instead."
        )
