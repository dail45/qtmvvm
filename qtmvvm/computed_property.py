from typing import TypeVar, Callable, Any, List, Union

from qtpy.QtCore import QObject, Signal

from qtmvvm.observable_property import ObservableProperty

T = TypeVar("T")


class ComputedProperty(ObservableProperty[T]):
    """
    Computed property inheriting from ObservableProperty.
    Read-only property that is computed based on dependencies.
    
    depends_on accepts list of ObservableProperty, ComputedProperty, or str (property names).
    Automatically connects to dependencies' signals on initialization.
    """

    def __init__(
        self,
        getter: Callable[[], T],
        depends_on: List[Union[ObservableProperty, "ComputedProperty", str]],
        parent: Any = None
    ):
        self._getter = getter
        self._depends_on: List[Union[ObservableProperty, "ComputedProperty", str]] = depends_on
        self._computing = False
        self._value: T = None
        # Initialize QObject
        QObject.__init__(self, parent)
        self._value = self._compute()
        # Automatically connect to dependencies
        self._connect_dependencies()

    def _compute(self) -> T:
        """Computes the property value with recursion protection"""
        if self._computing:
            raise RecursionError(
                "Computed property entered a recursion loop. "
                "Check your dependencies for circular references."
            )
        self._computing = True
        try:
            return self._getter()
        finally:
            self._computing = False

    @property
    def value(self) -> T:
        return self._value

    @value.setter
    def value(self, value: T):
        raise AttributeError(
            "ComputedProperty is read-only. "
            "Cannot set value on a computed property."
        )

    def set(self, value: T):
        raise AttributeError(
            "ComputedProperty is read-only. "
            "Cannot set value on a computed property."
        )

    def bindSignal(self, signal: Signal, modifyFunc: Callable[[Any], Any] = None):
        """
        bindSignal is disabled for ComputedProperty as it is read-only.
        """
        raise AttributeError(
            "ComputedProperty is read-only. "
            "bindSignal is disabled for computed properties."
        )

    def _connect_dependencies(self):
        """
        Connects to dependencies and updates value when they change.
        Called automatically on initialization.
        """
        for dep in self._depends_on:
            if isinstance(dep, str):
                # If it's a string, try to resolve it from parent
                if self.parent() is not None:
                    dep_obj = getattr(self.parent(), dep, None)
                    if isinstance(dep_obj, ObservableProperty):
                        dep_obj.valueChanged.connect(self._on_dependency_changed)
            elif isinstance(dep, ObservableProperty):
                dep.valueChanged.connect(self._on_dependency_changed)

    def _on_dependency_changed(self, _):
        """Handler for dependency change"""
        new_value = self._compute()
        if new_value != self._value:
            self._value = new_value
            self.valueChanged.emit(new_value)


class ComputedPropertyDescriptor:
    """
    Descriptor that creates ComputedProperty on first access.
    Used by @computed_property decorator.
    """
    
    def __init__(self, func: Callable, depends_on: List[str]):
        self._func = func
        self._depends_on = depends_on
        self._prop_name = None
    
    def __set_name__(self, owner, name):
        """Called when the descriptor is assigned to a class attribute"""
        self._prop_name = name
    
    def __get__(self, obj, objtype=None):
        """Called when accessing the attribute on an instance"""
        if obj is None:
            # Accessed on class, return self
            return self
        
        # Create ComputedProperty for this instance
        computed_prop = ComputedProperty(
            getter=lambda: self._func(obj),
            depends_on=self._depends_on,
            parent=obj
        )
        # Store it on the instance to avoid recreating
        object.__setattr__(obj, self._prop_name, computed_prop)
        return computed_prop


def computed_property(depends_on: List[str] = None):
    """
    Decorator for creating computed properties.
    
    Uses descriptor pattern to create ComputedProperty on first access.
    ViewModel doesn't need to know about this decorator.
    
    Usage example:
        @computed_property(depends_on=["name", "age"])
        def name_age(self):
            return f"{self.name} {self.age} age"
    """
    if depends_on is None:
        depends_on = []

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        return ComputedPropertyDescriptor(func, depends_on)
    return decorator
