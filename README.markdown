# FARFETCH E-Commerce Website

## Overview
This project is a Django-based e-commerce website inspired by FARFETCH, a luxury fashion platform. It allows users to browse products by category, brand, and other filters, add items to a cart or wishlist, and manage their profile. The site includes user authentication (login, register, logout), a tabbed auth interface, and a responsive navbar for navigation.

## Features
- **User Authentication**:
  - Tabbed login/signup page (`/auth/`) with email-based login (username field accepts email).
  - Logout functionality via POST request (`/logout/`).
  - Profile management (`/profile/`, `/profile/edit/`).
- **Product Browsing**:
  - Categories (Women, Men, Kids, Clothing, Shoes, Sneakers, Bags, Accessories, Watches).
  - Brands and product details pages.
  - Search functionality (`/search/`).
  - Sale and New In sections.
- **Cart and Wishlist**:
  - Add/remove items to/from cart (`/cart/`, `/cart/add/<slug>/`, `/cart/remove/<item_id>/`).
  - Add items to wishlist (`/wishlist/`, `/wishlist/add/<slug>/`).
  - Checkout and payment success/callback endpoints.
- **Responsive Design**:
  - Bootstrap 5.3 for styling.
  - Custom CSS for auth page (`auth.css`) and navbar (`navbar.css`).
  - Font Awesome icons for navbar actions.

## Prerequisites
- Python 3.12.8
- Django 5.2
- SQLite (default database, can be swapped for PostgreSQL or others)
- Virtual environment (recommended)

## Setup Instructions

### 1. Clone the Repository
```bash
git clone <repository-url>
cd farfetch_backend
```

### 2. Set Up a Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install django
# Add other dependencies if needed (e.g., django-bootstrap5 if used explicitly)
```

### 4. Apply Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Collect Static Files
```bash
python manage.py collectstatic
```

### 6. Create a Superuser (Admin)
```bash
python manage.py createsuperuser
```

### 7. Run the Development Server
```bash
python manage.py runserver
```
- Access the site at `http://127.0.0.1:9003/`.
- Access the admin panel at `http://127.0.0.1:9003/admin/`.

## Project Structure
```
farfetch_backend/
├── core/
│   ├── migrations/
│   ├── static/
│   │   ├── css/
│   │   │   ├── auth.css      # Styles for login/signup page
│   │   │   └── navbar.css    # Styles for navbar
│   │   └── js/
│   │       └── auth.js       # Tab switching for auth page
│   ├── templates/
│   │   ├── auth.html         # Login/Signup page
│   │   ├── navbar.html       # Navbar template
│   │   └── (other templates: home.html, profile.html, etc.)
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py             # Models: Customer, Product, etc.
│   ├── tests.py
│   ├── urls.py
│   └── views.py              # Views: CustomLoginView, register, etc.
├── farfetch_backend/
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py           # Django settings (static/media configs)
│   ├── urls.py               # Main URL routing
│   └── wsgi.py
├── media/                    # Uploaded files (e.g., product images)
├── static/                   # Source static files
├── staticfiles/              # Collected static files (after collectstatic)
├── manage.py
└── README.md
```

## Key URLs
- Homepage: `/`
- Login/Signup: `/auth/`
- Register: `/auth/register/`
- Logout: `/logout/` (POST request)
- Profile: `/profile/`
- Cart: `/cart/`
- Wishlist: `/wishlist/`
- Product Detail: `/product/<slug>/`
- Category Detail: `/category/<slug>/`
- Brand Detail: `/brand/<slug>/`
- Search: `/search/`
- Sale: `/sale/`
- New In: `/new-in/`
- Brands: `/brands/`

## Configuration Notes
- **Static Files**:
  - Ensure `STATIC_URL = '/static/'`, `STATICFILES_DIRS = [BASE_DIR / "static"]`, and `STATIC_ROOT = BASE_DIR / "staticfiles"` are set in `settings.py`.
  - Run `python manage.py collectstatic` after changes to static files.
- **Media Files**:
  - Product images are served from `/media/` (`MEDIA_URL = '/media/'`, `MEDIA_ROOT = BASE_DIR / "media"`).
- **Authentication**:
  - `LOGIN_URL = '/auth/'`
  - `LOGIN_REDIRECT_URL = '/profile/'`
  - `LOGOUT_REDIRECT_URL = '/'`

## Known Issues
- **Email-Based Login**: The login form labels say "Email address," but the backend expects a username. To enable email login, modify `CustomLoginView` (see below).
- **Navbar Styling**: If logout button styling doesn’t match other links, adjust CSS in `navbar.css`.

## Optional: Enable Email-Based Login
1. Update `core/views.py`:
```python
from django.contrib.auth import authenticate

class CustomLoginView(LoginView):
    template_name = 'auth.html'
    redirect_authenticated_user = True

    def get_credentials(self):
        username = self.request.POST.get('username')
        password = self.request.POST.get('password')
        user = User.objects.filter(email__iexact=username).first()
        return {'username': user.username if user else username, 'password': password}

    def form_valid(self, form):
        credentials = self.get_credentials()
        user = authenticate(**credentials)
        if user:
            form.cleaned_data['username'] = credentials['username']
            return super().form_valid(form)
        form.add_error(None, "Invalid email or password.")
        return self.form_invalid(form)
```
2. Update `auth.html`:
- Change `<input id="username" name="username" ...>` to `<input id="email" name="username" ...>` in the login form.

## Contributing
- Fork the repository.
- Create a new branch for your feature/bugfix.
- Submit a pull request with a detailed description of changes.

## License
This project is for educational purposes and not licensed for commercial use.