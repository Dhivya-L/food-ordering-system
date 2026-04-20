from django.urls import path
from . import views


urlpatterns = [

    path('', views.menu_list, name='menu'),

    path('add/<int:food_id>/', views.add_to_cart, name='add_to_cart'),

    path('cart/', views.cart_view, name='cart'),

    path('checkout/', views.checkout, name='checkout'),

    path('place-order/', views.place_order, name='place_order'),

    path('register/', views.register_view, name='register'),

    path('login/', views.login_view, name='login'),

    path('logout/', views.logout_view, name='logout'),

    path('place-order/',views.place_order,name='place_order'),

    path('orders/',views.order_history,name='order_history'),

    path('order/<int:order_id>/',views.order_detail,name='order_detail'),

    path('remove/<int:item_id>/',views.remove_from_cart,name='remove_from_cart'),

    path('increase/<int:item_id>/',views.increase_quantity,name='increase_quantity'),

    path('decrease/<int:item_id>/',views.decrease_quantity,name='decrease_quantity'),

    path("admin-orders/",views.admin_orders,name="admin_orders"),

    path("order-success/<int:order_id>/",views.order_success,name="order_success"),

    path("admin-dashboard/",views.admin_dashboard,name="admin_dashboard"),

    path("invoice/<int:order_id>/",views.download_invoice,name="download_invoice"),

    path("cancel-order/<int:order_id>/",views.cancel_order,name="cancel_order"),

    path("order/<int:order_id>/",views.order_detail,name="order_detail"),

    path("admin-dashboard/",views.admin_dashboard,name="admin_dashboard"),

    path('export-orders/',views.export_orders_csv,name='export_orders_csv'),

]






