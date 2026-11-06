import os
import uuid
import hashlib
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import FileExtensionValidator
from django.db import models, transaction
from django.utils import timezone


class User(AbstractUser):
    class Role(models.TextChoices):
        STUDENT = 'STUDENT', 'Student'
        STAFF = 'STAFF', 'Staff'
        MANAGER = 'MANAGER', 'Manager'

    role = models.CharField(
        max_length=12,
        choices=Role.choices,
        default=Role.STUDENT
    )
    phone = models.CharField(max_length=30, blank=True)
    staff_code_used = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.is_superuser:
            self.role = self.Role.MANAGER
            self.is_staff = True

        super().save(*args, **kwargs)

    @property
    def is_staff_member(self):
        return (
            self.role in {self.Role.STAFF, self.Role.MANAGER}
            or self.is_superuser
        )


class StaffRegistrationCode(models.Model):
    """One-time staff invitation. Only a hash of the code is stored."""
    code_hash = models.CharField(max_length=64, unique=True, editable=False)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='generated_staff_codes')
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    used_at = models.DateTimeField(null=True, blank=True)
    used_by = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True, blank=True, related_name='staff_invitation_used')
    revoked = models.BooleanField(default=False)

    class Meta:
        ordering = ('-created_at',)
        verbose_name = 'Staff registration code'
        verbose_name_plural = 'Staff registration codes'

    @staticmethod
    def hash_code(raw_code):
        return hashlib.sha256(raw_code.strip().upper().encode('utf-8')).hexdigest()

    @property
    def is_usable(self):
        return (not self.revoked and self.used_at is None and
                (self.expires_at is None or self.expires_at > timezone.now()))

    def __str__(self):
        state = 'used' if self.used_at else ('revoked' if self.revoked else 'available')
        return f'Staff code · {self.created_at:%Y-%m-%d %H:%M} · {state}'

    @classmethod
    def consume(cls, raw_code, user):
        digest = cls.hash_code(raw_code)
        with transaction.atomic():
            invitation = cls.objects.select_for_update().filter(code_hash=digest).first()
            if not invitation or not invitation.is_usable:
                return False
            invitation.used_at = timezone.now()
            invitation.used_by = user
            invitation.save(update_fields=['used_at', 'used_by'])
            return True


class StudentProfile(models.Model):
    class Origin(models.TextChoices):
        OWN = 'OWN_LPK', 'LPK sendiri'
        OTHER = 'OTHER_LPK', 'LPK lain'
        INDEPENDENT = 'INDEPENDENT', 'Mandiri'
    class Program(models.TextChoices):
        INTERNSHIP = 'INTERNSHIP', 'Internship'
        TOKUTEI = 'TOKUTEI', 'Tokutei Ginou'
        MATCHING = 'MATCHING', 'Matching Job'
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='student_profile')
    origin = models.CharField(max_length=20, choices=Origin.choices, default=Origin.OWN)
    origin_lpk_name = models.CharField(max_length=180, blank=True)
    program = models.CharField(max_length=20, choices=Program.choices, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    address = models.TextField(blank=True)
    emergency_contact = models.CharField(max_length=180, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self): return self.user.get_full_name() or self.user.username

class StudentStaffAssignment(models.Model):
    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name='staff_assignments',
    )
    staff = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='student_assignments',
    )
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='created_student_assignments',
    )
    assigned_at = models.DateTimeField(default=timezone.now)
    active = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['student', 'staff'],
                name='unique_student_staff_assignment',
            )
        ]
        ordering = ['-assigned_at']

    def clean(self):
        super().clean()
        if self.staff_id:
            staff_role = self.staff.role
            if staff_role not in {
                User.Role.STAFF,
                User.Role.MANAGER,
            } and not self.staff.is_superuser:
                from django.core.exceptions import ValidationError
                raise ValidationError({
                    'staff': 'Only staff members or managers can be assigned.'
                })

    def __str__(self):
        return f'{self.student} → {self.staff}'

class JobType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    ssw_category_code = models.CharField(max_length=50, blank=True)
    active = models.BooleanField(default=True)
    def __str__(self): return self.name

class TskKumiai(models.Model):
    name = models.CharField(max_length=180)
    address = models.TextField(blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=40, blank=True)
    active = models.BooleanField(default=True)
    def __str__(self): return self.name

class TskContact(models.Model):
    organization = models.ForeignKey(TskKumiai, on_delete=models.CASCADE, related_name='contacts')
    name = models.CharField(max_length=150)
    role = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=40, blank=True)
    def __str__(self): return f'{self.name} ({self.organization})'

class ReceivingCompany(models.Model):
    organization = models.ForeignKey(TskKumiai, on_delete=models.PROTECT, related_name='companies')
    name = models.CharField(max_length=180)
    address = models.TextField(blank=True)
    business_sector = models.CharField(max_length=150, blank=True)
    email = models.EmailField(blank=True)
    pic_name = models.CharField(max_length=150, blank=True)
    pic_phone = models.CharField(max_length=40, blank=True)
    def __str__(self): return self.name

class Order(models.Model):
    class Kind(models.TextChoices):
        TO = 'TO', 'Training Order'
        JO = 'JO', 'Job Order'
    class Pathway(models.TextChoices):
        INTERNSHIP = 'INTERNSHIP', 'Internship'
        TOKUTEI = 'TOKUTEI', 'Tokutei Ginou'
    code = models.CharField(max_length=80, unique=True)
    title = models.CharField(max_length=180)
    kind = models.CharField(max_length=2, choices=Kind.choices)
    pathway = models.CharField(max_length=20, choices=Pathway.choices)
    organization = models.ForeignKey(TskKumiai, on_delete=models.PROTECT)
    company = models.ForeignKey(ReceivingCompany, on_delete=models.PROTECT)
    job_type = models.ForeignKey(JobType, on_delete=models.PROTECT)
    location = models.CharField(max_length=150, blank=True)
    language_exam_required = models.CharField(max_length=30, default='JFT_A2_OR_JLPT_N4')
    ssw_exam_required = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    def __str__(self): return f'{self.code} - {self.title}'

class StudentOrderAssignment(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='assignments')
    order = models.ForeignKey(Order, on_delete=models.PROTECT)
    assigned_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    assigned_at = models.DateTimeField(default=timezone.now)
    active = models.BooleanField(default=True)
    class Meta: constraints = [models.UniqueConstraint(fields=['student', 'order'], name='unique_student_order')]

class ExamRule(models.Model):
    code = models.CharField(max_length=40, unique=True)
    name = models.CharField(max_length=100)
    retake_wait_days = models.PositiveIntegerField(null=True, blank=True, help_text='Only enter a verified rule; leave blank for manual confirmation.')
    active = models.BooleanField(default=True)
    def __str__(self): return self.name

class ExamAttempt(models.Model):
    class Status(models.TextChoices):
        PLANNED = 'PLANNED', 'Planned'
        RESERVED = 'RESERVED', 'Reserved'
        ISSUE = 'ISSUE', 'Issue reported'
        PASSED = 'PASSED', 'Passed'
        FAILED = 'FAILED', 'Failed'
        PENDING = 'PENDING', 'Pending verification'
        VERIFIED = 'VERIFIED', 'Verified'
        CANCELLED = 'CANCELLED', 'Cancelled'
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='exam_attempts')
    rule = models.ForeignKey(ExamRule, on_delete=models.PROTECT)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True)
    reservation_date = models.DateField(null=True, blank=True)
    exam_date = models.DateField(null=True, blank=True)
    result_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.PLANNED)
    score_or_level = models.CharField(max_length=80, blank=True)
    result_note = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='created_exam_attempts')
    created_at = models.DateTimeField(auto_now_add=True)
    @property
    def earliest_retake_date(self):
        if self.status != self.Status.FAILED or not self.result_date or self.rule.retake_wait_days is None: return None
        from datetime import timedelta
        return self.result_date + timedelta(days=self.rule.retake_wait_days)

class MedicalCheckup(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='medical_checks')
    scheduled_at = models.DateTimeField(null=True, blank=True)
    facility = models.CharField(max_length=180, blank=True)
    status = models.CharField(max_length=40, default='SCHEDULED')
    result_note = models.TextField(blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)

class Interview(models.Model):
    class Status(models.TextChoices):
        INVITED = 'INVITED', 'Invited'
        SCHEDULED = 'SCHEDULED', 'Scheduled'
        ATTENDED = 'ATTENDED', 'Attended'
        PASSED = 'PASSED', 'Passed'
        FAILED = 'FAILED', 'Failed'
        RESCHEDULED = 'RESCHEDULED', 'Rescheduled'
        CANCELLED = 'CANCELLED', 'Cancelled'
        ABSENT = 'ABSENT', 'Absent'
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='interviews')
    order = models.ForeignKey(Order, on_delete=models.PROTECT)
    mendan = models.ForeignKey(TskContact, on_delete=models.SET_NULL, null=True, blank=True)
    scheduled_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.INVITED)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)

class Offer(models.Model):
    class Status(models.TextChoices):
        AVAILABLE = 'AVAILABLE', 'Available'
        SELECTED = 'SELECTED', 'Selected'
        NOT_SELECTED = 'NOT_SELECTED', 'Not selected'
        WITHDRAWN = 'WITHDRAWN', 'Withdrawn'
        EXPIRED = 'EXPIRED', 'Expired'
    interview = models.OneToOneField(Interview, on_delete=models.PROTECT, related_name='offer')
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.AVAILABLE)
    selected_at = models.DateTimeField(null=True, blank=True)
    selection_note = models.TextField(blank=True)

class PassportCase(models.Model):
    class Status(models.TextChoices):
        NOT_STARTED = 'NOT_STARTED', 'Not started'
        PREPARING = 'PREPARING', 'Documents preparing'
        APPOINTMENT = 'APPOINTMENT', 'Appointment scheduled'
        SUBMITTED = 'SUBMITTED', 'Submitted'
        PROCESSING = 'PROCESSING', 'Processing'
        READY = 'READY', 'Ready for collection'
        ISSUED = 'ISSUED', 'Issued'
        ISSUE = 'ISSUE', 'Issue reported'
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='passport_cases')
    pathway = models.CharField(max_length=20, choices=[('INTERNSHIP','Internship'),('TOKUTEI','Tokutei Ginou')])
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NOT_STARTED)
    appointment_at = models.DateTimeField(null=True, blank=True)
    request_date = models.DateField(null=True, blank=True)
    target_deadline = models.DateField(null=True, blank=True)
    submitted_at = models.DateField(null=True, blank=True)
    received_at = models.DateField(null=True, blank=True)
    recommendation_required = models.BooleanField(default=False)
    recommendation_status = models.CharField(max_length=30, blank=True)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)

class DocumentRequirement(models.Model):
    code = models.CharField(max_length=60, unique=True)
    name = models.CharField(max_length=220)
    japanese_name = models.CharField(max_length=300, blank=True)
    form_reference = models.CharField(max_length=40, blank=True)
    pathway = models.CharField(max_length=20, choices=StudentProfile.Program.choices, blank=True)
    required = models.BooleanField(default=True)
    active = models.BooleanField(default=True)
    def __str__(self): return f'{self.name} {self.form_reference}'.strip()

def private_document_path(instance, filename):
    safe_name = os.path.basename(filename).replace(' ', '_')[:100]
    return f'private/{instance.student_id}/{uuid.uuid4().hex}_{safe_name}'

class StudentDocument(models.Model):
    class Status(models.TextChoices):
        REQUESTED = 'REQUESTED', 'Requested'
        UPLOADED = 'UPLOADED', 'Uploaded'
        REVIEW = 'REVIEW', 'Under review'
        ACCEPTED = 'ACCEPTED', 'Accepted'
        REJECTED = 'REJECTED', 'Rejected'
        EXPIRED = 'EXPIRED', 'Expired'
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='documents')
    requirement = models.ForeignKey(DocumentRequirement, on_delete=models.PROTECT)
    file = models.FileField(upload_to=private_document_path, validators=[FileExtensionValidator(['pdf','jpg','jpeg','png'])], blank=True)
    version = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.REQUESTED)
    visible_to_student = models.BooleanField(default=False)
    due_date = models.DateField(null=True, blank=True)
    review_note = models.TextField(blank=True)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='uploaded_student_documents')
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True, blank=True, related_name='reviewed_student_documents')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    class Meta: ordering = ['requirement__name', '-version']

class CalendarEvent(models.Model):
    class Kind(models.TextChoices):
        EXAM = 'EXAM', 'Exam'
        PASSPORT = 'PASSPORT', 'Passport'
        MEDICAL = 'MEDICAL', 'Medical'
        INTERVIEW = 'INTERVIEW', 'Interview'
        OTHER = 'OTHER', 'Other'
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='events')
    title = models.CharField(max_length=180)
    kind = models.CharField(max_length=12, choices=Kind.choices, default=Kind.OTHER)
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField(null=True, blank=True)
    location = models.CharField(max_length=180, blank=True)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    google_event_id = models.CharField(max_length=200, blank=True)
    sync_status = models.CharField(max_length=30, default='NOT_CONNECTED')
    created_at = models.DateTimeField(auto_now_add=True)

class SupportTicket(models.Model):
    class Status(models.TextChoices):
        OPEN = 'OPEN', 'Open'
        ASSIGNED = 'ASSIGNED', 'Assigned'
        WAITING = 'WAITING', 'Waiting for student'
        PROGRESS = 'PROGRESS', 'In progress'
        RESOLVED = 'RESOLVED', 'Resolved'
        CLOSED = 'CLOSED', 'Closed'
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='tickets')
    subject = models.CharField(max_length=180)
    category = models.CharField(max_length=50, default='DOCUMENT')
    description = models.TextField()
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.OPEN)
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tickets')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class TicketReply(models.Model):
    ticket = models.ForeignKey(SupportTicket, on_delete=models.CASCADE, related_name='replies')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_internal = models.BooleanField(default=False)

class TskVisit(models.Model):
    organization = models.ForeignKey(TskKumiai, on_delete=models.PROTECT)
    pic_name = models.CharField(max_length=150, blank=True)
    visit_at = models.DateTimeField()
    purpose = models.CharField(max_length=180)
    host_staff = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    attendees = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    follow_up_due = models.DateField(null=True, blank=True)

class PlacementCommunication(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='communications')
    organization = models.ForeignKey(TskKumiai, on_delete=models.PROTECT)
    company = models.ForeignKey(ReceivingCompany, on_delete=models.PROTECT)
    recipient_group = models.CharField(max_length=180)
    sent_at = models.DateTimeField(null=True, blank=True)
    sent_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    summary = models.TextField(blank=True)
    confirmation_status = models.CharField(max_length=40, default='PENDING')

class AuditLog(models.Model):
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    action = models.CharField(max_length=100)
    object_type = models.CharField(max_length=100)
    object_id = models.CharField(max_length=80)
    details = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta: ordering = ['-created_at']
