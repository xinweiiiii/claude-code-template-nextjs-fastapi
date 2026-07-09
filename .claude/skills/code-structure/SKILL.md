---
name: code-structure
displayName: Good Production Grade Code Structure
description: Go beyond readability to verify that code survives production reality. Use when writing, reviewing, or refactoring code to surface and test the hidden assumptions that clean code often hides — data shape, timing, partial failure, stale caches, migrations, and feature flags.
version: 1.0.0
---

# Production Grade Code Structure

Clean code helps humans read the system. It does not prove the system survives reality.

A function can look excellent in a pull request and still fail under real data, real
latency, real users, stale caches, partial failures, old migrations, feature flags, and
production timing. Readable code is easier to review — it is not automatically safer to
ship.

The difference between clean and correct is **assumptions**. This skill exists to make
those assumptions visible, tested, and safe under failure.

---

# When to Activate

Use this skill when:
- Writing or reviewing a pull request that "looks clean"
- Reviewing AI-generated code that reads well but was never run against real data
- Refactoring code where the happy path is obvious but failure paths are not
- Integrating an external API, webhook, queue, or third-party identity provider
- Working with cached data, feature flags, migrations, or background jobs
- Handling user actions that can be repeated, cancelled, or raced
- Anytime you are tempted to write "LGTM" because the diff is readable

Activate especially when code contains:
- A single happy-path flow with a generic `catch` block
- Types describing data that arrives from a boundary (API, DB, import, flag payload)
- `await` sequences that read like synchronous steps but cross time
- Business rules duplicated across UI, routes, and helpers
- Optimistic UI updates or success messages fired before confirmation

---

# The Core Question

For every piece of clean-looking code, ask:

**"What must be true for this to stay correct?"**

Then check whether each of those things is actually guaranteed, or merely assumed.

Do not reject clean code make its assumptions visible.

---

# The Seven Hidden Assumptions

Clean code most often hides risk in these seven places. Each has a symptom, the danger,
and what to do.

## 1. Data shape — "the input will match the type"

**Symptom:** A tidy function that reads fields straight off an object.

```ts
function getUserDisplayName(user: User) {
  return `${user.firstName} ${user.lastName}`;
}
```

```python
def get_user_display_name(user: User) -> str:
    return f"{user.first_name} {user.last_name}"
```

**Danger:** Production has imported users without `lastName`, older accounts with empty
`firstName`, an identity provider sending `name` instead of first/last, migration-created
partial users, deleted accounts still in audit history. The code is readable — it is just
not honest about the data it expects.

**Do:** Ask where the data *became* trustworthy. Validate and normalize at the boundary;
handle missing/partial fields explicitly rather than assuming the ideal shape.

```python
# Normalize at the boundary; the display function then trusts a real shape.
class UserProfile(BaseModel):
    first_name: str = ""
    last_name: str = ""
    display_name: str | None = None

    @model_validator(mode="after")
    def build_display_name(self) -> "UserProfile":
        full = f"{self.first_name} {self.last_name}".strip()
        object.__setattr__(self, "display_name", self.display_name or full or "Unknown user")
        return self

def get_user_display_name(user: UserProfile) -> str:
    return user.display_name  # guaranteed non-empty by the model
```

## 2. The happy path — "every step succeeds in order"

**Symptom:** The cleanest code in the diff is the path where everything goes right.

```ts
async function saveProfile(input: ProfileInput) {
  const profile = await updateProfile(input);
  showSuccessMessage();
  return profile;
}
```

```python
@router.post("/profile")
async def save_profile(input: ProfileInput) -> ProfileRead:
    profile = await update_profile(input)  # what if the row saves but the refresh below fails?
    await refresh_related_data(profile.id)
    return profile
```

**Danger:** The user clicks twice. The save succeeds but a dependent step fails. The
server returns stale data. The success message appears before related data refreshes. An
optimistic update was already applied when the request failed.

**Do:** Give the failure path as much attention as the readable path. Answer: what happens
on partial failure, retry, stale data, duplicate action, and user-visible recovery? Not
every function needs heavy defense — important flows do.

```python
@router.post("/profile")
async def save_profile(input: ProfileInput) -> ProfileRead:
    async with db.begin():  # multi-step write is atomic — no half-saved state
        profile = await update_profile(input)
        await record_audit(profile.id, action="profile_updated")
    # Cache refresh is best-effort and isolated: its failure must not report the write as failed.
    try:
        await refresh_related_data(profile.id)
    except CacheError:
        logger.warning("profile saved but cache refresh failed", extra={"profile_id": profile.id})
    return profile
```

## 3. Ownership — "a good name proves a good boundary"

**Symptom:** A clearly named function/helper the team stopped questioning.

```ts
canCancelSubscription(...)  // lives where? UI? auth? billing policy? a shared helper?
```

```python
can_cancel_subscription(...)  # copied into a route guard, a template, and two services?
```

**Danger:** The name improves the surface while the same decision exists in five places.
When the rule changes (enterprise cancels only after settlement, trials cancel
immediately, suspended needs approval, region-specific rules), the team must hunt through
buttons, routes, helpers, and tests. The code was readable; the rule was scattered.

**Do:** For any business rule that matters, know where the decision lives, who enforces
it, and which layer is allowed to reflect it. A clean name should make ownership visible,
not hide that it is missing.

```python
# One home for the rule; UI, routes, and jobs all consult it — none re-implement it.
class CancellationDecision(BaseModel):
    allowed: bool
    reason: str | None = None

def evaluate_cancellation(subscription: Subscription) -> CancellationDecision:
    if subscription.plan == "enterprise" and not subscription.invoice_settled:
        return CancellationDecision(allowed=False, reason="Settle outstanding invoice first")
    if subscription.status == "suspended":
        return CancellationDecision(allowed=False, reason="Requires support approval")
    return CancellationDecision(allowed=True)
```

## 4. Types at the edge — "the type describes production"

**Symptom:** A confident internal type applied to boundary data.

```ts
type Invoice = { id: string; status: "paid" | "failed" | "pending"; total: number };
```

```python
class Invoice(BaseModel):
    id: str
    status: Literal["paid", "failed", "pending"]
    total: float
```

**Danger:** Production has `status: "processing"`, a `total` of `null` from an import,
invoices without totals from a migration, a partial-refund status nobody added, a string
`total` from one buggy endpoint. The type describes what the code *wants*, not what it
*receives*.

**Do:** Types are powerful *inside* trusted code. At the edge — API responses, DB records,
webhooks, local storage, queues, CSV imports, flag payloads, migrated data — back them
with validation, normalization, contract tests, or defensive parsing. Never let a clean
type turn unknown input into trusted truth too early.

```python
# Parse untrusted boundary data explicitly; surface the unexpected instead of assuming it away.
class InvoiceIn(BaseModel):
    id: str
    status: str                       # accept what actually arrives, then map
    total: Decimal | None = None      # imports/migrations can omit it

    @field_validator("total", mode="before")
    @classmethod
    def coerce_total(cls, v: object) -> Decimal | None:
        if v in (None, ""):
            return None
        return Decimal(str(v))         # tolerate string totals from a buggy endpoint

    @model_validator(mode="after")
    def to_known_status(self) -> "InvoiceIn":
        known = {"paid", "failed", "pending", "processing", "refunded"}
        if self.status not in known:   # don't silently trust an unmodeled status
            raise ValueError(f"unhandled invoice status: {self.status!r}")
        return self
```

## 5. Error meaning — "a neat catch means failure is handled"

**Symptom:** A clean, generic error handler.

```ts
try {
  await submitOrder(order);
  showSuccess();
} catch {
  showError("Something went wrong");
}
```

```python
try:
    await submit_order(order)
except Exception:
    raise HTTPException(status_code=500, detail="Something went wrong")
```

**Danger:** Was it validation? Payment? Payment succeeded but order creation failed? A
timeout where the server may still have completed the work? A retryable provider error?
The exception was handled; the *meaning* was lost. Callers cannot decide if retry is safe;
support cannot explain it; developers cannot trace before/after a side effect.

**Do:** Preserve information the system needs to decide what happens next. Distinguish
user-correctable vs system vs permission vs temporary vs unsafe-to-retry vs unknown-state
errors. A generic message is sometimes fine for the UI; a generic failure *model* is not
fine for the system. Do not overbuild — match the error model to real consequences.

```python
# Map each failure to a stable code, correct status, and a retry-safety signal.
try:
    await submit_order(order)
except ValidationError as e:
    raise HTTPException(422, detail={"code": "ORDER_INVALID", "fields": e.errors()})
except PaymentDeclined as e:
    raise HTTPException(402, detail={"code": "PAYMENT_DECLINED", "retryable": False, "reason": e.reason})
except ProviderTimeout as e:
    # Outcome unknown — the charge may have gone through. Do NOT auto-retry blindly.
    logger.error("order submit timed out", extra={"order_id": order.id, "idempotency_key": e.key})
    raise HTTPException(504, detail={"code": "ORDER_STATE_UNKNOWN", "retryable": False,
                                     "next": "reconcile via idempotency key before retrying"})
```

## 6. Time — "requests finish in order and state doesn't move"

**Symptom:** `await` sequences that read as a clean, linear story.

```ts
const result = await fetchResults(query);
setResults(result);
```

```python
@router.post("/orders")
async def create_order(input: OrderInput) -> OrderRead:
    return await orders.create(input)  # a retried POST creates a duplicate order
```

**Danger:** Is the result still relevant? Did the query change? Did the user navigate
away? Did a newer request finish first? Users click twice, responses arrive out of order,
caches expire mid-flight, jobs retry, events deliver more than once, flags change after
deploy, another user updates the same record, a timeout does not prove failure.

**Do:** For the specific workflow, ask whether it breaks when timing changes. If yes,
design the waiting — cancellation, idempotency, deduplication, stale-response guards, or a
state machine. Not every call needs all of them; the risky ones do.

```python
# Idempotency key makes a duplicate submit (retry, double-click) safe: same key → same order.
@router.post("/orders")
async def create_order(input: OrderInput, idempotency_key: str = Header(...)) -> OrderRead:
    existing = await orders.find_by_idempotency_key(idempotency_key)
    if existing:
        return existing
    # Optimistic-concurrency write: the DB unique constraint on the key wins the race,
    # so two in-flight requests cannot both insert.
    try:
        return await orders.create(input, idempotency_key=idempotency_key)
    except UniqueViolation:
        return await orders.find_by_idempotency_key(idempotency_key)
```

## 7. Environment — "cache is fresh, flag stays off, migration saw clean data"

**Symptom:** Code that silently trusts cache freshness, flag state, or historical data.

```python
async def get_balance(account_id: str) -> Decimal:
    return await redis.get(f"balance:{account_id}")  # trusts the cache is fresh and present
```

**Danger:** The cache is stale. A feature flag flips one workspace onto an untested path
during deploy. A migration meets old, dirty records. The pull request looked ideal because
review sees the ideal version of the system, not old data or deployment timing.

**Do:** Make cache behavior non-magical (know the invalidation and TTL story). Confirm new
paths behind flags are covered. Confirm migrations handle old/partial records. Enforce
permissions on the backend, not just the UI.

```python
# Cache: explicit miss handling + TTL; the DB remains the source of truth.
async def get_balance(account_id: str) -> Decimal:
    cached = await redis.get(f"balance:{account_id}")
    if cached is not None:
        return Decimal(cached)
    balance = await accounts.compute_balance(account_id)   # fall back to truth on miss/stale
    await redis.set(f"balance:{account_id}", str(balance), ex=60)
    return balance

# Migration: never assume clean historical data — coalesce and backfill partial rows.
op.execute("UPDATE users SET first_name = '' WHERE first_name IS NULL")
op.alter_column("users", "first_name", nullable=False, server_default="")
```

---

# Review Checklist

Run this against any clean-looking change. "LGTM" is not the same as production
confidence.

- [ ] **Data shape:** Where did this data become trustworthy? Is the shape guaranteed or assumed?
- [ ] **Happy path:** What happens if a step fails after another step already succeeded?
- [ ] **Duplication of action:** Can this run twice? Is it idempotent where it needs to be?
- [ ] **Ownership:** Does this business rule live in exactly one clear place?
- [ ] **Boundary types:** Is untrusted input validated before the internal type is trusted?
- [ ] **Error meaning:** Can the caller/user/logs tell *which* failure this was and whether retry is safe?
- [ ] **Timing:** Does this break if responses arrive out of order or state changes underneath?
- [ ] **Cache:** Is freshness guaranteed, or is stale data possible here?
- [ ] **Migrations:** Does this handle old and partial records, not just clean ones?
- [ ] **Feature flags:** Is the flagged path actually tested, or only the default path?
- [ ] **Permissions:** Is the check enforced server-side, not just reflected in the UI?
- [ ] **Tests:** Do tests cover the risky assumption, not only the happy path?

---

# Writing Code Worth Trusting

The most trustworthy code is not always the shortest or most elegant. Its cleanliness
comes from **honesty**, not appearance. Aim for code that:

1. Makes the boundary between trusted and untrusted data explicit.
2. Gives failure paths names and meaning.
3. Makes retries either safe or intentionally avoided.
4. Puts each business rule in a single, obvious home.
5. Does not treat caches, migrations, flags, or external services as politely reliable.
6. Says what it needs and protects what can break.
7. Backs risky assumptions with tests.

Clean is not enough. Readable code helps humans understand the system; reliable code
survives it. When assumptions are hidden, clean code is *more* dangerous because it looks
safer than it is. When assumptions are visible, tested, and safe under failure, clean code
becomes trustworthy.

## Relationship to other skills

Pairs with `coding-patterns` (clean-code-production-patterns), which optimizes for
readability and maintainability. This skill is the counterweight: after code is clean,
verify it is *correct* under production reality.
