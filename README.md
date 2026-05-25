# 🏨 SmartStay — Hotel Booking Platform

> A full-featured hotel booking web application built with **Django 5.2** and **PostgreSQL**, supporting dual-role authentication (Guest & Vendor), email verification, OTP login, hotel management, and booking management.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Database Schema](#database-schema)
- [System Architecture](#system-architecture)
- [URL Routes](#url-routes)
- [User Flow Diagrams](#user-flow-diagrams)
- [Prerequisites](#prerequisites)
- [Installation & Setup](#installation--setup)
- [Running the Project](#running-the-project)
- [Email Configuration](#email-configuration)
- [Admin Panel](#admin-panel)
- [Environment Variables](#environment-variables)
- [Contributing](#contributing)

---

## Overview

**SmartStay** is a hotel booking platform where:

- **Guests** can browse hotels, search by name, view hotel details, and book rooms by selecting check-in/check-out dates.
- **Vendors** (hotel owners) can register their business, add hotels with descriptions, amenities, pricing, images, and manage their listings via a dedicated dashboard.

---

## Features

### 👤 Guest (User) Features
- User registration with email verification
- Login with email + password
- OTP-based login via email
- Hotel search (by name)
- View hotel details (images, amenities, pricing)
- Book a hotel room with date selection
- Price auto-calculated based on number of days

### 🏢 Vendor Features
- Vendor registration with business name and email verification
- Vendor login with dedicated portal
- Vendor dashboard showing all owned hotels
- Add new hotels (name, description, location, price, offer price, amenities)
- Upload/delete hotel images
- Edit hotel details
- Logout

### 🛠️ Admin Features
- Django Admin Panel for managing all models
- Full CRUD on Users, Vendors, Hotels, Amenities, Bookings

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend Framework | Django 5.2 |
| Database | PostgreSQL |
| Authentication | Django Auth + Custom User Models |
| Email | SMTP via Gmail |
| OTP | Random 4-digit OTP via Email |
| Token | UUID-based email verification tokens |
| Slug | Auto-generated unique slugs per hotel |
| Frontend | Django Templates (HTML/CSS) |
| Static Files | Django staticfiles |
| Media Files | Django media handling |

---

## Project Structure

```
smart_stay/
│
├── smart_stay/                  # Project configuration
│   ├── settings.py              # App settings (DB, Email, Static, Media)
│   ├── urls.py                  # Root URL configuration
│   ├── asgi.py
│   └── wsgi.py
│
├── accounts/                    # Core app: users, vendors, hotels, bookings
│   ├── models.py                # HotelUser, HotelVendor, Hotel, Amenities, HotelBooking, HotelImages, HotelManager
│   ├── views.py                 # All views (login, register, dashboard, hotel CRUD)
│   ├── urls.py                  # accounts/ URL patterns
│   ├── admin.py                 # Admin registrations
│   ├── utils.py                 # Token generator, Email sender, OTP sender, Slug generator
│   └── templates/
│       ├── login.html
│       ├── register.html
│       ├── verify_otp.html
│       ├── hotel_detail.html    # (shared with home app)
│       └── vendor/
│           ├── login_vendor.html
│           ├── register_vendor.html
│           ├── vendor_dashboard.html
│           ├── add_hotel.html
│           ├── edit_hotel.html
│           └── upload_images.html
│
├── home/                        # Public-facing app
│   ├── views.py                 # index (hotel listing + search), hotel_details + booking
│   ├── urls.py                  # home/ URL patterns
│   └── templates/
│       ├── index.html           # Hotel listing page
│       └── hotel_detail.html    # Hotel detail + booking page
│
├── public/
│   └── static/                  # Static assets (CSS, JS, Images)
│
├── profile/
│   └── logo.png
│
└── manage.py
```

---

## Database Schema

```
┌──────────────────────────────────┐
│          auth_user (Django)       │
│  id, username, email, password,  │
│  first_name, last_name, ...      │
└──────────────┬───────────────────┘
               │ (inherits via proxy/multi-table)
      ┌────────┴──────────┐
      │                   │
┌─────▼──────────┐  ┌─────▼────────────┐
│   hotel_user   │  │  hotel_vendor    │
│  phone_number  │  │  phone_number    │
│  profile_pic   │  │  business_name   │
│  email_token   │  │  profile_pic     │
│  otp           │  │  email_token     │
│  is_verified   │  │  otp             │
└────────────────┘  │  is_verified     │
                    └──────┬───────────┘
                           │ (FK: hotel_owner)
                    ┌──────▼───────────┐
                    │      Hotel        │
                    │  hotel_name      │
                    │  hotel_description│
                    │  hotel_slug      │
                    │  hotel_price     │
                    │  hotel_offer_price│
                    │  hotel_location  │
                    │  is_active       │
                    └──┬──────────┬────┘
                       │          │
          ┌────────────▼─┐   ┌────▼──────────────┐
          │  HotelImages  │   │    Amenities       │
          │  hotel (FK)   │   │  name, icon        │
          │  image        │   └────────────────────┘
          └───────────────┘         (M2M with Hotel)

          ┌────────────────────────────┐
          │       HotelBooking          │
          │  hotel (FK)                │
          │  booking_user (FK)         │
          │  booking_start_date        │
          │  booking_end_date          │
          │  price                     │
          └────────────────────────────┘

          ┌────────────────────────────┐
          │       HotelManager          │
          │  hotel (FK)                │
          │  manager_name              │
          │  manager_contact           │
          └────────────────────────────┘
```

---

## System Architecture

```
                     ┌─────────────────────────────┐
                     │         Browser / Client      │
                     └──────────────┬───────────────┘
                                    │ HTTP Request
                     ┌──────────────▼───────────────┐
                     │       Django WSGI Server       │
                     │  (manage.py runserver /        │
                     │   gunicorn in production)      │
                     └──────────────┬───────────────┘
                                    │
               ┌────────────────────▼──────────────────┐
               │              URL Router                │
               │  smart_stay/urls.py                    │
               │  ├── ''       → home.urls              │
               │  ├── account/ → accounts.urls          │
               │  └── admin/   → Django Admin           │
               └────────┬────────────────┬─────────────┘
                        │                │
          ┌─────────────▼──┐    ┌────────▼──────────────┐
          │   home/views.py │    │  accounts/views.py    │
          │  - index        │    │  - login/register     │
          │  - hotel_details│    │  - OTP verify         │
          └────────┬────────┘    │  - vendor portal      │
                   │             │  - hotel CRUD         │
                   │             └──────────┬────────────┘
                   │                        │
          ┌────────▼────────────────────────▼────────────┐
          │              Django ORM / Models               │
          │  HotelUser, HotelVendor, Hotel, Amenities,    │
          │  HotelImages, HotelBooking, HotelManager      │
          └────────────────────┬──────────────────────────┘
                               │
          ┌────────────────────▼──────────────────────────┐
          │              PostgreSQL Database               │
          └───────────────────────────────────────────────┘
                               │
          ┌────────────────────▼──────────────────────────┐
          │              Gmail SMTP Server                 │
          │  (Email Verification Tokens + OTP)            │
          └───────────────────────────────────────────────┘
```

---

## URL Routes

### Home App (`/`)

| Method | URL | View | Description |
|---|---|---|---|
| GET | `/` | `index` | Hotel listing page with optional `?search=` query |
| GET/POST | `/hotel-details/<slug>/` | `hotel_details` | Hotel detail page; POST submits booking |

### Accounts App (`/account/`)

| Method | URL | View | Description |
|---|---|---|---|
| GET/POST | `/account/login/` | `login_page` | Guest login |
| GET/POST | `/account/register/` | `register` | Guest registration |
| GET | `/account/verify-account/<token>/` | `verify_email_token` | Email verification |
| GET | `/account/send_otp/<email>/` | `send_otp` | Sends OTP to email |
| GET/POST | `/account/verify-otp/<email>/` | `verify_otp` | OTP verification & login |
| GET/POST | `/account/login-vendor/` | `login_vendor` | Vendor login |
| GET/POST | `/account/register-vendor/` | `register_vendor` | Vendor registration |
| GET | `/account/dashboard/` | `dashboard` | Vendor dashboard (auth required) |
| GET/POST | `/account/add-hotel/` | `add_hotel` | Add a new hotel (auth required) |
| GET/POST | `/account/<slug>/upload-images/` | `upload_images` | Upload hotel images (auth required) |
| GET | `/account/delete_image/<id>/` | `delete_image` | Delete hotel image (auth required) |
| GET/POST | `/account/edit_hotel/<slug>/` | `edit_hotel` | Edit hotel details (auth required) |
| GET | `/account/logout_view/` | `logout_view` | Logout |

### Admin (`/admin/`)

| URL | Description |
|---|---|
| `/admin/` | Django Admin — manage all models |

---

## User Flow Diagrams

### Guest Registration & Booking Flow

```
Guest visits /
     │
     ▼
Browse Hotels (index page)
     │
     ▼
Click Hotel → /hotel-details/<slug>/
     │
     ▼
Fill booking dates (POST)
     │
     ├── Not logged in? → Redirect to /account/login/
     │
     └── Logged in?
          │
          ▼
     Booking saved to HotelBooking
     (price = offer_price × days)
          │
          ▼
     Success message shown


Guest Registration:
     │
     ▼
/account/register/ (POST)
     │
     ▼
HotelUser created (is_verified=False)
     │
     ▼
Email sent with verification link
     │
     ▼
Guest clicks link → /account/verify-account/<token>/
     │
     ▼
is_verified = True → Redirect to Login
```

### OTP Login Flow

```
Guest at /account/login/
     │
     ▼
Click "Login with OTP"
     │
     ▼
/account/send_otp/<email>/
     │
     ▼
Random 4-digit OTP generated & emailed
     │
     ▼
/account/verify-otp/<email>/  (POST)
     │
     ├── OTP matches? → Login → Redirect to home
     └── Invalid OTP? → Error message
```

### Vendor Hotel Management Flow

```
Vendor registers → /account/register-vendor/
     │
     ▼
Email verification (same token flow)
     │
     ▼
Login → /account/login-vendor/
     │
     ▼
Dashboard → /account/dashboard/
  (shows all hotels owned by vendor)
     │
     ├── Add Hotel → /account/add-hotel/
     │       │
     │       ▼
     │   Select amenities, fill details
     │   Unique slug auto-generated
     │
     ├── Upload Images → /account/<slug>/upload-images/
     │
     ├── Edit Hotel → /account/edit_hotel/<slug>/
     │
     └── Delete Image → /account/delete_image/<id>/
```

---

## Prerequisites

Make sure you have the following installed:

- Python 3.10+
- PostgreSQL 13+
- pip
- virtualenv (recommended)
- Git

---

## Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/bpraveen5/smart_stay.git
cd smart_stay
```

### 2. Create and Activate a Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate (Linux/macOS)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install django psycopg2-binary pillow
```

> There is no `requirements.txt` yet. You can generate one after installing:
> ```bash
> pip freeze > requirements.txt
> ```

### 4. Create the PostgreSQL Database

```bash
# Login to PostgreSQL
psql -U postgres

# Inside psql shell:
CREATE DATABASE smart_stay;
\q
```

### 5. Configure Database Settings

Open `smart_stay/settings.py` and update the database section if needed:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'smart_stay',
        'USER': 'postgres',
        'PASSWORD': 'postgres',   # Change to your PostgreSQL password
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### 6. Configure Email Settings

In `smart_stay/settings.py`, update your Gmail SMTP credentials:

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your_email@gmail.com'
EMAIL_HOST_PASSWORD = 'your_gmail_app_password'
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
```

> ⚠️ **Important:** Use a [Gmail App Password](https://support.google.com/accounts/answer/185833), not your regular Gmail password. Enable 2-Factor Authentication on your Google account first, then generate an App Password under Security settings.

### 7. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 8. Create a Superuser (Admin)

```bash
python manage.py createsuperuser
```

Follow the prompts to set username, email, and password.

### 9. Collect Static Files (optional for development)

```bash
python manage.py collectstatic
```

---

## Running the Project

```bash
python manage.py runserver
```

The app will be available at: **http://127.0.0.1:8000/**

| URL | Description |
|---|---|
| http://127.0.0.1:8000/ | Home — Hotel listing |
| http://127.0.0.1:8000/account/login/ | Guest login |
| http://127.0.0.1:8000/account/register/ | Guest registration |
| http://127.0.0.1:8000/account/login-vendor/ | Vendor login |
| http://127.0.0.1:8000/account/register-vendor/ | Vendor registration |
| http://127.0.0.1:8000/account/dashboard/ | Vendor dashboard |
| http://127.0.0.1:8000/admin/ | Django admin panel |

---

## Email Configuration

SmartStay uses Gmail SMTP for two email flows:

### 1. Email Verification (Registration)
When a guest or vendor registers, a unique UUID token is emailed:
```
http://127.0.0.1:8000/account/verify-account/<uuid-token>/
```
Clicking this link sets `is_verified = True` and allows login.

### 2. OTP Login
A 4-digit OTP is sent to the user's email for passwordless login:
```
Subject: otp for account login
Body: Hi, Use this OTP to login: 4829. Please do not share this OTP with anyone.
```

### Setting up Gmail App Password

1. Go to your [Google Account](https://myaccount.google.com/)
2. Navigate to **Security → 2-Step Verification** → Enable it
3. Go to **Security → App passwords**
4. Select app: **Mail**, device: **Other** → Generate
5. Copy the 16-character password into `EMAIL_HOST_PASSWORD` in `settings.py`

---

## Admin Panel

Access the Django Admin at `/admin/` with your superuser credentials.

The following models are registered and manageable via Admin:

| Model | Description |
|---|---|
| `HotelUser` | Guest accounts |
| `HotelVendor` | Vendor/hotel owner accounts |
| `Amenities` | Amenity entries (name + icon) |
| `Hotel` | Hotel listings |
| `HotelBooking` | All bookings made by guests |

---

## Environment Variables

For production, move sensitive values to environment variables. Replace the following in `settings.py`:

| Variable | Current (dev) | Recommended for Production |
|---|---|---|
| `SECRET_KEY` | Hardcoded string | `os.environ['SECRET_KEY']` |
| `DEBUG` | `True` | `False` |
| `ALLOWED_HOSTS` | `['127.0.0.1', 'localhost']` | Your domain name |
| `DB_PASSWORD` | `'postgres'` | `os.environ['DB_PASSWORD']` |
| `EMAIL_HOST_USER` | Gmail address | `os.environ['EMAIL_HOST_USER']` |
| `EMAIL_HOST_PASSWORD` | App password | `os.environ['EMAIL_HOST_PASSWORD']` |

Example using `python-decouple`:

```bash
pip install python-decouple
```

Create a `.env` file:
```
SECRET_KEY=your-secret-key
DEBUG=False
DB_NAME=smart_stay
DB_USER=postgres
DB_PASSWORD=yourpassword
DB_HOST=localhost
DB_PORT=5432
EMAIL_HOST_USER=you@gmail.com
EMAIL_HOST_PASSWORD=your_app_password
```

Then in `settings.py`:
```python
from decouple import config

SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', cast=bool)
```

---

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Make your changes and commit: `git commit -m "Add: your feature description"`
4. Push to your fork: `git push origin feature/your-feature-name`
5. Open a Pull Request on GitHub

---

## License

This project is open-source. Feel free to use and modify it for learning or personal projects.

---

> Built with ❤️ using Django — SmartStay makes hotel management and booking simple.
