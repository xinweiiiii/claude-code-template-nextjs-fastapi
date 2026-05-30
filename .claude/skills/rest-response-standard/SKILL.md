---
name: rest-response-standard
description: REST response conventions for FastAPI — status codes, envelope format, error schema, and pagination shape.
---

# REST Response Standard

## Status codes

| Scenario | Code |
|---|---|
| Successful GET / PUT / PATCH | 200 |
| Successful POST (created resource) | 201 |
| Successful DELETE (no body) | 204 |
| Validation error | 422 |
| Auth missing / invalid | 401 |
| Permission denied | 403 |
| Resource not found | 404 |
| Conflict (duplicate) | 409 |

## Error schema

```python
class ErrorResponse(BaseModel):
    detail: str
    code: str | None = None  # machine-readable error code
```

```python
raise HTTPException(status_code=404, detail="User not found")
```

## Paginated response shape

```python
class Page(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    size: int
    pages: int
```

## Rules

- Never return raw ORM objects — always use response schemas
- Include `response_model=` on every route
- Use `status_code=201` on POST routes that create resources
- Return `204` with no body for successful deletes
- Use consistent `detail` wording for error messages