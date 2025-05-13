
# 🛰️ API Documentation

This backend is powered by FastAPI and exposes multiple endpoints for property-related data and machine learning predictions.

---

## 🔮 Prediction Endpoint

### `POST /predict`

Returns predicted rent and sale prices for a given property.

#### Request Body
```json
{
  "area": 95,
  "location": "Arabkir",
  "rooms": 3,
  "property_type": "Apartment"
}
```

#### Response Example
```json
{
  "predicted_rent": 200000,
  "predicted_sale": 23000000
}
```

---

## 👥 User Endpoints

### `POST /users/`
Creates a new user.

#### Request
```json
{
  "user_id": 1,
  "user_type": "Owner"
}
```

### `GET /users/{user_id}`
Fetch a user by their ID.

---

## 📍 Location Endpoints

### `POST /locations/`
Create a new location.

#### Request
```json
{
  "location_id": 101
}
```

### `GET /locations/{location_id}`
Retrieve a location by its ID.

---

## 🏢 Property Type Endpoints

### `POST /property_types/`
Create a new property type.

#### Request
```json
{
  "type_id": 1,
  "type_name": "Apartment"
}
```

### `GET /property_types/{type_id}`
Retrieve a property type by ID.

---

## 🏠 Property Endpoints

### `POST /properties/`
Create a new property.

#### Request
```json
{
  "property_id": 10,
  "user_id": 1,
  "location_id": 101
}
```

### `GET /properties/{property_id}`
Retrieve a property by ID.

---

## 🖼️ Image Endpoints

### `POST /images/`
Create a new image entry for a property.

#### Request
```json
{
  "image_id": 1,
  "property_id": 10,
  "image_url": "https://example.com/image.jpg"
}
```

### `GET /images/{image_id}`
Retrieve an image record.

### `GET /images/`
List all image records.

---

## 🧪 Testing Tips

You can test all endpoints at:

- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

Use tools like **Postman** or **cURL** for direct testing, or interact directly via Swagger.
