from django.shortcuts import render, redirect, get_object_or_404
from .models import Orders, Clients, Masters, TypeIssues, StatusOrders
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, FileResponse
from django.contrib import messages
from django.utils import timezone

import os
import json
from datetime import datetime

from scripts.order_to_docs import generate_order_report
from scripts.sqlite_to_df import load_json, postgres_to_dataframe_psycopg2, analyze_services, create_visualizations




# ACClogin (passwd)
# Accounts, Main - +info

@login_required
def statistic(request):
    path = ".\\config.json"
    data_json = load_json(path)
    dict_json = data_json[0]

    df = postgres_to_dataframe_psycopg2(dict_json['host'], dict_json['database'], dict_json['user'], dict_json['password'], dict_json['port'])
    df_new = analyze_services(df)

    name_pdf_stat = f"service_statistics_{datetime.now().day}-{datetime.now().month}-{datetime.now().year}.pdf" 
    pdf = create_visualizations(df, name_pdf_stat)
    
    # drop pdf
    response = FileResponse(open(name_pdf_stat, 'rb'), 
                           as_attachment=True, 
                           filename=name_pdf_stat)
    
    # del tempfile
    response._resource_closers.append(lambda: os.unlink(name_pdf_stat))
    
    return response

@login_required
def order_list(request):
    query = request.GET.get('q', '')
    
    if query:
        orders = Orders.objects.all().filter(comment_prob__icontains=query)
        context = {'full_ord': orders, 'query': query}
    else:
        {'full_ord': [], 'query': query}
    return render(request, "main/orders.html", context)


@login_required
def order_del(request, request_id):
    deleted = True
    
    new_request, created = Orders.objects.update_or_create(
                defaults={
                    "is_deleted": deleted,
                },
                id=request_id,
            )
    return redirect("../../")


@login_required
def client_del(request, request_id):
    deleted = True
    
    new_request, created = Clients.objects.update_or_create(
                defaults={
                    "is_deleted": deleted,
                },
                id=request_id,
            )
    return redirect("../../")


@login_required
def master_del(request, request_id):
    deleted = True
    
    new_request, created = Masters.objects.update_or_create(
                defaults={
                    "is_deleted": deleted,
                },
                id=request_id,
            )
    return redirect("../../")


@login_required
def order_docs(request, request_id):
    try:
        order = get_object_or_404(Orders, id=request_id)
        
        if not request.user.is_staff and request.user != order.client:
            messages.error(request, 'У вас нет доступа к этому отчету')
            return redirect('order_detail', order_id=request_id)
        
        doc_buffer = generate_order_report(order)
        
        response = HttpResponse(
            doc_buffer.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
        
        filename = f'order_report_{order.id}_{timezone.now().strftime("%Y%m%d")}.docx'
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        messages.success(request, f'Отчет по заявке #{order.id} успешно сформирован')
        return response
        
    except Exception as e:
        messages.error(request, f'Ошибка при формировании отчета: {str(e)}')
        return redirect('order_list')


 # GOOOD
@login_required
def postorderred(request, request_id):
    master = request.POST.get("master")
    client = request.POST.get("client")
    typeiss = request.POST.get("type")
    status = request.POST.get("status")
    comment_prob = request.POST.get("problem")
    idtech = request.POST.get("tech")
    price = request.POST.get("price")
    deleted = request.POST.get("deleted")
    
    if deleted == "true":
        deleted = True
    else: 
        deleted = False
    mas = Masters.objects.filter(id=master).first()
    cli = Clients.objects.filter(id=client).first()
    typ = TypeIssues.objects.filter(id=typeiss).first()
    stat = StatusOrders.objects.filter(id=status).first()
    
    new_request, created = Orders.objects.update_or_create(
                defaults={
                    "comment_prob": comment_prob,
                    "type_issue": typ,
                    "client_id": cli,
                    "master_id": mas,
                    "status_order": stat,
                    "price": price,
                    "is_deleted": deleted,
                    "idTech": idtech,
                },
                id=request_id,
            )
    if created:
        messages.success(request, f"Заявка №{new_request.id} успешно импортирована")
    else:
        messages.success(request, f"Заявка №{new_request.id} обновлена")
    return redirect("../../")


# GOOOD
@login_required
def order_redact(request, request_id):
    request_obj = get_object_or_404(Orders, id=request_id)
    master = Masters.objects.values()
    client = Clients.objects.values()
    typeiss = TypeIssues.objects.values()
    status = StatusOrders.objects.values()
    context = {
        "full_ord": request_obj,
        "masters": master,
        "clients": client,
        "typeissue": typeiss,
        "statuses": status,
    }
    return render(request, "main/orders_red.html", context)


# GOOOD
@login_required
def import_request_json(request):
    """
    Импорт одной заявки из JSON файла
    """
    if request.method == "POST" and request.FILES.get("json_file"):
        json_file = request.FILES["json_file"]
        
        try:
            data = json.loads(json_file.read().decode("utf-8"))
            
            mas = Masters.objects.filter(id=data.get("master_id")).first()
            cli = Clients.objects.filter(id=data.get("client_id")).first()
            typ = TypeIssues.objects.filter(id=data.get("problem_type")).first()
            stat = StatusOrders.objects.filter(id=data.get("status")).first()
            
            
            new_request, created = Orders.objects.update_or_create(
                defaults={
                    "comment_prob": data.get("description"),
                    "type_issue": typ,
                    "client_id": cli,
                    "master_id": mas,
                    "status_order": stat,
                    "price": data.get("price"),
                    "idTech": data.get("idtech"),
                },
                id=data.get("unique_code") if data.get("unique_code") else Orders.objects.last().pk,
            )
            
            if created:
                messages.success(request, f"Заявка №{new_request.id} успешно импортирована")
            else:
                messages.success(request, f"Заявка №{new_request.id} обновлена")
                
        except json.JSONDecodeError as e:
            messages.error(request, f"Ошибка парсинга JSON: {str(e)}")
        except Exception as e:
            messages.error(request, f"Ошибка импорта: {str(e)}")
        
        return redirect("../")
    
    messages.error(request, "Файл не загружен или неверный метод запроса")
    return redirect("../")


# GOOOD
@login_required
def export_request_json(request, request_id):
    """
    Экспорт одной заявки в JSON файл
    """
    request_obj = get_object_or_404(Orders, id=request_id)

    data = {
        "unique_code": request_obj.pk,
        "description": request_obj.comment_prob,
        "problem_type": request_obj.type_issue.pk,
        "master_id": request_obj.master.pk,
        "client_id": request_obj.client.pk,
        "status": request_obj.status_order.pk,
        "price": float(request_obj.price),
        "idtech": request_obj.idTech,
    }

    # drop JSON to client
    response = HttpResponse(
        json.dumps(data, ensure_ascii=False, indent=4), content_type="application/json"
    )
    response["Content-Disposition"] = (
        f'attachment; filename="ord{request_obj.pk}_{datetime.now().day}-{datetime.now().month}-{datetime.now().year}_{datetime.now().hour}-{datetime.now().minute}-{datetime.now().second}.json"'
    )
    return response


# GOOOD
def zero(request):
    context = {
        "content": "Пустая тестовая страница",
    }
    return render(request, "main/zero.html", context)


# GOOOD
@login_required
def types(request):
    queryset = TypeIssues.objects.all()
    context = {"full_ord": queryset}

    return render(request, "main/types.html", context)

# GOOOD
@login_required
def statuses(request):
    queryset = StatusOrders.objects.all()
    context = {"full_ord": queryset}

    return render(request, "main/statuses.html", context)


# GOOOD
# @login_required
def orders(request):
    queryset = Orders.objects.all()
    context = {"full_ord": queryset}

    return render(request, "main/orders.html", context)


# GOOOD
def orders_info(request, request_id):
    queryset = Orders.objects.filter(id=request_id).first()
    context = {"full_ord": queryset}

    return render(request, "main/orders_info.html", context)


# GOOOD
@login_required
def orders_add(request):
    master = Masters.objects.values()
    client = Clients.objects.values()
    typeiss = TypeIssues.objects.values()
    status = StatusOrders.objects.values()
    context = {
        "masters": master,
        "clients": client,
        "typeissue": typeiss,
        "statuses": status,
    }
    return render(request, "main/orders_add.html", context)


# GOOOD
@login_required
def postaddorder(request):
    master = request.POST.get("master")
    client = request.POST.get("client")
    typeiss = request.POST.get("type")
    status = request.POST.get("status")
    comment_prob = request.POST.get("problem")
    price = request.POST.get("price")
    idtech = request.POST.get("tech")

    mas = Masters.objects.filter(id=master).first()
    cli = Clients.objects.filter(id=client).first()
    typ = TypeIssues.objects.filter(id=typeiss).first()
    stat = StatusOrders.objects.filter(id=status).first()

    order = Orders.objects.create(
        master=mas,
        client=cli,
        type_issue=typ,
        status_order=stat,
        price=price,
        comment_prob=comment_prob,
        idTech = idtech,
    )
    return redirect("../")


# GOOOD
@login_required
def clients(request):
    queryset = Clients.objects.all()
    context = {"full_ord": queryset}

    return render(request, "main/clients.html", context)


# GOOOD
@login_required
def clients_add(request):
    return render(request, "main/clients_add.html")


# GOOOD
@login_required
def postaddclient(request):
    name = request.POST.get("name")
    phone = request.POST.get("phone")
    email = request.POST.get("email")

    client = Clients.objects.create(
        name=name,
        phone=phone,
        email=email,
    )
    return redirect("../")


# GOOOD
@login_required
def masters(request):
    queryset = Masters.objects.all()
    context = {"full_ord": queryset}

    return render(request, "main/masters.html", context)


# GOOOD
@login_required
def masters_add(request):
    return render(request, "main/masters_add.html")


# GOOOD
@login_required
def postaddmaster(request):
    name = request.POST.get("name")
    phone = request.POST.get("phone")
    email = request.POST.get("email")
    address = request.POST.get("address")

    master = Masters.objects.create(
        name=name,
        phone=phone,
        email=email,
        address=address,
    )
    return redirect("../")
