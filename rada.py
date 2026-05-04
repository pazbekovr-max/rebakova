import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

class BookTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Book Tracker")
        self.root.geometry("700x500")
        
        self.books = []
        self.load_data()

        # --- Элементы интерфейса ---
        
        # Фрейм для ввода данных
        input_frame = ttk.LabelFrame(root, text="Добавить книгу", padding=10)
        input_frame.pack(fill="x", padx=10, pady=5)

        # Поля ввода
        ttk.Label(input_frame, text="Название:").grid(row=0, column=0, sticky="w")
        self.entry_title = ttk.Entry(input_frame, width=30)
        self.entry_title.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(input_frame, text="Автор:").grid(row=0, column=2, sticky="w")
        self.entry_author = ttk.Entry(input_frame, width=20)
        self.entry_author.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(input_frame, text="Жанр:").grid(row=1, column=0, sticky="w")
        self.entry_genre = ttk.Entry(input_frame, width=30)
        self.entry_genre.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(input_frame, text="Страницы:").grid(row=1, column=2, sticky="w")
        self.entry_pages = ttk.Entry(input_frame, width=10)
        self.entry_pages.grid(row=1, column=3, padx=5, pady=5)

        # Кнопка добавления
        btn_add = ttk.Button(input_frame, text="Добавить книгу", command=self.add_book)
        btn_add.grid(row=2, column=0, columnspan=4, pady=10)

        # Фрейм для фильтров
        filter_frame = ttk.LabelFrame(root, text="Фильтрация", padding=10)
        filter_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(filter_frame, text="Жанр:").grid(row=0, column=0, sticky="w")
        self.combo_genre = ttk.Combobox(filter_frame, values=[], state="readonly", width=15)
        self.combo_genre.grid(row=0, column=1, padx=5, pady=5)
        self.combo_genre.bind("<<ComboboxSelected>>", self.apply_filters)
        
        # Кнопка сброса жанра
        ttk.Button(filter_frame, text="Сбросить жанр", command=self.reset_genre_filter).grid(row=0, column=2, padx=5)

        ttk.Label(filter_frame, text="Мин. страниц:").grid(row=0, column=3, sticky="w")
        self.entry_min_pages = ttk.Entry(filter_frame, width=10)
        self.entry_min_pages.grid(row=0, column=4, padx=5, pady=5)
        self.entry_min_pages.insert(0, "0")
        ttk.Button(filter_frame, text="Применить", command=self.apply_filters).grid(row=0, column=5, padx=5)

        # Таблица (Treeview)
        columns = ("title", "author", "genre", "pages")
        self.tree = ttk.Treeview(root, columns=columns, show="headings", height=15)
        
        self.tree.heading("title", text="Название")
        self.tree.heading("author", text="Автор")
        self.tree.heading("genre", text="Жанр")
        self.tree.heading("pages", text="Страницы")
        
        self.tree.column("title", width=200)
        self.tree.column("author", width=150)
        self.tree.column("genre", width=100)
        self.tree.column("pages", width=80)
        
        self.tree.pack(fill="both", expand=True, padx=10, pady=5)

        # Кнопки управления данными
        data_frame = ttk.Frame(root)
        data_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Button(data_frame, text="Сохранить в JSON", command=self.save_data).pack(side="left", padx=5)
        ttk.Button(data_frame, text="Загрузить из JSON", command=self.load_data).pack(side="left", padx=5)
        ttk.Button(data_frame, text="Удалить выбранную", command=self.delete_book).pack(side="left", padx=5)

        self.update_genre_combo()
        self.refresh_table()

    def add_book(self):
        title = self.entry_title.get().strip()
        author = self.entry_author.get().strip()
        genre = self.entry_genre.get().strip()
        pages_str = self.entry_pages.get().strip()

        # Валидация
        if not title or not author or not genre:
            messagebox.showerror("Ошибка", "Поля Название, Автор и Жанр не должны быть пустыми.")
            return
        
        try:
            pages = int(pages_str)
            if pages <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Ошибка", "Количество страниц должно быть положительным числом.")
            return

        book = {
            "title": title,
            "author": author,
            "genre": genre,
            "pages": pages
        }
        self.books.append(book)
        self.save_data() # Автосохранение
        self.refresh_table()
        self.update_genre_combo()
        
        # Очистка полей
        self.entry_title.delete(0, tk.END)
        self.entry_author.delete(0, tk.END)
        self.entry_genre.delete(0, tk.END)
        self.entry_pages.delete(0, tk.END)
        self.entry_title.focus()

    def apply_filters(self, event=None):
        self.refresh_table()

    def reset_genre_filter(self):
        self.combo_genre.set("")
        self.refresh_table()

    def refresh_table(self):
        # Очистка таблицы
        for item in self.tree.get_children():
            self.tree.delete(item)

        genre_filter = self.combo_genre.get()
        try:
            min_pages = int(self.entry_min_pages.get())
        except ValueError:
            min_pages = 0

        for book in self.books:
            # Проверка фильтров
            if genre_filter and book["genre"] != genre_filter:
                continue
            if book["pages"] < min_pages:
                continue
            
            self.tree.insert("", tk.END, values=(
                book["title"], 
                book["author"], 
                book["genre"], 
                book["pages"]
            ))

    def update_genre_combo(self):
        genres = list(set(book["genre"] for book in self.books))
        genres.sort()
        self.combo_genre["values"] = genres
        if genre_filter := self.combo_genre.get():
            if genre_filter not in genres:
                self.combo_genre.set("")

    def delete_book(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите книгу для удаления.")
            return
        
        item = self.tree.item(selected[0])
        values = item["values"]
        
        # Удаляем из списка
        self.books = [b for b in self.books if not (b["title"] == values[0] and b["author"] == values[1] and b["genre"] == values[2] and b["pages"] == values[3])]
        
        self.save_data()
        self.refresh_table()

    def save_data(self):
        try:
            with open("books.json", "w", encoding="utf-8") as f:
                json.dump(self.books, f, ensure_ascii=False, indent=4)
            # messagebox.showinfo("Успех", "Данные сохранены в books.json")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить данные: {e}")

    def load_data(self):
        if os.path.exists("books.json"):
            try:
                with open("books.json", "r", encoding="utf-8") as f:
                    self.books = json.load(f)
                self.refresh_table()
                self.update_genre_combo()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить данные: {e}")
                self.books = []
        else:
            self.books = []

if __name__ == "__main__":
    root = tk.Tk()
    app = BookTrackerApp(root)
    root.mainloop()
