---
name: clean-code-production-patterns
displayName: Clean Code Production Patterns
description: Enforce production-grade coding patterns that optimize maintainability, incident response, change safety, and long-term system evolution. Use when designing, reviewing, or refactoring application code.
version: 1.0.0
---

# Clean Code Production Patterns

Clean code is boring code.

Not because it lacks sophistication, but because it makes bugs easier to find, changes easier to make, and systems harder to misunderstand.

AI-assisted development often introduces the opposite problem: implementations become unnecessarily complex because generating code is easier than maintaining it.

This skill enforces a set of coding patterns designed for production systems where maintainability, incident response, and change safety matter more than clever implementations.

---

# When to Activate
Use this skill when:
- Reviewing pull requests
- Refactoring existing code
- Designing application services
- Building backend APIs
- Implementing business workflows
- Designing domain models
- Integrating external systems
- Writing TypeScript, JavaScript, Python, Go, Java, or C# services
- Investigating production incidents
- Improving testability
- Reducing cognitive complexity
- Evaluating AI-generated code
- Breaking down large feature implementations
- Reviewing architecture for maintainability

Activate especially when code contains:
- Deeply nested conditionals
- Generic variable names
- Leaky abstractions
- Excessive optional fields
- Complex orchestration logic
- Unstructured error handling

---

# Core Principles

1. Optimize for future maintainers.
2. Make failure paths obvious.
3. Model business concepts explicitly.
4. Prevent invalid states.
5. Isolate external dependencies.
6. Separate decisions from actions.
7. Make changes easy to review and rollback.

---

# Pattern 1: Return Early Instead of Building Conditional Mazes

## Problem

Deep nesting hides business logic and makes debugging difficult.

Bad:

```ts
if (user) {
  if (input.email) {
    if (user.canEditProfile) {
      if (user.isActive) {
        if (hasPermission) {
          return saveProfile();
        }
      }
    }
  }
}
```

## Preferred Approach

Remove negative paths immediately.

```ts
async function updateUserProfile(userId: string, input: ProfileInput) {
  const user = await getUser(userId);

  if (!user) {
    throw new NotFoundError("User not found");
  }

  if (!input.email) {
    throw new ValidationError("Email is required");
  }

  if (!user.canEditProfile) {
    throw new ForbiddenError("User cannot edit profile");
  }

  return saveProfile(user.id, input);
}
```

## Review Checklist

* Can nested conditionals be flattened?
* Are failure paths visible first?
* Is the happy path easy to follow?
* Can a developer understand the flow during an incident?

---

# Pattern 2: Name Business Meaning, Not Technical Containers

## Problem

Generic names communicate implementation details instead of business intent.

Bad:

```ts
const result = await getData(id);

if (result.status === "active") {
  await process(result);
}
```

The reader must infer what "result" actually represents.

## Preferred Approach

Name entities according to business meaning.

```ts
const subscription = await getSubscription(subscriptionId);

if (subscription.isBillable) {
  await chargeSubscription(subscription);
}
```

## Naming Rules

Avoid:
- data
- result
- item
- payload
- response
- value
- temp
- obj
- list

Prefer:
- customer
- invoice
- subscription
- paymentAuthorization
- refundEligibility
- shipment
- accountBalance

Long names are acceptable when they communicate business intent.

## Review Checklist

* Does the variable represent a business concept?
* Could a new engineer understand the workflow without opening definitions?
* Does the name explain why it exists?

---

# Pattern 3: Create Boundaries Around External Systems

## Problem

Directly exposing third-party schemas throughout the codebase creates widespread coupling.

Bad:

```ts
const userName = response.data.user_name;
const isActive = response.data.status === "ACTIVE";
const plan = response.data.subscription.plan_name;
```

Vendor-specific fields leak everywhere.

## Preferred Approach

Create translation layers.

```ts
function mapBillingCustomer(
  response: BillingCustomerResponse
): Customer {
  return {
    id: response.id,
    name: response.user_name,
    isBillable: response.status === "ACTIVE",
    planName: response.subscription?.plan_name ?? "Free"
  };
}
```

The rest of the application depends only on internal models.

## Apply This Rule To
* Third-party APIs
* Webhooks
* Databases
* Message queues
* Framework request objects
* Environment variables

Do not allow:

* Raw database rows in UI logic
* HTTP response shapes in domain logic
* Framework objects in business services
* Environment variable parsing scattered across files

## Review Checklist

* Is there a boundary layer?
* Can a vendor contract change without touching business logic?
* Are external models isolated?

---

# Pattern 4: Do Not Allow Invalid States

## Problem

Optional fields everywhere create impossible-to-reason-about objects.

Bad:

```ts
type User = {
  id?: string;
  email?: string;
  role?: string;
  status?: string;
};
```

Every usage now requires defensive checks.

## Preferred Approach

Represent states explicitly.

```ts
type DraftUser = {
  email: string;
  role: "admin" | "member";
};

type SavedUser = {
  id: string;
  email: string;
  role: "admin" | "member";
  status: "active" | "disabled";
};
```

Each type represents a valid business state.

## Review Checklist

* Can invalid combinations exist?
* Are lifecycle states modeled explicitly?
* Are optional fields actually optional?

---

# Pattern 5: Separate Decisions From Actions

## Problem

Business rules become tightly coupled to side effects.

Bad:

```ts
async function refundInvoice(invoiceId: string) {
  const invoice = await getInvoice(invoiceId);

  if (invoice.status !== "paid") {
    throw new Error("Invoice cannot be refunded");
  }

  if (invoice.refundedAt) {
    throw new Error("Invoice already refunded");
  }

  await paymentProvider.refund(invoice.paymentId);
  await markInvoiceRefunded(invoice.id);
  await sendRefundEmail(invoice.customerId);
}
```

Testing requires mocking multiple dependencies.

## Preferred Approach

Extract decisions into pure functions.

```ts
function getRefundEligibility(
  invoice: Invoice
): RefundEligibility {
  if (invoice.status !== "paid") {
    return {
      allowed: false,
      reason: "Invoice is not paid"
    };
  }

  if (invoice.refundedAt) {
    return {
      allowed: false,
      reason: "Invoice is already refunded"
    };
  }

  return { allowed: true };
}
```

```ts
async function refundInvoice(invoiceId: string) {
  const invoice = await getInvoice(invoiceId);

  const eligibility =
    getRefundEligibility(invoice);

  if (!eligibility.allowed) {
    throw new ValidationError(
      eligibility.reason
    );
  }

  await paymentProvider.refund(invoice.paymentId);
  await markInvoiceRefunded(invoice.id);
  await sendRefundEmail(invoice.customerId);
}
```

## Benefits

* Easier testing
* Easier reasoning
* Better reuse
* Cleaner orchestration

## Review Checklist

* Are business decisions pure?
* Can rules be tested without mocks?
* Are side effects isolated?

---

# Pattern 6: Make Errors Useful

## Problem

Errors are often written for developers but consumed by systems and users.

Bad:

```ts
throw new Error("Something went wrong");
```

Bad:

```ts
if (error.message.includes("already exists")) {
  showEmailTakenError();
}
```

Message parsing is fragile.

## Preferred Approach

Use structured errors.

```json
{
  "code": "USER_EMAIL_ALREADY_EXISTS",
  "message": "A user with this email already exists.",
  "details": {
    "field": "email"
  },
  "requestId": "req_8f91a2"
}
```

## Rules

### Error Codes

For machines:

```ts
USER_EMAIL_ALREADY_EXISTS
PAYMENT_DECLINED
REFUND_NOT_ALLOWED
```

### Error Messages

For humans:

```ts
"A user with this email already exists."
```

Never process messages programmatically.

## Logging

Include operational context.

```ts
logger.warn("Refund rejected", {
  invoiceId,
  customerId,
  reason: eligibility.reason,
  requestId
});
```

Never log:

* Passwords
* Tokens
* Payment information
* Secrets
* Sensitive personal data

## Review Checklist

* Are errors structured?
* Are codes stable?
* Are logs actionable?
* Is sensitive data excluded?

---

# Pattern 7: Optimize For Reviewable Changes, Not Demos

## Problem

Large pull requests hide risk.

Bad:

```txt
feat: update billing flow

- refactor invoice service
- rename payment fields
- update refund logic
- change dashboard UI
- add new webhook handler
- modify retry behavior
- fix customer status bug
- update tests
```

Reviewers cannot identify the true behavioral change.

Rollback becomes difficult.

## Preferred Approach

Split changes by behavior.

```txt
PR 1:
Rename payment fields without behavior changes

PR 2:
Add refund eligibility helper with tests

PR 3:
Wire refund eligibility into billing flow

PR 4:
Update dashboard UI to show refund reason

PR 5:
Add webhook retry behavior
```

## Rules

Separate:

* Refactoring
* Feature work
* Bug fixes
* Schema changes
* UI changes
* Infrastructure changes

Do not combine product changes with cleanup work.

## Review Checklist

* Can each PR be reviewed independently?
* Can each PR be reverted independently?
* Does the diff tell a clear story?
* Is behavior change obvious?

---

# AI Code Review Guidance

When reviewing AI-generated code:

1. Remove unnecessary abstractions.
2. Flatten excessive nesting.
3. Replace generic names with business language.
4. Extract pure business decisions.
5. Introduce external system boundaries.
6. Eliminate invalid states.
7. Improve error structures.
8. Break large changes into smaller diffs.

If the AI solution is harder to understand than the original implementation, simplify it.

The goal is not sophistication.

The goal is maintainability under production pressure.

---

# Success Criteria

Code should be:

* Easy to debug during incidents
* Easy to modify without fear
* Easy to review
* Easy to test
* Easy to rollback
* Easy for new engineers to understand
