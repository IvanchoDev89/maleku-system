# API Documentation - Costa Rica Travel

Complete REST API reference for the Costa Rica Travel platform.

**Base URL:** `https://api.costaricatravel.dev/api/v1`

---

## 🔐 Authentication

All authenticated endpoints require a Bearer token in the Authorization header:

```http
Authorization: Bearer <access_token>
```

### Token Lifecycle
- **Access Token**: Valid for 15 minutes
- **Refresh Token**: Valid for 7 days (store in httpOnly cookie)

### POST /auth/register
Register a new user account.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+50612345678"
}
```

**Response (201):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 900,
  "user": {
    "id": 1,
    "email": "user@example.com",
    "role": "client",
    "is_verified": false
  }
}
```

### POST /auth/login
Authenticate user and receive tokens.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 900
}
```

**Errors:**
- `401`: Invalid credentials
- `423`: Account locked (too many failed attempts)

### POST /auth/refresh
Get new access token using refresh token.

**Request:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIs..."
}
```

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 900
}
```

### POST /auth/logout
Invalidate tokens (add to blacklist).

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "message": "Successfully logged out"
}
```

### POST /auth/forgot-password
Request password reset email.

**Request:**
```json
{
  "email": "user@example.com"
}
```

**Response (200):**
```json
{
  "message": "Password reset instructions sent to email"
}
```

### POST /auth/reset-password
Complete password reset with token.

**Request:**
```json
{
  "token": "reset_token_from_email",
  "new_password": "NewSecurePass123!"
}
```

**Response (200):**
```json
{
  "message": "Password reset successfully"
}
```

### POST /auth/verify-email
Verify email address with token.

**Request:**
```json
{
  "token": "verification_token_from_email"
}
```

### GET /auth/me
Get current user profile.

**Response (200):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "role": "client",
  "is_verified": true,
  "created_at": "2024-01-15T10:30:00Z"
}
```

---

## 👤 Users

### GET /users/me
Get own profile (authenticated).

**Response (200):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+50612345678",
  "avatar_url": "https://...",
  "role": "client",
  "is_verified": true,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-20T14:20:00Z"
}
```

### PUT /users/me
Update own profile.

**Request:**
```json
{
  "first_name": "Jane",
  "phone": "+50687654321"
}
```

**Response (200):** Updated user object

### DELETE /users/me
Delete own account (soft delete).

**Response (200):**
```json
{
  "message": "Account scheduled for deletion (30 days to restore)"
}
```

---

## 🏢 Admin Users Endpoints

### GET /users/
List all users (Admin only).

**Query Parameters:**
- `skip`: int (default 0)
- `limit`: int (default 20, max 100)
- `role`: enum (client, vendor, admin)
- `is_active`: bool
- `search`: string

**Response (200):**
```json
{
  "items": [
    {
      "id": 1,
      "email": "user@example.com",
      "role": "client",
      "is_active": true,
      "created_at": "2024-01-15T10:30:00Z"
    }
  ],
  "total": 150,
  "page": 1,
  "pages": 8
}
```

### GET /users/{id}
Get specific user (Admin only).

**Response (200):** User object with full details

### PUT /users/{id}
Update any user (Admin only).

**Request:**
```json
{
  "role": "vendor",
  "is_active": false
}
```

### DELETE /users/{id}
Delete user (Admin only - soft delete).

### POST /users/{id}/restore
Restore deleted user (Admin only).

---

## 🏪 Vendors

### GET /vendors/
List all vendors (public).

**Query Parameters:**
- `skip`: int
- `limit`: int
- `is_verified`: bool
- `city`: string
- `search`: string

**Response (200):**
```json
{
  "items": [
    {
      "id": 1,
      "company_name": "Tropical Hotels",
      "slug": "tropical-hotels",
      "logo_url": "https://...",
      "is_verified": true,
      "rating_average": 4.5,
      "review_count": 128
    }
  ],
  "total": 45
}
```

### POST /vendors/
Create vendor (Admin only).

**Request:**
```json
{
  "user_id": 5,
  "company_name": "Costa Rica Adventures",
  "description": "Best tours in Costa Rica",
  "commission_rate": 0.12
}
```

### GET /vendors/dashboard
Get own vendor dashboard (Vendor only).

**Response (200):**
```json
{
  "vendor": {
    "id": 1,
    "company_name": "Tropical Hotels",
    "is_verified": true
  },
  "stats": {
    "properties_count": 12,
    "tours_count": 5,
    "total_bookings": 345,
    "revenue_this_month": 12500.00,
    "pending_bookings": 8
  },
  "recent_bookings": [...]
}
```

### PUT /vendors/dashboard
Update own vendor profile.

### GET /vendors/{id}
Get specific vendor (public).

### PUT /vendors/{id}
Update vendor (Admin only).

### POST /vendors/{id}/verify
Verify vendor (Admin only).

---

## 🏨 Properties

### GET /properties/
List properties with filters.

**Query Parameters:**
- `location`: string (city/region)
- `min_price`: number
- `max_price`: number
- `guests`: int
- `amenities`: array
- `check_in`: date (YYYY-MM-DD)
- `check_out`: date (YYYY-MM-DD)
- `page`: int
- `page_size`: int (max 100)

**Response (200):**
```json
{
  "items": [
    {
      "id": 1,
      "name": "Beachfront Villa",
      "slug": "beachfront-villa",
      "location": {
        "city": "Manuel Antonio",
        "region": "Puntarenas",
        "lat": 9.3968,
        "lng": -84.1397
      },
      "price_per_night": 250.00,
      "currency": "USD",
      "max_guests": 8,
      "rating": 4.8,
      "images": [
        {
          "url": "https://...",
          "caption": "Ocean view"
        }
      ]
    }
  ],
  "total": 245,
  "page": 1,
  "pages": 13
}
```

### POST /properties/
Create property (Vendor only).

**Request:**
```json
{
  "name": "Mountain Lodge",
  "description": "Cozy cabin in Monteverde",
  "property_type": "cabin",
  "location": {
    "address": "Santa Elena",
    "city": "Monteverde",
    "region": "Guanacaste",
    "lat": 10.3000,
    "lng": -84.8000
  },
  "price_per_night": 120.00,
  "max_guests": 4,
  "bedrooms": 2,
  "bathrooms": 1,
  "amenities": ["wifi", "kitchen", "parking"],
  "images": [
    {
      "url": "https://...",
      "order": 1
    }
  ]
}
```

### GET /properties/{id}
Get property details.

**Response includes:**
- Full property details
- Vendor info (public)
- Availability calendar
- Reviews (last 10)
- Similar properties

### PUT /properties/{id}
Update property (Owner or Admin).

### DELETE /properties/{id}
Delete property (Owner or Admin - soft delete).

---

## 🎯 Tours

Same endpoints as Properties:
- `GET /tours/`
- `POST /tours/` (Vendor)
- `GET /tours/{id}`
- `PUT /tours/{id}` (Owner)
- `DELETE /tours/{id}` (Owner)

**Additional tour fields:**
```json
{
  "duration_hours": 4,
  "difficulty": "moderate",
  "includes": ["guide", "transport", "lunch"],
  "meeting_point": "Hotel lobby"
}
```

---

## 🚗 Vehicles

- `GET /vehicles/`
- `POST /vehicles/` (Vendor)
- `GET /vehicles/{id}`
- `PUT /vehicles/{id}` (Owner)
- `DELETE /vehicles/{id}` (Owner)

**Vehicle fields:**
```json
{
  "vehicle_type": "suv",
  "brand": "Toyota",
  "model": "4Runner",
  "year": 2023,
  "transmission": "automatic",
  "price_per_day": 85.00
}
```

---

## ⛵ Boats

- `GET /boats/`
- `POST /boats/` (Vendor)
- `GET /boats/{id}`
- `PUT /boats/{id}` (Owner)
- `DELETE /boats/{id}` (Owner)

**Boat fields:**
```json
{
  "boat_type": "yacht",
  "capacity": 12,
  "amenities": ["bathroom", "kitchen", "sundeck"]
}
```

---

## ✈️ Flights

- `GET /flights/`
- `POST /flights/` (Vendor)
- `GET /flights/{id}`
- `PUT /flights/{id}` (Owner)
- `DELETE /flights/{id}` (Owner)

**Flight fields:**
```json
{
  "airline": "Nature Air",
  "origin": "SJO",
  "destination": "PMZ",
  "departure_time": "08:00",
  "arrival_time": "09:30",
  "price": 150.00
}
```

---

## 🚐 Transportation

- `GET /transport/`
- `POST /transport/` (Vendor)
- `GET /transport/{id}`
- `PUT /transport/{id}` (Owner)
- `DELETE /transport/{id}` (Owner)

**Transport fields:**
```json
{
  "service_type": "private",
  "pickup_location": "San José",
  "dropoff_location": "Manuel Antonio",
  "max_passengers": 4,
  "price": 180.00
}
```

---

## 📅 Bookings

### POST /bookings/property
Book a property.

**Request:**
```json
{
  "property_id": 1,
  "check_in": "2024-06-15",
  "check_out": "2024-06-20",
  "guests": 4,
  "guest_details": {
    "adults": 2,
    "children": 2
  },
  "special_requests": "Late check-in please"
}
```

**Response (201):**
```json
{
  "id": 123,
  "booking_number": "CR-2024-00123",
  "property": {...},
  "check_in": "2024-06-15",
  "check_out": "2024-06-20",
  "nights": 5,
  "guests": 4,
  "total_price": 1250.00,
  "status": "pending_payment",
  "payment_url": "https://checkout.stripe.com/...",
  "created_at": "2024-05-01T14:30:00Z"
}
```

### POST /bookings/tour
Book a tour.

**Request:**
```json
{
  "tour_id": 5,
  "date": "2024-06-16",
  "guests": 2,
  "pickup_location": "Hotel lobby"
}
```

### GET /bookings/
List my bookings (authenticated).

**Query Parameters:**
- `status`: pending, confirmed, cancelled, completed
- `upcoming`: bool (default true)

**Response:** Array of booking objects

### GET /bookings/{id}
Get booking details.

### PUT /bookings/{id}/cancel
Cancel booking (with refund policy).

---

## ⭐ Reviews

### GET /reviews/
List reviews with filters.

**Query Parameters:**
- `entity_type`: property, tour, vehicle, boat, flight, vendor
- `entity_id`: int
- `min_rating`: 1-5
- `sort`: newest, highest, lowest

### POST /reviews/
Create review (authenticated, must have booking).

**Request:**
```json
{
  "entity_type": "property",
  "entity_id": 1,
  "rating": 5,
  "title": "Amazing stay!",
  "comment": "The villa exceeded our expectations...",
  "recommend": true
}
```

### PUT /reviews/{id}
Update own review.

### DELETE /reviews/{id}
Delete own review (or Admin).

---

## 📝 Blog

### GET /blog/
List blog posts (public).

**Query Parameters:**
- `category`: destinations, tips, news
- `author`: string
- `featured`: bool

### POST /blog/
Create post (Admin only).

**Request:**
```json
{
  "title": "Top 10 Beaches in Costa Rica",
  "slug": "top-10-beaches-costa-rica",
  "content": "...",
  "excerpt": "Discover the best beaches...",
  "category": "destinations",
  "tags": ["beaches", "manuel-antonio", "guanacaste"],
  "featured_image": "https://...",
  "published": true
}
```

### GET /blog/{id}
Get post by ID.

### GET /blog/slug/{slug}
Get post by slug.

### PUT /blog/{id}
Update post (Admin).

### DELETE /blog/{id}
Delete post (Admin).

---

## 💬 Chat

### GET /chat/
Get my conversations.

### POST /chat/
Start new conversation.

**Request:**
```json
{
  "recipient_id": 5,
  "initial_message": "Hi, I have a question about your property..."
}
```

### GET /chat/{conversation_id}
Get conversation messages.

### POST /chat/{conversation_id}/messages
Send message.

---

## 🔍 Search

### GET /search/
Full-text search across all entities.

**Query Parameters:**
- `q`: search query (required)
- `type`: properties, tours, vehicles, boats, flights, blog, all
- `location`: city/region filter
- `price_min`: number
- `price_max`: number
- `sort`: relevance, price_asc, price_desc, rating

**Response:**
```json
{
  "results": [
    {
      "type": "property",
      "id": 1,
      "title": "Beachfront Villa",
      "description": "...",
      "image": "https://...",
      "price": 250.00,
      "location": "Manuel Antonio",
      "relevance_score": 0.95
    }
  ],
  "total": 42,
  "query": "beach villa",
  "search_time_ms": 45
}
```

### GET /search/map
Get map data for search results.

**Response:**
```json
{
  "markers": [
    {
      "id": 1,
      "type": "property",
      "lat": 9.3968,
      "lng": -84.1397,
      "title": "Beachfront Villa",
      "price": 250.00
    }
  ],
  "bounds": {
    "north": 9.8,
    "south": 8.5,
    "east": -83.0,
    "west": -85.5
  }
}
```

---

## ⚠️ Error Responses

### Standard Error Format
```json
{
  "detail": "Error message",
  "error_code": "RESOURCE_NOT_FOUND",
  "status_code": 404
}
```

### Common Status Codes

| Code | Meaning | Common Causes |
|------|---------|---------------|
| 400 | Bad Request | Invalid JSON, missing required fields |
| 401 | Unauthorized | Missing/invalid token, expired token |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource doesn't exist |
| 409 | Conflict | Duplicate email, booking conflict |
| 422 | Validation Error | Pydantic validation failed |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Server Error | Unexpected error (logged) |

### Rate Limit Headers
```http
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 58
X-RateLimit-Reset: 1640995200
```

---

## 📊 Pagination

All list endpoints support pagination:

```
GET /properties/?page=2&page_size=20
```

**Response includes:**
```json
{
  "items": [...],
  "total": 245,
  "page": 2,
  "page_size": 20,
  "pages": 13,
  "has_next": true,
  "has_prev": true
}
```

---

## 🌐 Internationalization

API supports multiple languages via header:

```http
Accept-Language: es  # Spanish (default)
Accept-Language: en  # English
Accept-Language: fr  # French
```

---

## 📱 Webhooks

### Stripe Webhooks

**Endpoint:** `POST /stripe/webhook`

**Events:**
- `checkout.session.completed`
- `invoice.paid`
- `invoice.payment_failed`
- `customer.subscription.created`

**Verification:** Stripe signature verified with webhook secret.

---

## 🛡️ Security

### Password Requirements
- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one digit
- At least one special character (@$!%*?&)

### CORS
- Origins must be explicitly whitelisted
- Credentials enabled for authentication
- Preflight cached for 10 minutes

### Rate Limiting
- 60 requests per minute per IP
- 5 login attempts per 15 minutes
- Blocking after exceeded limits

---

## 📚 OpenAPI / Swagger

Interactive documentation available at:

```
https://api.costaricatravel.dev/docs
```

Download OpenAPI spec:

```
https://api.costaricatravel.dev/openapi.json
```

---

<p align="center">
  <strong>API Version 1.0</strong> | 
  <a href="mailto:api@costaricatravel.dev">Support</a>
</p>
