from django.urls import path
from main import views

app_name = "main"

urlpatterns = [
    path("zero/", views.zero, name="zero"),
    path("statistic/", views.statistic, name="statistic"),
    
    # order
    path("", views.orders, name="index"),
    path("all/", views.orders, name="orders"),
    path("add/", views.orders_add, name="orders_add"),
    path("info/<int:request_id>/", views.orders_info, name="orders_info"),
    path("add/postorder/", views.postaddorder, name="postaddorder"),
    path("postjson/", views.import_request_json, name="ordimpr"),
    path("red/<int:request_id>/", views.order_redact, name="orders_red"),
    path("docs/<int:request_id>/", views.order_docs, name="orders_docs"),
    path("orderred/<int:request_id>/", views.postorderred, name="postorderred"),
    path("export/<int:request_id>/", views.export_request_json, name="ordexp"),
    path("orders/search/", views.order_list, name='order_search'),
    path("del/<int:request_id>/", views.order_del, name="order_del"),
    
    # client
    path("clients/", views.clients, name="clients"),
    path("clients/add/", views.clients_add, name="clients_add"),
    path("clients/add/clientadd/", views.postaddclient, name="postaddclient"),
    
    path("clients/del/<int:request_id>/", views.client_del, name="client_del"),
    path("masters/del/<int:request_id>/", views.master_del, name="master_del"),
    
    # master
    path("masters/", views.masters, name="masters"),
    path("masters/add/", views.masters_add, name="masters_add"),
    path("masters/add/masteradd/", views.postaddmaster, name="postaddmaster"),
    
    # types
    path("types/", views.types, name="types"),
    
    # statuses
    path("statuses/", views.statuses, name="statuses"),
]
