# QtMVVM

MVVM-библиотека для Qt с наблюдаемыми свойствами и привязками данных.

**Языки:** 🇬🇧 [English](README_EN.md) | 🇷🇺 **Русский** 

## Установка

```bash
uv add qtmvvm
```

## Быстрый старт

### 1. Создание наблюдаемых свойств

```python
from qtmvvm import ObservableProperty

# Создание свойства с начальным значением
name = ObservableProperty("John")
age = ObservableProperty(25)

# Получение значения
print(name.value)  # "John"
print(name())      # "John"

# Установка значения
name.value = "Jane"
age(30)            # Альтернативный синтаксис
```

### 2. Создание ViewModel

```python
from qtmvvm import BaseViewModel, computed_property

class PersonViewModel(BaseViewModel):
    # Простые свойства
    name: str = "John"
    age: int = 25
    
    # Вычисляемое свойство (только для чтения, авто-обновление)
    @computed_property(depends_on=["name", "age"])
    def description(self):
        return f"{self.name}, {self.age} лет"

# Использование
vm = PersonViewModel()
print(vm.name)         # "John"
print(vm.description)  # "John, 25 лет"

vm.name = "Jane"
print(vm.description)  # "Jane, 25 лет" (авто-обновление!)
```

### 3. Использование операторов биндингов

QtMVVM предоставляет три оператора для привязки данных:

| Оператор | Направление | Описание |
|----------|-------------|----------|
| `>>` | Свойство → Виджет | 1-way биндинг |
| `@` | Свойство ↔ Виджет | 2-way биндинг |
| `<<` | Сигнал → Свойство | Биндинг сигнала |

#### 1-Way биндинг (`>>`)

```python
from qtmvvm import ObservableProperty
from qtpy.QtWidgets import QLabel

name = ObservableProperty("John")
label = QLabel()

name >> label  # При изменении name, label обновляется автоматически
name.value = "Jane"  # label.text = "Jane"
```

#### 2-Way биндинг (`@`)

```python
from qtmvvm import ObservableProperty
from qtpy.QtWidgets import QLineEdit

name = ObservableProperty("John")
edit = QLineEdit()

name @ edit  # Синхронизация в обоих направлениях

edit.setText("Jane")  # name.value = "Jane"
name.value = "Bob"    # edit.text = "Bob"
```

#### Биндинг сигнала (`<<`)

```python
from qtmvvm import ObservableProperty
from qtpy.QtWidgets import QPushButton

click_count = ObservableProperty(0)
button = QPushButton("Click me")

click_count << button.clicked  # Каждый клик увеличивает click_count
```

## Документация

- [Полная документация (Русский)](DOCS_RU.md) — подробное API reference, все миксины биндингов и расширенные примеры
- [Full Documentation (English)](DOCS_EN.md)
