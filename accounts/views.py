
import random,io, uuid, qrcode, 
from django.shortcuts import render, redirect,get_object_or_404, redirect
from .models import  StudentUser, BookingRecord, MealSlot, SpecialOrderSlot
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from django.http import FileResponse
from django.core.files.base import ContentFile
from django.utils import timezone
from django.contrib import messages
from datetime import timedelta, datetime
from django.views.decorators.http import require_POST
from .utils  import SHOW_CUTOFF_TIMES, is_window_open, is_qr_visible_for_meal, is_special_order_window_open
import threading
from django.shortcuts import render, redirect
from django.core.mail import send_mail




def signup_view(request):
    if request.method == 'POST':
        name = request.POST['name']
        rollnumber = request.POST['rollnumber']
        department = request.POST['department']
        gender = request.POST['gender']
        email = request.POST['email']
        password = request.POST['password']
        repeat_password = request.POST['repeat_password']

        '''

        if not email.endswith('@student.nitw.ac.in'):
            return render(request, 'accounts/signup.html', {'error_message': 'Only NITW student emails allowed.'})
        
        '''

        if password != repeat_password:
            return render(request, 'accounts/signup.html', {'error_message': 'Passwords do not match.'})

        if StudentUser.objects.filter(email=email).exists():
            return render(request, 'accounts/signup.html', {'error_message': 'Email already exists.'})

        # Save the user
        user = StudentUser(
            name=name,
            rollnumber=rollnumber,
            department=department,
            gender=gender,
            email=email,
            password=make_password(password)
        )                            
        user.save()

        return render(request, 'accounts/signup.html', {'success_message': 'Signup successful!'})

    return render(request, 'accounts/signup.html')



# Thread-safe OTP storage
otp_storage = {}

# Utility function to send email asynchronously
def send_async_mail(subject, message, from_email, recipient_list):
    threading.Thread(
        target=send_mail,
        args=(subject, message, from_email, recipient_list),
        kwargs={'fail_silently': False}
    ).start()


def send_otp_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')

        # Check if email exists
        if not StudentUser.objects.filter(email=email).exists():
            return render(request, 'accounts/login.html', {
                'error': 'This email is not registered. Please sign up first.',
                'email': email
            })

        # Check OTP input
        if 'otp1' in request.POST:
            otp_entered = ''.join([
                request.POST.get('otp1', ''),
                request.POST.get('otp2', ''),
                request.POST.get('otp3', ''),
                request.POST.get('otp4', ''),
            ])

            if otp_storage.get(email) == otp_entered:
                request.session['user_email'] = email
                # Clear OTP after successful login
                otp_storage.pop(email, None)
                return redirect('home')
            else:
                return render(request, 'accounts/login.html', {
                    'email': email,
                    'otp_sent': True,
                    'error': "Invalid OTP. Try again.",
                })

        # Generate OTP and store
        otp = str(random.randint(1000, 9999))
        otp_storage[email] = otp

        # Send OTP asynchronously
        send_async_mail(
            subject='Your One-Time Password (OTP) for MyMess',
            message=f"""
Hello,

Your One-Time Password (OTP) to log in to your MyMess account is: {otp}
Please enter this code within 5 minutes to complete your login.
If you did not request this OTP, please ignore this message.

Regards,  
MyMess Team
            """,
            from_email='noreplymymessbooking@gmail.com',
            recipient_list=[email]
        )

        return render(request, 'accounts/login.html', {
            'email': email,
            'otp_sent': True,
            'message': 'OTP sent to your email!',
        })

    return render(request, 'accounts/login.html')


#  Session-based “login required” decorator
def session_login_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if 'user_email' not in request.session:
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return _wrapped_view


@session_login_required
def home_view(request):
    email = request.session.get('user_email')

    if not email:
        return redirect('login') 

    try:
        user = StudentUser.objects.get(email=email)
    except StudentUser.DoesNotExist:
        return redirect('login')

    return render(request, 'accounts/home.html', {
        'firstname': user.name,
        'email': user.email,
        'rollnumber': user.rollnumber,
        'department': user.department,
        'gender': user.gender,
    })


def logout_view(request):
    request.session.flush() # This clears all session data
    return redirect('login')


def orders_view(request):
    user      = StudentUser.objects.get(email=request.session["user_email"])
    now = datetime.now()
    today     = now.date()
    tomorrow  = today + timedelta(days=1)

    slots = MealSlot.objects.all().order_by("id")

    today_orders    = {b.meal_type_id: b for b in BookingRecord.objects.filter(user=user, date=today)}
    tomorrow_orders = {b.meal_type_id: b for b in BookingRecord.objects.filter(user=user, date=tomorrow)}

    today_flags    = {s.id: is_window_open(s.name, "today")    for s in slots}  #True or False 
    tomorrow_flags = {s.id: is_window_open(s.name, "tomorrow") for s in slots} #True or False

    cut_off = {s.id:is_qr_visible_for_meal(s.name) for s in slots }

    combined_orders = ( BookingRecord.objects.filter(user=user, date__in=[today, tomorrow]).order_by("-date") )
    transactions = BookingRecord.objects.filter(user=user).order_by("-booked_at") 

    return render(
        request,
        "accounts/orders.html",
        {
            "wallet":            user.refund_wallet,
            "today":             today,
            "tomorrow":          tomorrow,
            "slots":             slots,
            "today_orders":      today_orders,
            "tomorrow_orders":   tomorrow_orders,
            "today_flags":       today_flags,
            "tomorrow_flags":    tomorrow_flags,
            "combined_orders":   combined_orders,
            "transactions":      transactions,
            "cut_off":           cut_off,
            "window_text": {
                "Breakfast": "2 p.m. – midnight",
                "Lunch":     "today 5 p.m. to tomorrow 9 a.m.",
                "Dinner":    "today 10 p.m. to tomorrow 4 p.m.",
            },
        },
    )


def apply_confirm(request, slot_id, day):
    user        = StudentUser.objects.get(email=request.session["user_email"])
    slot        = get_object_or_404(MealSlot, id=slot_id)
    date_target = timezone.localdate() if day == "today" else timezone.localdate() + timedelta(days=1)

    already     = BookingRecord.objects.filter(user=user, meal_type=slot, date=date_target).exists()
    is_open     = is_window_open(slot.name, day)

    return render(
        request,
        "accounts/apply_confirm.html",
        {
            "slot": slot,
            "day": day,
            "date": date_target,
            "already_booked": already,
            "is_open": is_open,
        },
    )


def apply_meal(request, slot_id, day):
    user        = StudentUser.objects.get(email=request.session["user_email"])
    slot        = get_object_or_404(MealSlot, id=slot_id)
    date_target = timezone.localdate() if day == "today" else timezone.localdate() + timedelta(days=1)

    if not is_window_open(slot.name, day):
        messages.error(request, "Booking window closed.")
        return redirect("orders")

    if BookingRecord.objects.filter(user=user, meal_type=slot, date=date_target).exists():
        messages.warning(request, "Already booked.")
        return redirect("orders")

    if user.refund_wallet < slot.price:
        messages.error(request, "Insufficient balance.")
        return redirect("orders")

    BookingRecord.objects.create(user=user, meal_type=slot, date=date_target)
    user.refund_wallet -= slot.price
    user.save(update_fields=["refund_wallet"])

    messages.success(request, f"{slot.name} booked for {date_target}.")
    return redirect("orders")


@require_POST
@session_login_required
def cancel_booking(request, booking_id):
    booking = get_object_or_404(
        BookingRecord, id=booking_id, user__email=request.session["user_email"]
    )
    
    if booking.status in ["Canceled", "Transferred_Out"]:
        messages.warning(request, "This booking is already canceled or transferred.")
        return redirect("orders")

    meal_cutoff_end_time = SHOW_CUTOFF_TIMES.get(booking.meal_type.name, [None, None])[1]
    now_time = timezone.localtime().time()
    
    if booking.date == timezone.localdate() and meal_cutoff_end_time and now_time > meal_cutoff_end_time:
        messages.error(request, "Cut-off passed – cannot cancel this meal.")
        return redirect("orders")

    if booking.is_special_order:
        try:
            special_slot = SpecialOrderSlot.objects.get(
                meal_type=booking.meal_type,
                date=booking.date
            )
            special_slot.available_slots += 1
            special_slot.save()
        except SpecialOrderSlot.DoesNotExist:
            pass 
        
        booking.user.refund_wallet += booking.meal_type.price 
        messages.success(request, f"Special order canceled and refunded ₹{booking.meal_type.price}.")
    elif booking.status == "Booked":
        booking.user.refund_wallet += booking.meal_type.price 
        messages.success(request, f"Canceled and refunded ₹{booking.meal_type.price}.")
    elif booking.status == "Transferred_In": 
        booking.user.refund_wallet += booking.meal_type.price 
        messages.success(request, f"Transferred meal canceled and refunded ₹{booking.meal_type.price}.")
    
    booking.status   = "Canceled" 
    booking.qr_token = None
    if booking.qr_image:
        booking.qr_image.delete(save=False) 
    booking.qr_image = None
    booking.save(update_fields=["status", "qr_token", "qr_image"])
    booking.user.save(update_fields=["refund_wallet"]) 

    return redirect("orders")



def get_qr(request, booking_id):
    booking = get_object_or_404(
        BookingRecord, id=booking_id, user__email=request.session["user_email"]
    )

    #Generate QR only once
    if not booking.qr_token or not booking.qr_image:
        qr_text = (
            f"Meal:{booking.meal_type.name}|"
            f"Name:{booking.user.name}|"
            f"Roll:{booking.user.rollnumber}|"
            f"Date:{booking.date}|"
            f"Status:{booking.status}|"
            f"Type:{'Special' if booking.is_special_order else 'Regular'}" )
        img = qrcode.make(qr_text)

        # Save QR image to memory buffer
        buf = io.BytesIO()
        img.save(buf, format="PNG")

        # Save it to qr_codes/ inside media folder
        booking.qr_token = str(uuid.uuid4())
        booking.qr_image.save(
            f"qr_codes/qr_{booking.qr_token}.png",
            ContentFile(buf.getvalue()),
            save=True
        )

    return FileResponse(booking.qr_image.open("rb"), content_type="image/png")



@session_login_required
def special_orders_view(request):
    """
    Displays the special order options for today's meals.
    """
    user = StudentUser.objects.get(email=request.session["user_email"])
    today = timezone.localdate()
    slots = MealSlot.objects.all().order_by("id")

    special_order_data = []
    for meal_slot in slots:
        # Get or create the SpecialOrderSlot for today's date and this meal type.
        # This ensures an entry exists for each meal type for today, with default slots.
        special_slot, created = SpecialOrderSlot.objects.get_or_create(
            meal_type=meal_slot,
            date=today,
            defaults={'max_slots': 25, 'available_slots': 25, 'is_active': True}
        )

        has_regular_booking = BookingRecord.objects.filter(
            user=user,
            meal_type=meal_slot,
            date=today,
            is_special_order=False,
            status="Booked" 
        ).exists()

        has_special_booking = BookingRecord.objects.filter(
            user=user,
            meal_type=meal_slot,
            date=today,
            is_special_order=True,
            status="Booked" 
        ).exists()

        is_window_open_now = is_special_order_window_open(meal_slot.name)

        special_order_data.append({
            'meal_slot': meal_slot,
            'special_slot': special_slot,
            'can_book': (
                special_slot.is_active and
                special_slot.available_slots > 0 and
                not has_regular_booking and 
                not has_special_booking and 
                is_window_open_now 
            ),
            'has_regular_booking': has_regular_booking,
            'has_special_booking': has_special_booking,
            'is_window_open_now': is_window_open_now,
        })

    return render(request, 'accounts/special_orders.html', {
        'special_order_data': special_order_data,
        'today': today,
    })


@require_POST
@session_login_required
def apply_special_order(request, slot_id):
    """
    Handles the POST request to book a special order.
    """
    user = StudentUser.objects.get(email=request.session["user_email"])
    meal_slot = get_object_or_404(MealSlot, id=slot_id)
    today = timezone.localdate()

    special_slot = get_object_or_404(SpecialOrderSlot, meal_type=meal_slot, date=today)

    
    if not is_special_order_window_open(meal_slot.name):
        messages.error(request, "Special order window is closed.")
        return redirect('special_orders')

    if special_slot.available_slots <= 0:
        messages.error(request, f"No slots available for {meal_slot.name} special order.")
        return redirect('special_orders')

    if BookingRecord.objects.filter(user=user, meal_type=meal_slot, date=today, is_special_order=False, status="Booked").exists():
        messages.warning(request, f"You already have a regular booking for {meal_slot.name} today.")
        return redirect('special_orders')

    if BookingRecord.objects.filter(user=user, meal_type=meal_slot, date=today, is_special_order=True, status="Booked").exists():
        messages.warning(request, f"You already have a special order for {meal_slot.name} today.")
        return redirect('special_orders')

    if user.refund_wallet < meal_slot.price:
        messages.error(request, "Insufficient balance for special order.")
        return redirect('special_orders')

   
    try:
        special_slot.available_slots -= 1
        special_slot.save()

        BookingRecord.objects.create(
            user=user,
            meal_type=meal_slot,
            date=today,
            status="Booked",
            is_special_order=True 
        )

        user.refund_wallet -= meal_slot.price
        user.save(update_fields=["refund_wallet"])

        messages.success(request, f"Special order for {meal_slot.name} booked successfully!")
    except Exception as e:
        messages.error(request, f"Error booking special order: {e}")
        special_slot.available_slots += 1
        special_slot.save()
    return redirect('special_orders')

@session_login_required
def exchange_qr_view(request):
    current_user_email = request.session["user_email"]
    giver = get_object_or_404(StudentUser, email=current_user_email)
    
    meal_slots = MealSlot.objects.all().order_by('id')
    
    exchange_session_data = request.session.get('exchange_otp_data')

    if request.method == 'POST':
        if 'login' in request.POST:
            meal_type_id = request.POST.get('meal_type')
            exchange_date_str = request.POST.get('exchange_date')
            receiver_email = request.POST.get('receiver_email')

            if not all([meal_type_id, exchange_date_str, receiver_email]):
                messages.error(request, "Please fill all fields.")
                return redirect('exchange_qr')

            try:
                meal_type = get_object_or_404(MealSlot, id=meal_type_id)
                exchange_date = datetime.strptime(exchange_date_str, '%Y-%m-%d').date()
            except (ValueError, MealSlot.DoesNotExist):
                messages.error(request, "Invalid meal type or date format.")
                return redirect('exchange_qr')

            if exchange_date < timezone.localdate():
                messages.error(request, "Cannot exchange meals for a past date.")
                return redirect('exchange_qr')

            giver_booking = BookingRecord.objects.filter(
                user=giver,
                meal_type=meal_type,
                date=exchange_date,
                status="Booked",
                is_special_order=False 
            ).first()

            if not giver_booking:
                messages.error(request, f"You do not have an active regular booking for {meal_type.name} on {exchange_date}.")
                return redirect('exchange_qr')
            
            meal_cutoff_end_time = SHOW_CUTOFF_TIMES.get(meal_type.name, [None, None])[1]
            now_time = timezone.localtime().time()
            
            if exchange_date == timezone.localdate() and meal_cutoff_end_time and now_time > meal_cutoff_end_time:
                messages.error(request, f"Cut-off passed for {meal_type.name} on {exchange_date} – cannot exchange.")
                return redirect('exchange_qr')

            if receiver_email == giver.email:
                messages.error(request, "You cannot exchange a meal with yourself.")
                return redirect('exchange_qr')

            try:
                receiver = StudentUser.objects.get(email=receiver_email)
            except StudentUser.DoesNotExist:
                messages.error(request, "Receiver email is not registered.")
                return redirect('exchange_qr')

            receiver_has_active_booking = BookingRecord.objects.filter(
                user=receiver,
                meal_type=meal_type,
                date=exchange_date
            ).exclude(status="Canceled").exists()

            if receiver_has_active_booking:
                messages.error(request, f"{receiver.name} already has an active booking for {meal_type.name} on {exchange_date}.")
                return redirect('exchange_qr')
            
            if receiver.refund_wallet < meal_type.price:
                messages.error(request, f"{receiver.name} has insufficient balance (₹{receiver.refund_wallet}) to receive this meal (cost ₹{meal_type.price}).")
                return redirect('exchange_qr')

            otp = str(random.randint(1000, 9999))
            request.session['exchange_otp_data'] = {
                'giver_booking_id': giver_booking.id,
                'receiver_email': receiver_email,
                'meal_type_id': meal_type_id,
                'exchange_date_str': exchange_date_str,
                'otp': otp,
                'timestamp': datetime.now().isoformat() 
            }

            try:
                send_mail(
                    subject = 'OTP for Meal Exchange Confirmation',
                    message = f"""
Hello {receiver.name},
A student ({giver.name}) wants to transfer a {meal_type.name} meal for {exchange_date} to you.
Your One-Time Password (OTP) to confirm this exchange is:
OTP: {otp}
Please share this OTP with {giver.name} to complete the exchange. This OTP is valid for 5 minutes.
If you did not expect this, please ignore this email.
Regards,  
MyMess Team   """
                    ,
                    from_email='noreplymymessbooking@gmail.com',
                    recipient_list=[receiver_email],
                    fail_silently=False,
                )
                messages.info(request, f"OTP sent to {receiver_email}. Please get the OTP from them to complete the exchange.")

                return render(request, 'accounts/exchange_qr.html', {
                    'meal_slots': meal_slots,
                    'otp_sent_to_receiver': True,
                    'exchange_data_for_otp': request.session['exchange_otp_data'],
                    'selected_meal_type_id': meal_type_id,
                    'selected_exchange_date': exchange_date_str,
                    'selected_receiver_email': receiver_email,
                })
            except Exception as e:
                messages.error(request, f"Failed to send OTP to receiver. Please try again. Error: {e}")
                if 'exchange_otp_data' in request.session:
                    del request.session['exchange_otp_data'] 
                return redirect('exchange_qr')

        elif 'verify_otp' in request.POST:
            otp_entered = ''.join([
                request.POST.get('otp1', ''),
                request.POST.get('otp2', ''),
                request.POST.get('otp3', ''),
                request.POST.get('otp4', ''),
            ])

            if not exchange_session_data:
                messages.error(request, "Exchange session expired or invalid. Please start again.")
                return redirect('exchange_qr')

            session_timestamp = datetime.fromisoformat(exchange_session_data['timestamp'])
            if (datetime.now() - session_timestamp) > timedelta(minutes=5):
                messages.error(request, "OTP expired. Please restart the exchange process.")
                del request.session['exchange_otp_data']
                return redirect('exchange_qr')

            if exchange_session_data['otp'] != otp_entered:
                messages.error(request, "Invalid OTP. Please try again.")
                return render(request, 'accounts/exchange_qr.html', {
                    'meal_slots': meal_slots,
                    'otp_sent_to_receiver': True,
                    'exchange_data_for_otp': exchange_session_data,
                    'selected_meal_type_id': exchange_session_data['meal_type_id'],
                    'selected_exchange_date': exchange_session_data['exchange_date_str'],
                    'selected_receiver_email': exchange_session_data['receiver_email'],
                })

            try:
                giver_booking = get_object_or_404(BookingRecord, id=exchange_session_data['giver_booking_id'])
                receiver = get_object_or_404(StudentUser, email=exchange_session_data['receiver_email'])
                meal_type = get_object_or_404(MealSlot, id=exchange_session_data['meal_type_id'])
                exchange_date = datetime.strptime(exchange_session_data['exchange_date_str'], '%Y-%m-%d').date()

                if not (giver_booking.user == giver and giver_booking.meal_type == meal_type and 
                        giver_booking.date == exchange_date and giver_booking.status == "Booked" and 
                        giver_booking.is_special_order == False):
                    messages.error(request, "Giver's original booking is no longer valid for exchange. Please check your orders.")
                    del request.session['exchange_otp_data']
                    return redirect('exchange_qr')

                if BookingRecord.objects.filter(user=receiver, meal_type=meal_type, date=exchange_date).exclude(status="Canceled").exists():
                    messages.error(request, f"{receiver.name} already has an active booking for {meal_type.name} on {exchange_date}. Exchange aborted.")
                    del request.session['exchange_otp_data']
                    return redirect('exchange_qr')

                if receiver.refund_wallet < meal_type.price:
                    messages.error(request, f"{receiver.name} has insufficient balance to complete the exchange.")
                    del request.session['exchange_otp_data']
                    return redirect('exchange_qr')

                giver_booking.status = "Transferred_Out"
                giver_booking.qr_token = None
                if giver_booking.qr_image:
                    giver_booking.qr_image.delete(save=False)
                giver_booking.qr_image = None
                giver_booking.save(update_fields=["status", "qr_token", "qr_image"])

                refund_amount = 10 if meal_type.name == "Breakfast" else 40
                giver.refund_wallet += refund_amount
                giver.save(update_fields=["refund_wallet"])
                messages.success(request, f"Your {meal_type.name} booking for {exchange_date} has been transferred. You received a refund of ₹{refund_amount}.")

                receiver_booking = BookingRecord.objects.create(
                    user=receiver,
                    meal_type=meal_type,
                    date=exchange_date,
                    status="Transferred_In", 
                    is_special_order=False 
                )

                receiver.refund_wallet -= meal_type.price
                receiver.save(update_fields=["refund_wallet"])
                messages.success(request, f"{receiver.name}'s wallet deducted ₹{meal_type.price} for the transferred {meal_type.name} meal.")

                del request.session['exchange_otp_data'] 
                messages.success(request, "Meal exchange completed successfully!")
                return redirect('orders') 
            except Exception as e:
                messages.error(request, f"An error occurred during exchange: {e}. Please try again.")
                if 'exchange_otp_data' in request.session:
                    del request.session['exchange_otp_data']
                return redirect('exchange_qr')

    return render(request, 'accounts/exchange_qr.html', {
        'meal_slots': meal_slots,
        'otp_sent_to_receiver': False,
        'exchange_data_for_otp': None, 
        'selected_meal_type_id': '',
        'selected_exchange_date': '',
        'selected_receiver_email': '',
    })

