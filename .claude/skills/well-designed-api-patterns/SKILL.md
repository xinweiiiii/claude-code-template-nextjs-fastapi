---
name: well-designed-api-patterns
description: API design patterns that matters - predictable, backwards-compatible, resilent and self-documenting.
---

# Deployment Patterns for Python

Apply proven API design patterns that prevent breaking clients, improve reliability, simplify integrations, and enable long-term evolution of public and internal APIs.

Focus on four core qualities:
- Predictable — Consistent naming, behavior, and conventions
- Backward-Compatible — Existing clients continue working after changes
- Resilient — Handles retries, failures, and partial outages safely
- Self-Documenting — Clear contracts, discoverability, and meaningful errors

## When to Activate
Use this skill when:
- Designing REST APIs, HTTP APIs, or service interfaces
- Reviewing API contracts, endpoint designs, or OpenAPI specifications
- Planning API versioning and deprecation strategies
- Implementing idempotent operations and retry-safe workflows
- Designing pagination for large datasets
- Standardizing error handling and response contracts
- Introducing rate limiting or throttling policies
- Evolving APIs while maintaining backward compatibility
- Designing public APIs intended for long-term support
- Reviewing breaking changes before release
- Building payment, order, provisioning, or other side-effecting APIs
- Creating platform, partner, or external-facing integrations

# Pattern 1: Versioning Strategy
## Goals
- Allow API evolution without breaking clients
- Support multiple versions simultaneously
- Provide a predictable migration path

## Recommended Approaches

### URL Versioning

```http
/v1/users
/v2/users
```

**Pros**

- Easy routing
- Easy caching
- Explicit and discoverable

**Cons**

- Versions become part of the resource path

### Header Versioning

```http
Accept: application/vnd.company+json;version=2
```

**Pros**

- Cleaner URLs
- Resource-oriented

**Cons**

- Harder debugging
- Less discoverable

### Avoid Query Parameter Versioning

```http
/users?version=2
```

Use only for legacy compatibility.

## Version Lifecycle

1. Release new version
2. Announce deprecation
3. Add `Deprecation` header
4. Add `Sunset` header
5. Notify consumers
6. Remove after migration window

Public APIs should typically provide at least **6 months notice** before retirement.

## Implementation Pattern

Use adapters rather than duplicating business logic.

```text
/v1/* -> v1 adapter -> core business logic
/v2/* -> v2 adapter -> core business logic
```

# Pattern 2: Idempotency
## Goals
Prevent duplicate side effects caused by retries.

## Required For

- Payments
- Orders
- Resource creation
- Provisioning workflows
- Any operation with side effects

## Recommended Pattern

Require clients to send:

```http
Idempotency-Key: <unique-id>
```

Server behavior:

1. Check if key already exists
2. Return stored response if found
3. Execute operation otherwise
4. Store result with TTL
5. Return original response

### Example

```python
def create_payment(payload, idempotency_key):
    existing = cache.get(idempotency_key)

    if existing:
        return existing

    result = process_payment(payload)

    cache.set(
        idempotency_key,
        result,
        ttl=86400
    )

    return result
```

## Guidelines

- Store keys in Redis or equivalent
- Use a TTL (typically 24 hours)
- Treat idempotency as a correctness guarantee, not a caching optimization

# Pattern 3: Pagination
## Avoid Offset Pagination

```sql
SELECT *
FROM users
LIMIT 20 OFFSET 10000;
```

Problems:

- Poor performance at scale
- Duplicate records
- Missing records
- Data shifting during pagination

## Prefer Cursor Pagination

```json
{
  "data": [],
  "next_cursor": "abc123",
  "has_more": true
}
```

### Recommended Query Pattern

```sql
WHERE id > :last_id
ORDER BY id
LIMIT 20
```

Benefits:

- Stable ordering
- Index-friendly
- Consistent performance

## Response Requirements

Include:

- `data`
- `next_cursor`
- `has_more`

Avoid exposing database internals.

# Pattern 4: Error Contracts


Treat errors as part of the API contract.

## Use RFC 7807 Problem Details

```json
{
  "type": "https://api.example.com/errors/invalid-request",
  "title": "Validation Failed",
  "status": 422,
  "detail": "Email address is invalid",
  "instance": "/users",
  "request_id": "req_123",
  "error_code": "INVALID_EMAIL"
}
```

## Status Code Guidelines

| Status | Meaning |
|----------|----------|
| 400 | Invalid syntax |
| 401 | Authentication missing or invalid |
| 403 | Authenticated but unauthorized |
| 404 | Resource not found |
| 409 | Conflict |
| 422 | Validation or business rule failure |
| 429 | Rate limit exceeded |
| 500 | Internal error |
| 503 | Dependency unavailable |

## Requirements

Always include:

- `request_id`
- `error_code`
- actionable error messages

Never expose:

- stack traces
- internal implementation details
- database exceptions

# Pattern 5: Rate Limiting & Throlttling
## Goals
Protect systems while providing useful client feedback.

## Required Headers

Return on every response:

```http
X-RateLimit-Limit
X-RateLimit-Remaining
X-RateLimit-Reset
```

When throttled:

```http
429 Too Many Requests
Retry-After: 60
```

## Recommended Algorithms

### Token Bucket

Default recommendation.

Benefits:

- Supports bursts
- Predictable average rate

### Sliding Window

Use when precision matters.

### Leaky Bucket

Use for expensive workloads requiring smooth traffic.

## Design Guidelines

Different limits based on:

- API key tier
- Endpoint cost
- Consumer type

Always communicate limits clearly.

# Backwards Comaptibility
## Breaking Changes

Examples:

- Removing fields
- Renaming fields
- Changing field types
- Adding required request fields
- Changing status codes
- Changing error codes

## Usually Safe Changes

- Adding optional response fields
- Adding new endpoints
- Adding optional query parameters
- Adding optional request fields

## Use Expand-Contract

### Phase 1: Expand

```json
{
  "user_name": "alice",
  "username": "alice"
}
```

### Phase 2: Migrate

Consumers move to the new field.

### Phase 3: Contract

```json
{
  "username": "alice"
}
```

Only remove deprecated fields after consumers have migrated.

# Pattern 7: Contract First Design
## Principle

Define the API contract before implementation.

Use:

- OpenAPI
- AsyncAPI

## Benefits

- Parallel frontend/backend development
- Mock generation
- SDK generation
- Contract testing
- Better design reviews

## Recommended Practices

### Reusable Schemas

```yaml
components:
  schemas:
    User:
      type: object
      properties:
        id:
          type: string
        email:
          type: string
```

### Reference Everywhere

```yaml
$ref: '#/components/schemas/User'
```

