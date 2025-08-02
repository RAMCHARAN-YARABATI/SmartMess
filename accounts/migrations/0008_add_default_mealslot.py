
from django.db import migrations

def insert_default_meals(apps, schema_editor):
    MealSlot = apps.get_model('accounts', 'MealSlot')
    MealSlot.objects.get_or_create(name='Breakfast', price=15)
    MealSlot.objects.get_or_create(name='Lunch', price=50)
    MealSlot.objects.get_or_create(name='Dinner', price=50)

class Migration(migrations.Migration):
    dependencies = [
        ('accounts', '0007_alter_bookingrecord_unique_together_and_more'),
    ]
    
    operations = [
        migrations.RunPython(insert_default_meals),
    ]
