import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
import datetime

# --- 1. Настройки ---
API_KEY = "ВАШ_API_КЛЮЧ"  # Замените на свой ключ с exchangerate-api.com
HISTORY_FILE = "history.json"

# --- 2. Загрузка истории ---
def load_history():
    try:
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

# --- 3. Сохранение истории ---
def save_history(history):
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=4)

# --- 4. Логика конвертации ---
def get_exchange_rate(from_currency, to_currency):
    url = f"https://v6.exchangerate-api.com/v6/{API_KEY}/latest/{from_currency}"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status() # Проверка на ошибки HTTP
        data = response.json()
        if data['result'] == 'success':
            return data['conversion_rates'].get(to_currency)
        else:
            messagebox.showerror("Ошибка API", f"Сервер вернул ошибку: {data.get('error-type')}")
            return None
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Ошибка сети", f"Не удалось подключиться к серверу: {e}")
        return None

def convert_currency():
    from_curr = from_var.get()
    to_curr = to_var.get()
    
    # Валидация ввода суммы
    try:
        amount = float(amount_entry.get())
        if amount <= 0:
            raise ValueError("Сумма должна быть больше нуля.")
    except ValueError as e:
        messagebox.showerror("Ошибка ввода", str(e))
        return

    rate = get_exchange_rate(from_curr, to_curr)
    if rate is not None:
        result = round(amount * rate, 2)
        
        # Обновление поля результата
        result_label.config(text=f"Результат: {result} {to_curr}")

        # Добавление в историю
        history.append({
            "from": from_curr,
            "to": to_curr,
            "amount": amount,
            "result": result,
            "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        save_history(history)
        update_history_table()

# --- 5. Обновление таблицы истории ---
def update_history_table():
    for i in history_table.get_children():
        history_table.delete(i)
    for entry in history:
        history_table.insert("", "end", values=(
            entry['date'],
            entry['from'],
            entry['to'],
            entry['amount'],
            entry['result']
        ))

# --- 6. Инициализация данных ---
history = load_history()

# --- 7. Создание GUI ---
root = tk.Tk()
root.title("Конвертер валют")
root.geometry("700x500")
root.resizable(False, False)

# Основной фрейм для виджетов
main_frame = ttk.Frame(root, padding="10")
main_frame.pack(expand=True, fill='both')

# Строка 1: Валюты и сумма
ttk.Label(main_frame, text="Из:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
from_var = tk.StringVar(value="USD")
from_combo = ttk.Combobox(main_frame, textvariable=from_var, values=["USD", "EUR", "RUB", "GBP"], state="readonly", width=5)
from_combo.grid(row=0, column=1, padx=5, pady=5)

ttk.Label(main_frame, text="В:").grid(row=0, column=2, padx=5, pady=5, sticky="e")
to_var = tk.StringVar(value="EUR")
to_combo = ttk.Combobox(main_frame, textvariable=to_var, values=["USD", "EUR", "RUB", "GBP"], state="readonly", width=5)
to_combo.grid(row=0, column=3, padx=5, pady=5)

ttk.Label(main_frame, text="Сумма:").grid(row=0, column=4, padx=5, pady=5, sticky="e")
amount_entry = ttk.Entry(main_frame, width=15)
amount_entry.grid(row=0, column=5, padx=5, pady=5)
amount_entry.insert(0, "100")

# Строка 2: Кнопка и результат
convert_btn = ttk.Button(main_frame, text="Конвертировать", command=convert_currency)
convert_btn.grid(row=1, columnspan=6, pady=15)

result_label = ttk.Label(main_frame, text="Результат: ", font=('TkDefaultFont', 12))
result_label.grid(row=2, columnspan=6)

# Строка 3: Таблица истории
history_frame = ttk.Frame(main_frame)
history_frame.grid(row=3, columnspan=6, pady=(20, 0))

history_table = ttk.Treeview(history_frame, columns=("Дата", "Из", "В", "Сумма", "Результат"), show='headings')
history_table.heading("Дата", text="Дата")
history_table.heading("Из", text="Из")
history_table.heading("В", text="В")
history_table.heading("Сумма", text="Сумма")
history_table.heading("Результат", text="Результат")

# Настройка ширины колонок
history_table.column("Дата", width=150)
history_table.column("Из", width=80)
history_table.column("В", width=80)
history_table.column("Сумма", width=80)
history_table.column("Результат", width=100)

history_table.pack(fill='both', expand=True)

# Заполнение таблицы при запуске
update_history_table()

root.mainloop()
