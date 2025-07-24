# E-commerce API (Django + JWT + Redis + PostgreSQL)

This project is a simple e-commerce backend built using Django REST Framework. It supports user registration, JWT-based authentication, cart management, and order placement with Redis integration.

## 📦 Features

- JWT Authentication (Login/Register)
- Add/Remove Cart Items (Session-based & User-based)
- Place Order from Cart
- Admin Order Status Updates
- Product Filtering by Category, Price, and Stock
- Real-time WebSocket support using Django Channels

---

## 🔌 API Endpoints

### 🛒 Cart
| Method | URL | Description |
|--------|-----|-------------|
| `GET/POST` | `/cart/` | Get current user's cart items | Post cart items

### 📦 Order
| Method | URL | Description |
|--------|-----|-------------|
| `POST` | `/order/place_order/` | Place an order using current cart |
| `POST` | `/order/<int:id>/update_status/` | Admin: Update order status |

### 👤 Authentication & User
| Method | URL | Description |
|--------|-----|-------------|
| `POST` | `/api/token/` | Login using email/password – returns JWT |
| `POST` | `/api/token/refresh/` | Refresh JWT |
| `POST` | `/user/register/` | Register a new user |
| `GET/PUT` | `/user/profile/` | Get or update user profile |

### 🧾 Products & Filtering
### Method	URL	Description
GET	/products/	List all products
GET	/products/?category=<id>	Filter products by category ID
GET	/products/?min_price=<value>	Filter products with price greater than or equal to value
GET	/products/?max_price=<value>	Filter products with price less than or equal to value
GET	/products/?in_stock=true	Filter products in stock (stock > 0)
GET	/products/?in_stock=false	Filter products out of stock (stock ≤ 0)
GET	/products/<int:id>/	Retrieve a single product by ID
POST	/products/	Create a new product (requires authentication)
PUT	/products/<int:id>/	Update an existing product (requires authentication)
DELETE	/products/<int:id>/	Delete a product (requires authentication)

---

## 📤 Order API Details

### 1. Place Order

**POST** `/order/place_order/`

Places an order using items from the cart.

- Authenticated users: Uses `Cart.objects.filter(user=user)`
- Anonymous users: Uses `Cart.objects.filter(session_key=session_key)`

#### Response (Success)
```json
{
  "status": "Order placed"
}
```

#### Response (Failure)
```json
{
  "error": "Cart is empty"
}
```

### 2. Update Order Status

**POST** `/order/{id}/update_status/`

Updates the status of an order. Admin access required.

#### Body Params
```json
{
  "status": "shipped"  // Valid status from Order.STATUS_CHOICES
}
```

#### Response (Success)
```json
{
  "status": "Order status updated to shipped"
}
```

#### Response (Failure)
```json
{
  "error": "Order not found" // or "Invalid status"
}
```

---

## ⚙️ Setup Instructions

1. Clone the repository.
2. Create a virtual environment: `python -m venv venv && source venv/bin/activate`
3. Install dependencies: `pip install -r requirements.txt`
4. Run migrations: `python manage.py migrate`
5. Start server: `python manage.py runserver`

---

## 🧠 Notes

- Redis is used for caching session cart data.
- WebSocket support is optional but requires Django Channels + Redis.
- Cart management works for both authenticated and anonymous users using session keys.
- To enable anonymous session-based cart, use `request.session.save()`.

---
