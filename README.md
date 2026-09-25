# Kamau Nails — Full Website (Django + HTML + CSS)

A complete, working nail-salon website: homepage, about, services & pricing,
online booking, team profiles, filterable gallery with lightbox, M-Pesa
payment-proof upload, contact form, newsletter signup, FAQ accordion,
policy pages, and a full **admin dashboard** to manage everything.

Stack: **Python (Django)** for the backend/database, **HTML** templates,
and hand-written **CSS** (no framework) for the luxury pink/gold/black/sky-blue
design. This zip already contains every file — the walkthrough below explains
**how it was built**, in order, so you can rebuild, extend, or understand it
in VS Code.

---

## 0. What's already inside this zip

```
kamau_nails/
├── manage.py
├── requirements.txt
├── db.sqlite3                 # pre-seeded database (sample services, team, gallery, admin login)
├── kamau_nails/                # project settings
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py / asgi.py
├── salon/                      # the app — all business logic
│   ├── models.py               # database tables
│   ├── admin.py                 # admin dashboard config
│   ├── forms.py                  # booking / payment / contact forms
│   ├── views.py                   # page logic
│   ├── urls.py                     # page routes
│   ├── templatetags/salon_extras.py
│   └── management/commands/seed_data.py   # sample content loader
├── templates/                   # all HTML
│   ├── base.html
│   ├── includes/ (navbar.html, footer.html)
│   └── salon/ (home, about, services, service_detail, team, gallery,
│               booking, booking_success, payment, contact, faq, policy)
└── static/
    ├── css/style.css            # the entire design system
    └── js/main.js                # mobile menu, lightbox, FAQ accordion
```

Because `db.sqlite3` is already included and seeded, **you can run the site
immediately** (Step 4) without re-doing the setup steps — or follow every
step below to see exactly how it was built from scratch.

**Admin login (already created):**
- URL: `http://127.0.0.1:8000/admin/`
- Username: `admin`
- Password: `KamauNails2026!`

Change this password immediately after your first login (Step 7).

---

## 1. Install prerequisites

You need **Python 3.10+** installed and on your PATH.

Open **cmd** (Command Prompt) and check:

```cmd
python --version
```

If that fails, install Python from python.org and re-open cmd (tick "Add
Python to PATH" during install).

---

## 2. Unzip and open in VS Code

```cmd
cd Desktop
:: unzip kamau_nails.zip here, then:
cd kamau_nails
code .
```

`code .` opens the whole folder in Visual Studio Code (requires the `code`
command — in VS Code, run "Shell Command: Install 'code' command in PATH"
from the Command Palette if it's not recognized).

---

## 3. Create a virtual environment and install dependencies

Still in **cmd**, inside the `kamau_nails` folder:

```cmd
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

You'll see `(venv)` appear at the start of your prompt once it's active.
`requirements.txt` contains:

```
Django>=5.0,<6.0
Pillow>=10.0
```

(Pillow is required because `PaymentProof.screenshot` is an `ImageField`.)

---

## 4. Run the project immediately

```cmd
python manage.py runserver
```

Open **http://127.0.0.1:8000/** in your browser. You should see the full
site with sample services, team members, gallery photos and testimonials
already loaded (from the included `db.sqlite3`).

Press `CTRL+C` in cmd to stop the server.

---

## 5. Rebuilding from scratch (how every file was created)

Skip this section if Step 4 already worked and you just want to edit
content. Keep it if you want to understand — or recreate — the project
structure yourself.

### 5.1 Start the Django project and app

```cmd
django-admin startproject kamau_nails
cd kamau_nails
python manage.py startapp salon
```

This generates `manage.py`, the `kamau_nails/` settings package, and the
`salon/` app skeleton (`models.py`, `views.py`, `admin.py`, empty `urls.py`
which you add yourself).

### 5.2 `kamau_nails/settings.py` — wire everything together

Key edits made to the default file:

```python
INSTALLED_APPS = [
    ...
    'django.contrib.staticfiles',
    'salon',                       # register the app
]

TEMPLATES = [{
    ...
    'DIRS': [BASE_DIR / 'templates'],   # project-level templates folder
    ...
}]

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'          # uploaded payment screenshots go here

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'  # prints emails to cmd for now
DEFAULT_FROM_EMAIL = 'Kamau Nails <no-reply@kamaunails.com>'
SALON_ADMIN_EMAIL = 'jacktonecharles@gmail.com'
SALON_PHONE = '0740729339'
```

> See **Step 8** for how to switch `EMAIL_BACKEND` to a real Gmail/SMTP
> account so booking confirmations actually get emailed.

### 5.3 `salon/models.py` — the database

Defines every table the site needs: `ServiceCategory`, `Service`,
`Technician`, `GalleryImage`, `Testimonial`, `Booking`, `PaymentProof`,
`ContactMessage`, `NewsletterSubscriber`. Each field maps directly to a
form field or a piece of content shown in the templates (price, duration,
image URL, specialties, rating, etc).

### 5.4 `salon/admin.py` — the admin dashboard

Registers every model with `@admin.register(...)` and customizes the
list views (e.g. `Booking` has `list_editable = ('status',)` so the salon
owner can confirm/cancel appointments straight from the list page, and
`PaymentProof` has `list_editable = ('is_verified',)` for the payment
verification workflow).

### 5.5 `salon/forms.py` — user-facing forms

`BookingForm`, `PaymentProofForm`, `ContactForm`, `NewsletterForm` — all
`ModelForm`s, so validation and saving to the database come for free from
Django.

### 5.6 `salon/views.py` — page logic

One view per page (`home`, `about`, `services`, `service_detail`, `team`,
`gallery`, `booking`, `payment`, `contact`, `faq`, `policy`, etc.). The
`booking` view saves the form and calls `send_mail(...)` to email a
confirmation to the customer and the salon's admin address. The `gallery`
view filters images by `?category=` query string for the filter bar.

### 5.7 `salon/urls.py` + `kamau_nails/urls.py` — routing

App-level `urls.py` maps each URL path to its view function; the
project-level `urls.py` includes it and adds `/admin/` plus static/media
serving during development.

### 5.8 Templates (`templates/`)

`base.html` holds the `<head>`, navbar include, footer include, and a
`{% block content %}`. Every page template `{% extends 'base.html' %}` and
fills that block — this is why the header/footer/nav look identical on
every page while each page's body differs.

### 5.9 `static/css/style.css`

One hand-written stylesheet using CSS variables for the palette:

```css
:root {
  --blush: #F7E2E8;
  --gold: #C7A052;
  --sky: #AEE0EF;
  --ink: #1B1620;
  --rose: #C9748C;
}
```

Includes the responsive grid system, the "gold drip" SVG divider between
homepage sections, card hover animations, the mobile nav, the FAQ
accordion styles, and a `[data-theme="dark"]` variable set for dark mode.

### 5.10 `static/js/main.js`

Vanilla JS (no framework) for: mobile menu toggle, FAQ accordion
open/close, gallery lightbox, dark/light mode toggle, and basic client-side
form-validation focus handling.

### 5.11 Create the database tables

```cmd
python manage.py makemigrations salon
python manage.py migrate
```

### 5.12 Load sample content

A custom management command seeds realistic sample data so the site isn't
empty:

```cmd
python manage.py seed_data
```

This populates service categories/services (with photo URLs), 4
technicians, 8 gallery photos, and 3 testimonials — matching everything
listed in the original project brief.

### 5.13 Create your admin login

```cmd
python manage.py createsuperuser
```

Follow the prompts for username/email/password.

---

## 6. About the pictures

Every image on the site is loaded from a URL (`image_url` / `photo_url`
fields), not a local file — that's what makes the pre-seeded content work
immediately with **zero setup**. They currently point to royalty-free
Unsplash photos so you can see the full design instantly.

**To use your own salon's real photos:**

1. Log into `/admin/`.
2. Open **Services**, **Technicians**, or **Gallery images**.
3. Replace the `image_url` / `photo_url` field with a link to your own
   photo (e.g. uploaded to Imgur, Cloudinary, or your own hosting).

If you'd rather upload photos directly from your computer instead of
pasting URLs, tell me and I'll convert those fields to real `ImageField`
uploads (the `PaymentProof.screenshot` field already works this way as an
example — it's a genuine file upload, not a URL).

---

## 7. Using the Admin Dashboard

Go to `http://127.0.0.1:8000/admin/` and log in. From there the salon
owner can:

- **Bookings** — view every appointment, edit status (pending → confirmed
  → completed/cancelled) directly in the list.
- **Payment proofs** — see every submitted M-Pesa screenshot, transaction
  code and amount, and tick "is verified" once confirmed.
- **Services / Service categories** — add, edit or remove services and
  prices; toggle "is featured" to control the homepage.
- **Technicians** — add staff, their specialties and photo link.
- **Gallery images** — add new portfolio photos with a category, so they
  automatically appear in the filterable gallery.
- **Testimonials** — publish/unpublish reviews shown on the homepage.
- **Contact messages / Newsletter subscribers** — read enquiries and
  export subscriber emails for a mailing list tool.

To change the seeded admin password:

```cmd
python manage.py changepassword admin
```

---

## 8. Making booking emails actually send

Right now `EMAIL_BACKEND` prints emails to the cmd console instead of
sending them (so you can test without an email account). To send real
emails via Gmail:

```python
# kamau_nails/settings.py
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'jacktonecharles@gmail.com'
EMAIL_HOST_PASSWORD = 'your-16-character-gmail-app-password'
```

Gmail requires an **App Password** (not your normal password) — generate
one from your Google Account → Security → 2-Step Verification → App
Passwords. Never commit real passwords to source control; use environment
variables in production (see Step 10).

---

## 9. Extending the project

The brief also mentioned a shop, loyalty points, and a blog. The
architecture supports adding these the same way every other feature was
built:

- **Shop**: add `Product`, `Order`, `OrderItem` models, a `cart` session
  helper, and `shop/` templates — same pattern as `Booking`.
- **Loyalty & memberships**: add a `LoyaltyAccount` model linked to a
  customer, and award points inside the `booking` view when a `Booking`
  is marked `completed`.
- **Blog**: add a `Post` model (title, slug, body, category, published_at)
  and `blog_list` / `blog_detail` views — mirrors `services` /
  `service_detail` almost exactly.

Ask me to build any of these next and I'll add them the same way.

---

## 10. Deployment (making it live on the internet)

1. Set `DEBUG = False` in `settings.py` and add your real domain to
   `ALLOWED_HOSTS`.
2. Move secrets (`SECRET_KEY`, email password) into environment variables
   instead of hard-coding them.
3. Switch the database from SQLite to PostgreSQL for production traffic.
4. Run `python manage.py collectstatic` to gather static files for
   serving.
5. Deploy to a host such as Railway, Render, or PythonAnywhere — all have
   free/low-cost tiers that support Django out of the box.
6. Point your domain's DNS at the host, and enable HTTPS (most of these
   hosts issue a free TLS certificate automatically).

---

## Quick command reference

```cmd
venv\Scripts\activate              :: activate the virtual environment
python manage.py runserver         :: start the site at 127.0.0.1:8000
python manage.py makemigrations    :: after changing models.py
python manage.py migrate           :: apply database changes
python manage.py seed_data         :: reload sample content
python manage.py createsuperuser   :: create an admin login
python manage.py changepassword admin   :: reset the admin password
```
"# kamau" 
"# kamau" 
"# kamau-nails" 
"# kamau-nails" 
"# kamaunails" 
"# kamau" 
"# kamau" 
"# kamau-" 
