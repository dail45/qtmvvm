# QtMVVM

MVVM library for Qt with observable properties and data bindings.

**Languages:** 🇬🇧 **English** | 🇷🇺 [Русский](README.md)

## Installation

```bash
uv add qtmvvm
```

## Quick Start

### 1. Create Observable Properties

```python
from qtmvvm import ObservableProperty

# Create a property with initial value
name = ObservableProperty("John")
age = ObservableProperty(25)

# Get value
print(name.value)  # "John"
print(name())      # "John"

# Set value
name.value = "Jane"
age(30)            # Alternative syntax
```

### 2. Create ViewModel

```python
from qtmvvm import BaseViewModel, computed_property

class PersonViewModel(BaseViewModel):
    # Simple properties
    name: str = "John"
    age: int = 25

    # Computed property (read-only, auto-updates)
    @computed_property(depends_on=["name", "age"])
    def description(self):
        return f"{self.name}, {self.age} years old"

# Usage
vm = PersonViewModel()
print(vm.name)         # "John"
print(vm.description)  # "John, 25 years old"

vm.name = "Jane"
print(vm.description)  # "Jane, 25 years old" (auto-updated!)
```

### 3. Use Binding Operators

QtMVVM provides three operators for data binding:

| Operator | Direction | Description |
|----------|-----------|-------------|
| `>>` | Property → Widget | 1-way binding |
| `@` | Property ↔ Widget | 2-way binding |
| `<<` | Signal → Property | Signal binding |

#### 1-Way Binding (`>>`)

```python
from qtmvvm import ObservableProperty
from qtpy.QtWidgets import QLabel

name = ObservableProperty("John")
label = QLabel()

name >> label  # When name changes, label updates automatically
name.value = "Jane"  # label.text = "Jane"
```

#### 2-Way Binding (`@`)

```python
from qtmvvm import ObservableProperty
from qtpy.QtWidgets import QLineEdit

name = ObservableProperty("John")
edit = QLineEdit()

name @ edit  # Sync in both directions

edit.setText("Jane")  # name.value = "Jane"
name.value = "Bob"    # edit.text = "Bob"
```

#### Signal Binding (`<<`)

```python
from qtmvvm import ObservableProperty
from qtpy.QtWidgets import QPushButton

click_count = ObservableProperty(0)
button = QPushButton("Click me")

click_count << button.clicked  # Each click increments click_count
```

### 4. Using Command

`Command` wraps ViewModel methods for binding to buttons with automatic disabling during execution.

```python
from qtmvvm import BaseViewModel, command
from qtpy.QtWidgets import QPushButton

class CounterViewModel(BaseViewModel):
    count: int = 0

    @command
    def increment(self):
        self.count += 1

    @command
    async def load_data(self):
        import asyncio
        await asyncio.sleep(1)  # Async operation

vm = CounterViewModel()

# Bind to buttons
inc_btn = QPushButton("+")
load_btn = QPushButton("Load")

vm.increment << inc_btn    # Click → increment()
vm.load_data << load_btn   # Button disabled during loading
```

## Documentation

- [Full Documentation (English)](DOCS_EN.md) — detailed API reference, all binding mixins, and advanced examples
- [Полная документация (Русский)](DOCS_RU.md)
