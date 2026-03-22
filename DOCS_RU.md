# Документация QtMVVM

**Языки:** 🇬🇧 [English](DOCS_EN.md) | 🇷🇺 **Русский**

## Содержание

1. [Установка](#установка)
2. [Быстрый старт](#быстрый-старт)
3. [ObservableProperty](#observableproperty)
4. [ComputedProperty](#computedproperty)
5. [BaseViewModel](#baseviewmodel)
6. [Операторы биндингов](#операторы-биндингов)
7. [Миксины биндингов](#миксины-биндингов)
8. [Command](#command)
9. [Примеры](#примеры)

---

## Установка

```bash
uv add qtmvvm
```

**Требования:**
- Python 3.10+
- QtPy >= 2.4.3

---

## Быстрый старт

### Создание наблюдаемых свойств

```python
from qtmvvm import ObservableProperty

# Создание свойства с начальным значением
name = ObservableProperty("John")

# Получение значения
print(name.value)  # "John"
print(name())      # "John"

# Установка значения
name.value = "Jane"
name("Bob")  # Альтернативный синтаксис
```

### Создание ViewModel

```python
from qtmvvm import BaseViewModel, computed_property

class PersonViewModel(BaseViewModel):
    name: str = "John"
    age: int = 18

    @computed_property(depends_on=["name", "age"])
    def name_age(self):
        return f"{self.name} {self.age} лет"

vm = PersonViewModel()
print(vm.name)           # "John"
print(vm.name_age)       # "John 18 лет"
vm.age = 20
print(vm.name_age)       # "John 20 лет"
```

### Использование операторов биндингов

```python
from qtmvvm import ObservableProperty
from qtpy.QtWidgets import QLabel, QLineEdit, QPushButton

prop = ObservableProperty("Hello")

# 1-way биндинг: свойство -> виджет
prop >> label

# 2-way биндинг: свойство <-> виджет
prop @ text_input

# Биндинг сигнала: сигнал -> свойство
button.clicked << prop
```

---

## ObservableProperty

`ObservableProperty` — это основной строительный блок QtMVVM. Он оборачивает значение и уведомляет наблюдателей об изменениях.

### Базовое использование

```python
from qtmvvm import ObservableProperty

# Создание свойства
count = ObservableProperty(0)

# Чтение значения
value = count.value
value = count()  # Альтернативный способ

# Запись значения
count.value = 10
count(20)  # Альтернативный способ
count.set(30)  # Альтернативный способ
```

### Возможности

- **Автоматические уведомления**: сигнал `valueChanged` испускается при каждом изменении
- **Перегрузка операторов**: Поддержка арифметических, сравнения и логических операторов
- **Типобезопасность**: Дженерик параметр типа для type hints

### Поддержка операторов

```python
x = ObservableProperty(10)

# Арифметические
x += 5      # x.value = 15
x -= 3      # x.value = 12
x *= 2      # x.value = 24
x /= 4      # x.value = 6.0

# Сравнения
if x > 5:   # True
    pass

# Булевы
if x:       # True (не ноль)
    pass

# Унарные
-x          # -6.0
abs(x)      # 6.0
```

---

## ComputedProperty

`ComputedProperty` — это свойство только для чтения, которое автоматически обновляется при изменении зависимостей.

### Использование декоратора

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
print(vm.sum)       # 30 (авто-обновление)
```

### Прямое создание

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

### Особенности

- **Только для чтения**: Нельзя установить значение напрямую
- **Авто-обновление**: Пересчитывается при изменении зависимостей
- **Защита от рекурсии**: Обнаруживает циклические зависимости
- **bindSignal отключен**: Нельзя привязывать сигналы к вычисляемым свойствам

---

## BaseViewModel

`BaseViewModel` — это базовый класс для ViewModel с автоматической конвертацией полей в ObservableProperty.

### Базовое использование

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

### С вычисляемыми свойствами

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

### Параметры конструктора

```python
vm = UserViewModel(
    first_name="Jane",
    last_name="Smith"
)
```

---

## Операторы биндингов

QtMVVM предоставляет три оператора для привязки данных:

| Оператор | Направление | Описание |
|----------|-------------|----------|
| `>>` | Свойство → Виджет | 1-way биндинг |
| `@` | Свойство ↔ Виджет | 2-way биндинг |
| `<<` | Сигнал → Свойство | Биндинг сигнала |

### 1-Way биндинг (`>>`)

Изменения свойства обновляют виджет, но изменения виджета не влияют на свойство.

```python
from qtmvvm import ObservableProperty
from qtpy.QtWidgets import QLabel

name = ObservableProperty("John")
label = QLabel()

name >> label  # label.text = "John"
name.value = "Jane"  # label.text = "Jane"
```

### 2-Way биндинг (`@`)

Изменения синхронизируются в обоих направлениях.

```python
from qtmvvm import ObservableProperty
from qtpy.QtWidgets import QLineEdit

name = ObservableProperty("John")
edit = QLineEdit()

name @ edit  # edit.text = "John"
edit.setText("Jane")  # name.value = "Jane"
name.value = "Bob"    # edit.text = "Bob"
```

### Биндинг сигнала (`<<`)

Испускание сигнала обновляет свойство.

```python
from qtmvvm import ObservableProperty
from qtpy.QtWidgets import QPushButton

click_count = ObservableProperty(0)
button = QPushButton("Click me")

button.clicked << click_count  # Каждый клик увеличивает счётчик
```

---

## Миксины биндингов

Миксины предоставляют удобные методы для привязки к определённым типам виджетов.

### Доступные миксины

| Миксин | Метод | Виджеты |
|--------|-------|---------|
| `TextBindingMixin` | `bindText()` | QLineEdit, QTextEdit, QPlainTextEdit, QLabel |
| `ValueBindingMixin` | `bindValue()` | QSpinBox, QDoubleSpinBox, QSlider, QProgressBar |
| `CheckBindingMixin` | `bindChecked()` | QCheckBox, QRadioButton |
| `CurrentIndexBindingMixin` | `bindCurrentIndex()` | QComboBox, QListWidget, QTableWidget |
| `CurrentTextBindingMixin` | `bindCurrentText()` | QComboBox |
| `DateTimeBindingMixin` | `bindDateTime()`, `bindDate()`, `bindTime()` | QDateEdit, QTimeEdit, QDateTimeEdit |
| `SuperBindingMixin` | `bindAuto()` | Все поддерживаемые виджеты |

### Использование bindAuto

`SuperBindingMixin` (включён в `ObservableProperty`) предоставляет автоматическую привязку:

```python
from qtmvvm import ObservableProperty

prop = ObservableProperty("Hello")

# Автоматически определяет тип биндинга
prop.bindAuto(line_edit)      # Использует bindText
prop.bindAuto(spinbox)        # Использует bindValue
prop.bindAuto(checkbox)       # Использует bindChecked
prop.bindAuto(combobox)       # Использует bindCurrentText
prop.bindAuto(date_edit)      # Использует bindDate
```

### Явные методы биндинга

```python
prop = ObservableProperty(42)

prop.bindText(text_edit)           # Привязка к тексту
prop.bindValue(spinbox)            # Привязка к значению
prop.bindChecked(checkbox)         # Привязка к состоянию checked
prop.bindCurrentIndex(list_widget) # Привязка к текущему индексу
prop.bindCurrentText(combobox)     # Привязка к текущему тексту
prop.bindDateTime(datetime_edit)   # Привязка к дате/времени
prop.bindDate(date_edit)           # Привязка только к дате
prop.bindTime(time_edit)           # Привязка только ко времени
```

### Режим биндинга

Все методы биндинга принимают необязательный параметр `mode`:

```python
prop.bindText(edit, mode="1-way")  # Только свойство -> виджет
prop.bindText(edit, mode="2-way")  # Двусторонняя синхронизация (по умолчанию)
```

---

## Command

`Command` оборачивает методы ViewModel для удобной привязки к кнопкам/сигналам с автоматическим управлением состоянием.

### Базовое использование

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

### Привязка к кнопкам

```python
from qtpy.QtWidgets import QPushButton

increment_btn = QPushButton("Increment")
reset_btn = QPushButton("Reset")

# Кнопка автоматически отключается во время выполнения
vm.increment << increment_btn
vm.reset << reset_btn
```

### Привязка к сигналам

```python
from qtpy.QtCore import QTimer

timer = QTimer()
timer.timeout << vm.increment  # Увеличение при каждом таймауте
```

### Асинхронные команды

```python
from qtmvvm import BaseViewModel, command

class MainViewModel(BaseViewModel):
    status: str = ""

    @command
    async def load_data(self):
        # Асинхронная операция
        import asyncio
        await asyncio.sleep(1)
        self.status = "Загружено!"
```

### Состояние команды

```python
cmd = vm.load_data

print(cmd.is_running)  # Проверка выполнения

cmd.started.connect(lambda: print("Начато"))
cmd.finished.connect(lambda: print("Завершено"))
```

---

## Примеры

### Форма входа

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
            print(f"Вход как {self.username}")
```

### Калькулятор

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

## Структура проекта

```
qtmvvm/
├── __init__.py              # Основные экспорты
├── observable_property.py   # Класс ObservableProperty
├── computed_property.py     # ComputedProperty и декоратор
├── viewmodel.py             # BaseViewModel и метакласс
├── command.py               # Command класс и декоратор
├── binding_state.py         # BindingState для управления состоянием
├── binding_rules/           # Реализации правил биндинга
│   ├── abstract.py          # AbstractBindingRule
│   ├── property.py          # PropertyBindingRule
│   ├── signal.py            # SignalBindingRule
│   └── lambda_rule.py       # LambdaBindingRule
└── binding_mixins/          # Миксины биндингов
    ├── mixins.py            # Все классы миксинов
    └── __init__.py
```

---

## Справочник API

### Классы

| Класс | Описание |
|-------|----------|
| `ObservableProperty[T]` | Наблюдаемое свойство с поддержкой биндингов |
| `ComputedProperty[T]` | Вычисляемое свойство только для чтения |
| `BaseViewModel` | Базовый класс для ViewModel |
| `Command` | Обёртка команды для методов |
| `BindingState` | Управление состоянием для биндингов |

### Декораторы

| Декоратор | Описание |
|-----------|----------|
| `@computed_property(depends_on)` | Создание вычисляемого свойства |
| `@command` | Создание команды из метода |

### Операторы

| Оператор | Использование | Результат |
|----------|---------------|-----------|
| `>>` | `prop >> widget` | 1-way биндинг |
| `@` | `prop @ widget` | 2-way биндинг |
| `<<` | `signal << prop` или `cmd << button` | Биндинг сигнала/команды |
