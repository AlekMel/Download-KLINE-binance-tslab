import ccxt
import pandas as pd
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, timedelta
import threading
import time
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests.exceptions

class NeumorphicWidget(tk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        #цветовая схема
        self.colors = {
            'bg': "#f0f2f5",
            'shadow_dark': "#d1d9e6",
            'shadow_light': "#ffffff",
            'accent': "#4a90e2",
            'text': "#2d3436"
        }
        
        #внешний вид виджетов
        self.configure(
            bg=self.colors['bg'],
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightbackground=self.colors['shadow_dark'],
            highlightcolor=self.colors['accent']
        )
        
        # Добавляем эффект тени
        self.shadow = ttk.Frame(self, style="Shadow.TFrame")
        self.shadow.place(relx=0.02, rely=0.02, relwidth=0.98, relheight=0.98)

    def create_inner_frame(self):
        inner_frame = tk.Frame(
            self,
            bg=self.colors['bg'],
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightbackground=self.colors['shadow_dark']
        )
        inner_frame.place(relx=0.05, rely=0.05, relwidth=0.9, relheight=0.9)
        return inner_frame

class CryptoDownloader:
    def __init__(self, master):
        self.master = master
        self.master.title("Crypto Data Downloader")
        self.master.geometry("1000x1200")  #размер окна
        
        # цветовая схема
        self.colors = {
            'bg': "#f0f2f5",
            'text': "#2d3436",
            'accent': "#4a90e2",
            'success': "#27ae60",
            'warning': "#f39c12",
            'error': "#e74c3c",
            'shadow_dark': "#d1d9e6",
            'shadow_light': "#ffffff"
        }
        
        self.master.configure(bg=self.colors['bg'])

        # Настраиваем стили
        self.setup_styles()

        self.exchange = ccxt.binance()

        # Основной фрейм с отступами
        self.main_frame = NeumorphicWidget(master)
        self.main_frame.pack(expand=True, fill="both", padx=30, pady=30)

        # Заголовок с стилем
        header_frame = NeumorphicWidget(self.main_frame)
        header_frame.pack(fill="x", pady=15)
        ttk.Label(
            header_frame,
            text="Crypto Data Downloader",
            style="Header.TLabel"
        ).pack(pady=10)

        # Контент
        content_frame = self.main_frame.create_inner_frame()
        content_frame.pack(expand=True, fill="both", padx=20, pady=20)

        # Создаем колонки
        left_column = NeumorphicWidget(content_frame)
        left_column.pack(side="left", fill="both", expand=True, padx=(0, 10))

        right_column = NeumorphicWidget(content_frame)
        right_column.pack(side="right", fill="both", expand=True, padx=(10, 0))

        # Создаем виджеты 
        self.create_left_column_widgets(left_column)
        self.create_right_column_widgets(right_column)

        # Нижний колонтитул
        footer_frame = NeumorphicWidget(self.main_frame)
        footer_frame.pack(fill="x", pady=15)
        
        # Статус
        self.status_label = ttk.Label(
            footer_frame,
            text="Ready",
            style="Status.TLabel"
        )
        self.status_label.pack(pady=5)

        self.current_date_display = ttk.Label(
            footer_frame,
            text="",
            style="Status.TLabel"
        )
        self.current_date_display.pack(pady=5)

        #прогресс-бар
        self.progress_bar = ttk.Progressbar(
            footer_frame,
            mode='determinate',
            style="Accent.Horizontal.TProgressbar"
        )
        self.progress_bar.pack(fill='x', pady=10, padx=20)

        # Инициализация остальных компонентов
        self.markets_list = []
        self.data_cache = {}
        self.prefetch_cache = {}
        
        # Добавляем статус-бар
        self.create_status_bar(footer_frame)
        
        # Создаем контекстное меню
        self.create_context_menu()
        
        # Привязываем горячие клавиши
        self.bind_shortcuts()

        # Добавляем кнопку "Оставить на чай" в правый нижний угол
        self.create_donate_button()

    def setup_styles(self):
        """Настройка современных стилей для виджетов"""
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Стиль заголовка
        self.style.configure(
            "Header.TLabel",
            font=("Segoe UI", 24, "bold"),
            foreground=self.colors['text'],
            background=self.colors['bg']
        )
        
        # Стиль кнопок
        self.style.configure(
            "Accent.TButton",
            font=("Segoe UI", 10),
            padding=10,
            background=self.colors['accent'],
            foreground="white"
        )
        
        # Стиль меток
        self.style.configure(
            "TLabel",
            font=("Segoe UI", 10),
            background=self.colors['bg'],
            foreground=self.colors['text']
        )
        
        # Стиль статуса
        self.style.configure(
            "Status.TLabel",
            font=("Segoe UI", 9),
            background=self.colors['bg'],
            foreground=self.colors['text']
        )
        
        # Стиль прогресс-бара
        self.style.configure(
            "Accent.Horizontal.TProgressbar",
            troughcolor=self.colors['bg'],
            background=self.colors['accent']
        )

        # Стиль для ссылок
        self.style.configure(
            "Link.TLabel",
            foreground=self.colors['accent'],
            font=("Segoe UI", 9, "underline")
        )
        
        # Добавляем специальный стиль для кнопки доната
        self.style.configure(
            "Donate.TLabel",
            foreground=self.colors['accent'],
            font=("Segoe UI", 12, "underline"),
            background=self.colors['bg']
        )

    def create_left_column_widgets(self, parent):
        """Создание виджетов левой колонки с улучшенным дизайном"""
        # Информационная панель
        info_frame = ttk.LabelFrame(
            parent,
            text="API Settings",
            style="Card.TLabelframe"
        )
        info_frame.pack(fill="x", pady=10, padx=10)
        
        # Информационные метки с улучшенным форматированием
        labels = [
            "Binance API Limits:",
            "• Batch size: 1000 records",
            "• Delay: 120ms",
            "• Max requests: 10"
        ]
        
        for text in labels:
            ttk.Label(
                info_frame,
                text=text,
                style="Info.TLabel"
            ).pack(anchor="w", pady=2, padx=5)
        
        # Кнопка загрузки активов
        ttk.Button(
            parent,
            text="Load Assets",
            style="Accent.TButton",
            command=self.load_markets
        ).pack(fill="x", pady=10, padx=10)
        
        # Фрейм выбора
        selection_frame = ttk.Frame(parent)
        selection_frame.pack(fill="x", pady=5, padx=10)
        
        # Кнопки выбора с современным стилем
        ttk.Button(
            selection_frame,
            text="Select All",
            style="Accent.TButton",
            command=self.select_all_assets
        ).pack(side="left", expand=True, padx=2)
        
        ttk.Button(
            selection_frame,
            text="Deselect All",
            style="Accent.TButton",
            command=self.deselect_all_assets
        ).pack(side="left", expand=True, padx=2)
        
        # Поле поиска с улучшенным дизайном
        ttk.Label(
            parent,
            text="Search:",
            style="TLabel"
        ).pack(anchor="w", pady=(10, 0), padx=10)
        
        self.search_entry = ttk.Entry(
            parent,
            style="Accent.TEntry"
        )
        self.search_entry.pack(fill="x", pady=(0, 10), padx=10)
        self.search_entry.bind("<KeyRelease>", self.filter_markets)
        
        # Список активов
        self.asset_listbox = tk.Listbox(
            parent,
            height=10,
            selectmode=tk.MULTIPLE,
            bg=self.colors['bg'],
            fg=self.colors['text'],
            relief="flat",
            borderwidth=1,
            highlightthickness=1,
            highlightbackground=self.colors['shadow_dark'],
            selectbackground=self.colors['accent'],
            selectforeground="white",
            font=("Segoe UI", 9)
        )
        self.asset_listbox.pack(fill="both", expand=True, pady=5, padx=10)
        
        # Список загруженных активов
        ttk.Label(
            parent,
            text="Downloaded Assets:",
            style="TLabel"
        ).pack(anchor="w", pady=(10, 0), padx=10)
        
        self.loaded_assets_listbox = tk.Listbox(
            parent,
            height=5,
            bg=self.colors['bg'],
            fg=self.colors['text'],
            relief="flat",
            borderwidth=1,
            highlightthickness=1,
            highlightbackground=self.colors['shadow_dark'],
            font=("Segoe UI", 9)
        )
        self.loaded_assets_listbox.pack(fill="both", expand=True, pady=5, padx=10)

    def create_right_column_widgets(self, parent):
        """Создание виджетов правой колонки с улучшенным дизайном"""
        # Секция дат
        date_frame = ttk.LabelFrame(
            parent,
            text="Date Range",
            style="Card.TLabelframe"
        )
        date_frame.pack(fill="x", pady=10, padx=10)
        
        # Поля ввода дат
        ttk.Label(
            date_frame,
            text="From (YYYY-MM-DD HH:MM:SS):",
            style="TLabel"
        ).pack(anchor="w", pady=(5, 0), padx=5)
        
        self.from_entry = ttk.Entry(
            date_frame,
            style="Accent.TEntry"
        )
        self.from_entry.pack(fill="x", pady=(0, 10), padx=5)
        
        ttk.Label(
            date_frame,
            text="To (YYYY-MM-DD HH:MM:SS):",
            style="TLabel"
        ).pack(anchor="w", pady=(5, 0), padx=5)
        
        self.to_entry = ttk.Entry(
            date_frame,
            style="Accent.TEntry"
        )
        self.to_entry.pack(fill="x", pady=(0, 10), padx=5)
        
        # Кнопки быстрого выбора дат
        button_frame = ttk.Frame(date_frame)
        button_frame.pack(fill="x", pady=5, padx=5)
        
        ttk.Button(
            button_frame,
            text="All History",
            style="Accent.TButton",
            command=self.set_all_history
        ).pack(side="left", expand=True, padx=2)
        
        ttk.Button(
            button_frame,
            text="Today",
            style="Accent.TButton",
            command=self.set_today
        ).pack(side="left", expand=True, padx=2)
        
        # Секция настроек
        settings_frame = ttk.LabelFrame(
            parent,
            text="Settings",
            style="Card.TLabelframe"
        )
        settings_frame.pack(fill="x", pady=10, padx=10)
        
        # Таймфрейм
        ttk.Label(
            settings_frame,
            text="Timeframe:",
            style="TLabel"
        ).pack(anchor="w", pady=(5, 0), padx=5)
        
        self.timeframe_combobox = ttk.Combobox(
            settings_frame,
            values=["1m", "5m", "15m", "30m", "1h", "4h", "1d"],
            state="readonly",
            style="Accent.TCombobox"
        )
        self.timeframe_combobox.current(0)
        self.timeframe_combobox.pack(fill="x", pady=(0, 10), padx=5)
        
        # Путь сохранения
        ttk.Label(
            settings_frame,
            text="Save Path:",
            style="TLabel"
        ).pack(anchor="w", pady=(5, 0), padx=5)
        
        path_frame = ttk.Frame(settings_frame)
        path_frame.pack(fill="x", pady=(0, 10), padx=5)
        
        self.save_path_entry = ttk.Entry(
            path_frame,
            style="Accent.TEntry"
        )
        self.save_path_entry.pack(side="left", fill="x", expand=True)
        
        ttk.Button(
            path_frame,
            text="Browse",
            style="Accent.TButton",
            command=self.browse_directory
        ).pack(side="right", padx=(5, 0))
        
        # Настройки оптимизации
        optimization_frame = ttk.LabelFrame(
            parent,
            text="Optimization",
            style="Card.TLabelframe"
        )
        optimization_frame.pack(fill="x", pady=10, padx=10)
        
        # Количество потоков
        ttk.Label(
            optimization_frame,
            text="Thread Count:",
            style="TLabel"
        ).pack(anchor="w", pady=(5, 0), padx=5)
        
        self.threads_spinbox = ttk.Spinbox(
            optimization_frame,
            from_=1,
            to=10,
            style="Accent.TSpinbox"
        )
        self.threads_spinbox.set(5)
        self.threads_spinbox.pack(fill="x", pady=(0, 10), padx=5)
        
        # Размер batch-запроса
        ttk.Label(
            optimization_frame,
            text="Batch Size:",
            style="TLabel"
        ).pack(anchor="w", pady=(5, 0), padx=5)
        
        self.batch_size_spinbox = ttk.Spinbox(
            optimization_frame,
            from_=100,
            to=1000,
            increment=100,
            style="Accent.TSpinbox"
        )
        self.batch_size_spinbox.set(1000)
        self.batch_size_spinbox.pack(fill="x", pady=(0, 10), padx=5)
        
        # Задержка между запросами
        ttk.Label(
            optimization_frame,
            text="Request Delay (ms):",
            style="TLabel"
        ).pack(anchor="w", pady=(5, 0), padx=5)
        
        self.delay_spinbox = ttk.Spinbox(
            optimization_frame,
            from_=0,
            to=1000,
            increment=10,
            style="Accent.TSpinbox"
        )
        self.delay_spinbox.set(50)
        self.delay_spinbox.pack(fill="x", pady=(0, 10), padx=5)
        
        # Кнопка загрузки
        ttk.Button(
            parent,
            text="Download Data",
            style="Accent.TButton",
            command=self.download_data
        ).pack(fill="x", pady=20, padx=10)

    def load_markets(self):
        markets = self.exchange.fetch_markets()
        for market in markets:
            symbol = market['symbol']
            if '/' in symbol:
                self.asset_listbox.insert(tk.END, symbol)
                if symbol not in self.markets_list:
                    self.markets_list.append(symbol)

    def filter_markets(self, event):
        search_term = self.search_entry.get().lower()
        
        # Сохраняем текущие выбранные элементы
        selected_items = [self.asset_listbox.get(idx) for idx in self.asset_listbox.curselection()]
        
        # Очистка списка перед добавлением отфильрованных элементов
        self.asset_listbox.delete(0, tk.END)
        
        # Добавляем отфильтрованные элементы и восстанавливаем выделение
        for asset in self.markets_list:
            if search_term in asset.lower():
                self.asset_listbox.insert(tk.END, asset)
                # Если этот актив был выбран ранее, выделяем его сноа
                if asset in selected_items:
                    last_index = self.asset_listbox.size() - 1
                    self.asset_listbox.selection_set(last_index)

    def browse_directory(self):
        directory = filedialog.askdirectory()
        
        if directory:
            self.save_path_entry.delete(0, tk.END)
            self.save_path_entry.insert(0, directory)

    def set_today(self):
        today_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.to_entry.delete(0, tk.END)
        self.to_entry.insert(0, today_str)
        
        # Устанавливаем начало дня как дату "От"
        start_of_day = datetime.now().replace(hour=0, minute=0, second=0).strftime('%Y-%m-%d %H:%M:%S')
        self.from_entry.delete(0, tk.END)
        self.from_entry.insert(0, start_of_day)

    def set_all_history(self):
        all_history_str = "2010-01-01 00:00:00"
        self.from_entry.delete(0, tk.END)
        self.from_entry.insert(0, all_history_str)
        
        # Устанавливаем текущее время как дату "До"
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.to_entry.delete(0, tk.END)
        self.to_entry.insert(0, current_time)

    def download_data(self):
        threading.Thread(target=self.download_data_thread).start()

    def download_data_thread(self):
        try:
            # Анимация начала загрузки
            self.animate_download_start()
            
            selected_assets_indices = list(self.asset_listbox.curselection())
            total_assets = len(selected_assets_indices)
            
            if total_assets == 0:
                messagebox.showwarning("Предупреждение", "Пожалуйста, выберите хотя бы один актв для загрузки")
                return
            
            # Увеличиваем количество рабочих потоков
            max_workers = min(int(self.threads_spinbox.get()), total_assets)
            chunk_size = 1  # Устанавливаем минимальный размер чанка
            
            if max_workers > 1:
                chunk_size = max(total_assets // max_workers, 1)
            
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = []
                for i in range(0, total_assets, chunk_size):
                    chunk_indices = selected_assets_indices[i:i + chunk_size]
                    chunk_assets = [self.asset_listbox.get(idx) for idx in chunk_indices]
                    
                    futures.append(
                        executor.submit(self.download_asset_chunk, chunk_assets)
                    )
                
                completed = 0
                for future in as_completed(futures):
                    completed += chunk_size
                    self.progress_bar['value'] = (completed / total_assets) * 100
                    self.master.update_idletasks()
                    
                    results = future.result()
                    for result in results:
                        if result:
                            self.loaded_assets_listbox.insert(tk.END, result)
                        
            # Обновление прогресса с анимацией
            self.update_progress_with_animation(completed, total_assets)
            
        except Exception as e:
            self.show_error_animation()
            messagebox.showerror("Ошибка", str(e))
        finally:
            self.animate_download_end()

    def download_asset_chunk(self, chunk_assets):
        results = []
        for asset in chunk_assets:
            result = self.download_single_asset(asset)
            results.append(result)
        return results

    def download_single_asset(self, selected_asset):
        """Загружает данные для одного актива"""
        try:
            timeframe = self.timeframe_combobox.get()
            from_date_str = self.from_entry.get()
            to_date_str = self.to_entry.get()
            
            # Формируем имя файла
            save_path = self.save_path_entry.get()
            safe_asset_name = selected_asset.replace('/', '_').replace(':', '')
            filename = os.path.join(save_path, f"{safe_asset_name}_{timeframe}.csv")
            
            # Проверяем существующий файл
            last_date = self.check_existing_file(filename)
            if last_date:
                from_date_str = (last_date + timedelta(minutes=1)).strftime('%Y-%m-%d %H:%M:%S')
                print(f"Докачиваем данные с {from_date_str}")
                
                if last_date >= pd.to_datetime(to_date_str):
                    print("Файл уже содержит актуальные данные")
                    return f"{selected_asset} - Актуален"

            # Конвертируем даты
            from_date = int(pd.to_datetime(from_date_str).timestamp() * 1000)
            to_date = int(pd.to_datetime(to_date_str).timestamp() * 1000)
            
            # Загружаем данные
            all_ohlcv = []
            current_timestamp = from_date
            request_count = 0
            
            while current_timestamp < to_date:
                try:
                    # Добавляем задержку между запросами
                    if request_count > 0:
                        time.sleep(0.12)  # 120ms задержка
                    
                    print(f"\nЗапрос #{request_count + 1}")
                    print(f"Текущая метка времени: {datetime.fromtimestamp(current_timestamp/1000)}")
                    print(f"Конечная метка времени: {datetime.fromtimestamp(to_date/1000)}")
                    
                    batch = self.exchange.fetch_ohlcv(
                        selected_asset,
                        timeframe=timeframe,
                        since=current_timestamp,
                        limit=1000
                    )
                    
                    if not batch:
                        break
                        
                    all_ohlcv.extend(batch)
                    request_count += 1
                    
                    # Обновляем timestamp для следующего запроса
                    current_timestamp = batch[-1][0] + 1
                    
                    print(f"Получено свечей в batch: {len(batch)}")
                    print(f"Последняя метка времени в batch: {datetime.fromtimestamp(batch[-1][0]/1000)}")
                    
                    # Если достигли лимита запросов, делаем паузу
                    if request_count % 10 == 0:
                        print("Достигнут лимит запросов, ожидание 1 секунда...")
                        time.sleep(1)
                    
                except Exception as e:
                    print(f"Ошибка при загрузке batch: {str(e)}")
                    time.sleep(1)  # Пауза при ошибке
                    continue  # Продолжаем следующую итерацию вместо break
            
            if all_ohlcv:
                df = pd.DataFrame(
                    all_ohlcv,
                    columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
                )
                
                # Преобразуем timestamp в datetime
                df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                
                # Фильтруем данные по указанному периоду
                mask = (df['timestamp'] >= pd.to_datetime(from_date_str)) & (df['timestamp'] <= pd.to_datetime(to_date_str))
                df = df[mask].copy()
                
                if not df.empty:
                    self.save_to_file(filename, df, append=bool(last_date))
                    return f"{selected_asset} - ОК ({len(df)} записей)"
                
            return f"{selected_asset} - Нет данных"
            
        except Exception as e:
            print(f"Ошибка при загрузке {selected_asset}: {str(e)}")
            return f"{selected_asset} - Ошибка: {str(e)}"

    def save_to_file(self, filename, df, append=False):
        """Сохраняет данные в формате TSLab CSV без заголовков"""
        try:
            # Преобразуем данные в формат TSLab
            tslab_df = pd.DataFrame()
            
            # Форматируем дату и время в нужный формат
            tslab_df['<DATE>'] = df['timestamp'].dt.strftime('%m/%d/%Y')
            tslab_df['<TIME>'] = df['timestamp'].dt.strftime('%H:%M')
            
            # Добавляем остальные колонки с правильными именами
            tslab_df['<OPEN>'] = df['open'].round(8)
            tslab_df['<HIGH>'] = df['high'].round(8)
            tslab_df['<LOW>'] = df['low'].round(8)
            tslab_df['<CLOSE>'] = df['close'].round(8)
            tslab_df['<VOL>'] = df['volume'].round(8)
            
            print(f"Сохранение файла: {filename}")
            
            # Создаем директорию если её нет
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            
            # Сохраняем с нужными параметрами форматирования:
            # - всегда без заголовков (header=False)
            # - разделитель ;
            # - без индекса
            # - decimal точка
            if append and os.path.exists(filename):
                tslab_df.to_csv(
                    filename,
                    mode='a',
                    sep=';',
                    index=False,
                    header=False,  # Никогда не добавляем заголовки
                    decimal='.',
                    float_format='%.8f'
                )
            else:
                tslab_df.to_csv(
                    filename,
                    mode='w',
                    sep=';',
                    index=False,
                    header=False,  # Никогда не добавляем заголовки
                    decimal='.',
                    float_format='%.8f'
                )
            
            print(f"Файл успешно сохранен: {filename}")
            
        except Exception as e:
            print(f"Ошибка при сохранении файла: {str(e)}")
            raise

    def prefetch_next_assets(self, selected_assets, current_index):
        """Предварительная загрузка следующих активов"""
        if current_index + 1 >= len(selected_assets):
            return
            
        next_assets = selected_assets[current_index + 1:current_index + 3]  # Предзагружаем 2 следующих актива
        for asset in next_assets:
            if asset not in self.prefetch_cache:
                threading.Thread(
                    target=self.prefetch_asset,
                    args=(asset,),
                    daemon=True
                ).start()
    
    def prefetch_asset(self, asset):
        """Фоновая загрузка актива"""
        try:
            cache_key = f"{asset}_{self.timeframe_combobox.get()}"
            if cache_key not in self.prefetch_cache:
                data = self.exchange.fetch_ohlcv(
                    asset,
                    self.timeframe_combobox.get(),
                    limit=100  # Загружаем только последние данные для проверки доступности
                )
                self.prefetch_cache[cache_key] = data
        except Exception:
            pass

    def select_all_assets(self):
        """Выделить все видимые элементы  списке"""
        self.asset_listbox.select_set(0, tk.END)

    def deselect_all_assets(self):
        """Снять выделение со всех элементов"""
        self.asset_listbox.selection_clear(0, tk.END)

    def create_status_bar(self, parent):
        status_frame = ttk.Frame(parent)
        status_frame.pack(fill="x", pady=5)
        
        # Добавляем индикаторы состояния
        self.connection_status = ttk.Label(status_frame, text="●", foreground="green")
        self.connection_status.pack(side="left", padx=5)
        
        self.status_message = ttk.Label(status_frame, text="Готов к работе")
        self.status_message.pack(side="left", fill="x", expand=True)
        
        self.download_speed = ttk.Label(status_frame, text="0 KB/s")
        self.download_speed.pack(side="right", padx=5)

    def animate_download_start(self):
        self.status_label.configure(foreground="blue")
        self.progress_bar.configure(mode="indeterminate")
        self.progress_bar.start(10)

    def animate_download_end(self):
        self.progress_bar.stop()
        self.progress_bar.configure(mode="determinate")
        self.status_label.configure(foreground="black")

    def bind_shortcuts(self):
        self.master.bind("<Control-a>", lambda e: self.select_all_assets())
        self.master.bind("<Control-d>", lambda e: self.deselect_all_assets())
        self.master.bind("<F5>", lambda e: self.load_markets())
        self.master.bind("<Control-s>", lambda e: self.download_data())

    def create_context_menu(self):
        self.context_menu = tk.Menu(self.master, tearoff=0)
        self.context_menu.add_command(label="Выделить все", command=self.select_all_assets)
        self.context_menu.add_command(label="Снять выделение", command=self.deselect_all_assets)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Копировать выбранное", command=self.copy_selected)
        
        self.asset_listbox.bind("<Button-3>", self.show_context_menu)

    def show_notification(self, message, level="info"):
        colors = {
            "info": "#2196F3",
            "success": "#4CAF50",
            "warning": "#FFC107",
            "error": "#F44336"
        }
        
        notification = tk.Toplevel(self.master)
        notification.overrideredirect(True)
        notification.configure(bg=colors[level])
        
        ttk.Label(
            notification,
            text=message,
            background=colors[level],
            foreground="white",
            padding=10
        ).pack()
        
        # Автоматически скрываем через 3 секунды
        self.master.after(3000, notification.destroy)

    def create_tooltip(self, widget, text):
        """Создает всплывающую подсказку для виджета"""
        
        def show_tooltip(event=None):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root + 10}+{event.y_root + 10}")
            
            # Создаем рамку для подсказки
            frame = ttk.Frame(tooltip, relief="solid", borderwidth=1)
            frame.pack(fill="both", expand=True)
            
            # Добавляем текст подсказки
            label = ttk.Label(frame, text=text, justify="left", padding=(5, 3))
            label.pack()
            
            def hide_tooltip():
                tooltip.destroy()
            
            # Сохраняем ссылку на tooltip, чтобы избежать его уничтожения сборщиком мусора
            widget.tooltip = tooltip
            widget.tooltip_id = widget.after(3000, hide_tooltip)  # Скрываем через 3 секунды
        
        def hide_tooltip(event=None):
            if hasattr(widget, 'tooltip'):
                widget.after_cancel(widget.tooltip_id)
                widget.tooltip.destroy()
                del widget.tooltip
        
        # Привязываем события показа/скрытия подсказки
        widget.bind('<Enter>', show_tooltip)
        widget.bind('<Leave>', hide_tooltip)
        widget.bind('<Button-1>', hide_tooltip)  # Скрываем при клике

    def copy_selected(self):
        """Копирует выбранные элементы в буфер обмена"""
        selected_indices = self.asset_listbox.curselection()
        if not selected_indices:
            return
        
        selected_items = [self.asset_listbox.get(idx) for idx in selected_indices]
        selected_text = '\n'.join(selected_items)
        
        # Копируем в буфер обмена
        self.master.clipboard_clear()
        self.master.clipboard_append(selected_text)
        
        # Показываем уведомление
        self.show_notification(f"Скопировано {len(selected_items)} элементов", "info")

    def show_context_menu(self, event):
        """Показывает контекстное меню в позиции клика правой кнопкой мыши"""
        try:
            # Получаем индекс элемента под курсором
            clicked_index = self.asset_listbox.nearest(event.y)
            
            # Если клик был не на элементе, выходим
            if clicked_index < 0:
                return
            
            # Если элемент под курсором не выбран, выбираем его
            if clicked_index not in self.asset_listbox.curselection():
                self.asset_listbox.selection_clear(0, tk.END)
                self.asset_listbox.selection_set(clicked_index)
            
            # Показываем контекстное меню
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            # Убираем захват меню
            self.context_menu.grab_release()

    def update_progress_with_animation(self, completed, total):
        """Обновляет прогресс-бар с анимацией"""
        # Плавно обновляем прогресс
        current = self.progress_bar['value']
        target = (completed / total) * 100
        
        def animate_to(current_value):
            if current_value < target:
                next_value = min(current_value + 1, target)
                self.progress_bar['value'] = next_value
                if next_value < target:
                    self.master.after(10, lambda: animate_to(next_value))
        
        animate_to(current)
        
        # Обновляем статус
        if completed == total:
            self.status_message.configure(text="Загрузка завершена")
            self.show_notification("Загрузка завершена успешно", "success")

    def show_error_animation(self):
        """Показывает анимацию ошибки"""
        # Останавливаем прогресс-бар
        self.progress_bar.stop()
        
        # Мигаем касным цветом
        def flash_error(count=3):
            if count > 0:
                self.status_message.configure(foreground="red")
                self.master.after(500, lambda: self.status_message.configure(foreground="black"))
                self.master.after(1000, lambda: flash_error(count - 1))
        
        flash_error()
        
        # Обновляем статус
        self.status_message.configure(text="Произошла ошибка при загрузке")
        self.show_notification("Ошибка при загрузке данных", "error")

    def check_existing_file(self, filename):
        """Проверяет существующий файл и возвращает последнюю дату"""
        try:
            if not os.path.exists(filename):
                return None
            
            # Читаем последние строки файла
            df = pd.read_csv(filename, sep=',')
            
            if df.empty:
                return None
            
            # Проверяем формат данных
            required_columns = ['<DATE>', '<TIME>', '<OPEN>', '<HIGH>', '<LOW>', '<CLOSE>', '<VOL>']
            if not all(col in df.columns for col in required_columns):
                print(f"Неверный формат файла {filename}")
                return None
            
            # Получаем последнюю дату
            last_date = pd.to_datetime(
                df['<DATE>'].iloc[-1] + ' ' + df['<TIME>'].iloc[-1], 
                format='%d.%m.%Y %H:%M:%S'
            )
            
            print(f"Найден существующий файл. Последняя дата: {last_date}")
            return last_date
            
        except Exception as e:
            print(f"Ошибка при проверке файла {filename}: {str(e)}")
            return None

    def create_donate_button(self):
        """Создает кнопку для доната в правом нижнем углу"""
        donate_button = ttk.Label(
            self.master,
            text="Оставить на чай",
            style="Donate.TLabel",  # Используем новый стиль
            cursor="hand2"
        )
        donate_button.pack(side="bottom", anchor="se", padx=15, pady=10)  # Немного увеличиваем отступы
        donate_button.bind("<Button-1>", lambda e: self.show_donate_window())
        
    def show_donate_window(self):
        """Показывает окно с информацией о донате"""
        donate_window = tk.Toplevel(self.master)
        donate_window.title("Поддержать проект")
        donate_window.geometry("400x250")
        donate_window.resizable(False, False)
        
        # Настраиваем стиль окна
        donate_window.configure(bg=self.colors['bg'])
        
        # Создаем фрейм для контента
        content_frame = ttk.Frame(donate_window)
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        ttk.Label(
            content_frame,
            text="Если вы хотите оставить на чай создателю",
            style="TLabel",
            font=("Segoe UI", 10, "bold")
        ).pack(pady=(0, 20))
        
        # USDT TRC20
        trc20_frame = ttk.Frame(content_frame)
        trc20_frame.pack(fill="x", pady=5)
        
        ttk.Label(
            trc20_frame,
            text="USDT(TRC20):",
            style="TLabel"
        ).pack(side="left")
        
        trc20_address = ttk.Label(
            trc20_frame,
            text="THZ6KS242EWwiM4wZY4A9Xb2ad6CzLBJWW",
            style="Link.TLabel",
            cursor="hand2"
        )
        trc20_address.pack(side="left", padx=5)
        trc20_address.bind("<Button-1>", lambda e: self.copy_to_clipboard(
            "THZ6KS242EWwiM4wZY4A9Xb2ad6CzLBJWW", 
            "USDT(TRC20) адрес скопирован в буфер обмена"
        ))
        
        # USDT BEP20
        bep20_frame = ttk.Frame(content_frame)
        bep20_frame.pack(fill="x", pady=5)
        
        ttk.Label(
            bep20_frame,
            text="USDT(BEP20):",
            style="TLabel"
        ).pack(side="left")
        
        bep20_address = ttk.Label(
            bep20_frame,
            text="0xAcA1bD5C4FEe1c02E7523476C2ad7913B2d78485",
            style="Link.TLabel",
            cursor="hand2"
        )
        bep20_address.pack(side="left", padx=5)
        bep20_address.bind("<Button-1>", lambda e: self.copy_to_clipboard(
            "0xAcA1bD5C4FEe1c02E7523476C2ad7913B2d78485",
            "USDT(BEP20) адрес скопирован в буфер обмена"
        ))
        
        # Telegram
        telegram_frame = ttk.Frame(content_frame)
        telegram_frame.pack(fill="x", pady=(20, 5))
        
        ttk.Label(
            telegram_frame,
            text="Для связи TELEGRAM:",
            style="TLabel"
        ).pack(side="left")
        
        telegram_link = ttk.Label(
            telegram_frame,
            text="@Alek_Mel",
            style="Link.TLabel",
            cursor="hand2"
        )
        telegram_link.pack(side="left", padx=5)
        telegram_link.bind("<Button-1>", lambda e: self.copy_to_clipboard(
            "@Alek_Mel",
            "Telegram контакт скопирован в буфер обмена"
        ))
        
        # Центрируем окно относительно главного окна
        donate_window.transient(self.master)
        donate_window.grab_set()
        self.master.wait_window(donate_window)
        
    def copy_to_clipboard(self, text, notification_text):
        """Копирует текст в буфер обмена и показывает уведомление"""
        self.master.clipboard_clear()
        self.master.clipboard_append(text)
        self.show_notification(notification_text, "info")

if __name__ == "__main__":
    root = tk.Tk()
    app = CryptoDownloader(root)
    root.mainloop()