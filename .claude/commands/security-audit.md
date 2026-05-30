Run a security audit on the current changes using the `security-auditor` subagent.

1. Identify the files changed in the last commit.

2. Use the `security-auditor` subagent on those files. Ask it to check for: authentication gaps, authorization flaws, secrets exposure, injection vectors (SQL, command, XSS, SSRF), unsafe data handling, insecure session/cookie/token patterns, and misconfigured CORS or deployment settings.

3. Report findings grouped by: MUST FIX, SHOULD FIX, CONSIDER.

4. End with an APPROVAL STATUS: APPROVED, APPROVED WITH MINOR ISSUES, or CHANGES REQUESTED, with a rationale.
