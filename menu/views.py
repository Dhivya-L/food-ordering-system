from sqlite3 import Date
from django.shortcuts import render, get_object_or_404, redirect
from .models import Order, OrderItem
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .models import FoodItem, Cart
from django.core.mail import send_mail
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.shortcuts import redirect
from .models import Order, OrderItem, Cart
from django.shortcuts import redirect, render
from django.contrib.admin.views.decorators import staff_member_required
from .models import Order
from django.contrib.auth.models import User
from django.db.models import Sum
from datetime import date
from django.db.models.functions import TruncDate
from django.shortcuts import render
from django.core.paginator import Paginator
from django.utils import timezone
from django.db.models import Count
from django.db.models.functions import TruncDate
import json
import csv
from django.http import HttpResponse
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from django.http import HttpResponse




def menu_list(request):

    query = request.GET.get("q")

    if query:
        foods = FoodItem.objects.filter(
            name__icontains=query
        )
    else:
        foods = FoodItem.objects.all()

    return render(
        request,
        "menu/menu_list.html",
        {
            "foods": foods
        }
    )


def add_to_cart(request, food_id):
    food = FoodItem.objects.get(id=food_id)

    user = User.objects.first()

    cart_item, created = Cart.objects.get_or_create(
        user=user,
        food=food
    )

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    return redirect('menu')


def cart_view(request):
    user = User.objects.first()
    cart_items = Cart.objects.filter(user=user)

    return render(request, 'menu/cart.html', {
        'cart_items': cart_items
    })

def checkout(request):
    if not request.user.is_authenticated:
        return redirect("login")

    cart_items = Cart.objects.filter(
        user=request.user
    )

    total = 0

    for item in cart_items:
        total += item.food.price * item.quantity
    print("TOTAL =", total)

    return render(
        request,
        "menu/checkout.html",
        {
            "cart_items": cart_items,
            "total": total
        }
    )

    

def add_to_cart(request, food_id):
    food = FoodItem.objects.get(id=food_id)

    user = User.objects.first()

    cart_item, created = Cart.objects.get_or_create(
        user=user,
        food=food
    )

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    return redirect('menu')

def cart_view(request):

    if not request.user.is_authenticated:
        return redirect("login")

    cart_items = Cart.objects.filter(
        user=request.user
    )

    total = 0

    for item in cart_items:

        item.item_total = (
            item.food.price *
            item.quantity
        )

        total += item.item_total

    # Optional safe debug
    if cart_items.exists():
        first_item = cart_items.first()
        print(
            first_item.food.price,
            first_item.quantity
        )

    return render(
        request,
        "menu/cart.html",
        {
            "cart_items": cart_items,
            "total": total
        }
    )
    

def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            login(request, user)
            return redirect("menu")

        else:
            return render(
                request,
                "menu/login.html",
                {"error": "Invalid username or password"}
            )

    return render(request, "menu/login.html")

def register_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        # check duplicate username
        if User.objects.filter(username=username).exists():
            return render(
                request,
                "menu/register.html",
                {"error": "Username already exists"}
            )

        # create user
        User.objects.create_user(
            username=username,
            password=password
        )

        return redirect("login")

    return render(request, "menu/register.html")



def order_history(request):

    if not request.user.is_authenticated:
        return redirect("login")

    orders = Order.objects.filter(
        user=request.user
    ).order_by("-created_at")

    print("Orders found:", orders.count())

    return render(
        request,
        "menu/order_history.html",
        {
            "orders": orders
        }
    )



def logout_view(request):
    logout(request)
    return redirect("menu")



def add_to_cart(request, food_id):
    if not request.user.is_authenticated:
        return redirect("login")

    try:
        food = FoodItem.objects.get(id=food_id)
    except FoodItem.DoesNotExist:
        return redirect("menu")

    cart_item, created = Cart.objects.get_or_create(
        user=request.user,
        food=food
    )

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    return redirect("menu")


def place_order(request):

    if not request.user.is_authenticated:
        return redirect("login")

    cart_items = Cart.objects.filter(
        user=request.user
    )

    print("Cart count:", cart_items.count())

    total = 0

    # Calculate total
    for item in cart_items:
        total += item.food.price * item.quantity

    payment_method = request.POST.get(
        "payment_method",
        "Cash"
    )

    order = Order.objects.create(
        user=request.user,
        total_price=total,
        payment_method=payment_method
    )

    for item in cart_items:

        OrderItem.objects.create(
            order=order,
            food=item.food,
            quantity=item.quantity,
            price=item.food.price
        )
    # Clear cart AFTER saving items
    cart_items.delete()

    print("Creating item:", item.food.name)
    print("EMAIL FUNCTION RUNNING")

    send_mail(
        subject="Order Confirmation",

        message=(
            f"Hello {request.user.username},\n\n"
            f"Your order has been placed successfully.\n\n"
            f"Order ID: {order.id}\n"
            f"Total: ₹{total}\n"
            f"Payment: {payment_method}\n"
            f"Status: Pending"
        ),

        from_email=None,

        recipient_list=[
            request.user.email
        ],

        fail_silently=False,
        
    )

    return redirect(
        "order_success",
        order_id=order.id
    )

def order_success(request, order_id):

    order = Order.objects.get(
        id=order_id,
        user=request.user
    )

    return render(
        request,
        "menu/order_success.html",
        {
            "order": order
        }
    )


def order_detail(request, order_id):

    if not request.user.is_authenticated:
        return redirect("login")

    order = get_object_or_404(
        Order,
        id=order_id
    )

    # Get order items
    order_items = OrderItem.objects.filter(
        order=order
    )

    # Calculate total
    total_amount = 0

    for item in order_items:
        total_amount += item.price * item.quantity

    # SIMPLE status update
    if request.method == "POST":

        new_status = request.POST.get(
            "status"
        )

        print("Updating status to:", new_status)

        if new_status:
            order.status = new_status
            order.save()

            print("Status saved in DB:", order.status)

            return redirect(
                "order_detail",
                order_id=order.id
            )

    return render(
        request,
        "menu/order_detail.html",
        {
            "order": order,
            "order_items": order_items,
            "total_amount": total_amount,
        }
    )



def remove_from_cart(request, item_id):

    if not request.user.is_authenticated:
        return redirect("login")

    cart_item = Cart.objects.get(
        id=item_id,
        user=request.user
    )

    cart_item.delete()

    return redirect("cart")

def increase_quantity(request, item_id):

    cart_item = Cart.objects.get(
        id=item_id,
        user=request.user
    )

    cart_item.quantity += 1
    cart_item.save()

    return redirect("cart")

def decrease_quantity(request, item_id):

    if not request.user.is_authenticated:
        return redirect("login")

    cart_item = Cart.objects.get(
        id=item_id,
        user=request.user
    )

    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()

    return redirect("cart")


@staff_member_required
def admin_orders(request):

    orders = Order.objects.all().order_by(
        "-created_at"
    )

    return render(
        request,
        "menu/admin_orders.html",
        {
            "orders": orders
        }
    )


def admin_dashboard(request):

    recent_orders = list(
    Order.objects.all().order_by("-created_at")[:5])

    total_orders = Order.objects.count()

    total_revenue = Order.objects.aggregate(
        Sum("total_price")
    )["total_price__sum"] or 0

    pending_orders = Order.objects.filter(
        status="Pending"
    ).count()

    completed_orders = Order.objects.filter(
        status="Delivered"
    ).count()

    context = {
        "recent_orders": recent_orders,
        "total_orders": total_orders,
        "total_revenue": total_revenue,
        "pending_orders": pending_orders,
        "completed_orders": completed_orders,
    }

    print("Recent orders:", recent_orders)

    return render(
        request,
        "menu/admin_dashboard.html",
        context
    )


def download_invoice(request, order_id):

    order = Order.objects.get(
        id=order_id,
        user=request.user
    )

    response = HttpResponse(
        content_type="application/pdf"
    )

    response["Content-Disposition"] = (
        f'attachment; filename="invoice_{order.id}.pdf"'
    )

    doc = SimpleDocTemplate(response)

    styles = getSampleStyleSheet()

    elements = []

    elements.append(
        Paragraph("Order Invoice", styles["Title"])
    )

    elements.append(Spacer(1, 20))

    elements.append(
        Paragraph(f"Order ID: {order.id}", styles["BodyText"])
    )

    elements.append(
        Paragraph(
            f"Customer: {request.user.username}",
            styles["BodyText"]
        )
    )

    elements.append(
        Paragraph(
            f"Total: ₹{order.total_price}",
            styles["BodyText"]
        )
    )

    elements.append(
        Paragraph(
            f"Payment: {order.payment_method}",
            styles["BodyText"]
        )
    )

    elements.append(
        Paragraph(
            f"Status: {order.status}",
            styles["BodyText"]
        )
    )

    elements.append(
        Paragraph(
            f"Date: {order.created_at}",
            styles["BodyText"]
        )
    )

    doc.build(elements)

    return response

def cancel_order(request, order_id):

    if not request.user.is_authenticated:
        return redirect("login")

    order = Order.objects.get(
        id=order_id,
        user=request.user
    )

    # Allow cancel only if order is still pending
    if order.status == "Pending":
        order.status = "Cancelled"
        order.save()

    return redirect(
        "order_detail",
        order_id=order.id
    )

@staff_member_required


def admin_dashboard(request):

    # Recent Orders
    recent_orders = Order.objects.order_by(
        "-created_at"
    )[:5]

    # Total Orders
    total_orders = Order.objects.count()

    # Total Revenue
    total_revenue = Order.objects.aggregate(
        Sum("total_price")
    )["total_price__sum"] or 0

    # Pending Orders
    pending_orders = Order.objects.filter(
        status="Pending"
    ).count()

    # Today's Orders
    today = date.today()

    today_orders = Order.objects.filter(
        created_at__date=today
    ).count()

    completed_orders = Order.objects.filter(
    status="Delivered"
    ).count()

    # Top Selling Items

    top_items = (
        OrderItem.objects.values("food__name").annotate(
        total_sold=Sum("quantity")
        )
        .order_by("-total_sold")[:5]
    )

    


    #orders per day

    orders_per_day = (
        Order.objects
        .annotate(order_date=TruncDate("created_at"))
        .values("order_date")
        .annotate(count=Count("id"))
        .order_by("order_date")
    )

    order_dates = []
    order_counts = []

    for item in orders_per_day:
        order_dates.append(
            item["order_date"].strftime("%Y-%m-%d")
        )
        order_counts.append(
            item["count"]
        )

    print("ORDER DATES:", order_dates)
    print("ORDER COUNTS:", order_counts)
    # Revenue per day chart data

    revenue_per_day = (
        Order.objects
        .annotate(revenue_date=TruncDate("created_at"))
        .values("revenue_date")
        .annotate(total_revenue=Sum("total_price"))
        .order_by("revenue_date")
    )

    revenue_dates = []
    revenue_totals = []

    for item in revenue_per_day:
        revenue_dates.append(
            item["revenue_date"].strftime("%Y-%m-%d")
        )
        revenue_totals.append(
            float(item["total_revenue"])
        )

    print("REVENUE DATES:", revenue_dates)
    print("REVENUE TOTALS:", revenue_totals)

   

# Order Status Distribution

    status_data = (
        Order.objects
        .values("status")
        .annotate(count=Count("id"))
    )

    status_labels = []
    status_counts = []

    for item in status_data:
        status_labels.append(item["status"])
        status_counts.append(item["count"])

    print("STATUS LABELS:", status_labels)
    print("STATUS COUNTS:", status_counts)

    context = {

    "recent_orders": recent_orders,
    "today_orders": today_orders,
    "total_orders": total_orders,
    "total_revenue": total_revenue,
    "pending_orders": pending_orders,
    "completed_orders": completed_orders,
    "top_items": top_items,

    "order_dates": json.dumps(order_dates),
    "order_counts": json.dumps(order_counts),


    # ADD THESE

    "revenue_dates": json.dumps(revenue_dates),
    "revenue_totals": json.dumps(revenue_totals),
    "status_labels": json.dumps(status_labels),
    "status_counts": json.dumps(status_counts),
    }
    return render(
        request,
        "menu/admin_dashboard.html",
        context
    )


def export_orders_csv(request):

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="orders.csv"'

    writer = csv.writer(response)

    # Header
    writer.writerow([
        'Order ID',
        'User',
        'Total',
        'Order Date'
    ])

    orders = Order.objects.all()

    for order in orders:

        # Get total field safely
        total_value = getattr(order, 'total', None) \
                   or getattr(order, 'total_price', None) \
                   or getattr(order, 'amount', None) \
                   or getattr(order, 'price', None)

        writer.writerow([
            order.id,
            order.user.username,
            total_value,
            order.created_at
        ])

    return response