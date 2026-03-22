from typing import Any, Dict, Type

from qtpy.QtCore import QObject

from qtmvvm.observable_property import ObservableProperty


class ViewModelMeta(type(QObject)):
    """Metaclass for automatic conversion of fields to ObservableProperty"""

    def __new__(mcs, name: str, bases: tuple, attrs: Dict[str, Any]) -> Type:
        # Collect annotations from all base classes and current class
        annotations = {}
        for base in bases:
            if hasattr(base, '__annotations__'):
                annotations.update(getattr(base, '__annotations__', {}))

        # Add annotations from current class
        if '__annotations__' in attrs:
            annotations.update(attrs['__annotations__'])

        # Convert regular fields to ObservableProperty
        for field_name, field_type in annotations.items():
            if field_name in attrs and field_name not in ('_computed_properties',):
                value = attrs[field_name]
                # If value is not yet ObservableProperty, wrap it
                if not isinstance(value, ObservableProperty):
                    attrs[field_name] = ObservableProperty(value)

        cls = super().__new__(mcs, name, bases, attrs)
        return cls


class BaseViewModel(QObject, metaclass=ViewModelMeta):
    """
    Base class for ViewModel in Pydantic style.
    Automatically converts annotated fields to ObservableProperty.

    Example:
        class PersonViewModel(BaseViewModel):
            name: str = "John"
            age: int = 18
    """

    def __init__(self, parent: Any = None, **kwargs):
        """Initialize ViewModel with ability to override values"""
        QObject.__init__(self, parent)

        # Get all annotations
        annotations = getattr(self.__class__, '__annotations__', {})

        # Initialize fields that are not yet initialized
        for field_name, field_type in annotations.items():
            if not hasattr(self, field_name):
                # Create ObservableProperty with default value
                object.__setattr__(self, field_name, ObservableProperty(None, parent=self))

        # Set values from kwargs
        for field_name, value in kwargs.items():
            if hasattr(self, field_name):
                attr = object.__getattribute__(self, field_name)
                if isinstance(attr, ObservableProperty):
                    attr.value = value

    def __setattr__(self, name: str, value: Any) -> None:
        """Automatically sets value in ObservableProperty"""
        if name.startswith('_'):
            object.__setattr__(self, name, value)
            return

        attr = object.__getattribute__(self, name)
        if isinstance(attr, ObservableProperty):
            # Don't set ObservableProperty as value
            if isinstance(value, ObservableProperty):
                return
            attr.value = value
        else:
            object.__setattr__(self, name, value)
