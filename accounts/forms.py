from django import forms
from .models import MealType

class MealBookingForm(forms.Form):
    meal_type = forms.ChoiceField(choices=MealType.choices)
    date = forms.DateField(widget=forms.HiddenInput)
    action = forms.CharField(widget=forms.HiddenInput)  