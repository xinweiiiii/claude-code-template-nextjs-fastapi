---
name: nextjs-anti-patterns
description: Enforce Next.js App Router best practices, identify anti-patterns, reduce unnecessary client-side JavaScript, improve performance, and ensure proper Server Component architecture.
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
--------------------------------------------------

# Skill: Next.js App Router Standards & Anti-Patterns

## Purpose

Provide architectural guidance, performance optimization, and anti-pattern detection for Next.js App Router applications.

This skill helps ensure:

* Minimal client-side JavaScript
* Correct Server Component usage
* Proper data-fetching patterns
* Better performance
* Better SEO
* Cleaner component architecture
* Better maintainability

---

# Use This Skill Whenever
* Creating new pages
* Creating layouts
* Creating React components
* Implementing forms
* Implementing data fetching
* Adding authentication
* Adding authorization
* Reviewing Next.js code
* Refactoring frontend code
* Migrating from Pages Router
* Debugging hydration issues
* Debugging performance issues
* Reviewing useEffect usage
* Reviewing useState usage
* Investigating bundle size problems
* Designing frontend architecture

---

# Core Philosophy

When building with Next.js App Router:

1. Default to Server Components
2. Add Client Components only when required
3. Fetch data on the server whenever possible
4. Minimize client-side JavaScript
5. Keep the `use client` boundary as low as possible
6. Prefer framework-native features over React workarounds
7. Prefer URL state over local state where appropriate
8. Prefer composition over deeply nested client state
9. Optimize for simplicity first
10. Make caching decisions explicit

---

# TypeScript Rules

## Never Use `any`

This codebase enforces:

```json
{
  "@typescript-eslint/no-explicit-any": "error"
}
```

Using `any` is prohibited.

### Bad

```typescript
function handleSubmit(e: any) {}
const users: any[] = [];
```

### Good

```typescript
function handleSubmit(
  e: React.FormEvent<HTMLFormElement>
) {}

const users: User[] = [];
```

---

# Component Decision Tree

Before creating a component ask:

Does the component need:

* Event handlers?
* Browser APIs?
* Local state?
* React Context?
* Client-side libraries?

If NO:

```typescript
Server Component
```

If YES:

```typescript
Client Component
```

Default answer should be:

```typescript
Server Component
```

---

# Server Components

Use Server Components for:

* Data fetching
* Page rendering
* Layout rendering
* Database access
* API integration
* SEO content
* Authentication checks
* Authorization checks

Example:

```typescript
export default async function UsersPage() {
  const users = await getUsers();

  return (
    <UsersTable users={users} />
  );
}
```

---

# Client Components

Use Client Components only for:

* Event handlers
* Form interactions
* Local UI state
* Browser APIs
* Third-party browser libraries
* Context consumers

Example:

```typescript
'use client';

import { useState } from 'react';

export function Counter() {
  const [count, setCount] = useState(0);

  return (
    <button
      onClick={() => setCount(c => c + 1)}
    >
      {count}
    </button>
  );
}
```

---

# Data Fetching Rules

## Preferred

Fetch data in Server Components.

```typescript
export default async function PostsPage() {
  const posts = await getPosts();

  return (
    <PostsList posts={posts} />
  );
}
```

---

## Anti-Pattern: useEffect Data Fetching

### Bad

```typescript
'use client';

useEffect(() => {
  fetch('/api/posts')
    .then(r => r.json())
    .then(setPosts);
}, []);
```

### Why

* Slower first render
* Additional loading states
* More client-side JS
* Worse SEO
* Hydration complexity

### Good

```typescript
export default async function PostsPage() {
  const posts = await getPosts();

  return (
    <PostsList posts={posts} />
  );
}
```

---

# Server Actions Preferred

Use Server Actions for mutations.

### Preferred

```typescript
'use server';

export async function createProject(
  formData: FormData
) {
  // create project
}
```

---

### Avoid

```typescript
await fetch('/api/projects', {
  method: 'POST'
});
```

for internal application mutations.

---

## Use API Routes Only For

* Public APIs
* Third-party integrations
* Webhooks
* External consumers

---

# useEffect Anti-Patterns

## Browser Detection

### Bad

```typescript
const [isSafari, setIsSafari] = useState(false);

useEffect(() => {
  setIsSafari(
    /Safari/.test(navigator.userAgent)
  );
}, []);
```

### Good

```typescript
const isSafari =
  typeof navigator !== 'undefined' &&
  /Safari/.test(navigator.userAgent) &&
  !/Chrome/.test(navigator.userAgent);
```

Perform detection directly.

Avoid unnecessary state.

---

## URL Detection

### Bad

```typescript
const [url, setUrl] = useState('');

useEffect(() => {
  setUrl(window.location.href);
}, []);
```

### Good

```typescript
const handleShare = () => {
  navigator.share({
    url: window.location.href
  });
};
```

Read values when needed.

---

# useState Anti-Patterns

## Derived State

### Bad

```typescript
const [total, setTotal] = useState(0);

useEffect(() => {
  setTotal(
    products.reduce(
      (sum, p) => sum + p.price,
      0
    )
  );
}, [products]);
```

### Good

```typescript
const total = products.reduce(
  (sum, p) => sum + p.price,
  0
);
```

---

## Server Data

### Bad

```typescript
const [user, setUser] = useState(null);

useEffect(() => {
  fetchUser().then(setUser);
}, []);
```

### Good

```typescript
export default async function Page() {
  const user = await getUser();

  return <UserCard user={user} />;
}
```

---

# Performance Rules

## Avoid Waterfall Requests

### Bad

```typescript
const user = await getUser();
const projects = await getProjects();
const tasks = await getTasks();
```

### Good

```typescript
const [user, projects, tasks] =
  await Promise.all([
    getUser(),
    getProjects(),
    getTasks(),
  ]);
```

---

## Use Suspense

### Preferred

```typescript
<Suspense fallback={<Loading />}>
  <Projects />
</Suspense>
```

Avoid blocking the entire page on slow operations.

---

## Minimize use client

### Bad

```typescript
'use client';

export default function Page() {
  return (
    <>
      <Header />
      <Content />
    </>
  );
}
```

### Good

```typescript
export default function Page() {
  return (
    <>
      <Header />
      <Content />
      <InteractiveButton />
    </>
  );
}
```

Only interactive pieces should be client components.

---

# Routing Rules

## Use Link

### Bad

```typescript
window.location.href = '/dashboard';
```

### Good

```typescript
<Link href="/dashboard">
  Dashboard
</Link>
```

---

## Server Redirects

### Bad

```typescript
useRouter();
```

inside Server Components.

### Good

```typescript
redirect('/login');
```

---

# Metadata Rules

Never use:

```typescript
import Head from 'next/head';
```

Use:

```typescript
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Projects',
  description: 'Project dashboard'
};
```

---

# Loading & Error States

Route segments should consider:

```text
loading.tsx
error.tsx
not-found.tsx
```

Structure:

```text
app/
 ├── page.tsx
 ├── loading.tsx
 ├── error.tsx
 └── not-found.tsx
```

---

# Caching Rules

Caching must be explicit.

## Static

```typescript
fetch(url, {
  cache: 'force-cache'
});
```

## Revalidated

```typescript
fetch(url, {
  next: {
    revalidate: 60
  }
});
```

## Dynamic

```typescript
fetch(url, {
  cache: 'no-store'
});
```

Never rely on accidental caching behavior.

---

# Form Standards

Prefer:

* React Hook Form
* Zod
* Server Actions

Avoid:

* Large local form state
* Duplicated validation logic
* Manual validation everywhere

---

# Security Anti-Patterns

Flag immediately:

## Client-side Authorization

### Bad

```typescript
if (user.role === 'admin')
```

without server verification.

---

## Exposing Secrets

### Bad

```typescript
NEXT_PUBLIC_API_KEY
```

for private values.

---

## Unsanitized HTML

### Bad

```typescript
dangerouslySetInnerHTML
```

without sanitization.

---

## Trusting Client Input

All validation must happen on the server.

Frontend validation is UX only.

---

# Architecture Anti-Patterns

## Bad

```text
page.tsx
 ├── business logic
 ├── validation
 ├── API orchestration
 ├── data transformations
 └── rendering
```

## Good

```text
page.tsx
    ↓
service layer
    ↓
API layer
    ↓
backend
```

Pages should focus on composition.

---

# Performance Review Checklist

Flag:

* Unnecessary useEffect
* Unnecessary useState
* Unnecessary use client
* Waterfall requests
* Missing Suspense
* Large bundles
* Duplicate fetches
* Client-side fetching of server data
* Excessive context providers
* Heavy client libraries

---

# SEO Checklist

Verify:

* metadata export exists
* title exists
* description exists
* canonical URL exists when needed
* Open Graph metadata exists when needed

Avoid:

```typescript
next/head
```

in App Router.

---

# Detection Checklist

Review code for:

* useEffect used for data fetching
* useEffect used for browser detection
* useState storing server data
* Pages Router APIs
* next/head usage
* Waterfall requests
* Excessive use client
* Missing Suspense
* Client components importing server components incorrectly
* API routes used unnecessarily
* window.location navigation
* Missing metadata

---

# Success Criteria

A Next.js implementation is correct when:

* Server Components are the default
* Client Components are minimal
* Data is fetched on the server
* Server Actions handle mutations
* Caching is explicit
* Suspense is used intentionally
* Bundle size is minimized
* No unnecessary useEffect exists
* No unnecessary useState exists
* No Pages Router patterns exist
* The application remains performant, maintainable, and SEO-friendly
