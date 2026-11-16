# IJB Student Portal --- Product Requirements Document (PRD)

**Document status:** Active development\
**Product:** IJB Student Portal\
**Organization:** LPK (Indonesian training and placement organization)\
**Primary users:** Students/candidates, LPK staff, management, system
administrator\
**Version:** 1.02 + implementation tracking revision\
**Original baseline date:** 1 November 2026\
**Last updated:** 12 November 2026

## 1. Product overview

IJB Student Portal is a web-based operational platform for managing
candidates who join the LPK, prepare for work in Japan, participate in
interviews, complete language and skills examinations, obtain passports,
prepare placement documents, and progress through internship or Tokutei
Ginou processes.

The portal is intended to replace fragmented spreadsheets, chat
histories, paper checklists, and individual staff reminders with one
auditable source of operational information.

The system must support: - New candidate registration, including
candidates from other LPKs and people who want to work in Japan. - Three
candidate pathways: Internship, Tokutei Ginou, and Matching Job. -
Training Orders (TO) and Job Orders (JO), including job type,
TSK/KUMIAI, receiver company, and destination. - Language and SSW exam
tracking, reservations, results, and retake eligibility. - Medical
checkup scheduling and result uploads. - Multiple interviews and offers
per student, with a complete history and a recorded final selection. -
Passport processing and recommendation-letter coordination. -
Placement-document preparation, review, urgency, deadlines, and
printing. - TSK/KUMIAI PIC visits. - Staff and student timelines,
reminders, and calendar integration. - Google Drive document storage and
Google Calendar synchronization. - LINE reminders for staff only; no
LINE chatbot is required.

## 2. Product goals

1.  Give staff a reliable view of each candidate's current status and
    next required action.
2.  Prevent missed exam, interview, medical, passport, and document
    deadlines.
3.  Preserve the full history of interviews, offers, exam attempts,
    document revisions, and status changes.
4.  Make it clear which requirements apply to Internship, Tokutei Ginou,
    and each specific job order.
5.  Let students manage their own schedules and upload required
    evidence.
6.  Let staff publish documents to a student's portal and retrieve
    print-ready copies.
7.  Work in a low-cost environment where the application is developed
    and initially hosted on an LPK-owned PC or tablet.
8.  Avoid dependence on paid VPS hosting during development.

## 3. Non-goals and boundaries

-   The portal does not decide immigration, Kemenaker, Japanese
    government, or exam-provider outcomes.
-   The portal does not replace official forms, official legal advice,
    or external government systems.
-   The portal does not automatically send messages to TSK/KUMIAI or
    receiver-company LINE groups in the initial release. It records
    communication readiness and provides staff reminders/checklists.
-   The portal does not guarantee that a local PC/tablet is continuously
    reachable from the internet.
-   The portal is not a public job marketplace. Staff manage the TO/JO
    catalogue and determine which opportunities can be offered.
-   The portal does not assume every job type is civil engineering. Job
    types and SSW categories must be configurable.

## 4. Users and permissions

### 4.1 Student / Candidate

A student can: - Register and log in immediately. - Complete and update
permitted personal/profile fields. - Select or request a program
pathway. - View assigned TO/JO opportunities and offer details. - View
their own exam requirements, exam reservations, results, and retake
dates. - Add personal schedule entries, such as passport appointments
and exam dates. - Request help with missing documents through a support
ticket. - Upload exam results, medical-checkup results, and other
requested files. - View interview invitations, select an available
interview date, and submit an offer preference. - View their own process
timeline, published documents, and document checklist. - See status
updates and reminders relevant to their account.

A student must never see another student's personal information, exam
results, interviews, or documents.

### 4.2 Staff

All STAFF accounts receive operational access to student workflows and
documents across the student population. Access is not restricted by
StudentStaffAssignment.

Staff can:

- View and maintain student operational profiles and workflow records.
- View student document checklists and applicable requirements.
- Upload documents on behalf of any student.
- Download permitted student documents and active blank templates.
- Update workflow progress and operational statuses.
- Review, approve, or reject submitted documents.
- Record follow-up dates and operational notes.
- Work in parallel with other staff on the same student's records.

Staff access does not grant permission to manage staff accounts,
elevate roles, change system security settings, or administer manager-only
configuration.

StudentStaffAssignment may be retained for responsibility tracking,
workload reporting, and historical records. It is not an access-control
restriction.

The system must record the authenticated staff member responsible for
each upload, review, approval, rejection, and other audited action.
Staff identity is available in internal activity and audit history but
need not be prominent on the ordinary student workflow board.

Internal staff notes and private operational activity must not be
exposed to students.
### 4.3 Management

Management permissions may include: - Cross-team dashboards and
reports. - Staff workload and deadline monitoring. - Approval of
designated internal business steps, where configured. - Audit history
and operational oversight. - Configuration of job types, document
templates, and workflow rules, if granted.

### 4.4 Superuser / System administrator

The superuser manages: - User roles and permission groups. - System
configuration and integration credentials. - Staff access elevation and
account suspension. - Audit/security settings, backups, and technical
maintenance.

**Registration rule:** Student and staff registration must not require a
superuser to approve the account before first login. A public staff
registration option should be protected by a configurable LPK
staff-registration code or equivalent enrollment control. Newly
registered staff receive only baseline permissions; superuser and
sensitive permissions are never self-granted.

## 5. Core business concepts

### 5.1 Program pathways

The system supports: - **Internship** - **Tokutei Ginou (Specified
Skilled Worker / SSW)** - **Matching Job**

Matching Job is an opportunity/selection pathway and may be associated
with an Internship or Tokutei Ginou placement. It is not a replacement
for the underlying program requirements. The selected TO/JO and
staff-assigned program determine the actual requirements.

### 5.2 Training Order and Job Order

A TO/JO opportunity should contain: - Order reference and type (Training
Order or Job Order). - Program eligibility (Internship, Tokutei Ginou,
or both where applicable). - TSK/KUMIAI. - Receiver company. -
Mendan/interview company or contact, where applicable. - Job type /
sector. - Work location (prefecture/city, e.g. Kumamoto or Nagano). -
Number of openings, if known. - Required language exam and SSW
category/skill exam. - Requirements, notes, active dates, and status.

Job types must be configurable. Initial examples include Doboku,
Kenchiku, and Lifeline, but the system must support
non-civil-engineering categories.

### 5.3 Student opportunity and offer

A student may receive multiple interview invitations and pass more than
one interview. Each invitation/offer is a separate historical record. A
student may compare offers and select one. Selecting an offer must not
delete or overwrite other interview outcomes.

## 6. Functional requirements

Priority legend: **P0** = essential for initial operational release;
**P1** = important next; **P2** = later enhancement.

### 6.1 Registration, authentication, and profiles

-   **FR-001 (P0):** Students can self-register and log in immediately.
-   **FR-002 (P0):** Staff can self-register and log in immediately
    without superuser approval.
-   **FR-003 (P0):** Registration supports account type selection with
    secure staff enrollment protection.
-   **FR-004 (P0):** Passwords are stored only as secure password hashes
    using Django authentication.
-   **FR-005 (P0):** Users can reset passwords through a verified
    recovery process.
-   **FR-006 (P0):** Staff can create or correct a candidate profile
    with an audit trail.
-   **FR-007 (P0):** Candidate records include origin (own LPK, other
    LPK, independent applicant), contact details, and consent/status
    fields.
-   **FR-008 (P1):** Support configurable profile fields and document
    expiry dates.

### 6.2 Program and order management

-   **FR-010 (P0):** Staff can create, edit, archive, and publish TO/JO
    opportunities.
-   **FR-011 (P0):** Staff can assign one or more eligible program
    pathways to an order.
-   **FR-012 (P0):** Staff can define job type, sector, TSK/KUMIAI,
    receiver company, location, and interview contact.
-   **FR-013 (P0):** Staff can assign a student to a program and an
    order.
-   **FR-014 (P0):** Matching Job can be associated with Internship or
    Tokutei Ginou.
-   **FR-015 (P1):** Students can express interest in opportunities that
    staff have made visible to them.
-   **FR-016 (P1):** Record order changes without losing previous
    student assignment history.

### 6.3 Exam requirements and exam tracking

The portal must use configurable requirement rules, not hard-coded
assumptions.

Initial business rules: - **Internship:** require either JFT A2 or JLPT
N4, according to the LPK's current rule. - **Tokutei Ginou:** require
either JFT A2 or JLPT N4, plus the relevant SSW skill exam/category for
the selected job order. - SSW categories initially include Doboku,
Kenchiku, and Lifeline where applicable; additional categories must be
configurable. - Matching Job inherits the requirements of its underlying
Internship or Tokutei Ginou program and selected order.

Requirements: - **FR-020 (P0):** Display each student's required exams
based on program and selected order. - **FR-021 (P0):** Track JFT, JLPT,
and SSW exam types/categories. - **FR-022 (P0):** Record exam provider,
reservation date, exam date, location, booking reference, and
reservation status. - **FR-023 (P0):** Track reservation problems,
cancellation, rescheduling, and staff follow-up. - **FR-024 (P0):**
Record attempt number, result, score/grade where available, result date,
and evidence upload. - **FR-025 (P0):** Calculate the earliest retake
date from configurable exam-specific rules after a failed attempt. -
**FR-026 (P0):** Show the calculated retake date and the rule used;
allow authorized staff to record an exception with reason. - **FR-027
(P0):** Students can upload exam result evidence for staff review. -
**FR-028 (P0):** Staff can verify, reject with reason, or request a
clearer/corrected upload. - **FR-029 (P1):** Report upcoming exam dates,
failed attempts, overdue follow-ups, and candidates blocked by missing
requirements.

The system must not assume a universal retake waiting period. Retake
intervals must be configurable by exam type/provider and verified
against current official rules by LPK staff.

### 6.4 Medical checkups

-   **FR-030 (P0):** Staff or students can add medical-checkup
    appointments, subject to review rules.
-   **FR-031 (P0):** Track appointment date, facility, status, and
    follow-up.
-   **FR-032 (P0):** Students can upload medical-checkup result
    documents.
-   **FR-033 (P0):** Staff can review the upload and mark it accepted,
    rejected, or requiring correction.
-   **FR-034 (P1):** Track validity/expiry dates where applicable and
    alert staff before expiry.

### 6.5 Interviews and offer selection

-   **FR-040 (P0):** Staff can create interview events with date, time,
    mode/location, order, TSK/KUMIAI, receiver company, mendan/contact,
    and participant list.
-   **FR-041 (P0):** Staff can propose interview schedules and publish
    available dates.
-   **FR-042 (P0):** Students can choose or request an interview date
    from staff-published options.
-   **FR-043 (P0):** Staff can record attendance and interview result
    (pending, passed, failed, rescheduled, cancelled, absent).
-   **FR-044 (P0):** A student can have multiple interviews, including
    different programs, TSK/KUMIAI, receiver companies, job types, and
    destinations.
-   **FR-045 (P0):** Store each interview and result as a separate
    immutable history record; corrections must be audited.
-   **FR-046 (P0):** A student can select a preferred offer after
    receiving one or more passed results.
-   **FR-047 (P0):** Record selected offer, selection date, and status
    of other offers (not selected, withdrawn, expired, or still open).
-   **FR-048 (P0):** Prevent an offer selection from deleting the
    student's other interview history.
-   **FR-049 (P1):** Show a chronological interview timeline and offer
    comparison.

Example: A candidate passes an Internship interview for a Lifeline role
in Kumamoto with TSK/KUMIAI A and receiver company A on 10 October 2026,
then passes a Tokutei Ginou interview for a similar role in Nagano with
TSK/KUMIAI B and receiver company B on 15 October 2026. The portal must
retain both records and record which offer the candidate chooses.

### 6.6 Passport processing

Passport workflow differs by program:

**Internship** - After a passed interview and selection, track passport
issuance. - Record immigration appointment date, location, status,
expected collection date, and actual issue/collection date. - Track
recommendation-letter request to **WIWITAN BARU SUKABUMI**. - Record
request date, required-by date, submitted supporting information,
received date, letter file, and status. - Recommendation-letter
supporting information includes: 1. Training Order 2. Form 1-23 3. Email
peserta 4. Receiver-company email address, person in charge name, and
phone number 5. Business sector - Show deadline and urgency until the
recommendation letter is received.

**Tokutei Ginou** - Passport issuance is handled by the LPK workflow,
not the WIWITAN BARU SUKABUMI recommendation-letter workflow. - Track
the responsible staff member, appointment, documents, status, and
issue/collection date.

Requirements: - **FR-050 (P0):** Apply the correct passport workflow
from the selected program. - **FR-051 (P0):** Track passport appointment
and issuance milestones. - **FR-052 (P0):** Track Internship
recommendation-letter requests to WIWITAN BARU SUKABUMI. - **FR-053
(P0):** Validate and checklist the five supporting information groups
before submitting the recommendation-letter request. - **FR-054 (P0):**
Track requested-by date, target receipt date, received date, and overdue
status. - **FR-055 (P0):** Upload and publish passport evidence only to
authorized users. - **FR-056 (P1):** Notify staff of approaching and
overdue passport milestones.

### 6.7 Placement document management

The portal must support the following document catalogue for Internship
and Tokutei Ginou processing, subject to staff confirming which
documents apply to each case:

  -------------------------------------------------------------------------------------------------
  Document                                          Reference / description Special handling
  ------------------------------------------------- ----------------------- -----------------------
  Passport                                          Passport copy           Sensitive personal data

  Photo                                             Candidate photo         Image file

  Checklist docs                                    Case checklist          Track completion

  技能実習生の履歴書                                CV, reference Form 1-3  Per candidate

  技能実習計画の認定に関する取次送出機関の誓約書    LPK undertaking,        Per case
                                                    reference Form 1-10     

  雇用契約書及び雇用条件書                          Employment contract,    Two copies: unsigned
                                                    Form 1-14               and signed

  技能実習の期間中の待遇関する重要事項説明書        Benefits/facilities     Per case
                                                    list, Form 1-19         

  技能実習生の申告書                                Candidate declaration,  Per candidate
                                                    Form 1-20               

  同種業務従事経験等説明書                          Work experience         If applicable
                                                    statement, Form 1-27    

  外国の所属機関因る説明書                          Statement from overseas Per case
                                                    organization, Form 1-28 

  入国前講習実施（予定)表に関する申請者等の誓約書   Pre-entry training plan Per case
                                                    undertaking, Form 1-29  

  技能実習生の個人情報の取り扱い係る同意書          Personal-data consent,  Per candidate
                                                    Form 1-39               

  送り出し機関との誓約書                            Sending-organization    Per case
                                                    undertaking             

  Kemenaker recommendation                          Recommendation from     Track request and
                                                    Kemenaker               receipt

  Form 1-23                                         Form 1-23 signed by     Track signature status
                                                    Kemenaker               
  -------------------------------------------------------------------------------------------------

Requirements: - **FR-060 (P0):** Maintain a configurable checklist
template by program/order/case. - **FR-061 (P0):** Track each document
as not required, missing, requested, uploaded, under review, accepted,
rejected, expired, or superseded. - **FR-062 (P0):** Record responsible
staff, requested date, due date, received date, reviewer, and review
notes. - **FR-063 (P0):** Support multiple versions and retain previous
versions. - **FR-064 (P0):** Support the two distinct Form 1-14 copies
(unsigned and signed). - **FR-065 (P0):** Flag urgent and overdue
documents. - **FR-066 (P0):** Allow authorized staff to download/print
documents and checklists. - **FR-067 (P0):** Staff can publish selected
documents to the student's portal. - **FR-068 (P0):** Students can
upload documents only into permitted upload slots. - **FR-069 (P1):**
Generate a printable case checklist and missing-document report. -
**FR-070 (P1):** Track whether a document is held in Google Drive and
its portal metadata.

### 6.8 Student support tickets

-   **FR-080 (P0):** Students can submit a ticket when they need a
    document, sample document, correction, or staff assistance.
-   **FR-081 (P0):** Ticket includes category, description, priority,
    attachment, created date, status, assigned staff, and response
    history.
-   **FR-082 (P0):** Staff can respond, request more information, attach
    a sample/template, and close/reopen a ticket.
-   **FR-083 (P0):** Students can see ticket status and staff responses.
-   **FR-084 (P1):** Track ticket response deadlines and unresolved
    ticket dashboard.

### 6.9 Student schedules, timeline, and reminders

-   **FR-090 (P0):** Students can create personal schedule entries,
    including passport appointments, exams, and other relevant
    appointments.
-   **FR-091 (P0):** Staff can create and assign events to students or
    groups.
-   **FR-092 (P0):** Provide calendar and chronological timeline views.
-   **FR-093 (P0):** Support event categories, start/end time, location,
    notes, reminder settings, owner, and status.
-   **FR-094 (P0):** Students can see their own events; staff can see
    events within their permissions.
-   **FR-095 (P1):** Synchronize selected events with Google Calendar.
-   **FR-096 (P1):** Record sync status and handle duplicate/retry cases
    safely.
-   **FR-097 (P0):** Provide in-app reminders and dashboard alerts.
-   **FR-098 (P1):** Provide staff-only LINE reminders through an
    approved LINE Messaging API/bot arrangement, if configured. No
    student-facing chatbot is in scope.

### 6.10 TSK/KUMIAI PIC visits

-   **FR-100 (P0):** Staff can record a TSK/KUMIAI PIC visit to the LPK.
-   **FR-101 (P0):** Visit record includes organization, PIC name, visit
    date/time, purpose, staff host, attendees, notes, follow-up actions,
    and attachments.
-   **FR-102 (P1):** Add visit events to staff timeline/calendar and
    track follow-up deadlines.

### 6.11 Communication readiness after placement

-   **FR-110 (P0):** For students who passed required exams and have a
    selected placement, show a communication checklist for the relevant
    TSK/KUMIAI and receiver-company LINE group.
-   **FR-111 (P0):** Staff can record recipient group, date/time sent,
    staff sender, summary, and confirmation/status.
-   **FR-112 (P0):** The portal does not automatically send to LINE
    groups in the initial release.
-   **FR-113 (P1):** Provide a copyable summary of placement information
    for staff to send manually.

### 6.12 Dashboards and reports

-   **FR-120 (P0):** Student dashboard shows current pathway, next
    actions, upcoming events, exam requirements, ticket status, and
    published documents.
-   **FR-121 (P0):** Staff dashboard shows urgent/overdue documents,
    upcoming exams/interviews/medical appointments, passport deadlines,
    tickets, and placement follow-ups.
-   **FR-122 (P0):** Filter candidates by program, order, job type, exam
    status, interview status, passport status, document status, and
    assigned staff.
-   **FR-123 (P1):** Export permitted reports to CSV/XLSX or printable
    PDF.
-   **FR-124 (P1):** Show audit history for critical changes.

## 7. Core student lifecycle

1.  Candidate registers and logs in.
2.  Candidate completes profile and identifies origin (own LPK, other
    LPK, independent).
3.  Staff reviews profile completeness and assigns program pathway.
4.  Staff assigns or offers a suitable TO/JO.
5.  Portal calculates required language and SSW exams from program and
    order rules.
6.  Candidate books or records exam reservation; staff tracks issues and
    dates.
7.  Candidate takes exams and uploads result evidence.
8.  Staff verifies results; failed exams produce a calculated earliest
    retake date using configurable rules.
9.  Candidate completes medical checkup and uploads the result.
10. Staff creates interview schedule/invitation; candidate selects a
    date.
11. Staff records interview result. All interview history remains.
12. Candidate chooses from passed offers; staff records the selected
    offer.
13. Passport process starts according to Internship or Tokutei Ginou
    rules.
14. Staff manages the required placement document checklist, Kemenaker
    recommendation, and Form 1-23 status.
15. Staff marks required documents accepted and ready for the next
    operational stage.
16. Staff records communication to the relevant TSK/KUMIAI and
    receiver-company LINE group.
17. Candidate's case progresses to the next configured
    placement/departure stage.

Each stage must support exceptions, pauses, withdrawal, and reopening
with a reason and audit record.

## 8. Status and workflow design

Statuses should be configurable where possible. Initial suggested
values:

-   Candidate: Registered, Profile Incomplete, Active, On Hold,
    Withdrawn, Completed.
-   Exam booking: Planned, Reserved, Issue Reported, Rescheduled,
    Cancelled, Completed.
-   Exam result: Pending, Passed, Failed, Not Attended, Evidence
    Required, Verified.
-   Interview: Invited, Date Selection Needed, Scheduled, Attended,
    Passed, Failed, Rescheduled, Cancelled, Absent.
-   Offer: Available, Passed, Selected, Not Selected, Withdrawn,
    Expired.
-   Passport: Not Started, Documents Preparing, Appointment Scheduled,
    Submitted, Processing, Ready for Collection, Issued, Issue Reported.
-   Document: Not Required, Missing, Requested, Uploaded, Under Review,
    Accepted, Rejected, Expired, Superseded.
-   Ticket: Open, Assigned, Waiting for Student, In Progress, Resolved,
    Closed.
-   Recommendation letter: Drafting, Information Incomplete, Submitted,
    In Process, Received, Rejected, Overdue.

## 9. Non-functional requirements

-   **NFR-001 Security:** Use Django authentication, CSRF protection,
    secure sessions, permission checks, and server-side validation.
-   **NFR-002 Privacy:** Students can access only their own records.
    Staff access is permission-scoped.
-   **NFR-003 Auditability:** Record actor, timestamp, action, and
    relevant before/after values for critical changes.
-   **NFR-004 Reliability:** Database backups and documented restore
    procedures are required.
-   **NFR-005 Low cost:** Initial development and pilot deployment
    should run on existing LPK hardware and free-tier/local services
    where feasible.
-   **NFR-006 Responsiveness:** Core student and staff workflows must
    work on desktop, tablet, and mobile browsers.
-   **NFR-007 Accessibility:** Forms must have labels, validation
    messages, keyboard support, and readable contrast.
-   **NFR-008 Performance:** Paginate large candidate/document lists and
    avoid loading all file content into the database.
-   **NFR-009 Maintainability:** Use modular Django apps, migrations,
    tests, and documented configuration.
-   **NFR-010 Availability transparency:** If the local server is off,
    the portal may be unavailable. The UI must not imply 24/7
    availability.
-   **NFR-011 Data integrity:** Interview, exam-attempt, and
    document-version history must not be silently overwritten.
-   **NFR-012 Localization:** Support Indonesian as the primary UI
    language, with English labels where useful and Japanese document
    names preserved.

## 10. Integrations and deployment constraints

### Google Drive

Use Drive for file storage where possible. Store file metadata, owner,
document type, version, visibility, and Drive file ID in Django. Access
must be mediated by the portal; do not expose public Drive links for
sensitive files.

### Google Calendar

Synchronize selected events. Store external event IDs and sync state.
Avoid duplicate events on retries. Calendar integration is an
enhancement to the portal's own event database, not the system of
record.

### Static URL tunnel

A tunnel may expose the local development/pilot server through a stable
public URL. Use HTTPS, authentication, least-privilege firewall rules,
and a trusted tunnel provider. Never expose Django's development server,
database admin ports, or unrestricted debug pages to the public
internet. A tunnel does not provide uptime: when the host PC/tablet or
network is off, the portal is unavailable.

### Local PC/tablet hosting

Use a production-capable WSGI/ASGI server for any network-accessible
pilot; do not use `runserver` as a public production server. The host
must be powered, connected, patched, and backed up during working hours.
A tablet is a temporary host only if it can reliably run the required
Python/Django stack and storage. Verify device OS, power, thermal,
network, and background-process limitations before choosing it.

### LINE

Initial release uses staff reminders only. Store reminder configuration
securely. Do not store LINE channel secrets in source control.

## 11. Acceptance criteria for initial release

The initial release is acceptable when: 1. Student and staff can
register and log in immediately under the defined registration controls.
2. A staff member can create an order and assign it to a student. 3. The
portal derives the correct language/SSW exam checklist from program and
order configuration. 4. Exam bookings, problems, attempts, results,
uploads, and retake dates can be tracked. 5. Medical appointments and
result uploads can be tracked. 6. A student can receive multiple
interviews, and the system preserves every interview and outcome. 7. The
student can select one passed offer without losing other offers. 8.
Internship and Tokutei Ginou passport workflows differ correctly. 9.
Staff can manage the specified document checklist, including separate
unsigned/signed Form 1-14 files. 10. Staff can flag urgent/overdue
documents and retrieve authorized files for printing. 11. Students can
create schedule entries and support tickets. 12. Staff can record PIC
visits and placement communication. 13. The staff dashboard shows the
next actions and urgent deadlines. 14. Access controls prevent students
from viewing another student's records. 15. Backup and restore
instructions are tested.

## 12. Open policy/configuration items

These items should be confirmed by LPK management before production
use: - Exact eligibility rules and acceptable combinations for each
program and order. - Current official retake waiting periods for JFT,
JLPT, and each SSW exam/provider. - Whether medical-checkup requirements
vary by order, employer, or stage. - Which placement documents apply to
Internship, Tokutei Ginou, and specific cases. - Exact Kemenaker
recommendation and Form 1-23 process, responsible office, and
deadlines. - Whether staff self-registration uses an enrollment code,
approved email domain, or another controlled method. - Which Google
account owns Drive/Calendar integration and the required sharing
model. - Which LINE reminder channel/group mechanism is approved. -
Retention period and deletion policy for identity, medical, passport,
and employment documents.

## 13. Suggested phased delivery

**Phase 1 --- Core portal:** Authentication, profiles, staff roles,
TO/JO, program rules, exams, interviews/offers, student timeline, basic
document checklist, tickets.

**Phase 2 --- Case processing:** Passport workflows,
recommendation-letter tracking, medical checkups, document
versions/review/printing, PIC visits, placement communication checklist.

**Phase 3 --- Integrations and reporting:** Google Drive, Google
Calendar, staff LINE reminders, exports, management dashboards, backup
monitoring.

**Phase 4 --- Refinement:** Advanced analytics, configurable workflow
automation, richer notifications, and operational improvements.

## 14. Student Workflow Board and Document Management Requirements

This section records the approved workflow and document-management
direction. Requirements in this section are approved design decisions;
they are not considered implemented until verified in the application.

### 14.1 Staff access policy

All STAFF members have operational access to every student's workflow
and document records.

- Staff access is not limited by active StudentStaffAssignment records.
- Staff can upload documents on behalf of any student.
- Staff can review, approve, reject, and update document workflow items.
- Multiple staff members can work on the same student simultaneously.
- StudentStaffAssignment may remain for responsibility tracking and
  workload history, but must not block operational access.
- MANAGER and superuser retain broader administrative privileges.
- Students can access only their own permitted records and upload only
  their own documents.

This policy supersedes the earlier assignment-restricted staff access
requirements in this document.

### 14.2 Student-centered Workflow Board

- **FR-125 (P0):** Provide a staff Workflow Board organized by student.
  Each student is displayed as a student card with their applicable
  required documents and operational tasks.
- **FR-126 (P0):** Display required document and task completion under
  each student rather than grouping the board primarily by staff member.
- **FR-127 (P0):** Display relevant progress, outstanding requirements,
  due dates, urgency indicators, and latest activity.
- **FR-128 (P0):** Allow STAFF to update workflow statuses and work on
  any student's operational items.
- **FR-129 (P0):** Allow multiple staff members to work on the same
  student and document requirements in parallel without exclusive
  ownership locks.
- **FR-130 (P0):** Keep staff names out of the ordinary board's primary
  presentation. Preserve actor identity in internal activity and audit
  history.
- **FR-131 (P0):** Students can see their own permitted progress,
  document requirements, and next actions, but cannot see internal
  staff notes or private operational activity.
- **FR-132 (P0):** Record workflow changes and document actions with
  the authenticated actor and timestamp.
- **FR-133 (P0):** Reference existing authoritative student, document,
  exam, passport, and other process records instead of duplicating
  their business data.
- **FR-134 (P0):** Generate checklist items from applicable requirements
  and existing process records. Avoid duplicate checklist entries for
  the same applicable requirement.

### 14.3 Workflow statuses and progress

The document/task workflow uses these five operational statuses:

- `PENDING` — work has not started.
- `IN_PROGRESS` — a staff member is working on the item.
- `SUBMITTED` — a document or required result has been submitted.
- `APPROVED` — the submitted item has been accepted.
- `REJECTED` — the submitted item requires correction or resubmission.

These workflow statuses are separate from existing
StudentDocument.status values. Existing document review statuses must
remain authoritative for document-specific review and storage logic.

Synchronization rules:

- A successful upload moves the corresponding workflow item to
  `SUBMITTED`.
- Starting work may move an item to `IN_PROGRESS` without changing the
  underlying document review status.
- Approval moves the workflow item to `APPROVED` and the corresponding
  document to its existing accepted state.
- Rejection moves the workflow item to `REJECTED` and preserves the
  existing rejected-document state and review notes.
- Resubmission moves the workflow item back to `SUBMITTED`, retaining
  the previous document versions and review history.
- Expiry and overdue conditions are urgency indicators, not additional
  workflow statuses.

Progress is calculated from applicable required items:

`Approved required items / Total applicable required items`

Optional requirements do not reduce the required completion
percentage. Missing required documents must appear in the checklist
before an upload exists. The implementation must prevent duplicate
instances for the same student and applicable requirement.

Urgency rules:

- Overdue: incomplete item whose due date has passed.
- Urgent: incomplete item due within three days.
- Due soon: incomplete item due within seven days.
- No due date: no date-based urgency indicator.

The board should make urgent and overdue work easy to identify without
replacing the underlying process status.

### 14.4 Document Template Library

- **FR-135 (P0):** Provide a centralized library of approved blank
  document templates.
- **FR-136 (P0):** Link templates to their applicable
  DocumentRequirement and program pathway.
- **FR-137 (P0):** Allow MANAGER to upload, update, activate, deactivate,
  and maintain templates.
- **FR-138 (P0):** Allow STAFF to download active templates for
  operational use.
- **FR-139 (P0):** Support multiple template versions and language
  variants where required.
- **FR-140 (P0):** Keep blank templates separate from completed
  student-submitted documents and their version history.
- **FR-141 (P0):** Record template metadata, including name, form
  reference, pathway, language, version, active state, and instructions.
- **FR-142 (P0):** Validate uploaded template file types and size.

Initial template metadata should support:

- Template name and official form reference.
- Applicable pathway: General, Internship, or Tokutei Ginou.
- Related document requirement.
- Language.
- Version and effective/active state.
- Staff instructions.
- Uploaded file and uploader metadata.

Initial scope supports downloading a blank template, completing it
outside the portal, and uploading the completed file to the student's
document requirement. Online form filling is a possible future
enhancement and is not required for the initial implementation.

Updating a blank template must never overwrite a student's completed
document or historical submission.

### 14.5 Program-specific document requirements

The checklist must support the applicable forms and requirements for
each student's underlying program:

- Ginoujishuusei / Internship: applicable Forms 1–14 and other
  confirmed program requirements.
- Tokutei Ginou: applicable Forms 1, 5, and 6 and other confirmed
  requirements.
- Matching Job: derive requirements from its linked Internship or
  Tokutei Ginou program/order rather than treating Matching Job as an
  unrelated document pathway.

The system must allow staff to confirm applicability and distinguish
required from optional documents. Avoid duplicate checklist entries
when multiple orders refer to the same applicable student requirement.

### 14.6 Document upload and audit requirements

- Students may upload only their own permitted documents.
- STAFF may upload documents on behalf of any student.
- The actual authenticated uploader must be recorded automatically.
- The uploader must never be selected or overridden through a
  user-controlled form field.
- Record the student, requirement, uploader, upload timestamp, version,
  and review history.
- Every upload, review, approval, rejection, and relevant status change
  must create an audit record.
- Uploading a document must not automatically approve it.
- Previous versions must remain available according to the retention
  policy.
- Private files must only be available through authorized access checks.

### 14.7 Scope boundaries

The initial Workflow Board is focused on student document requirements
and operational tasks. Existing exam, medical, passport, interview,
calendar, and ticket modules remain the authoritative sources for their
own records and statuses.

The board may later integrate these modules as linked tasks. It must
not duplicate or silently modify their authoritative business data.

### 14.8 Acceptance criteria

The approved design is acceptable when:

1. STAFF can access operational workflows and documents for all students.
2. STAFF can upload documents on behalf of any student.
3. Students cannot access another student's records or upload on behalf
   of another student.
4. Multiple staff can work on the same student's workflow without
   assignment locks.
5. The board groups work by student and displays applicable
   requirements beneath each student.
6. Required and optional documents are distinguished correctly.
7. Workflow statuses remain separate from existing document statuses.
8. Approval, rejection, and resubmission preserve document history.
9. Uploads and reviews record the actual authenticated actor.
10. Students cannot view internal staff notes or private activity.
11. Managers can administer blank document templates.
12. Staff can download active blank templates.
13. Updating templates does not overwrite student submissions.
14. Existing process records remain authoritative.
15. Existing tests continue to pass, with new permission and workflow
    tests added for the approved behavior.

### 14.9 Delivery scope

The next Workflow Board delivery includes the student-centered board,
document/task checklist, five operational statuses, parallel staff
operations, urgency indicators, audit history, and student-visible
progress.

The Document Template Library includes manager template administration,
staff downloads, template versioning, and completed-document upload.

**Status:** Requirements approved; implementation pending.

### 14.10 JITCO Preparation Checklist

#### 14.10.1 Purpose and scope

Provide a JITCO Preparation page for each Training Order. The page
organizes the information and documents required for JITCO preparation,
tracks readiness, and supports manual handover to the staff member
responsible for the external submission.

IJB is responsible for document collection, preparation tracking, and
handover only. IJB does not directly submit documents to JITCO or
Kemnaker. Wiwitan performs the actual external upload.

This feature must remain separate from the existing passport
recommendation-letter workflow.

#### 14.10.2 Training Order and company information

Display the associated Japanese company name as the main page heading,
with the Indonesian company name underneath.

Do not display the TO Registration Number in the page heading.

The page must show:
- Japanese company name
- Indonesian company name
- Company email
- Business sector
- Kumiai name
- Kumiai PIC name
- Kumiai PIC phone number

Use the existing company, Kumiai, contact, and sector records as the
authoritative sources. Do not create unnecessary duplicate company
records for this feature.

#### 14.10.3 General JITCO documents

Provide order-level document records for:
- Training Order (TO) PDF
- Kumiai PIC name card (image or PDF)

Provide a JITCO Forms 1–23 completion checklist for the Training Order.

Track the completion state of each applicable form individually.
Calculate overall checklist completion from the individual form states.
Do not rely on a single manually maintained Boolean value to represent
the completion of all forms.

These are Training Order documents and must not be stored as documents
belonging to an individual student.

#### 14.10.4 Student information and documents

Automatically list all students assigned to the selected Training Order.

The list must expand or update when student assignments change.

For each student, provide:
- Participant email address
- Employment contract completion and document status
- Passport document status

Employment contract documentation must support the applicable Forms
1–14 requirements.

Reuse existing student document requirements, submissions, review
statuses, and document version history wherever applicable. Do not
create duplicate student document records solely for JITCO preparation.

#### 14.10.5 Upload and staff responsibilities

Any STAFF member may upload the required documents on behalf of any
student, regardless of StudentStaffAssignment.

Multiple staff members may contribute to the same Training Order
preparation. Do not impose exclusive ownership or upload locks.

Record the actual authenticated uploader and upload timestamp for
every upload. Preserve document versions and audit history.

The staff member responsible for preparing or coordinating the JITCO
package must be tracked separately from the person who uploaded an
individual document. These responsibilities may belong to different
staff members.

Uploading a document must not automatically mark it as approved or
complete. Existing document review rules remain authoritative.

#### 14.10.6 Preparation and handover status

Provide the following Training Order preparation statuses:

- Collecting Documents
- Documents Incomplete
- Preparing JITCO Documents
- Ready for Wiwitan
- Handed Over to Wiwitan
- Completed (confirmation received)

Track preparation and handover activity with the responsible actor
and timestamp.

The status must describe IJB's preparation and handover progress.
Do not use a status such as "Submitted to JITCO" to represent an action
that IJB staff do not perform.

"Completed" means confirmation has been received after the handover;
it must not imply that IJB performed the external upload.

#### 14.10.7 Information copying and document handover

Provide a **Copy All Information** action that generates readable,
formatted text suitable for copying into WhatsApp.

The copied information must include the relevant company details,
Kumiai contact details, Training Order information, and participant
emails and document completion status.

Do not generate raw JSON as the normal user-facing copy format.

Provide a **Download Documents** action that collects the available
Training Order PDF, Kumiai PIC name card, student employment contracts,
and student passports for manual handover.

The handover process must remain manual and must not claim that IJB
has submitted files to JITCO or Kemnaker.

#### 14.10.8 Acceptance criteria

1. Each Training Order has its own JITCO Preparation checklist.
2. Company and Kumiai information comes from existing authoritative
   records.
3. The page heading displays Japanese and Indonesian company names,
   without the TO Registration Number.
4. Training Order documents are stored at the order level.
5. Assigned students are listed automatically.
6. Student-specific employment contracts and passports reuse the
   existing document management workflow.
7. Any STAFF member can upload documents for any student.
8. Uploads record the actual uploader, timestamp, and version history.
9. Preparation responsibility is tracked separately from upload
   ownership.
10. Multiple staff members can contribute without exclusive locks.
11. Preparation and handover statuses do not misrepresent external
    JITCO submission.
12. Information can be copied in a readable format for WhatsApp.
13. Available documents can be collected for manual handover.
14. Existing document permissions, review rules, and audit history
    remain intact.
15. Each applicable JITCO Form 1–23 has an individual completion
    state, and overall checklist completion is calculated from
    those individual states.

**Status:** Requirements approved; implementation pending.

## 15. Implementation Status and Development Roadmap

This section tracks implementation progress and distinguishes implemented functionality from approved requirements and planned work.

### 15.1 Development baseline

- Current development version: v1.02
- Current main development commit: `c33cbe5`
- Requirements commit: `da892e9`
- Previous implementation baseline: `04996ac`
- Main branch: `main`

### 15.2 Implemented functionality

| Feature | Status |
|---|---|
| Student, Staff, and Manager roles | Implemented |
| Staff registration code | Implemented |
| Student-to-staff assignments | Implemented |
| Multiple staff assignments per student | Implemented |
| Assignment-restricted staff access | Implemented historically; superseded by approved all-student operational access policy |
| Manager cross-team student access | Implemented |
| Manager-only Django administration | Implemented |
| Internal ticket replies | Implemented |
| Role-based group synchronization | Implemented |

The staff access policy change, Workflow Board, and template library
must not be marked implemented until code and tests verify the new
behavior.

Recorded v1.02 verification:

- 24 portal tests passed.
- Django system checks passed.
- Migration consistency check passed.

These results must be rerun after integration or relevant changes.
### 15.3 Approved requirements awaiting implementation

#### 15.3.1 Staff-assisted password reset

- STAFF can reset passwords for any STUDENT.
- MANAGER can reset passwords for any STUDENT.
- Only MANAGER can reset STAFF passwords.
- Existing passwords must never be viewable.
- Password updates must use Django's secure password-setting mechanism.
- Every reset must be recorded in AuditLog.
- Temporary passwords and forced password changes are not required.

**Status:** Approved; implementation pending.

#### 15.3.2 Date and time formatting

- Display dates using `dd-mm-yyyy`.
- Display time using 24-hour `HH:mm`.
- Combined date and time: `dd-mm-yyyy HH:mm`.
- Apply consistent formatting throughout relevant portal pages.

**Status:** Approved; implementation pending.

#### 15.3.3 Interview timezone handling

- Interview input uses JST (`Asia/Tokyo`).
- Interview display uses WIB (`Asia/Jakarta`).
- Convert timezone-aware timestamps correctly.
- Preserve timezone-aware database storage.
- Keep the portal's global default timezone as WIB.

**Status:** Approved; implementation pending.

### 15.4 Workflow Board delivery

Requirements are defined in Section 14.

Remaining implementation work:

- Replace assignment-restricted staff operational access with access
  for all STAFF across all student workflows and documents.
- Keep student access restricted to the student's own records.
- Build the student-centered Workflow Board.
- Display each student's required documents and tasks.
- Support the five operational statuses.
- Support parallel staff work without exclusive ownership locks.
- Calculate required-document progress.
- Display due dates and urgency indicators.
- Preserve internal activity and audit history.
- Keep internal staff notes hidden from students.
- Link to authoritative process records rather than duplicating them.

**Status:** Requirements approved; implementation pending.
### 15.5 Document management improvements

Approved work:

- Create a Document Template Library.
- Link templates to document requirements and program pathways.
- Allow MANAGER to administer blank templates.
- Allow STAFF to download active templates.
- Support template language variants and version history.
- Support completed-document upload by students and staff.
- Allow STAFF to upload on behalf of any student.
- Record actual uploader identity and audit all relevant actions.
- Preserve completed document versions when templates are updated.
- Confirm applicable Ginoujishuusei Forms 1-14 and Tokutei Forms 1, 5,
  and 6 requirements.
- Support required/optional checklist entries and prevent duplicates.
- Preserve existing document review and download authorization.

Online form filling is deferred to a future phase.

**Status:** Requirements approved; implementation pending.
### 15.6 Future development

- Google Drive integration.
- Google Calendar synchronization.
- Staff LINE reminders.
- Improved operational dashboards.
- Backup monitoring.
- Advanced workflow automation.
- Reporting and analytics.

Prioritize these according to operational needs and available infrastructure.

### 15.7 Development tracking rules

1. Document requirements before implementation.
2. Do not silently change approved requirements.
3. Mark features implemented only after source-code verification.
4. Test security-sensitive functionality.
5. Review database migrations before application.
6. Test changes before committing.
7. Ensure Git commits accurately describe their changes.
8. Never commit or push without explicit approval.
9. Reconcile development across computers through Git before database or migration operations.
10. Preserve project backups and local databases unless removal is explicitly approved.

### 15.8 Revision history

| Version | Description |
|---|---|
| 1.00 | Initial product requirements baseline, 1 November 2026 |
| 1.02 | Student self-service and workflow requirements |
| 1.02 tracking revision | Implementation progress and additional approved requirements |

**Last tracking revision:** 12 November 2026
