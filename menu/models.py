from django.db import models
from django.contrib.auth.models import User

class FoodItem(models.Model):

    name = models.CharField(
        max_length=100
    )

    description = models.TextField()

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    available = models.BooleanField(
        default=True
    )

    image = models.ImageField(upload_to="food_images/",blank=True,null=True)

    def __str__(self):
        return self.name


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    food = models.ForeignKey(FoodItem, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.food.name} ({self.quantity})"

from django.contrib.auth.models import User
from django.db import models
    


class Order(models.Model):

    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Preparing", "Preparing"),
        ("Out for Delivery", "Out for Delivery"),
        ("Delivered", "Delivered"),
        ("Cancelled", "Cancelled"),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    payment_method = models.CharField(
        max_length=50
    )


    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="Pending"
    )


    created_at = models.DateTimeField(
        auto_now_add=True
    )


class OrderItem(models.Model):

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE
    )

    food = models.ForeignKey(
        FoodItem,
        on_delete=models.CASCADE
    )

    quantity = models.IntegerField()

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    @property
    def subtotal(self):
        return self.quantity * self.price

    def __str__(self):
        return self.food.name


