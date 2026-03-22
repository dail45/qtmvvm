# QtMVVM Documentation

**Languages:** 🇬🇧 **English** | 🇷🇺 [Русский](DOCS_RU.md)

## Table of Contents

1. [Installation](#installation)
2. [Quick Start](#quick-start)
3. [ObservableProperty](#observableproperty)
4. [ComputedProperty](#computedproperty)
5. [BaseViewModel](#baseviewmodel)
6. [Binding Operators](#binding-operators)
7. [Binding Mixins](#binding-mixins)
8. [Command](#command)
9. [Examples](#examples)

---

## Installation

```bash
uv add qtmvvm
```

**Requirements:**
- Python 3.10+
- QtPy >= 2.4.3

---

## Quick Start

### Creating Observable Properties

```python
from qtmvvm import ObservableProperty

# Create an observable property with initial value
name = ObservableProperty("John")

# Get value
print(name.value)  # "John"
print(name())      # "John"

# Set value
name.value = "Jane"
name("Bob")  # Alternative syntax
```

### Creating ViewModel

```python
from qtmvvm import BaseViewModel, computed_property

class PersonViewModel(BaseViewModel):
    name: str = "John"
    age: int = 18

    @computed_property(depends_on=["name", "age"])
    def name_age(self):
        return f"{self.name} {self.age} age"

vm = PersonViewModel()
print(vm.name)           # "John"
print(vm.name_age)       # "John 18 age"
vm.age = 20
print(vm.name_age)       # "John 20 age"
```

### Using Binding Operators

```python
from qtmvvm import ObservableProperty
from qtpy.QtWidgets import QLabel, QLineEdit, QPushButton

prop = ObservableProperty("Hello")

# 1-way binding: property -> widget
prop >> label

# 2-way binding: property <-> widget
prop @ text_input

# Signal binding: signal -> property
prop << button.clicked
```

---

## ObservableProperty

`ObservableProperty` is the core building block of QtMVVM. It wraps a value and notifies observers when it changes.

### Basic Usage

```python
from qtmvvm import ObservableProperty

# Create property
count = ObservableProperty(0)

# Read value
value = count.value
value = count()  # Alternative

# Write value
count.value = 10
count(20)  # Alternative
count.set(30)  # Alternative
```

### Features

- **Automatic notifications**: `valueChanged` signal emitted on every change
- **Operator overloading**: Supports arithmetic, comparison, and logical operators
- **Type safe**: Generic type parameter for type hints

### Operators Support

```python
x = ObservableProperty(10)

# Arithmetic
x += 5      # x.value = 15
x -= 3      # x.value = 12
x *= 2      # x.value = 24
x /= 4      # x.value = 6.0

# Comparison
if x > 5:   # True
    pass

# Boolean
if x:       # True (non-zero)
    pass

# Unary
-x          # -6.0
abs(x)      # 6.0
```

---

## ComputedProperty

`ComputedProperty` is a read-only property that automatically updates when its dependencies change.

### Using Decorator

```python
from qtmvvm import BaseViewModel, computed_property

class CalculatorViewModel(BaseViewModel):
    first: int = 5
    second: int = 10

    @computed_property(depends_on=["first", "second"])
    def sum(self):
        return self.first + self.second

    @computed_property(depends_on=["first", "second"])
    def product(self):
        return self.first * self.second

vm = CalculatorViewModel()
print(vm.sum)       # 15
print(vm.product)   # 50

vm.first = 20
print(vm.sum)       # 30 (auto-updated)
```

### Direct Creation

```python
from qtmvvm import ComputedProperty, ObservableProperty

first = ObservableProperty(5)
second = ObservableProperty(10)

sum_prop = ComputedProperty(
    getter=lambda: first.value + second.value,
    depends_on=[first, second]
)

print(sum_prop.value)  # 15
```

### Features

- **Read-only**: Cannot set value directly
- **Auto-update**: Recalculates when dependencies change
- **Recursion protection**: Detects circular dependencies
- **bindSignal disabled**: Cannot bind signals to computed properties

---

## BaseViewModel

`BaseViewModel` is the base class for ViewModels with automatic property conversion.

### Basic Usage

```python
from qtmvvm import BaseViewModel

class UserViewModel(BaseViewModel):
    username: str = ""
    email: str = ""
    age: int = 0
    is_active: bool = True

vm = UserViewModel()
vm.username = "john_doe"
vm.email = "john@example.com"
```

### With Computed Properties

```python
from qtmvvm import BaseViewModel, computed_property

class UserViewModel(BaseViewModel):
    first_name: str = ""
    last_name: str = ""

    @computed_property(depends_on=["first_name", "last_name"])
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @computed_property(depends_on=["first_name", "last_name"])
    def display_name(self):
        return self.full_name.upper()

vm = UserViewModel(first_name="John", last_name="Doe")
print(vm.full_name)     # "John Doe"
print(vm.display_name)  # "JOHN DOE"
```

### Constructor Parameters

```python
vm = UserViewModel(
    first_name="Jane",
    last_name="Smith"
)
```

---

## Binding Operators

QtMVVM provides three operators for data binding:

| Operator | Direction | Description |
|----------|-----------|-------------|
| `>>` | Property → Widget | 1-way binding |
| `@` | Property ↔ Widget | 2-way binding |
| `<<` | Signal → Property | Signal binding |

### 1-Way Binding (`>>`)

Property changes update the widget, but widget changes don't affect the property.

```python
from qtmvvm import ObservableProperty
from qtpy.QtWidgets import QLabel

name = ObservableProperty("John")
label = QLabel()

name >> label  # label.text = "John"
name.value = "Jane"  # label.text = "Jane"
```

### 2-Way Binding (`@`)

Changes sync in both directions.

```python
from qtmvvm import ObservableProperty
from qtpy.QtWidgets import QLineEdit

name = ObservableProperty("John")
edit = QLineEdit()

name @ edit  # edit.text = "John"
edit.setText("Jane")  # name.value = "Jane"
name.value = "Bob"    # edit.text = "Bob"
```

### Signal Binding (`<<`)

Signal emissions update the property.

```python
from qtmvvm import ObservableProperty
from qtpy.QtWidgets import QPushButton

click_count = ObservableProperty(0)
button = QPushButton("Click me")

click_count << button.clicked  # Each click increments count
```

---

## Binding Mixins

Mixins provide convenient methods for binding to specific widget types.

### Available Mixins

| Mixin | Method | Widgets |
|-------|--------|---------|
| `TextBindingMixin` | `bindText()` | QLineEdit, QTextEdit, QPlainTextEdit, QLabel |
| `ValueBindingMixin` | `bindValue()` | QSpinBox, QDoubleSpinBox, QSlider, QProgressBar |
| `CheckBindingMixin` | `bindChecked()` | QCheckBox, QRadioButton |
| `CurrentIndexBindingMixin` | `bindCurrentIndex()` | QComboBox, QListWidget, QTableWidget |
| `CurrentTextBindingMixin` | `bindCurrentText()` | QComboBox |
| `DateTimeBindingMixin` | `bindDateTime()`, `bindDate()`, `bindTime()` | QDateEdit, QTimeEdit, QDateTimeEdit |
| `SuperBindingMixin` | `bindAuto()` | All supported widgets |

### Using bindAuto

`SuperBindingMixin` (included in `ObservableProperty`) provides automatic binding:

```python
from qtmvvm import ObservableProperty

prop = ObservableProperty("Hello")

# Automatically determines binding type
prop.bindAuto(line_edit)      # Uses bindText
prop.bindAuto(spinbox)        # Uses bindValue
prop.bindAuto(checkbox)       # Uses bindChecked
prop.bindAuto(combobox)       # Uses bindCurrentText
prop.bindAuto(date_edit)      # Uses bindDate
```

### Explicit Binding Methods

```python
prop = ObservableProperty(42)

prop.bindText(text_edit)           # Bind to text
prop.bindValue(spinbox)            # Bind to value
prop.bindChecked(checkbox)         # Bind to checked state
prop.bindCurrentIndex(list_widget) # Bind to current index
prop.bindCurrentText(combobox)     # Bind to current text
prop.bindDateTime(datetime_edit)   # Bind to date/time
prop.bindDate(date_edit)           # Bind to date only
prop.bindTime(time_edit)           # Bind to time only
```

### Binding Mode

All binding methods accept an optional `mode` parameter:

```python
prop.bindText(edit, mode="1-way")  # Property -> Widget only
prop.bindText(edit, mode="2-way")  # Bidirectional sync (default)
```

---

## Command

`Command` wraps ViewModel methods for easy button/signal binding with automatic state management.

### Basic Usage

```python
from qtmvvm import BaseViewModel, command

class MainViewModel(BaseViewModel):
    counter: int = 0

    @command
    def increment(self):
        self.counter += 1

    @command
    def reset(self):
        self.counter = 0

vm = MainViewModel()
```

### Binding to Buttons

```python
from qtpy.QtWidgets import QPushButton

increment_btn = QPushButton("Increment")
reset_btn = QPushButton("Reset")

# Button auto-disables during execution
vm.increment << increment_btn
vm.reset << reset_btn
```

### Binding to Signals

```python
from qtpy.QtCore import QTimer

timer = QTimer()
timer.timeout << vm.increment  # Increment on each timeout
```

### Async Commands

```python
from qtmvvm import BaseViewModel, command

class MainViewModel(BaseViewModel):
    status: str = ""

    @command
    async def load_data(self):
        # Async operation
        import asyncio
        await asyncio.sleep(1)
        self.status = "Loaded!"
```

### Command State

```python
cmd = vm.load_data

print(cmd.is_running)  # Check if running

cmd.started.connect(lambda: print("Started"))
cmd.finished.connect(lambda: print("Finished"))
```

---

## Examples

### Login Form

```python
from qtmvvm import BaseViewModel, computed_property, command

class LoginViewModel(BaseViewModel):
    username: str = ""
    password: str = ""
    remember: bool = False

    @computed_property(depends_on=["username"])
    def username_valid(self):
        return len(self.username) >= 3

    @computed_property(depends_on=["password"])
    def password_valid(self):
        return len(self.password) >= 6

    @computed_property(depends_on=["username_valid", "password_valid"])
    def can_login(self):
        return self.username_valid and self.password_valid

    @command
    def login(self):
        if self.can_login:
            print(f"Logging in as {self.username}")
```

### Calculator

```python
from qtmvvm import BaseViewModel, computed_property, command

class CalculatorViewModel(BaseViewModel):
    value_a: int = 0
    value_b: int = 0

    @computed_property(depends_on=["value_a", "value_b"])
    def sum(self):
        return self.value_a + self.value_b

    @computed_property(depends_on=["value_a", "value_b"])
    def difference(self):
        return self.value_a - self.value_b

    @computed_property(depends_on=["value_a", "value_b"])
    def product(self):
        return self.value_a * self.value_b

    @command
    def reset(self):
        self.value_a = 0
        self.value_b = 0
```

---

## Project Structure

```
qtmvvm/
├── __init__.py              # Main exports
├── observable_property.py   # ObservableProperty class
├── computed_property.py     # ComputedProperty and decorator
├── viewmodel.py             # BaseViewModel and metaclass
├── command.py               # Command class and decorator
├── binding_state.py         # BindingState for managing state
├── binding_rules/           # Binding rule implementations
│   ├── abstract.py          # AbstractBindingRule
│   ├── property.py          # PropertyBindingRule
│   ├── signal.py            # SignalBindingRule
│   └── lambda_rule.py       # LambdaBindingRule
└── binding_mixins/          # Binding mixins
    ├── mixins.py            # All mixin classes
    └── __init__.py
```

---

## API Reference

### Classes

| Class | Description |
|-------|-------------|
| `ObservableProperty[T]` | Observable property with binding support |
| `ComputedProperty[T]` | Read-only computed property |
| `BaseViewModel` | Base class for ViewModels |
| `Command` | Command wrapper for methods |
| `BindingState` | State management for bindings |

### Decorators

| Decorator | Description |
|-----------|-------------|
| `@computed_property(depends_on)` | Create computed property |
| `@command` | Create command from method |

### Operators

| Operator | Usage | Result |
|----------|-------|--------|
| `>>` | `prop >> widget` | 1-way binding |
| `@` | `prop @ widget` | 2-way binding |
| `<<` | `signal << prop` or `cmd << button` | Signal/command binding |
