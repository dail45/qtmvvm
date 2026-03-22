from typing import Callable, Any
import asyncio
import inspect
import threading

from qtpy.QtCore import QObject, Signal, QTimer
from qtpy.QtWidgets import QPushButton, QAbstractButton


# Global event loop for async commands - runs in background thread
_async_loop = None
_async_thread = None


def _get_async_loop():
    """Get or create the global async event loop"""
    global _async_loop, _async_thread

    if _async_loop is not None and _async_loop.is_running():
        return _async_loop

    def run_loop():
        global _async_loop
        _async_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(_async_loop)
        _async_loop.run_forever()

    _async_thread = threading.Thread(target=run_loop, daemon=True)
    _async_thread.start()

    # Wait for loop to be ready
    while _async_loop is None:
        pass

    return _async_loop


class Command(QObject):
    """
    Command class for wrapping ViewModel methods.
    Supports sync and async execution with automatic button locking.

    Operators:
        << : Bind to signal or button
            - command << signal  → command executes on signal emit
            - command << button  → command executes on button click, button disabled during execution
    """

    started = Signal()
    finished = Signal()

    def __init__(
        self,
        func: Callable[..., Any],
        parent: Any = None,
        is_async: bool = None
    ):
        super().__init__(parent)
        self._func = func
        self._is_running = False
        # Check if async if not provided
        self._is_async = is_async if is_async is not None else inspect.iscoroutinefunction(func)

    @property
    def is_running(self) -> bool:
        return self._is_running

    def execute(self, *args, **kwargs) -> Any:
        """Execute the command (sync only)"""
        self._is_running = True
        self.started.emit()
        try:
            result = self._func(*args, **kwargs)
            self._is_running = False
            self.finished.emit()
            return result
        except Exception as e:
            self._is_running = False
            self.finished.emit()
            raise

    def __call__(self, *args, **kwargs):
        """Execute the command directly"""
        if self._is_async:
            return self._execute_async(*args, **kwargs)
        return self.execute(*args, **kwargs)

    def _on_async_finished(self, exception=None):
        """Callback for async command completion (called in main thread)"""
        self._is_running = False
        if exception:
            import traceback
            traceback.print_exception(type(exception), exception, exception.__traceback__)
        self.finished.emit()

    def _execute_async(self, *args, **kwargs):
        """Execute async command in background thread, callback in main thread"""
        self._is_running = True
        self.started.emit()

        loop = _get_async_loop()
        coro = self._func(*args, **kwargs)

        # Schedule coroutine in async loop
        future = asyncio.run_coroutine_threadsafe(coro, loop)

        # Poll for completion using QTimer (in main thread)
        def check_future():
            if future.done():
                try:
                    exception = future.exception()
                except Exception as e:
                    exception = e
                self._on_async_finished(exception)
            else:
                QTimer.singleShot(50, check_future)

        check_future()
        return future

    def __lshift__(self, other: Any) -> "Command":
        """
        Bind command to signal or button.

        command << signal  → execute on signal emit
        command << button  → execute on button click with auto disable/enable
        """
        if isinstance(other, QPushButton) or isinstance(other, QAbstractButton):
            # Bind to button click
            other.clicked.connect(self._on_button_trigger)
            # Store reference to button for disable/enable
            if not hasattr(self, '_bound_buttons'):
                self._bound_buttons = []
            self._bound_buttons.append(other)
            # Connect finished signal to re-enable button
            self.finished.connect(lambda: self._reenable_button(other))
            # Disable button while running
            self.started.connect(lambda: self._disable_button(other))
        elif hasattr(other, 'connect') and callable(getattr(other, 'connect')):
            # It's a signal (has connect method)
            other.connect(self._on_signal_trigger)
        else:
            raise TypeError(
                f"Command can only be bound to Signal or Button, "
                f"got {type(other).__name__}"
            )
        return self

    def _on_signal_trigger(self, *args):
        """Handler for signal trigger"""
        self()

    def _on_button_trigger(self):
        """Handler for button trigger"""
        self()

    def _disable_button(self, button):
        """Disable button during execution"""
        button.setEnabled(False)

    def _reenable_button(self, button):
        """Re-enable button after execution"""
        button.setEnabled(True)


class CommandDescriptor:
    """
    Descriptor that creates Command on first access.
    Used by @command decorator.
    """

    def __init__(self, func: Callable):
        self._func = func
        self._prop_name = None
        self._is_async = inspect.iscoroutinefunction(func)

    def __set_name__(self, owner, name):
        """Called when the descriptor is assigned to a class attribute"""
        self._prop_name = name

    def __get__(self, obj, objtype=None):
        """Called when accessing the attribute on an instance"""
        if obj is None:
            # Accessed on class, return self
            return self

        # Create Command for this instance with bound method
        command = Command(lambda: self._func(obj), parent=obj, is_async=self._is_async)
        # Store it on the instance to avoid recreating
        object.__setattr__(obj, self._prop_name, command)
        return command


def command(func: Callable[..., Any]) -> Command:
    """
    Decorator for creating commands from ViewModel methods.
    
    Uses descriptor pattern to create Command on first access.
    ViewModel doesn't need to know about this decorator.
    
    Usage example:
        @command
        def save(self):
            # Save logic here
            pass
        
        # Bind to button:
        self.vm.save << self.save_button
        
        # Or bind to signal:
        self.vm.save << some_signal
    """
    return CommandDescriptor(func)
