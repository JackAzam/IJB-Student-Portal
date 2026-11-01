# IJB Student Portal --- Agent and Developer Instructions

**Version:** 1.0\
**Date:** 1 November 2026

This document defines how AI coding agents and human developers should
work on the IJB Student Portal repository. It is optional for the
application runtime but recommended for consistent development.

## 1. Mission

Build and maintain a secure, auditable, low-cost Django portal that
supports the real operational workflow of the LPK. Optimize for
correctness of student records, traceability, document safety, and
maintainability.

## 2. Read before changing code

Before implementing a feature: 1. Read `PRD.md`, `Design_System.md`, and
`Architecture.md`. 2. Inspect the current repository tree and existing
Django settings. 3. Inspect existing models, migrations, tests, and URL
patterns. 4. Check the current database and migration state before
proposing schema changes. 5. Reuse existing apps and patterns where
appropriate; do not recreate working modules without a reason. 6.
Identify whether the change affects student privacy, permissions,
document access, or historical records.

Do not assume that the documentation overrides the actual repository. If
the repository differs, explain the difference and propose a safe
migration plan.

## 3. Technical rules

-   Use Python and the existing Django project conventions.
-   Keep business logic in service/domain modules rather than putting
    complex rules in views or templates.
-   Use Django ORM and migrations for schema changes.
-   Use the configured custom user model; do not replace
    `AUTH_USER_MODEL` after migrations/data exist without a migration
    plan.
-   Prefer a modular monolith. Do not introduce microservices without an
    explicit requirement.
-   Keep external integrations behind adapters/services.
-   Use environment variables for secrets and deployment-specific
    settings.
-   Never commit `.env`, OAuth tokens, Google service-account keys, LINE
    secrets, or private student documents.
-   Do not use Django `runserver` as a public production server.
-   Do not set `DEBUG=True` on a public/tunnel-accessible deployment.
-   Do not add dependencies unless they solve a clear need; document why
    they are needed.
-   Add tests for business rules and permissions.

## 4. Business rules that must not be broken

### 4.1 Program requirements

-   The system has Internship, Tokutei Ginou, and Matching Job pathways.
-   Matching Job can be associated with Internship or Tokutei Ginou.
-   The underlying program and assigned TO/JO determine requirements.
-   Internship language requirement is either JFT A2 or JLPT N4
    according to configured LPK rules.
-   Tokutei Ginou requires the language requirement plus the SSW skill
    exam/category relevant to the assigned order.
-   Doboku, Kenchiku, and Lifeline are initial examples, not a complete
    fixed list.
-   Job types and SSW categories must be data-driven and extensible.

Never hard-code a single SSW category list into a view or assume every
job is civil engineering.

### 4.2 Exam history

-   Every exam booking and attempt must be retained.
-   A later pass must not overwrite a previous failure.
-   Retake dates must come from configurable, verified rules.
-   If a valid rule is unavailable, show that manual confirmation is
    required.
-   Never invent an official retake interval.
-   Result evidence must be private until reviewed and appropriately
    published.

### 4.3 Interviews and offers

-   A student can receive multiple interviews from different TSK/KUMIAI
    and receiver companies.
-   Store each interview, mendan, company, order, location, date, and
    outcome independently.
-   A student may pass more than one interview.
-   Selecting an offer must not delete or rewrite other interview
    history.
-   Distinguish interview result "Passed" from offer status "Selected".
-   Any change to a selected offer must be recorded with actor,
    timestamp, and reason.

### 4.4 Passport processing

-   Internship passport processing includes the recommendation-letter
    coordination with WIWITAN BARU SUKABUMI.
-   Tokutei Ginou passport processing is handled by the LPK workflow.
-   Do not apply the Internship recommendation-letter step to Tokutei
    Ginou by default.
-   Record appointments, deadlines, submitted information, received
    files, and status history.

### 4.5 Documents

-   Document requirements must be configurable by program/order/case.
-   Preserve official Japanese names and form references.
-   Form 1-14 must have distinct unsigned and signed copies.
-   Never overwrite document versions silently.
-   Never expose passport, medical, identity, or employment files
    through public URLs.
-   Student uploads go only to permitted slots.
-   Staff publication to the student portal must be explicit and
    auditable.
-   Printing/download actions require authorization.

### 4.6 Registration and permissions

-   Students can register and log in immediately.
-   Staff can register and log in immediately without waiting for
    superuser approval.
-   Staff self-registration must not grant superuser or sensitive
    elevated permissions.
-   Use a controlled staff enrollment mechanism, such as an LPK
    registration code, and grant baseline staff permissions.
-   Enforce permissions on the server, not only in the UI.
-   A student must never access another student's records by changing a
    URL or request parameter.

## 5. Data integrity and audit rules

-   Prefer append-only history for exam attempts, interview outcomes,
    document versions, and important status transitions.
-   Use database constraints for uniqueness and valid relationships
    where possible.
-   Use transactions for multi-record operations such as offer
    selection.
-   Make external integration jobs idempotent.
-   Record who changed critical fields and when.
-   Do not delete operational history to make a dashboard look cleaner.
-   Use soft deletion/archive for records that may be referenced by
    history.
-   Avoid storing duplicate personal data in unrelated tables.

## 6. Security and privacy

Treat the following as sensitive: - Passport scans and passport
numbers. - Medical-checkup results. - Personal identity and contact
information. - Exam results and candidate history. - Employment
contracts and placement documents. - OAuth tokens and integration
credentials.

Required behavior: - Apply least privilege. - Validate ownership and
role on every read/write/download endpoint. - Use CSRF protection and
secure session settings. - Validate uploaded file size, extension, MIME
type, and safe filename. - Do not trust MIME type supplied only by the
browser. - Avoid putting sensitive details in logs, notifications, URLs,
or error messages. - Use test fixtures with synthetic data. - Do not
copy real student files into development or AI prompts unless explicitly
authorized and necessary. - Never include secrets in generated code or
documentation examples.

## 7. UI and UX rules

-   Follow `Design_System.md`.
-   Indonesian is the default UI language.
-   Preserve official Japanese document names.
-   Make next action, owner, due date, and status clear.
-   Use text labels in addition to status colors.
-   Ensure mobile/tablet usability.
-   Do not show student-facing staff controls.
-   Provide clear validation and error messages.
-   Confirm consequential actions such as offer selection, document
    rejection, and account suspension.

## 8. Integration rules

### Google Drive

-   Use a storage adapter.
-   Store Drive file IDs and metadata, not public links as the
    access-control mechanism.
-   Set and verify explicit Drive permissions.
-   Check portal authorization before returning a file or download link.
-   Handle missing files, revoked permissions, quota/rate limits, and
    transient errors.

### Google Calendar

-   Portal database remains the event source of truth.
-   Store external event IDs and sync state.
-   Use idempotent sync to avoid duplicates.
-   Do not silently delete portal events if Google Calendar changes.
-   Record sync errors and allow retry.

### LINE

-   Initial requirement is staff reminders only.
-   Do not build a student chatbot unless scope is explicitly changed.
-   Do not assume arbitrary group messaging is available; verify LINE
    platform permissions and group membership.
-   Keep channel secrets outside source control.
-   Keep in-app reminders available as fallback.

### Tunnel and local hosting

-   A tunnel provides access, not uptime.
-   Do not expose debug pages, database ports, or admin infrastructure.
-   Use HTTPS and secure Django settings for public/tunnel access.
-   Clearly document that the local host must be powered on and
    connected.
-   Do not promise 24/7 availability when hosted on a working-hours
    PC/tablet.

## 9. Development workflow

For each task: 1. State the user story and acceptance criteria. 2.
Identify impacted apps/models/permissions. 3. Propose the smallest
coherent change. 4. Implement models/services/views/forms/templates as
needed. 5. Add or update migrations. 6. Add tests for normal, edge, and
permission-denied cases. 7. Run focused tests and
`python manage.py check`. 8. Inspect migration plan before applying
migrations to a database with important data. 9. Update documentation if
business behavior or configuration changes. 10. Summarize files changed,
tests run, migration impact, and any remaining risks.

Do not claim tests passed unless they were actually run.

## 10. Migration and database safety

-   Back up the database before risky migrations or data migrations.
-   Inspect `showmigrations` and `migrate --plan`.
-   Do not delete migration files to fix a migration problem.
-   Do not edit an applied migration in a shared/used database.
-   Prefer a new migration to correct schema.
-   For data migrations, make the operation reversible where practical.
-   Do not run destructive SQL or reset the database without explicit
    authorization.
-   If a migration fails, inspect the complete traceback and database
    state before suggesting the next command.

## 11. Testing requirements

At minimum, add tests for: - Student and staff immediate registration
behavior. - Staff baseline permission restrictions. - Student
object-level isolation. - Internship vs Tokutei Ginou exam
requirements. - Dynamic SSW category selection by order. - Retake
calculation with missing/expired rules. - Exam-attempt history
preservation. - Multiple interviews and offer selection. - Internship vs
Tokutei Ginou passport workflow. - Form 1-14 unsigned/signed document
separation. - Document versioning and student publication access. -
Calendar sync idempotency. - Permission checks for file download and
print.

## 12. Agent behavior

An AI agent must: - Ask for clarification only when a missing decision
blocks safe implementation. - Prefer configurable rules over assumptions
about official processes. - Clearly separate confirmed requirements from
recommendations and open questions. - Never fabricate official exam
rules, immigration requirements, Kemenaker procedures, or Japanese form
requirements. - Never invent credentials, IDs, URLs, API responses, or
integration success. - Avoid broad refactors unrelated to the requested
task. - Explain security implications when a request would expose
student data or grant broad access. - Provide commands appropriate to
the user's operating system and current project structure. - Avoid
overwriting user files without explaining the impact. - End
implementation work with a concise summary and next safe step.

## 13. Definition of done

A feature is complete only when: - It meets the acceptance criteria. -
Permissions are enforced server-side. - Validation and error states are
handled. - Relevant tests are added and run. - Migrations are
reviewed. - Sensitive data is protected. - Audit/history behavior is
correct. - Documentation and configuration examples are updated. - The
implementation does not break existing project structure or data.
