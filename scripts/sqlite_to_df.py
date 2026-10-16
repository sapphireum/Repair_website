from datetime import datetime

import sqlite3
import pandas as pd
import numpy as np
import psycopg2
import json

import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

import warnings

warnings.filterwarnings("ignore")

def load_json(file_path):
    """Загружает JSON файл и возвращает данные"""
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data

def postgres_to_dataframe_psycopg2(host, database, user, password, port):
    """Загружает данные из PostgreSQL в DataFrame pandas используя psycopg2"""
    
    # Устанавливаем соединение
    conn = psycopg2.connect(
        host=host,
        database=database,
        user=user,
        password=password,
        port=int(port)
    )
    
    # SQL запрос
    query = """
        SELECT 
            "order".id as "Уникальный номер",
            "order".comment_prob as "Описание заявки",
            "client".name as "Клиент",
            "master".name as "Мастер",
            "typeissue".name as "Тип проблемы",
            "statusorder".name as "Статус",
            "order".price as "Цена"
        FROM "order"
        INNER JOIN "client" ON "order"."client_id" = "client"."id"
        INNER JOIN "master" ON "order"."master_id" = "master"."id"
        INNER JOIN "statusorder" ON "order"."status_order_id" = "statusorder"."id"
        INNER JOIN "typeissue" ON "order"."type_issue_id" = "typeissue"."id"
    """
    
    # Загружаем данные в DataFrame
    df = pd.read_sql_query(query, conn)
    
    # Закрываем соединение
    conn.close()
    
    return df



def sqlite_to_dataframe(db_path, table_name):
    """Загружает таблицу из SQLite в DataFrame pandas"""
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query(
        f'SELECT "order".id as "Уникальный номер", "order".comment_prob as "Описание заявки",'
        f' "client".name as "Клиент", "master".name as "Мастер", "typeissue".name as "Тип проблемы", "statusorder".name as "Статус", "order".price as "Цена" FROM "{table_name}"'
        f'INNER JOIN "client" on "order"."client_id" = "client"."id"'
        f'INNER JOIN "master" on "order"."master_id" = "master"."id"'
        f'INNER JOIN "statusorder" on "order"."status_order_id" = "statusorder"."id"'
        f'INNER JOIN "typeissue" on "order"."type_issue_id" = "typeissue"."id"',
        conn,
    )
    conn.close()
    return df


def analyze_services(df):
    """Анализирует данные по типам услуг и ценам"""

    # Базовая статистика по типам услуг
    # print("=" * 60)
    # print("СТАТИСТИКА ПО ТИПАМ УСЛУГ")
    # print("=" * 60)

    stats = (
        df.groupby("Тип проблемы")
        .agg({"Цена": ["count", "sum", "mean", "min", "max"]})
        .round(2)
    )

    stats.columns = [
        "Количество",
        "Общая сумма",
        "Средняя цена",
        "Мин. цена",
        "Макс. цена",
    ]
    stats = stats.sort_values("Количество", ascending=False)

    # print(stats)

    # print("\n" + "=" * 60)
    # print("ОБЩАЯ СТАТИСТИКА")
    # print("=" * 60)
    # print(f"Всего заказов: {len(df)}")
    # print(f"Общая выручка: {df['Цена'].sum():.2f} руб.")
    # print(f"Средний чек: {df['Цена'].mean():.2f} руб.")
    # print(f"Минимальная цена услуги: {df['Цена'].min():.2f} руб.")
    # print(f"Максимальная цена услуги: {df['Цена'].max():.2f} руб.")

    # Самый популярный тип услуги
    most_popular = df["Тип проблемы"].mode()[0]
    most_popular_count = df["Тип проблемы"].value_counts()[most_popular]
    # print(f"\nСамая популярная услуга: '{most_popular}' ({most_popular_count} заказов)")

    # Самая дорогая услуга
    most_expensive = df.loc[df["Цена"].idxmax(), "Тип проблемы"]
    # print(f"Самая дорогая услуга: '{most_expensive}' ({df['Цена'].max():.2f} руб.)")

    return df


def create_visualizations(df, pdf_path=f"service_statistics_{datetime.now().day}-{datetime.now().month}-{datetime.now().year}.pdf"):
    """Создает графики и сохраняет их в PDF"""

    with PdfPages(pdf_path) as pdf:

        # Страница 1: Общая информация
        fig = plt.figure(figsize=(12, 8))
        fig.suptitle("Анализ услуг сервисного центра", fontsize=16, fontweight="bold")

        # Текстовая информация
        plt.axis("off")
        text = f"""
        ОБЩАЯ СТАТИСТИКА:
        
        • Всего заказов: {len(df)}
        • Общая выручка: {df['Цена'].sum():,.2f} руб.
        • Средний чек: {df['Цена'].mean():,.2f} руб.
        • Минимальная цена: {df['Цена'].min():,.2f} руб.
        • Максимальная цена: {df['Цена'].max():,.2f} руб.
        
        КОЛИЧЕСТВО УСЛУГ:
        
        """

        for service, count in df["Тип проблемы"].value_counts().head(10).items():
            text += f"• {service}: {count} заказов\n"

        plt.text(
            0.1,
            0.9,
            text,
            transform=plt.gca().transAxes,
            fontsize=12,
            verticalalignment="top",
            fontfamily="monospace",
        )

        pdf.savefig(fig, bbox_inches="tight")
        plt.close()

        # График 1: Количество заказов по типам услуг (горизонтальная гистограмма)
        fig, ax = plt.subplots(figsize=(12, 8))
        service_counts = df["Тип проблемы"].value_counts()
        colors = plt.cm.viridis(np.linspace(0, 1, len(service_counts)))
        bars = ax.barh(range(len(service_counts)), service_counts.values, color=colors)
        ax.set_yticks(range(len(service_counts)))
        ax.set_yticklabels(service_counts.index)
        ax.set_xlabel("Количество заказов", fontsize=12)
        ax.set_title("Популярность услуг", fontsize=14, fontweight="bold")

        # Добавляем значения на бары
        for i, (bar, count) in enumerate(zip(bars, service_counts.values)):
            ax.text(
                bar.get_width() + 0.5,
                bar.get_y() + bar.get_height() / 2,
                str(count),
                ha="left",
                va="center",
                fontsize=10,
            )

        plt.tight_layout()
        pdf.savefig(fig, bbox_inches="tight")
        plt.close()

        # График 2: Выручка по типам услуг
        fig, ax = plt.subplots(figsize=(12, 8))
        revenue_by_service = (
            df.groupby("Тип проблемы")["Цена"].sum().sort_values(ascending=True)
        )
        colors = plt.cm.plasma(np.linspace(0, 1, len(revenue_by_service)))
        bars = ax.barh(
            range(len(revenue_by_service)), revenue_by_service.values, color=colors
        )
        ax.set_yticks(range(len(revenue_by_service)))
        ax.set_yticklabels(revenue_by_service.index)
        ax.set_xlabel("Выручка (руб.)", fontsize=12)
        ax.set_title("Выручка по типам услуг", fontsize=14, fontweight="bold")

        # Добавляем значения
        for i, (bar, revenue) in enumerate(zip(bars, revenue_by_service.values)):
            ax.text(
                bar.get_width() + 100,
                bar.get_y() + bar.get_height() / 2,
                f"{revenue:,.0f} руб.",
                ha="left",
                va="center",
                fontsize=9,
            )

        plt.tight_layout()
        pdf.savefig(fig, bbox_inches="tight")
        plt.close()

        # График 3: Средняя цена по типам услуг
        fig, ax = plt.subplots(figsize=(12, 8))
        avg_price = (
            df.groupby("Тип проблемы")["Цена"].mean().sort_values(ascending=False)
        )
        colors = plt.cm.RdYlGn(np.linspace(0, 1, len(avg_price)))
        bars = ax.bar(range(len(avg_price)), avg_price.values, color=colors)
        ax.set_xticks(range(len(avg_price)))
        ax.set_xticklabels(avg_price.index, rotation=45, ha="right")
        ax.set_ylabel("Средняя цена (руб.)", fontsize=12)
        ax.set_title("Средняя стоимость услуг", fontsize=14, fontweight="bold")

        # Добавляем значения
        for bar, price in zip(bars, avg_price.values):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 10,
                f"{price:,.0f} руб.",
                ha="center",
                va="bottom",
                fontsize=9,
            )

        plt.tight_layout()
        pdf.savefig(fig, bbox_inches="tight")
        plt.close()

        # График 4: Круговая диаграмма распределения заказов
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 7))

        # Круговая диаграмма для топ-5 услуг
        top_services = df["Тип проблемы"].value_counts().head(5)
        other_count = len(df) - top_services.sum()
        if other_count > 0:
            top_services["Другие"] = other_count

        colors = plt.cm.Set3(np.linspace(0, 1, len(top_services)))
        wedges, texts, autotexts = ax1.pie(
            top_services.values,
            labels=top_services.index,
            autopct="%1.1f%%",
            colors=colors,
            startangle=90,
        )
        ax1.set_title(
            "Распределение заказов по услугам", fontsize=12, fontweight="bold"
        )

        # Круговая диаграмма распределения выручки
        top_revenue = (
            df.groupby("Тип проблемы")["Цена"]
            .sum()
            .sort_values(ascending=False)
            .head(5)
        )
        other_revenue = df["Цена"].sum() - top_revenue.sum()
        if other_revenue > 0:
            top_revenue["Другие"] = other_revenue

        wedges2, texts2, autotexts2 = ax2.pie(
            top_revenue.values,
            labels=top_revenue.index,
            autopct="%1.1f%%",
            colors=colors,
            startangle=90,
        )
        ax2.set_title(
            "Распределение выручки по услугам", fontsize=12, fontweight="bold"
        )

        plt.tight_layout()
        pdf.savefig(fig, bbox_inches="tight")
        plt.close()

        # График 5: Ящик с усами (boxplot) для цен
        fig, ax = plt.subplots(figsize=(12, 8))

        # Подготовка данных для boxplot
        services = df["Тип проблемы"].value_counts().head(10).index
        data_for_box = [
            df[df["Тип проблемы"] == service]["Цена"].values for service in services
        ]

        bp = ax.boxplot(data_for_box, labels=services, patch_artist=True)

        # Раскрашиваем ящики
        for patch, color in zip(
            bp["boxes"], plt.cm.viridis(np.linspace(0, 1, len(services)))
        ):
            patch.set_facecolor(color)

        ax.set_ylabel("Цена (руб.)", fontsize=12)
        ax.set_title("Распределение цен по типам услуг", fontsize=14, fontweight="bold")
        plt.xticks(rotation=45, ha="right")
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        pdf.savefig(fig, bbox_inches="tight")
        plt.close()

        # График 6: Статистика по статусам заказов
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 7))

        # Количество по статусам
        status_counts = df["Статус"].value_counts()
        colors = plt.cm.Paired(np.linspace(0, 1, len(status_counts)))
        bars = ax1.bar(range(len(status_counts)), status_counts.values, color=colors)
        ax1.set_xticks(range(len(status_counts)))
        ax1.set_xticklabels(status_counts.index, rotation=45, ha="right")
        ax1.set_ylabel("Количество заказов", fontsize=12)
        ax1.set_title("Заказы по статусам", fontsize=12, fontweight="bold")

        # Добавляем значения
        for bar, count in zip(bars, status_counts.values):
            ax1.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.5,
                str(count),
                ha="center",
                va="bottom",
                fontsize=10,
            )

        # Круговая диаграмма по статусам
        wedges, texts, autotexts = ax2.pie(
            status_counts.values,
            labels=status_counts.index,
            autopct="%1.1f%%",
            colors=colors,
            startangle=90,
        )
        ax2.set_title("Распределение по статусам", fontsize=12, fontweight="bold")

        plt.tight_layout()
        pdf.savefig(fig, bbox_inches="tight")
        plt.close()

        # График 7: Топ-10 клиентов по сумме заказов
        fig, ax = plt.subplots(figsize=(12, 8))
        top_clients = (
            df.groupby("Клиент")["Цена"].sum().sort_values(ascending=False).head(10)
        )
        colors = plt.cm.RdYlGn(np.linspace(0, 1, len(top_clients)))[::-1]
        bars = ax.barh(range(len(top_clients)), top_clients.values, color=colors)
        ax.set_yticks(range(len(top_clients)))
        ax.set_yticklabels(top_clients.index)
        ax.set_xlabel("Сумма заказов (руб.)", fontsize=12)
        ax.set_title("Топ-10 клиентов по сумме заказов", fontsize=14, fontweight="bold")

        # Добавляем значения
        for i, (bar, amount) in enumerate(zip(bars, top_clients.values)):
            ax.text(
                bar.get_width() + 100,
                bar.get_y() + bar.get_height() / 2,
                f"{amount:,.0f} руб.",
                ha="left",
                va="center",
                fontsize=9,
            )

        plt.tight_layout()
        pdf.savefig(fig, bbox_inches="tight")
        plt.close()

        # График 8: Топ-10 мастеров по выручке
        fig, ax = plt.subplots(figsize=(12, 8))
        top_masters = (
            df.groupby("Мастер")["Цена"].sum().sort_values(ascending=False).head(10)
        )
        colors = plt.cm.plasma(np.linspace(0, 1, len(top_masters)))
        bars = ax.bar(range(len(top_masters)), top_masters.values, color=colors)
        ax.set_xticks(range(len(top_masters)))
        ax.set_xticklabels(top_masters.index, rotation=45, ha="right")
        ax.set_ylabel("Выручка (руб.)", fontsize=12)
        ax.set_title("Топ-10 мастеров по выручке", fontsize=14, fontweight="bold")

        # Добавляем значения
        for bar, amount in zip(bars, top_masters.values):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 500,
                f"{amount:,.0f}",
                ha="center",
                va="bottom",
                fontsize=9,
                rotation=45,
            )

        plt.tight_layout()
        pdf.savefig(fig, bbox_inches="tight")
        plt.close()

        # График 9: Тепловая карта корреляции (если есть числовые данные)
        fig, ax = plt.subplots(figsize=(10, 8))

        # Создаем сводную таблицу
        pivot_table = df.pivot_table(
            values="Цена",
            index="Мастер",
            columns="Тип проблемы",
            aggfunc="count",
            fill_value=0,
        )

        # Ограничиваем размер для читаемости
        if pivot_table.shape[0] > 15:
            pivot_table = pivot_table.iloc[:15, :]
        if pivot_table.shape[1] > 10:
            pivot_table = pivot_table.iloc[:, :10]

        im = ax.imshow(pivot_table.values, cmap="YlOrRd", aspect="auto")
        ax.set_xticks(range(len(pivot_table.columns)))
        ax.set_yticks(range(len(pivot_table.index)))
        ax.set_xticklabels(pivot_table.columns, rotation=45, ha="right", fontsize=8)
        ax.set_yticklabels(pivot_table.index, fontsize=8)
        ax.set_xlabel("Тип проблемы", fontsize=12)
        ax.set_ylabel("Мастер", fontsize=12)
        ax.set_title(
            "Тепловая карта: количество заказов по мастерам и услугам",
            fontsize=12,
            fontweight="bold",
        )

        # Добавляем цветовую шкалу
        plt.colorbar(im, ax=ax, label="Количество заказов")

        plt.tight_layout()
        pdf.savefig(fig, bbox_inches="tight")
        plt.close()
        # print(type(pdf))
        # print("--------------------------")
        # print(pdf)
        
    return pdf

    # print(f"\n✅ Графики успешно сохранены в файл: {pdf_path}")



if __name__ == "__main__":
    # SQLite3
    # path = "C:\\Users\\Momo\\Desktop\\Hobby\\Pythons\\Web_django\\dev_env\\app1\\db.sqlite3"
    # df = sqlite_to_dataframe(path, "Order")
    
    path = "C:\\Users\\Momo\\Desktop\\Hobby\\Pythons\\Web_django\\dev_env\\app1\\config.json"
    data_json = load_json(path)
    dict_json = data_json[0]

    df = postgres_to_dataframe_psycopg2(dict_json['host'], dict_json['database'], dict_json['user'], dict_json['password'], dict_json['port'])

    df_new = analyze_services(df)
    print(df_new)
    create_visualizations(df)
