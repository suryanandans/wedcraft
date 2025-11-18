# WedCraft Form Handling API Documentation

This document provides comprehensive documentation for the WedCraft form handling APIs that replace the hardcoded RSVP forms section.

## Overview

The form handling system provides flexible APIs for:
- Creating dynamic form templates
- Managing form responses
- Retrieving form data
- Building custom frontends

## Base URL
```
http://localhost:8000
```

## Authentication
Most admin endpoints require authentication. Include the JWT token in the Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

---

## Form Template Management APIs

### 1. Create Form Template
**POST** `/api/admin/form-templates`

Create a new form template with custom fields and validation.

**Request Body:**
```json
{
  "name": "Wedding RSVP Form",
  "description": "Guest response form for wedding invitation",
  "form_schema": "{\"fields\":[{\"name\":\"family_name\",\"type\":\"text\",\"label\":\"Family Name\",\"required\":true},{\"name\":\"attendance\",\"type\":\"select\",\"label\":\"Will you attend?\",\"options\":[\"Yes\",\"No\",\"Maybe\"],\"required\":true},{\"name\":\"members_count\",\"type\":\"number\",\"label\":\"Number of members\",\"required\":false},{\"name\":\"food_preference\",\"type\":\"radio\",\"label\":\"Food Preference\",\"options\":[\"Vegetarian\",\"Non-Vegetarian\"],\"required\":true}]}"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Form template created successfully",
  "form_template": {
    "id": 1,
    "name": "Wedding RSVP Form",
    "description": "Guest response form for wedding invitation",
    "form_schema": "...",
    "is_active": true,
    "created_at": "2024-11-18T12:00:00"
  }
}
```

### 2. Get All Form Templates
**GET** `/api/admin/form-templates`

Retrieve all form templates.

**Response:**
```json
{
  "success": true,
  "templates": [
    {
      "id": 1,
      "name": "Wedding RSVP Form",
      "description": "Guest response form for wedding invitation",
      "form_schema": "...",
      "is_active": true,
      "created_by": 1,
      "created_at": "2024-11-18T12:00:00",
      "updated_at": "2024-11-18T12:00:00"
    }
  ]
}
```

### 3. Get Specific Form Template
**GET** `/api/admin/form-templates/{template_id}`

Retrieve a specific form template by ID.

**Response:**
```json
{
  "success": true,
  "template": {
    "id": 1,
    "name": "Wedding RSVP Form",
    "description": "Guest response form for wedding invitation",
    "form_schema": "...",
    "is_active": true,
    "created_by": 1,
    "created_at": "2024-11-18T12:00:00",
    "updated_at": "2024-11-18T12:00:00"
  }
}
```

### 4. Update Form Template
**PUT** `/api/admin/form-templates/{template_id}`

Update an existing form template.

**Request Body:**
```json
{
  "name": "Updated Wedding RSVP Form",
  "description": "Updated description",
  "form_schema": "{\"fields\":[...]}",
  "is_active": true
}
```

**Response:**
```json
{
  "success": true,
  "message": "Form template updated successfully"
}
```

### 5. Delete Form Template
**DELETE** `/api/admin/form-templates/{template_id}`

Delete a form template.

**Response:**
```json
{
  "success": true,
  "message": "Form template deleted successfully"
}
```

---

## Form Response Management APIs

### 1. Submit Form Response (Public)
**POST** `/api/forms/{template_id}/submit`

Submit a response to a form template. This is a public endpoint that doesn't require authentication.

**Request Body:**
```json
{
  "response_data": "{\"family_name\":\"The Smith Family\",\"attendance\":\"Yes\",\"members_count\":4,\"food_preference\":\"Vegetarian\"}",
  "submitted_by_email": "smith@example.com",
  "submitted_by_name": "John Smith"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Form response submitted successfully",
  "response_id": 1
}
```

### 2. Get All Form Responses
**GET** `/api/admin/form-responses`

Retrieve all form responses across all templates.

**Response:**
```json
{
  "success": true,
  "responses": [
    {
      "id": 1,
      "form_template_id": 1,
      "response_data": "{\"family_name\":\"The Smith Family\",\"attendance\":\"Yes\"}",
      "submitted_by_email": "smith@example.com",
      "submitted_by_name": "John Smith",
      "created_at": "2024-11-18T12:30:00"
    }
  ]
}
```

### 3. Get Responses by Template
**GET** `/api/admin/form-responses/{template_id}`

Retrieve all responses for a specific form template.

**Response:**
```json
{
  "success": true,
  "template_id": 1,
  "responses": [
    {
      "id": 1,
      "response_data": "{\"family_name\":\"The Smith Family\",\"attendance\":\"Yes\"}",
      "submitted_by_email": "smith@example.com",
      "submitted_by_name": "John Smith",
      "created_at": "2024-11-18T12:30:00"
    }
  ]
}
```

### 4. Get Specific Form Response
**GET** `/api/admin/form-responses/response/{response_id}`

Retrieve a specific form response by ID.

**Response:**
```json
{
  "success": true,
  "response": {
    "id": 1,
    "form_template_id": 1,
    "response_data": "{\"family_name\":\"The Smith Family\",\"attendance\":\"Yes\"}",
    "submitted_by_email": "smith@example.com",
    "submitted_by_name": "John Smith",
    "created_at": "2024-11-18T12:30:00"
  }
}
```

### 5. Delete Form Response
**DELETE** `/api/admin/form-responses/{response_id}`

Delete a form response.

**Response:**
```json
{
  "success": true,
  "message": "Form response deleted successfully"
}
```

---

## Form Schema Format

The `form_schema` field uses JSON format to define form fields:

```json
{
  "fields": [
    {
      "name": "field_name",
      "type": "text|email|number|select|radio|checkbox|textarea|date",
      "label": "Field Label",
      "placeholder": "Placeholder text",
      "required": true|false,
      "options": ["Option 1", "Option 2"],  // For select/radio/checkbox
      "validation": {
        "min": 1,
        "max": 100,
        "pattern": "regex_pattern"
      }
    }
  ]
}
```

### Field Types:
- **text**: Single line text input
- **email**: Email input with validation
- **number**: Numeric input
- **select**: Dropdown selection
- **radio**: Radio button group
- **checkbox**: Checkbox group
- **textarea**: Multi-line text input
- **date**: Date picker

### Example Form Schema:
```json
{
  "fields": [
    {
      "name": "family_name",
      "type": "text",
      "label": "Family Name",
      "placeholder": "e.g., The Smith Family",
      "required": true
    },
    {
      "name": "attendance",
      "type": "select",
      "label": "Will you attend the wedding?",
      "options": ["Yes", "No", "Maybe"],
      "required": true
    },
    {
      "name": "members_count",
      "type": "number",
      "label": "Number of family members attending",
      "required": false,
      "validation": {
        "min": 1,
        "max": 20
      }
    },
    {
      "name": "food_preference",
      "type": "radio",
      "label": "Food Preference",
      "options": ["Vegetarian", "Non-Vegetarian"],
      "required": true
    },
    {
      "name": "special_requirements",
      "type": "textarea",
      "label": "Special Requirements or Messages",
      "placeholder": "Any dietary restrictions, accessibility needs, etc.",
      "required": false
    }
  ]
}
```

---

## Usage Examples

### Creating a Wedding RSVP Form

1. **Create the form template:**
```bash
curl -X POST "http://localhost:8000/api/admin/form-templates" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "name": "Wedding RSVP Form",
    "description": "Guest response form for John & Sarah wedding",
    "form_schema": "{\"fields\":[{\"name\":\"family_name\",\"type\":\"text\",\"label\":\"Family Name\",\"required\":true},{\"name\":\"attendance\",\"type\":\"select\",\"label\":\"Will you attend?\",\"options\":[\"Yes\",\"No\",\"Maybe\"],\"required\":true}]}"
  }'
```

2. **Submit a response (public endpoint):**
```bash
curl -X POST "http://localhost:8000/api/forms/1/submit" \
  -H "Content-Type: application/json" \
  -d '{
    "response_data": "{\"family_name\":\"The Johnson Family\",\"attendance\":\"Yes\"}",
    "submitted_by_email": "johnson@example.com",
    "submitted_by_name": "Mike Johnson"
  }'
```

3. **Retrieve responses:**
```bash
curl -X GET "http://localhost:8000/api/admin/form-responses/1" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Building a Custom Frontend

You can use these APIs to build any frontend (React, Vue, Angular, etc.):

1. Fetch form template to get field definitions
2. Render form based on schema
3. Submit responses to the public endpoint
4. Admin can view responses through admin endpoints

---

## Error Responses

All endpoints return consistent error responses:

```json
{
  "detail": "Error message describing what went wrong"
}
```

Common HTTP status codes:
- **200**: Success
- **201**: Created
- **400**: Bad Request
- **401**: Unauthorized
- **404**: Not Found
- **422**: Validation Error
- **500**: Internal Server Error

---

## Dashboard Integration

The dashboard stats endpoint now includes form metrics:

**GET** `/api/admin/stats`

```json
{
  "success": true,
  "stats": {
    "total_users": 5,
    "total_events": 2,
    "total_rsvps": 3,
    "active_events": 2,
    "total_form_templates": 2,
    "total_form_responses": 15
  }
}
```

This flexible API system allows you to create any type of form and handle responses dynamically, replacing the need for hardcoded RSVP forms in the frontend.