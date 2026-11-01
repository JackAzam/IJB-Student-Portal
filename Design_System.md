# IJB Student Portal --- Design System

**Version:** 1.0\
**Date:** 1 November 2026\
**Primary language:** Indonesian\
**Supported layouts:** Desktop, tablet, mobile

## 1. Design direction

The portal is an operational work tool for an LPK. The visual system
should feel clear, dependable, calm, and administrative rather than
promotional. Staff need to identify urgent work quickly; students need
to understand their next action without being overwhelmed.

Design principles: 1. **Clarity before decoration:** show status, owner,
due date, and next action. 2. **One source of truth:** use consistent
labels and status colors throughout the app. 3. **Progressive
disclosure:** show essential information first and detailed history on
demand. 4. **Student-safe by default:** students see only their own data
and only documents published to them. 5. **Actionable urgency:** urgent
items must include a deadline and a responsible person. 6. **Responsive
by design:** staff tables should become readable cards or horizontally
scrollable tables on small screens. 7. **Accessible:** never communicate
status by color alone.

## 2. Brand and visual foundations

The following is a proposed starting palette. It can be adjusted to
match the official LPK identity.

  Token           Suggested value   Use
  --------------- ----------------- -------------------------------------------
  Primary         `#173B57`         Main navigation, primary actions
  Primary hover   `#102C42`         Hover/active primary controls
  Secondary       `#2D7180`         Secondary actions and supporting emphasis
  Accent          `#E4A64A`         Highlights and selected items
  Background      `#F4F6F8`         Main application background
  Surface         `#FFFFFF`         Cards, dialogs, panels
  Text            `#1D2935`         Main text
  Muted text      `#637381`         Help text, metadata
  Border          `#DCE3E8`         Dividers and control borders
  Success         `#237A52`         Passed, accepted, completed
  Warning         `#A96712`         Due soon, attention required
  Danger          `#B23A3A`         Overdue, rejected, blocked
  Info            `#286A9B`         Informational status

Use neutral surfaces for most content. Use semantic colors only for
status or important actions. Maintain sufficient contrast for text and
controls.

## 3. Typography

Recommended font stack: - Primary: Inter, if locally available. -
Fallback: system sans-serif (`Arial`, `Segoe UI`, sans-serif). -
Japanese document names: a system font with Japanese glyph support.

Type scale: - Page title: 24--28 px, semibold. - Section title: 18--20
px, semibold. - Card title: 15--16 px, semibold. - Body: 14--16 px. -
Labels and metadata: 12--13 px. - Table content: 13--14 px.

Use sentence case. Avoid long all-caps labels. Preserve official
Japanese form names exactly where necessary.

## 4. Layout and spacing

-   Desktop sidebar: approximately 240--260 px.
-   Header: approximately 60--68 px.
-   Main content max width: 1440 px for dense operational pages.
-   Page padding: 24 px desktop, 16 px tablet, 12--16 px mobile.
-   Spacing scale: 4, 8, 12, 16, 24, 32, 40 px.
-   Card radius: 8--12 px.
-   Input/control height: 40--44 px.
-   Use a 12-column desktop grid where helpful; collapse to one column
    on mobile.

Avoid dashboards that place too many unrelated charts above the actual
work queue. The first screen should answer: what needs attention, what
is next, and what is overdue?

## 5. Navigation structure

### Staff navigation

-   Dashboard
-   Students
    -   All students
    -   New registrations
    -   My assigned students
-   Opportunities
    -   Training Orders
    -   Job Orders
    -   Job types / sectors
-   Exams
    -   Exam schedule
    -   Reservations and issues
    -   Results and retakes
-   Medical checkups
-   Interviews & offers
-   Passport processing
-   Documents
    -   Document checklist
    -   Urgent / overdue
    -   Templates
-   Support tickets
-   Calendar & timeline
-   TSK/KUMIAI visits
-   Placement communication
-   Reports
-   Administration (permission-controlled)

### Student navigation

-   My dashboard
-   My profile
-   My program & opportunity
-   My exams
-   My medical checkup
-   My interviews & offers
-   My passport schedule
-   My documents
-   Support tickets
-   My calendar / timeline
-   Account settings

Hide staff-only navigation entirely from student accounts.

## 6. Core page patterns

### 6.1 Dashboard

**Staff dashboard** - Top summary: active students, exams upcoming,
interviews upcoming, urgent documents, overdue tasks. - Main work queue:
urgent/overdue tasks with due date, student, task type, owner, and
direct action. - Upcoming timeline: next 7 days by default. - Quick
actions: add student, create order, schedule interview, record exam,
create document request. - Filters: team, assigned staff, program, date
range.

**Student dashboard** - Welcome and current program status. - Next
required action. - Upcoming schedule. - Exam requirements and result
status. - Interview invitations and offer selection, if applicable. -
Missing documents published as action items. - Open ticket updates.

### 6.2 Student profile

Use tabs or grouped sections: - Overview - Personal information -
Program & order - Exams - Medical - Interviews & offers - Passport -
Documents - Tickets - Timeline / audit history (staff only as
appropriate)

Display a compact case summary at the top: program, selected order,
current stage, assigned staff, next deadline.

### 6.3 Status badges

Use consistent semantic mapping: - Green: Passed, Accepted, Completed,
Issued. - Amber: Pending, Due soon, Waiting, Needs attention. - Red:
Failed, Rejected, Overdue, Blocked. - Blue: Scheduled, In progress,
Information. - Gray: Draft, Not started, Cancelled, Not required.

Always include text labels and, where useful, an icon. Do not rely on
color alone.

### 6.4 Tables and lists

Staff tables should support: - Search. - Filters. - Sort by due
date/status/name. - Pagination. - Column visibility where useful. - Row
action menu with permission checks.

On mobile, prioritize student/name, status, due date, and next action.
Convert rows to cards or allow deliberate horizontal scrolling.

### 6.5 Forms

-   Group related fields into sections.
-   Mark required fields clearly.
-   Explain why a field is needed.
-   Validate on the server and show errors next to the relevant field.
-   Use date/time pickers with timezone labels.
-   Use searchable dropdowns for TSK/KUMIAI, receiver company, job type,
    and order.
-   Confirm destructive or irreversible actions.
-   Save drafts for long forms where feasible.

### 6.6 Timelines and calendars

-   Calendar views: month, week, agenda/list.
-   Timeline views: chronological event feed grouped by date.
-   Event colors represent event category, with a visible category
    label.
-   Each event displays title, date/time, location, owner, linked
    student/order, and status.
-   Support reminders and event ownership.
-   Distinguish portal events from Google Calendar sync status.

## 7. Document-management UI

Document list columns: - Document name - Form/reference - Student -
Program/order - Status - Responsible staff - Due date - Urgency - Latest
version - Visibility (staff-only / published to student) - Actions

Document detail should show: - Required/optional status. - Upload
history and versions. - Review notes. - Due date and responsible
staff. - Download/print action if authorized. - Publish/unpublish action
if authorized.

For Form 1-14, show two separate required slots: - Employment contract
--- unsigned copy. - Employment contract --- signed copy.

Urgency treatment: - Overdue: danger status and overdue duration. - Due
today: high attention. - Due soon: warning. - No deadline: neutral.
Urgency must be based on due dates and workflow priority, not manually
applied color alone.

## 8. Interview and offer UI

-   Interview history must be chronological and never collapse different
    offers into one record.
-   Offer comparison should show program, order, job type, TSK/KUMIAI,
    receiver company, mendan, location, interview date, and result.
-   Clearly distinguish **passed interview** from **selected offer**.
-   Student selection should require an explicit confirmation.
-   After selection, other offers remain visible with their updated
    state.

## 9. Passport workflow UI

Show a program-specific stepper: - Internship: interview passed → offer
selected → supporting information → WIWITAN BARU SUKABUMI recommendation
request → immigration appointment → passport processing → passport
received. - Tokutei Ginou: interview passed → offer selected → LPK
passport preparation → immigration appointment → passport processing →
passport received.

A stepper is a visual summary only; the underlying events and documents
remain separately auditable.

## 10. Components

Reusable components: - Application shell (sidebar, header, user menu). -
Breadcrumbs. - Page header and action toolbar. - Summary metric card. -
Status badge. - Priority/urgency indicator. - Searchable filter bar. -
Data table and responsive record card. - Student identity summary. -
Program/order summary. - Exam requirement card. - Exam attempt
history. - Interview event card. - Offer comparison panel. - Document
checklist item. - File upload dropzone with file rules. - Version
history list. - Ticket conversation panel. - Calendar event card. -
Timeline item. - Confirmation dialog. - Empty state and error state. -
Permission-denied state.

## 11. Interaction rules

-   Every primary action must have a clear label: "Simpan", "Jadwalkan",
    "Kirim permintaan", "Verifikasi", etc.
-   After a successful save, show a concise confirmation and the
    resulting status.
-   If a file upload fails, preserve form data and explain how to retry.
-   Warn before leaving a form with unsaved changes.
-   Do not show actions that the current user cannot perform.
-   Show the reason when a workflow is blocked, such as a missing exam
    result or required document.
-   Use confirmation for offer selection, document rejection, account
    suspension, and other consequential actions.

## 12. Accessibility and responsive requirements

-   All form controls must have programmatic labels.
-   All interactive controls must be keyboard accessible.
-   Focus indicators must be visible.
-   Status must include text, not color only.
-   Tables must have meaningful headers.
-   Images and uploaded scans need appropriate labels.
-   Avoid tiny tap targets; aim for 40--44 px controls.
-   Support tablet portrait and landscape.
-   Ensure the student portal remains usable on a narrow mobile screen.

## 13. Content and language conventions

-   Indonesian is the default UI language.
-   Use consistent terms: "Siswa/Peserta", "Staf", "Program", "Training
    Order", "Job Order", "TSK/KUMIAI", "Perusahaan Penerima", "Mendan",
    "Ujian", "Pemeriksaan Kesehatan", "Paspor", "Dokumen".
-   Keep official Japanese document names and form references unchanged.
-   Dates should display in an unambiguous format, e.g. `10 Okt 2026`;
    store dates in ISO-compatible database fields.
-   Display timezone consistently, preferably `Asia/Jakarta` for LPK
    operations, while allowing event location timezone to be recorded
    when needed.

## 14. Design acceptance checklist

-   Staff can identify urgent and overdue tasks quickly.
-   Students can identify their next action from the dashboard.
-   Staff-only navigation and data are hidden from students.
-   The same status uses the same label and semantic color everywhere.
-   Multiple interviews and offers are visually distinct.
-   Internship and Tokutei Ginou passport paths are distinguishable.
-   Form 1-14 unsigned and signed copies are separate.
-   Document download/print and publish actions are
    permission-controlled.
-   Core pages work on desktop, tablet, and mobile.
