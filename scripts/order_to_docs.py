from io import BytesIO
from django.utils import timezone
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from datetime import datetime


def generate_order_report(order):
    """
    Генерирует отчет о заявке в формате DOCX
    
    Args:
        order: Объект модели Orders
        
    Returns:
        BytesIO: Буфер с документом
    """
    # Создаем документ
    doc = Document()
    
    # Устанавливаем поля документа
    section = doc.sections[0]
    section.left_margin = Inches(1)
    section.right_margin = Inches(1)
    section.top_margin = Inches(1)
    section.bottom_margin = Inches(1)
    
    # Добавляем заголовок
    title = doc.add_heading(f'Отчет по заявке #{order.extid()}', 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # Добавляем дату создания отчета
    date_paragraph = doc.add_paragraph()
    date_paragraph.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    date_paragraph.add_run(f'Дата формирования: {timezone.now().strftime("%d.%m.%Y %H:%M")}')
    
    doc.add_paragraph()
    
    # Основная информация
    doc.add_heading('Основная информация', level=1)
    
    # Создаем таблицу для информации
    table = doc.add_table(rows=9, cols=2)
    table.style = 'Table Grid'
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    
    # Заполняем таблицу
    info_data = [
        ('Номер заявки:', str(order.extid())),
        ('Тип проблемы:', order.type_issue),
        ('Статус:', order.get_status_order_display() if hasattr(order, 'get_status_order_display') else order.status_order),
        ('Цена:', f'{order.price} руб.' if order.price else 'Не указана'),
        ('Клиент:', str(order.client)),
        ('Мастер:', str(order.master) if order.master else 'Не назначен'),
        ('Дата создания:', order.created_date.strftime("%d.%m.%Y %H:%M") if hasattr(order, 'created_date') else 'Не указана'),
        ('Последнее обновление:', order.created_date.strftime("%d.%m.%Y %H:%M") if hasattr(order, 'created_date') else 'Не указана'),
        ('Код прилагаемой техники:', order.idTech if order.idTech else 'Не указана'),
    ]
    
    for i, (label, value) in enumerate(info_data):
        cell_label = table.cell(i, 0)
        cell_value = table.cell(i, 1)
        
        cell_label.text = label
        cell_value.text = str(value)
        
        # Настраиваем стиль первой колонки
        cell_label.paragraphs[0].runs[0].bold = True
        cell_label.paragraphs[0].runs[0].font.size = Pt(11)
        
    # Описание проблемы
    doc.add_heading('Описание проблемы', level=1)
    description_para = doc.add_paragraph()
    if order.comment_prob:
        description_para.add_run(order.comment_prob)
    else:
        description_para.add_run('Нет описания')
    
    # Дополнительная информация (если есть поля)
    doc.add_heading('Дополнительная информация о клиенте', level=1)
    
    # Проверяем наличие дополнительных полей
    extra_fields = []
    
    
    if hasattr(order.client, 'phone') and order.client.phone:
        extra_fields.append(('Телефон:', order.client.phone))
    
    if hasattr(order.client, 'email') and order.client.email:
        extra_fields.append(('Email:', order.client.email))
    
    
    if extra_fields:
        extra_table = doc.add_table(rows=len(extra_fields), cols=2)
        extra_table.style = 'Table Grid'
        
        for i, (label, value) in enumerate(extra_fields):
            cell_label = extra_table.cell(i, 0)
            cell_value = extra_table.cell(i, 1)
            
            cell_label.text = label
            cell_value.text = value
            
            cell_label.paragraphs[0].runs[0].bold = True
    else:
        doc.add_paragraph('Дополнительная информация отсутствует')
    
    # Подписи
    doc.add_paragraph()
    doc.add_paragraph()
    
    doc.add_heading('Ответственный стороны', level=1)
    
    signatures_table = doc.add_table(rows=2, cols=2)
    signatures_table.style = 'Table Grid'
    
    signatures_table.cell(0, 0).text = 'Руководитель:'
    signatures_table.cell(0, 1).text = f'{str(order.master)}   ___________________'
    signatures_table.cell(1, 0).text = 'Клиент:'
    signatures_table.cell(1, 1).text = f'{str(order.client)}   ___________________'
    
    # Сохраняем в буфер
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    
    return buffer