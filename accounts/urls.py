from django.urls import path
from . import views
from django.conf.urls.static import static
from Smart_Meal_Management_System import settings


urlpatterns = [
    path('', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('home/', views.home_view, name='home'),
    path('logout/', views.logout_view, name='logout'),
    path('orders/', views.orders_view, name='orders'),

    path("orders/apply_confirm/<int:slot_id>/<str:day>/",views.apply_confirm, name="apply_confirm"),

    path("orders/apply_meal/<int:slot_id>/<str:day>/",views.apply_meal, name="apply_meal"),

    path("orders/cancel/<int:booking_id>/",views.cancel_booking, name="cancel_booking"),

    path("orders/qr/<int:booking_id>/",views.get_qr, name="get_qr"),
     
    path('special_orders/', views.special_orders_view, name='special_orders'),
    path('special_orders/apply/<int:slot_id>/', views.apply_special_order, name='apply_special_order'),
    path('exchange_qr/', views.exchange_qr_view, name='exchange_qr'),
] 


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 


try:
    from accounts.create_superuser import run
    run()
except Exception as e:
    print("Error creating superuser:", e)
