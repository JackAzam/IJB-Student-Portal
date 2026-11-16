# IJB Student Portal --- Technical Architecture

**Version:** 1.0\
**Date:** 1 November 2026\
**Implementation language:** Python\
**Framework baseline:** Django\
**Deployment target:** Local LPK PC initially; tablet considered as
temporary host

## 1. Architecture goals

-   Keep the system affordable and maintainable.
-   Use a modular Django monolith rather than microservices.
-   Keep business rules in tested service/domain functions, not
    scattered through templates.
-   Treat the portal database as the source of truth for operational
    records.
-   Store large files in Google Drive or controlled local storage, while
    storing metadata and access rules in Django.
-   Make external integrations optional and resilient.
-   Preserve history and auditability for important workflow changes.
-   Support local development and a working-hours pilot without
    pretending the service is always online.

## 2. Known project baseline and assumptions

The existing project context indicates: - Django project entrypoint:
`manage.py`. - Settings module: `config.settings.dev`. - Settings are
split under `config/settings/`, with a shared base settings module. -
Environment variables are loaded from `.env` using `django-environ`. -
Existing apps include Django built-ins, two-factor authentication
packages, `axes`, and project apps. - Existing project apps include
`accounts`, `exams`, and `masterdata`. - Initial migrations have been
created for `accounts`, `exams`, and `masterdata`; migration execution
should be checked before adding more models. - `seed_defaults` already
creates initial exam rules and job types such as Doboku, Kenchiku, and
Lifeline. - `python manage.py check` previously reported no system-check
issues.

This document proposes an architecture that should extend the existing
project instead of replacing it. Confirm the current repository before
moving or renaming apps.

## 3. High-level system context

``` mermaid
flowchart TD
    Student[Student browser / tablet / phone]
    Staff[Staff browser / PC / tablet]
    Tunnel[HTTPS tunnel / stable public URL]
    Django[Django application]
    DB[(Relational database)]
    Drive[Google Drive API]
    Calendar[Google Calendar API]
    Line[LINE staff reminder channel]
    Mail[Email / account recovery provider]

    Student --> Tunnel
    Staff --> Tunnel
    Tunnel --> Django
    Django --> DB
    Django <--> Drive
    Django <--> Calendar
    Django --> Line
    Django --> Mail
```

The tunnel is a network entry point, not a hosting platform. The
PC/tablet still runs Django and must remain powered and connected for
the service to be available.

## 4. Recommended application structure

Keep a modular monolith with Django apps grouped by business capability.
Proposed structure (adapt to the current repository):

``` text
project-root/
├── manage.py
├── config/
│   ├── settings/
│   │   ├── base.py
│   │   ├── dev.py
│   │   └── production.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── apps/
│   ├── accounts/
│   ├── students/
│   ├── masterdata/
│   ├── orders/
│   ├── programs/
│   ├── exams/
│   ├── medical/
│   ├── interviews/
│   ├── passports/
│   ├── documents/
│   ├── tickets/
│   ├── scheduling/
│   ├── visits/
│   ├── communications/
│   ├── integrations/
│   └── auditlog/
├── templates/
├── static/
├── media/                 # development/local storage only; protect from public serving
├── requirements/
├── .env.example
└── docs/
```

Do not create all apps at once. Implement incrementally, and keep
existing `accounts`, `exams`, and `masterdata` apps if they already
contain useful migrations/data.

### App responsibilities

  -----------------------------------------------------------------------
  App                                 Responsibility
  ----------------------------------- -----------------------------------
  accounts                            Custom user, authentication,
                                      staff/student account type,
                                      permission groups

  students                            Candidate profile, origin,
                                      enrollment, case overview

  masterdata                          Job types, sectors, TSK/KUMIAI,
                                      receiver companies, contacts,
                                      locations

  orders                              Training Orders, Job Orders,
                                      openings, order requirements

  programs                            Program pathway and student program
                                      enrollment

  exams                               Exam rules, requirements,
                                      reservations, attempts, results,
                                      retakes

  medical                             Medical appointments, results,
                                      validity

  interviews                          Interview events, invitations,
                                      attendance, outcomes, offers and
                                      selection

  passports                           Program-specific passport workflow
                                      and recommendation-letter requests

  documents                           Document catalogue, checklist
                                      instances, uploads, versions,
                                      review, publishing

  tickets                             Student support requests and
                                      conversations

  scheduling                          Portal calendar events, reminders,
                                      timeline

  visits                              TSK/KUMIAI PIC visits and
                                      follow-ups

  communications                      Placement communication log and
                                      LINE reminder jobs

  integrations                        Google Drive, Google Calendar,
                                      LINE, email adapters

  auditlog                            Critical change history and
                                      access/security events
  -----------------------------------------------------------------------

## 5. Data architecture

Use a relational database. SQLite may be acceptable for early
single-user development, but a multi-user pilot should move to
PostgreSQL if the host can support it. Avoid placing a live SQLite
database on a network share or allowing multiple devices to write to an
unreliable synced folder.

### 5.1 Core entities

-   `User`: authentication identity, account type, active status.
-   `StaffProfile`: staff-specific information and team.
-   `StudentProfile`: candidate identity, origin, contact and consent
    metadata.
-   `StudentProgram`: student, program type, lifecycle status, assigned
    staff, dates.
-   `TSKKumiai`: organization record.
-   `ReceiverCompany`: Japanese receiving company.
-   `CompanyContact`: email, PIC, phone, role.
-   `JobType`: configurable job type/category.
-   `Sector`: configurable business sector.
-   `Order`: Training Order or Job Order, reference, organization,
    company, location, status.
-   `OrderRequirement`: exam, skill category, document, or other
    requirement attached to an order.
-   `StudentOrderAssignment`: student's association with an order and
    program.
-   `ExamRule`: exam type/provider/category, retake interval, effective
    dates, active state.
-   `ExamRequirement`: requirement attached to a program/order.
-   `ExamBooking`: reservation, date, venue, booking status, reported
    issue.
-   `ExamAttempt`: attempt number, date, result, score/grade, evidence.
-   `MedicalAppointment`: appointment date, facility, status.
-   `MedicalResult`: uploaded evidence, review, validity.
-   `InterviewEvent`: scheduled event, order, company, mendan,
    date/time, mode/location.
-   `InterviewInvitation`: student invited to event and selected
    date/response.
-   `InterviewOutcome`: outcome and notes for a student's interview.
-   `Offer`: passed interview/placement offer details.
-   `OfferSelection`: student's selected offer and selection timestamp.
-   `PassportCase`: program-specific passport workflow and current
    status.
-   `RecommendationLetterRequest`: WIWITAN BARU SUKABUMI request,
    supporting data, deadlines, received file.
-   `DocumentTemplate`: catalogue/template and applicability rules.
-   `StudentDocument`: per-student required document instance.
-   `DocumentVersion`: file metadata, version, uploader, checksum,
    review state.
-   `SupportTicket`: student request, category, priority, assignment,
    status.
-   `TicketMessage`: conversation and attachments.
-   `CalendarEvent`: portal-owned event and participants.
-   `ExternalCalendarLink`: Google Calendar event ID and sync state.
-   `PICVisit`: TSK/KUMIAI visit and follow-up actions.
-   `PlacementCommunication`: recipient group, sender, timestamp,
    summary, confirmation.
-   `AuditEvent`: actor, timestamp, entity, action, before/after
    snapshot or safe diff.

### 5.2 Important relationship rules

-   One student can have multiple `StudentProgram` records over time.
-   One student can have multiple order assignments, interviews,
    outcomes, and offers.
-   One interview event can invite multiple students; each student's
    outcome is separate.
-   One student can pass multiple interviews and have multiple offers.
-   Exactly one active selected offer should normally exist per
    placement decision; retain historical selections if the student
    changes their decision, with reason and audit trail.
-   Exam attempts are append-only history. A failed attempt must not be
    overwritten by a later pass.
-   Document uploads are versioned. Replacing a file creates a new
    version; it does not erase the old version.
-   Document requirements are generated from templates plus
    program/order applicability rules.
-   Form 1-14 has separate document slots for unsigned and signed
    copies.
-   A student's Matching Job activity must reference its underlying
    Internship or Tokutei Ginou program.
-   Passport workflow is selected from the underlying program, not
    merely the label "Matching Job".

## 6. Business-rule architecture

Implement business rules in explicit service modules, for example: -
`apps/exams/services/requirements.py` -
`apps/exams/services/retake.py` -
`apps/interviews/services/offer_selection.py` -
`apps/passports/services/workflow.py` -
`apps/documents/services/checklist.py` -
`apps/scheduling/services/calendar_sync.py`

### 6.1 Exam eligibility

Represent rules as data: - Program: Internship or Tokutei Ginou. -
Language requirement: JFT A2 OR JLPT N4 (configurable). - Tokutei Ginou
skill requirement: SSW category selected from the assigned order. -
Matching Job: inherit the underlying program and order rules.

Do not hard-code only Doboku/Kenchiku/Lifeline. Store the SSW category
on the order requirement so other categories can be added without code
changes.

### 6.2 Retake calculation

-   Store retake interval/rule by exam provider/type/category and
    effective date.
-   On failed result, calculate `earliest_retake_date` from the relevant
    configured rule.
-   Display the source rule and calculation date.
-   Allow authorized override only with reason and audit record.
-   If the rule is unknown or expired, mark "manual confirmation
    required"; do not invent a date.
-   Confirm official rules before enabling automated calculations in
    production.

### 6.3 Interview and offer history

Keep separate records for: 1. Interview event. 2. Student
invitation/booking. 3. Interview outcome. 4. Offer. 5. Offer selection.

Never use a single mutable field such as `student.company` as the only
record of placement history.

### 6.4 Passport workflow

Use program-specific workflow configuration: - Internship:
recommendation-letter coordination with WIWITAN BARU SUKABUMI, then
passport issuance tracking. - Tokutei Ginou: LPK-managed passport
issuance tracking. The portal records operational steps; staff must
verify external requirements and official document versions.

### 6.5 Document checklist

Templates define: - Document type and official reference. -
Program/order applicability. - Required/optional condition. - Whether
student or staff uploads. - Whether signed/unsigned variants are
required. - Review requirement. - Default due-date calculation, if
known.

Each student document instance tracks status, owner, due date, urgency,
visibility, and versions.

## 7. Authentication and authorization

Use Django's custom user model from the beginning of the project. If the
existing custom `accounts.User` model is already migrated, preserve it
and avoid changing `AUTH_USER_MODEL` after production data exists.

Recommended roles: - Student - Staff Basic - Staff Operations - Staff
Document - Staff Supervisor - Management - Superuser

Use Django Groups and permissions, plus object-level checks for
student-owned records. Do not rely only on hiding menu links.

Registration: - Student signup creates an active student account
immediately. - Staff signup creates an active baseline staff account
immediately. - Protect staff signup with an LPK-controlled registration
code or controlled enrollment mechanism. - Staff cannot assign
themselves elevated groups. - Superuser permissions are assigned only by
an existing authorized administrator. - Record signup, login failures,
password reset, permission changes, and account suspension.

Sensitive data: - Passport scans, medical results, and identity
documents require restricted access. - Do not expose private files
through guessable media URLs. - Check authorization on every
download/preview request. - Use short-lived signed URLs or a controlled
download proxy for Drive files. - Do not log passwords, access tokens,
full medical data, or unnecessary identity details.

## 8. File storage architecture

### Recommended approach

-   Database stores document metadata and Google Drive file ID.
-   Google Drive stores file bytes for the integrated deployment.
-   During development, local private storage may be used behind
    authenticated views.
-   Use a storage adapter so the application can switch between local
    storage and Google Drive without changing business logic.

Document metadata should include: - Student/document instance. -
Document type and version. - Original filename and safe stored
filename. - MIME type and size. - SHA-256 checksum. - Uploader and
upload time. - Review status and reviewer. - Visibility (staff-only or
published to student). - Storage backend and Drive file ID. -
Retention/deletion policy metadata.

Never assume that a Google Drive folder is private simply because its
URL is difficult to guess. Configure explicit permissions and test
access using a non-staff account.

## 9. Google Calendar integration

The portal database remains the source of truth for schedules. Google
Calendar is a synchronized view.

Recommended design: - Staff configures a Google OAuth connection or
service account according to Google Workspace/account capabilities. -
Store OAuth refresh tokens encrypted and outside source control. - Each
syncable portal event stores external calendar ID and Google event ID. -
Use idempotent create/update logic to avoid duplicates. - Track
`sync_status`, `last_synced_at`, and `last_sync_error`. - Retry
transient failures through a background task or a staff-triggered
retry. - Do not delete portal events merely because an external calendar
event is removed. - Define whether students receive individual calendar
events or whether only staff calendars are synchronized.

## 10. LINE staff reminders

No chatbot is required. The initial use case is staff reminders.

Architecture: - A scheduled reminder task identifies events/tasks due
soon or overdue. - A LINE integration adapter sends only configured
staff reminders. - Store channel access token in environment/secret
storage, never in Git. - Log message delivery status without storing
unnecessary personal information. - Do not assume the bot can post to
arbitrary LINE groups; verify the current LINE Messaging API group
permissions and bot membership requirements before implementation. -
Provide in-app reminders as the fallback if LINE is unavailable.

## 11. Hosting and network architecture

### 11.1 Development

-   Run locally on the development PC.
-   Use `.env` for secrets and environment-specific values.
-   Use Django `runserver` only for local development.
-   Keep `DEBUG=True` only on localhost.
-   Use test data, not real passport or medical documents.

### 11.2 Working-hours pilot on LPK hardware

-   Use a production-capable WSGI server (e.g. Gunicorn on Linux or an
    appropriate Windows deployment server) behind a reverse proxy where
    supported.
-   Set `DEBUG=False`.
-   Configure `ALLOWED_HOSTS`, trusted HTTPS origins, secure cookies,
    CSRF settings, and a stable `PORTAL_HOSTNAME`.
-   Use a trusted HTTPS tunnel for inbound access if the LPK network has
    no public IP.
-   Restrict tunnel routes to the web application only.
-   Do not expose database ports, remote desktop, SSH, or Django debug
    tools through the tunnel.
-   Keep host PC/tablet physically secured and powered during operating
    hours.
-   Configure scheduled database and file backups to a separate storage
    location.
-   Display planned operating hours and an unavailable notice when the
    server is offline, where feasible.

### 11.3 Tablet as temporary server

Treat tablet hosting as an experiment, not an assumed capability. Before
adopting it, verify: - Operating system supports the required Python
version and Django dependencies. - The process can run persistently
while the screen is off. - Device does not terminate the server under
battery or memory pressure. - Local storage is reliable and has
sufficient capacity. - It can be kept powered and cooled. - It can run
backup and recovery tasks. - Network and tunnel client remain connected.

If these requirements cannot be met, use the PC as the host and the
tablet as a client/admin device.

### 11.4 Availability and risk

A tunnel provides reachability, not uptime. If the PC/tablet is shut
down, asleep, disconnected, or the tunnel fails, external users cannot
reach the portal. Important student instructions must make this
limitation clear. Do not promise 24/7 access on a working-hours host.

## 12. Environment configuration

Maintain `.env.example` with placeholders only. Based on the existing
project baseline, retain and review settings such as: - `SECRET_KEY` -
`DEBUG` - `PORTAL_HOSTNAME` - `ALLOWED_HOSTS` - `ADMIN_URL` -
`TEAM_SIGNUP_ENABLED` - `IDLE_TIMEOUT_TEAM` - `IDLE_TIMEOUT_STUDENT` -
`SECURE_HSTS_SECONDS`

Add integration settings only when implementing each integration, for
example: - Google OAuth client ID/secret and redirect URI. - Google
Drive root folder ID. - Google Calendar target calendar ID. - LINE
channel access token and target staff destination. - Email provider
credentials.

Never commit `.env`, service-account JSON, OAuth refresh tokens, or real
student files. Ensure `DEBUG=False` in any publicly reachable
environment.

## 13. Background jobs and scheduling

For the first release, keep background processing simple: - Django
management commands or a lightweight scheduler can process reminders and
integration sync jobs. - Use a persistent job/outbox table for retryable
external actions. - Ensure jobs are idempotent. - Record success,
failure, retry count, and next retry time. - Do not rely on an in-memory
timer that disappears when the server restarts. - A later phase may
adopt Celery + Redis if the deployment environment can support and
maintain them.

## 14. API and frontend approach

For a first implementation, Django templates with progressive
enhancement are sufficient and reduce operational complexity. A separate
SPA is not required unless the UI needs justify the added
build/deployment work.

If APIs are needed: - Use Django REST Framework only where there is a
concrete need. - Version external API routes, e.g. `/api/v1/`. - Apply
authentication, permissions, validation, pagination, and throttling. -
Never trust a student ID supplied by the browser; derive permitted
ownership from the authenticated user and verify object access
server-side.

## 15. Security baseline

-   HTTPS for any access beyond localhost.
-   `DEBUG=False` for public/tunnel access.
-   Strong unique `SECRET_KEY`.
-   Secure session and CSRF cookies.
-   CSRF protection on state-changing requests.
-   Rate limiting / login attack protection (the project already
    includes `axes`; verify configuration).
-   Password reset and email verification policy.
-   Staff enrollment protection.
-   Least-privilege role permissions.
-   Object-level authorization for student records.
-   Private file storage and authorized downloads.
-   Upload size/type limits and safe filename handling.
-   Malware scanning where feasible before handling files operationally.
-   Audit logging for status, permission, offer selection, document, and
    passport changes.
-   Dependency updates and security checks.
-   Backup encryption and restore testing.
-   No real sensitive data in development fixtures or screenshots.

## 16. Testing strategy

-   Unit tests for exam eligibility and retake calculations.
-   Unit tests for Internship vs Tokutei Ginou passport workflow
    selection.
-   Tests proving interview/offer history is retained.
-   Permission tests proving students cannot access another student's
    data.
-   Tests for staff self-registration baseline permissions.
-   Tests for document versioning and Form 1-14 copy separation.
-   Tests for due-date and urgency calculations.
-   Integration tests with mocked Google Drive/Calendar/LINE APIs.
-   Backup and restore rehearsal.
-   Manual responsive tests on desktop, tablet, and mobile.

## 17. Migration and implementation sequence

1.  Inspect current repository and migration state; back up the
    database.
2.  Confirm the custom `accounts.User` migration is applied and that
    `AUTH_USER_MODEL` is configured correctly.
3.  Stabilize account roles and registration.
4.  Complete master data and TO/JO models.
5.  Build student program assignment and requirement rules.
6.  Build exam bookings, attempts, results, and retake rules.
7.  Build interview event, invitation, outcome, offer, and selection
    models.
8.  Build medical and passport tracking.
9.  Build document templates, checklist instances, versions, and
    permissions.
10. Build student tickets and calendar/timeline.
11. Add PIC visits and placement communication records.
12. Add Google Drive and Calendar integrations.
13. Add staff LINE reminders.
14. Test backups, security, and pilot operations.

Do not run `makemigrations` or `migrate` blindly on a database with
important records. Inspect migration plans, back up first, and resolve
migration errors before continuing.

## 18. Operational runbook

Staff/administrator should have documented steps for: - Starting and
stopping the application. - Checking server and tunnel status. -
Confirming working-hours availability. - Backing up database and
documents. - Restoring from backup. - Rotating secrets and integration
credentials. - Handling failed Google sync or LINE reminders. -
Disabling a compromised account. - Responding to accidental document
publication. - Updating dependencies and applying migrations.

## 19. Architecture decisions and trade-offs

  -----------------------------------------------------------------------
  Decision                Choice                  Reason
  ----------------------- ----------------------- -----------------------
  Application style       Django modular monolith Lower operational
                                                  complexity and cost

  Source of truth         Django database         Avoid calendar/Drive
                                                  becoming the workflow
                                                  database

  File storage            Drive adapter + private Supports integration
                          local dev storage       without coupling domain
                                                  logic

  Calendar                Portal events first,    Avoid loss/duplication
                          Google sync second      from external sync

  Reminders               In-app first, LINE      Works even without LINE
                          staff reminders later   integration

  Hosting                 Local PC pilot + HTTPS  Avoid paid VPS
                          tunnel                  initially; accept
                                                  limited uptime

  Tablet host             Conditional experiment  Device/background
                                                  constraints vary

  Frontend                Django templates        Less complexity for a
                          initially               small team

  Background jobs         Persistent outbox/light Avoid requiring
                          scheduler initially     Redis/Celery at the
                                                  start
  -----------------------------------------------------------------------

## 20. Decisions requiring confirmation

-   Current database engine and whether it contains production data.
-   Current Django version and exact app tree.
-   Whether the PC host runs Windows or Linux.
-   Whether tablet hosting is Android, iPadOS, or Windows.
-   Google account type and Drive/Calendar sharing model.
-   Official exam retake intervals.
-   Exact Kemenaker and WIWITAN BARU SUKABUMI process details.
-   Staff registration enrollment mechanism.
-   Backup destination and retention period.
