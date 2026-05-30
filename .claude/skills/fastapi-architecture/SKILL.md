---
name: fastapi-architecture
description: Standard REST API response conventions for FastAPI including status codes, response models, error handling, pagination, and API consistency rules.

# Skill: REST Response Standard

## Purpose

Provide consistent REST API response patterns across all FastAPI endpoints.

This skill ensures predictable APIs, easier frontend integration, and consistent error handling.

## Use This Skill Whenever

* Creating FastAPI routes
* Modifying API responses
* Designing CRUD endpoints
* Adding pagination
* Adding filtering or sorting
* Implementing error handling
* Creating response schemas
* Designing API contracts
* Reviewing FastAPI endpoints
* Refactoring API layers

---

# Response Principles

## API Responses Must Be
* Consistent
* Predictable
* Explicitly typed
* Backward compatible when possible
* Serializable via Pydantic models

Never return:
* Raw ORM models
* Database entities
* SQLAlchemy models
* Internal exceptions
* Unstructured dictionaries

Always return response schemas.

---

# Status Codes

| Scenario                      | Status |
| ----------------------------- | ------ |
| Successful GET                | 200    |
| Successful PUT                | 200    |
| Successful PATCH              | 200    |
| Successful POST (create)      | 201    |
| Successful DELETE             | 204    |
| Validation Error              | 422    |
| Authentication Required       | 401    |
| Permission Denied             | 403    |
| Resource Not Found            | 404    |
| Conflict / Duplicate Resource | 409    |
| Rate Limited                  | 429    |
| Internal Server Error         | 500    |

---

# Success Response Rules

## Read Operations

```python
@router.get("/{user_id}", response_model=UserResponse)
```

Return:

```json
{
  "id": "123",
  "email": "maya@example.com",
  "name": "Maya"
}
```

## Create Operations

Always:

* Return the created resource
* Use HTTP 201

```python
@router.post(
    "/",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
```

## Delete Operations

Always:

```python
status_code=204
```

Return no body.

```python
return Response(status_code=204)
```

---

# Error Response Standard

All API errors should follow the same shape.

```python
class ErrorResponse(BaseModel):
    detail: str
    code: str | None = None
```

Example:

```json
{
  "detail": "User not found",
  "code": "USER_NOT_FOUND"
}
```

### Good Error Messages

```json
{
  "detail": "User not found"
}
```

```json
{
  "detail": "Email already exists"
}
```

```json
{
  "detail": "Insufficient permissions"
}
```

### Avoid

```json
{
  "detail": "Exception occurred"
}
```

```json
{
  "detail": "Database error"
}
```

```json
{
  "detail": "Something went wrong"
}
```

Errors should be actionable and user-friendly.

---

# Pagination Standard

All list endpoints should support pagination.

```python
class Page(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    size: int
    pages: int
```

Example:

```json
{
  "items": [...],
  "total": 124,
  "page": 2,
  "size": 25,
  "pages": 5
}
```

### Pagination Rules

* Default page size should be defined
* Maximum page size should be enforced
* Return total record count
* Return total pages
* Never return unbounded collections

---

# Filtering and Sorting

List endpoints should support:

* Pagination
* Filtering
* Sorting

Example:

```http
GET /users?page=1&size=25
GET /users?status=active
GET /users?sort_by=created_at&sort_order=desc
```

Validate all query parameters.

---

# Response Model Requirements

Every route must define:

```python
response_model=
```

Example:

```python
@router.get(
    "/{id}",
    response_model=UserResponse
)
```

Never omit response models.

Benefits:

* Documentation generation
* Response validation
* Field filtering
* Type safety

---

# Serialization Rules

Separate schemas for:

```python
UserCreate
UserUpdate
UserResponse
UserListItem
```

Do not reuse create schemas as response schemas.

Do not expose:

* Password hashes
* Internal IDs not meant for clients
* Audit fields unless explicitly required
* Sensitive metadata

---

# Error Handling

Prefer domain-specific exceptions.

Example:

```python
UserNotFoundError
DuplicateEmailError
InsufficientPermissionsError
```

Translate domain exceptions into HTTP responses at the API layer.

Do not raise generic exceptions from services.

---

# Consistency Rules
Use consistent wording across the API.

Preferred:

```text
User not found
Email already exists
Invalid credentials
Insufficient permissions
```

Avoid multiple variations for the same error.

Bad:

```text
User missing
No user found
Could not locate user
```

Choose one standard phrase.

---

# API Review Checklist

Before creating or modifying an endpoint verify:

* Response model exists
* Status code is correct
* Errors follow ErrorResponse
* Sensitive fields are hidden
* Pagination is implemented for list endpoints
* Validation is performed through schemas
* Delete returns 204 with no body
* Create returns 201 with created resource
* No ORM models are returned directly

## Success Criteria

An endpoint is compliant when:

* Responses are predictable
* Status codes are correct
* Errors are standardized
* Pagination is consistent
* Response models are explicit
* Sensitive fields cannot leak
* Frontend consumers can rely on a stable contract
