import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

import warnings

warnings.filterwarnings("ignore")



def prepare_features(df):
    """Подготовка признаков для модели"""

    # Создаем копию данных
    data = df.copy()

    # Кодируем категориальные признаки
    le_type = LabelEncoder()
    le_master = LabelEncoder()
    le_client = LabelEncoder()
    le_status = LabelEncoder()

    data["Тип_услуги_код"] = le_type.fit_transform(data["Тип проблемы"])
    data["Мастер_код"] = le_master.fit_transform(data["Мастер"])
    data["Клиент_код"] = le_client.fit_transform(data["Клиент"])
    data["Статус_код"] = le_status.fit_transform(data["Статус"])

    # Добавляем доп признаки
    # Длина описания заявки (как признак сложности)
    data["Длина_описания"] = data["Описание заявки"].fillna("").apply(len)

    data["Есть_описание"] = data["Описание заявки"].notna().astype(int)

    return data, le_type, le_master, le_client, le_status


def predict_price_by_service(df):
    """Предсказание цены на основе типа услуги и других параметров"""

    # print("=" * 70)
    # print("ПРЕДСКАЗАНИЕ СТОИМОСТИ ЗАЯВКИ НА ОСНОВЕ ТИПА УСЛУГИ")
    # print("=" * 70)

    # Подготовка признаков
    data, le_type, le_master, le_client, le_status = prepare_features(df)

    feature_columns = [
        "Тип_услуги_код",
        "Мастер_код",
        "Клиент_код",
        "Статус_код",
        "Длина_описания",
        "Есть_описание",
    ]

    X = data[feature_columns]
    y = data["Цена"]

    # обуч и тест выборки
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # Обуч модель
    model = LinearRegression()
    model.fit(X_train, y_train)

    # Предсказ на тест выборке
    y_pred_train = model.predict(X_train)
    y_pred_test = model.predict(X_test)

    # Оценка
    # print("\n[ + ] КАЧЕСТВО МОДЕЛИ:")
    # print("-" * 70)
    # print(f"R² Score (обучение): {r2_score(y_train, y_pred_train):.4f}")
    # print(f"R² Score (тест): {r2_score(y_test, y_pred_test):.4f}")
    # print(f"MAE (тест): {mean_absolute_error(y_test, y_pred_test):.2f} руб.")
    # print(f"RMSE (тест): {np.sqrt(mean_squared_error(y_test, y_pred_test)):.2f} руб.")

    # print("\n[ + ] ПРОГНОЗ СТОИМОСТИ ПО ТИПАМ УСЛУГ:")
    # print("-" * 70)

    # df для прогноза
    unique_services = df["Тип проблемы"].unique()
    predictions = []

    for service in unique_services:
        # Берем средние значения для других признаков
        service_data = (
            df[df["Тип проблемы"] == service].iloc[0]
            if len(df[df["Тип проблемы"] == service]) > 0
            else None
        )
        if service_data is not None:
            # Средние значения для прогноза
            avg_master = le_type.transform([service])[0]
            avg_client = data["Клиент_код"].mode()[0]
            avg_status = data["Статус_код"].mode()[0]
            avg_desc_len = data["Длина_описания"].mean()
            avg_has_desc = data["Есть_описание"].mean()

            # Формируем признаки для прогноза
            features = np.array(
                [
                    [
                        avg_master,
                        data["Мастер_код"].mode()[0],
                        avg_client,
                        avg_status,
                        avg_desc_len,
                        avg_has_desc,
                    ]
                ]
            )
            predicted_price = model.predict(features)[0]
            # Реальная средняя цена
            actual_avg_price = df[df["Тип проблемы"] == service]["Цена"].mean()

            predictions.append(
                {
                    "Тип услуги": service,
                    "Текущая_средняя_цена": actual_avg_price,
                    "Прогнозируемая_цена": predicted_price,
                    "Отклонение": predicted_price - actual_avg_price,
                    "Количество_заказов": len(df[df["Тип проблемы"] == service]),
                }
            )

    # df с прогнозами
    predictions_df = pd.DataFrame(predictions)
    predictions_df = predictions_df.sort_values("Прогнозируемая_цена", ascending=False)
    predictions_df["Текущая_средняя_цена"] = (
        predictions_df["Текущая_средняя_цена"].round(0).astype(int)
    )
    predictions_df["Прогнозируемая_цена"] = (
        predictions_df["Прогнозируемая_цена"].round(0).astype(int)
    )
    predictions_df["Отклонение"] = predictions_df["Отклонение"].round(0).astype(int)

    # print(predictions_df.to_string(index=False))

    return model, predictions_df, data

