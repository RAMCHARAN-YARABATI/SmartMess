# SmartMess

📌 **Project Overview**  
MyMess is a Django-based web application designed to manage **student meal bookings in a hostel mess**.  
It provides a complete solution for:  

- Student sign-up & login with OTP verification  
- Daily meal booking (Breakfast, Lunch, Dinner)  
- Special meal booking with limited slots  
- QR code generation for meal verification  
- Meal exchange between students (with OTP authentication)  
- Refund & wallet system for cancellations and transfers  

The project ensures **fair, transparent, and efficient mess management** by integrating booking windows, cut-off times, and real-time updates.  

---

## ⚙️ Features  

✅ **Student Management**  
- Secure sign-up and login (OTP-based authentication)  
- Session-based login system (no need for repeated credentials)  

✅ **Meal Booking**  
- Book meals for today and tomorrow within cut-off times  
- Automatic wallet deduction per meal  
- Cancel meals before cut-off and receive a refund  

✅ **Special Orders**  
- Limited slots (default 25 per meal type)  
- Separate booking windows  
- Prevents duplicate bookings (cannot book both regular & special for same meal)  

✅ **QR Code System**  
- Unique QR code generated for every booked meal  
- Can be scanned at the counter for validation  

✅ **Meal Exchange System**  
- Students can transfer booked meals to others  
- OTP verification for secure exchange  
- Automatic wallet adjustments (refund to giver, deduction from receiver)  

✅ **Wallet Management**  
- Wallet balance updated for every booking, cancellation, or transfer  
- Partial refund logic for transferred meals (e.g., ₹10 for breakfast, ₹40 for lunch/dinner)  

---

## 🛠️ Tech Stack  

- **Backend:** Django (Python)  
- **Database:** SQLite (default, can be changed to PostgreSQL/MySQL)  
- **Frontend:** Django Templates (HTML, CSS)  
- **Authentication:** OTP via Email (Django `send_mail`)  
- **Utilities:**  
  - `qrcode` – for QR code generation  
  - `uuid` – for unique QR identifiers  
  - `datetime` & Django `timezone` – for booking cut-offs  
