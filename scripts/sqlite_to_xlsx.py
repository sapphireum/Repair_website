import sqlite3
import pandas as pd
from pathlib import Path

def export_sqlite_table_to_excel(db_path, table_name, excel_path, sheet_name=None):
    """
    Экспортирует таблицу из SQLite базы данных в файл Excel.
    
    Параметры:
    db_path (str): Путь к файлу SQLite базы данных
    table_name (str): Имя таблицы для экспорта
    excel_path (str): Путь для сохранения Excel файла
    sheet_name (str, optional): Имя листа в Excel (по умолчанию - имя таблицы)
    """
    
    try:
        # Подключаемся к базе данных
        conn = sqlite3.connect(db_path)
        
        # Читаем таблицу в DataFrame
        query = f"SELECT * FROM {table_name}"
        df = pd.read_sql_query(query, conn)
        
        # Проверяем, есть ли данные
        if df.empty:
            print(f"Предупреждение: Таблица '{table_name}' пуста")
        else:
            print(f"Найдено {len(df)} строк в таблице '{table_name}'")
        
        # Закрываем соединение с БД
        conn.close()
        
        # Создаем имя листа, если не указано
        if sheet_name is None:
            sheet_name = table_name
        
        # Ограничиваем длину имени листа (Excel ограничивает 31 символом)
        if len(sheet_name) > 31:
            sheet_name = sheet_name[:31]
            print(f"Имя листа сокращено до: {sheet_name}")
        
        # Сохраняем в Excel
        with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name=sheet_name, index=False)
            
            # Автоматически подгоняем ширину столбцов
            worksheet = writer.sheets[sheet_name]
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
        
        print(f"✅ Таблица '{table_name}' успешно экспортирована в '{excel_path}'")
        
    except sqlite3.Error as e:
        print(f"❌ Ошибка базы данных: {e}")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

def list_tables(db_path):
    """Выводит список всех таблиц в базе данных."""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        conn.close()
        
        if tables:
            print("\nДоступные таблицы в базе данных:")
            for i, (table_name,) in enumerate(tables, 1):
                print(f"  {i}. {table_name}")
            return [table[0] for table in tables]
        else:
            print("В базе данных нет таблиц")
            return []
    except sqlite3.Error as e:
        print(f"❌ Ошибка при получении списка таблиц: {e}")
        return []



if __name__ == "__main__":
    # Пример 1: Экспорт конкретной таблицы
    db_file = "C:\\Users\\Momo\\Desktop\\Hobby\\Pythons\\Web_django\\dev_env\\app1\\db.sqlite3" # "example.db"  # Укажите путь к вашему файлу .db
    excel_file = "exported_data.xlsx"
    
    # Показываем список таблиц
    tables = list_tables(db_file)
    
    if tables:
        # Экспортируем таблицу
        export_sqlite_table_to_excel(db_file, "orders", excel_file)
        
        # Пример экспорта с пользовательским именем листа
        # export_sqlite_table_to_excel(db_file, "employees", "my_data.xlsx", "Сотрудники")
    