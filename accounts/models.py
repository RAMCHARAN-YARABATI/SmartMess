
from django.db import models
from django.utils import timezone

class StudentUser(models.Model):
    name        = models.CharField(max_length=100)
    rollnumber  = models.CharField(max_length=20)
    department  = models.CharField(max_length=50)
    gender      = models.CharField(max_length=10)
    email       = models.EmailField(unique=True)
    password    = models.CharField(max_length=200)

    refund_wallet = models.DecimalField(default=15000.00,
                                        max_digits=10, decimal_places=2)

    def __str__(self):
        return self.email
    

class MealSlot(models.Model):
    BREAKFAST = "Breakfast"
    LUNCH     = "Lunch"
    DINNER    = "Dinner"
    MEALS = [(BREAKFAST, BREAKFAST), (LUNCH, LUNCH), (DINNER, DINNER)]

    name  = models.CharField(max_length=15, choices=MEALS, unique=True)
    price = models.PositiveIntegerField()                  

    def __str__(self):
        return self.name



class BookingRecord(models.Model):
    user = models.ForeignKey(StudentUser, on_delete=models.CASCADE)
    meal_type = models.ForeignKey(MealSlot, on_delete=models.CASCADE)
    date = models.DateField()
    status = models.CharField(max_length=20, default="Booked")
    booked_at = models.DateTimeField(auto_now_add=True)
    qr_token = models.CharField(max_length=100, blank=True, null=True)
    qr_image = models.ImageField(upload_to='qr_codes/', blank=True, null=True)
    is_special_order = models.BooleanField(default=False) 

    def __str__(self):
        return f"{self.user.name} - {self.meal_type.name} - {self.date} ({self.status})"

    class Meta:
        unique_together = (('user', 'meal_type', 'date', 'is_special_order', 'status'),)


class SpecialOrderSlot(models.Model):
    meal_type = models.ForeignKey(MealSlot, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.localdate) 
    max_slots = models.PositiveIntegerField(default=25) 
    available_slots = models.PositiveIntegerField(default=25) 
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('meal_type', 'date') 

    def __str__(self):
        return f"Special Order: {self.meal_type.name} on {self.date} - {self.available_slots}/{self.max_slots} slots"

