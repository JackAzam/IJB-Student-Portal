
import os
import uuid
import hashlib

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.utils import timezone


# ============================================================
# PRIVATE FILE UPLOAD PATHS
# ============================================================

def _safe_upload_filename(filename):
    safe_name = os.path.basename(filename).replace(' ', '_')[:100]
    return f'{uuid.uuid4().hex}_{safe_name}'

def private_document_path(instance, filename):
    return student_document_path(instance, filename)

def student_document_path(instance, filename):
    return (
        f'private/students/{instance.student_id}/'
        f'{_safe_upload_filename(filename)}'
    )


def document_version_path(instance, filename):
    student_id = instance.student_document.student_id
    return (
        f'private/students/{student_id}/versions/'
        f'{_safe_upload_filename(filename)}'
    )


def document_template_version_path(instance, filename):
    return (
        f'private/templates/{instance.template_id}/versions/'
        f'{_safe_upload_filename(filename)}'
    )


def order_source_path(instance, filename):
    return (
        f'private/orders/{uuid.uuid4().hex}/'
        f'{_safe_upload_filename(filename)}'
    )


# ============================================================
# USER AND STUDENT MODELS
# ============================================================

class User(AbstractUser):
    class Role(models.TextChoices):
        STUDENT = 'STUDENT', 'Student'
        STAFF = 'STAFF', 'Staff'
        MANAGER = 'MANAGER', 'Manager'

    role = models.CharField(
        max_length=12,
        choices=Role.choices,
        default=Role.STUDENT,
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

    code_hash = models.CharField(
        max_length=64,
        unique=True,
        editable=False,
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='generated_staff_codes',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    used_at = models.DateTimeField(null=True, blank=True)
    used_by = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='staff_invitation_used',
    )
    revoked = models.BooleanField(default=False)

    class Meta:
        ordering = ('-created_at',)
        verbose_name = 'Staff registration code'
        verbose_name_plural = 'Staff registration codes'

    @staticmethod
    def hash_code(raw_code):
        return hashlib.sha256(
            raw_code.strip().upper().encode('utf-8')
        ).hexdigest()

    @property
    def is_usable(self):
        return (
            not self.revoked
            and self.used_at is None
            and (
                self.expires_at is None
                or self.expires_at > timezone.now()
            )
        )

    def __str__(self):
        state = (
            'used'
            if self.used_at
            else ('revoked' if self.revoked else 'available')
        )
        return (
            f'Staff code · {self.created_at:%Y-%m-%d %H:%M} · {state}'
        )

    @classmethod
    def consume(cls, raw_code, user):
        digest = cls.hash_code(raw_code)

        with transaction.atomic():
            invitation = (
                cls.objects
                .select_for_update()
                .filter(code_hash=digest)
                .first()
            )

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

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='student_profile',
    )
    origin = models.CharField(
        max_length=20,
        choices=Origin.choices,
        default=Origin.OWN,
    )
    origin_lpk_name = models.CharField(max_length=180, blank=True)
    program = models.CharField(
        max_length=20,
        choices=Program.choices,
        blank=True,
    )
    date_of_birth = models.DateField(null=True, blank=True)
    address = models.TextField(blank=True)
    emergency_contact = models.CharField(max_length=180, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.get_full_name() or self.user.username


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
            ),
        ]
        ordering = ['-assigned_at']

    def clean(self):
        super().clean()

        if self.staff_id:
            staff_role = self.staff.role

            if (
                staff_role not in {
                    User.Role.STAFF,
                    User.Role.MANAGER,
                }
                and not self.staff.is_superuser
            ):
                raise ValidationError({
                    'staff': (
                        'Only staff members or managers can be assigned.'
                    )
                })

    def __str__(self):
        return f'{self.student} → {self.staff}'


# ============================================================
# ORGANIZATION AND JOB MODELS
# ============================================================

class JobType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    ssw_category_code = models.CharField(max_length=50, blank=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class TskKumiai(models.Model):
    name = models.CharField(max_length=180)
    address = models.TextField(blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=40, blank=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class TskContact(models.Model):
    organization = models.ForeignKey(
        TskKumiai,
        on_delete=models.CASCADE,
        related_name='contacts',
    )
    name = models.CharField(max_length=150)
    role = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=40, blank=True)

    def __str__(self):
        return f'{self.name} ({self.organization})'


class ReceivingCompany(models.Model):
    organization = models.ForeignKey(
        TskKumiai,
        on_delete=models.PROTECT,
        related_name='companies',
    )
    name = models.CharField(max_length=180)
    address = models.TextField(blank=True)
    business_sector = models.CharField(max_length=150, blank=True)
    email = models.EmailField(blank=True)
    pic_name = models.CharField(max_length=150, blank=True)
    pic_phone = models.CharField(max_length=40, blank=True)

    def __str__(self):
        return self.name


# ============================================================
# ORDER MODELS
# ============================================================

class Order(models.Model):
    class Kind(models.TextChoices):
        TO = 'TO', 'Training Order'
        JO = 'JO', 'Job Order'

    class Pathway(models.TextChoices):
        INTERNSHIP = 'INTERNSHIP', 'Internship'
        TOKUTEI = 'TOKUTEI', 'Tokutei Ginou'

    # Internal IJB order number
    code = models.CharField(
        max_length=80,
        unique=True,
    )

    # Original order information
    source_order_number = models.CharField(
        max_length=80,
        blank=True,
        help_text='Original order number from the uploaded TO/JO document.',
    )

    source_attachment = models.FileField(
        upload_to=order_source_path,
        blank=False,
        null=False,
        help_text='Original TO/JO document uploaded by staff.',
    )

    # Basic order information
    title = models.CharField(max_length=180)

    kind = models.CharField(
        max_length=2,
        choices=Kind.choices,
    )

    pathway = models.CharField(
        max_length=20,
        choices=Pathway.choices,
    )

    # Organization and company
    organization = models.ForeignKey(
        TskKumiai,
        on_delete=models.PROTECT,
    )

    company = models.ForeignKey(
        ReceivingCompany,
        on_delete=models.PROTECT,
    )

    job_type = models.ForeignKey(
        JobType,
        on_delete=models.PROTECT,
    )

    # Job information
    location = models.CharField(
        max_length=150,
        blank=True,
    )

    language_exam_required = models.CharField(
        max_length=30,
        default='JFT_A2_OR_JLPT_N4',
    )

    ssw_exam_required = models.BooleanField(default=False)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.code} - {self.title}'

    def clean(self):
        super().clean()

        expected_pathways = {
            self.Kind.TO: self.Pathway.INTERNSHIP,
            self.Kind.JO: self.Pathway.TOKUTEI,
        }

        expected_pathway = expected_pathways.get(self.kind)

        if expected_pathway and self.pathway != expected_pathway:
            raise ValidationError({
                'pathway': (
                    f'{self.get_kind_display()} must use '
                    f'{expected_pathway.label}.'
                )
            })


class StudentOrderAssignment(models.Model):
    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name='assignments',
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.PROTECT,
    )
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
    )
    assigned_at = models.DateTimeField(default=timezone.now)
    active = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['student', 'order'],
                name='unique_student_order',
            ),
        ]


# ============================================================
# EXAM MODELS
# ============================================================

class ExamRule(models.Model):
    code = models.CharField(max_length=40, unique=True)
    name = models.CharField(max_length=100)
    retake_wait_days = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text='Only enter a verified rule; leave blank for manual confirmation.',
    )
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


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

    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name='exam_attempts',
    )
    rule = models.ForeignKey(ExamRule, on_delete=models.PROTECT)
    order = models.ForeignKey(
        Order,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    reservation_date = models.DateField(null=True, blank=True)
    exam_date = models.DateField(null=True, blank=True)
    result_date = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=12,
        choices=Status.choices,
        default=Status.PLANNED,
    )
    score_or_level = models.CharField(max_length=80, blank=True)
    result_note = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='created_exam_attempts',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def earliest_retake_date(self):
        if (
            self.status != self.Status.FAILED
            or not self.result_date
            or self.rule.retake_wait_days is None
        ):
            return None

        from datetime import timedelta

        return self.result_date + timedelta(
            days=self.rule.retake_wait_days
        )


# ============================================================
# MEDICAL, INTERVIEW, OFFER AND PASSPORT MODELS
# ============================================================

class MedicalCheckup(models.Model):
    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name='medical_checks',
    )
    scheduled_at = models.DateTimeField(null=True, blank=True)
    facility = models.CharField(max_length=180, blank=True)
    status = models.CharField(max_length=40, default='SCHEDULED')
    result_note = models.TextField(blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
    )


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

    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name='interviews',
    )
    order = models.ForeignKey(Order, on_delete=models.PROTECT)
    mendan = models.ForeignKey(
        TskContact,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    scheduled_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=15,
        choices=Status.choices,
        default=Status.INVITED,
    )
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
    )
    created_at = models.DateTimeField(auto_now_add=True)


class Offer(models.Model):
    class Status(models.TextChoices):
        AVAILABLE = 'AVAILABLE', 'Available'
        SELECTED = 'SELECTED', 'Selected'
        NOT_SELECTED = 'NOT_SELECTED', 'Not selected'
        WITHDRAWN = 'WITHDRAWN', 'Withdrawn'
        EXPIRED = 'EXPIRED', 'Expired'

    interview = models.OneToOneField(
        Interview,
        on_delete=models.PROTECT,
        related_name='offer',
    )
    status = models.CharField(
        max_length=15,
        choices=Status.choices,
        default=Status.AVAILABLE,
    )
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

    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name='passport_cases',
    )
    pathway = models.CharField(
        max_length=20,
        choices=[
            ('INTERNSHIP', 'Internship'),
            ('TOKUTEI', 'Tokutei Ginou'),
        ],
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.NOT_STARTED,
    )
    appointment_at = models.DateTimeField(null=True, blank=True)
    request_date = models.DateField(null=True, blank=True)
    target_deadline = models.DateField(null=True, blank=True)
    submitted_at = models.DateField(null=True, blank=True)
    received_at = models.DateField(null=True, blank=True)
    recommendation_required = models.BooleanField(default=False)
    recommendation_status = models.CharField(max_length=30, blank=True)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
    )


# ============================================================
# DOCUMENT REQUIREMENTS
# ============================================================

class DocumentRequirement(models.Model):
    class Applicability(models.TextChoices):
        GENERAL = 'GENERAL', 'General'
        INTERNSHIP = 'INTERNSHIP', 'Internship'
        TOKUTEI = 'TOKUTEI', 'Tokutei Ginou'

    class Handling(models.TextChoices):
        STAFF_PREPARED = 'STAFF_PREPARED', 'Staff prepared'
        STUDENT_PROVIDED = 'STUDENT_PROVIDED', 'Student provided'
        EXTERNAL_PROCESS = 'EXTERNAL_PROCESS', 'External process'
        EXTERNAL_PREPARATION = (
            'EXTERNAL_PREPARATION',
            'External preparation',
        )

    code = models.CharField(max_length=60, unique=True)
    name = models.CharField(max_length=220)
    japanese_name = models.CharField(max_length=300, blank=True)
    form_reference = models.CharField(max_length=40, blank=True)

    # Retained temporarily for backward compatibility.
    pathway = models.CharField(
        max_length=20,
        choices=Applicability.choices,
        blank=True,
    )

    applicability = models.CharField(
        max_length=20,
        choices=Applicability.choices,
        default=Applicability.GENERAL,
    )
    handling = models.CharField(
        max_length=24,
        choices=Handling.choices,
        default=Handling.STAFF_PREPARED,
    )

    required = models.BooleanField(default=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.name} {self.form_reference}'.strip()


# ============================================================
# STUDENT WORKFLOW
# ============================================================

class StudentWorkflowItem(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        IN_PROGRESS = 'IN_PROGRESS', 'In Progress'
        SUBMITTED = 'SUBMITTED', 'Submitted'
        APPROVED = 'APPROVED', 'Approved'
        REJECTED = 'REJECTED', 'Rejected'

    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name='workflow_items',
    )
    requirement = models.ForeignKey(
        DocumentRequirement,
        on_delete=models.PROTECT,
        related_name='workflow_items',
    )
    status = models.CharField(
        max_length=12,
        choices=Status.choices,
        default=Status.PENDING,
    )
    due_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='updated_workflow_items',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['student', 'requirement'],
                name='unique_student_workflow_requirement',
            ),
        ]
        ordering = ['student_id', 'requirement__name']

    def __str__(self):
        return f'{self.student} - {self.requirement.name}'


class WorkflowItemOrderSource(models.Model):
    workflow_item = models.ForeignKey(
        StudentWorkflowItem,
        on_delete=models.CASCADE,
        related_name='order_sources',
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.PROTECT,
        related_name='workflow_item_sources',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['workflow_item', 'order'],
                name='unique_workflow_item_order_source',
            ),
        ]
        ordering = ['created_at']

    def __str__(self):
        return f'{self.workflow_item} ← {self.order}'


# ============================================================
# STUDENT DOCUMENTS
# ============================================================

class StudentDocument(models.Model):
    class Status(models.TextChoices):
        REQUESTED = 'REQUESTED', 'Requested'
        UPLOADED = 'UPLOADED', 'Uploaded'
        REVIEW = 'REVIEW', 'Under review'
        ACCEPTED = 'ACCEPTED', 'Accepted'
        REJECTED = 'REJECTED', 'Rejected'
        EXPIRED = 'EXPIRED', 'Expired'

    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name='documents',
    )
    requirement = models.ForeignKey(
        DocumentRequirement,
        on_delete=models.PROTECT,
    )
    file = models.FileField(
        upload_to=student_document_path,
        validators=[
            FileExtensionValidator(['pdf', 'jpg', 'jpeg', 'png']),
        ],
        blank=True,
    )
    version = models.PositiveIntegerField(default=1)
    status = models.CharField(
        max_length=12,
        choices=Status.choices,
        default=Status.REQUESTED,
    )
    visible_to_student = models.BooleanField(default=False)
    due_date = models.DateField(null=True, blank=True)
    review_note = models.TextField(blank=True)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='uploaded_student_documents',
    )
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='reviewed_student_documents',
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    workflow_item = models.OneToOneField(
        StudentWorkflowItem,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='student_document',
    )

    class Meta:
        ordering = ['requirement__name', '-version']


# ============================================================
# DOCUMENT VERSION HISTORY
# ============================================================

class DocumentVersion(models.Model):
    class SourceType(models.TextChoices):
        STUDENT_UPLOAD = 'STUDENT_UPLOAD', 'Student upload'
        STAFF_UPLOAD = 'STAFF_UPLOAD', 'Staff upload'
        GENERATED = 'GENERATED', 'Generated'
        CORRECTED_UPLOAD = 'CORRECTED_UPLOAD', 'Corrected upload'

    student_document = models.ForeignKey(
        StudentDocument,
        on_delete=models.CASCADE,
        related_name='versions',
    )
    version_number = models.PositiveIntegerField()

    file = models.FileField(
        upload_to=document_version_path,
        validators=[
            FileExtensionValidator(['docx', 'pdf', 'jpg', 'jpeg', 'png']),
        ],
    )
    pdf_file = models.FileField(
        upload_to=document_version_path,
        validators=[
            FileExtensionValidator(['pdf']),
        ],
        blank=True,
    )

    source_type = models.CharField(
        max_length=24,
        choices=SourceType.choices,
    )
    template_version = models.ForeignKey(
        'DocumentTemplateVersion',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='generated_documents',
    )
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='uploaded_document_versions',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['student_document', 'version_number'],
                name='unique_student_document_version',
            ),
        ]
        ordering = ['student_document_id', 'version_number']

    def __str__(self):
        return f'{self.student_document} - v{self.version_number}'


# ============================================================
# DOCUMENT TEMPLATES
# ============================================================

class DocumentTemplate(models.Model):
    requirement = models.ForeignKey(
        DocumentRequirement,
        on_delete=models.PROTECT,
        related_name='templates',
    )
    name = models.CharField(max_length=220)
    description = models.TextField(blank=True)
    active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='created_document_templates',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['requirement__name', 'name']

    def __str__(self):
        return f'{self.requirement.name} - {self.name}'


class DocumentTemplateVersion(models.Model):
    template = models.ForeignKey(
        DocumentTemplate,
        on_delete=models.PROTECT,
        related_name='versions',
    )
    version_number = models.PositiveIntegerField()

    file = models.FileField(
        upload_to=document_template_version_path,
        validators=[
            FileExtensionValidator(['docx']),
        ],
    )
    field_mapping = models.JSONField(default=dict, blank=True)
    active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='created_document_template_versions',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    change_notes = models.TextField(blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['template', 'version_number'],
                name='unique_document_template_version',
            ),
        ]
        ordering = ['template_id', 'version_number']

    def __str__(self):
        return f'{self.template.name} - v{self.version_number}'


# ============================================================
# KEMENAKER BATCH MANAGEMENT
# ============================================================

class KemenakerBatch(models.Model):
    class Stage(models.TextChoices):
        PREPARATION = 'PREPARATION', 'Preparation'
        REGISTRATION = 'REGISTRATION', 'Registration'
        INVITATION = 'INVITATION', 'Invitation'
        ACCEPTANCE = 'ACCEPTANCE', 'Acceptance'
        SUBMISSION = 'SUBMISSION', 'Submission'
        VERIFICATION = 'VERIFICATION', 'Verification'
        COMPLETED = 'COMPLETED', 'Completed'

    receiving_company = models.ForeignKey(
        ReceivingCompany,
        on_delete=models.PROTECT,
        related_name='kemenaker_batches',
    )
    name = models.CharField(max_length=180)
    reference_code = models.CharField(
        max_length=255,
        unique=True,
        editable=False,
    )
    batch_date = models.DateField(null=True, blank=True)
    stage = models.CharField(
        max_length=20,
        choices=Stage.choices,
        default=Stage.PREPARATION,
    )
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='created_kemenaker_batches',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.reference_code} - {self.name}'


class KemenakerBatchStudent(models.Model):
    class RegistrationStatus(models.TextChoices):
        NOT_STARTED = 'NOT_STARTED', 'Not started'
        APPLICATION_CREATED = 'APPLICATION_CREATED', 'Application created'
        REGISTERED = 'REGISTERED', 'Registered'

    class InvitationStatus(models.TextChoices):
        NOT_SENT = 'NOT_SENT', 'Not sent'
        SENT = 'SENT', 'Sent'

    class AcceptanceStatus(models.TextChoices):
        NOT_STARTED = 'NOT_STARTED', 'Not started'
        PENDING = 'PENDING', 'Pending'
        ACCEPTED = 'ACCEPTED', 'Accepted'
        DECLINED = 'DECLINED', 'Declined'

    class SubmissionStatus(models.TextChoices):
        NOT_READY = 'NOT_READY', 'Not ready'
        READY = 'READY', 'Ready for submission'
        SUBMITTED = 'SUBMITTED', 'Submitted'

    class VerificationStatus(models.TextChoices):
        NOT_SUBMITTED = 'NOT_SUBMITTED', 'Not submitted'
        UNDER_REVIEW = 'UNDER_REVIEW', 'Under review'
        VERIFIED = 'VERIFIED', 'Verified'
        REJECTED = 'REJECTED', 'Rejected'

    batch = models.ForeignKey(
        KemenakerBatch,
        on_delete=models.CASCADE,
        related_name='students',
    )
    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.PROTECT,
        related_name='kemenaker_batch_records',
    )

    registration_status = models.CharField(
        max_length=24,
        choices=RegistrationStatus.choices,
        default=RegistrationStatus.NOT_STARTED,
    )
    invitation_status = models.CharField(
        max_length=12,
        choices=InvitationStatus.choices,
        default=InvitationStatus.NOT_SENT,
    )
    acceptance_status = models.CharField(
        max_length=12,
        choices=AcceptanceStatus.choices,
        default=AcceptanceStatus.NOT_STARTED,
    )
    submission_status = models.CharField(
        max_length=12,
        choices=SubmissionStatus.choices,
        default=SubmissionStatus.NOT_READY,
    )
    verification_status = models.CharField(
        max_length=16,
        choices=VerificationStatus.choices,
        default=VerificationStatus.NOT_SUBMITTED,
    )

    accepted_at = models.DateTimeField(null=True, blank=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    verified_at = models.DateTimeField(null=True, blank=True)

    progress_notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['batch', 'student'],
                name='unique_kemenaker_batch_student',
            ),
        ]
        ordering = ['batch_id', 'student_id']

    def __str__(self):
        return f'{self.batch.reference_code} - {self.student}'


class KemenakerBatchEvent(models.Model):
    class EventType(models.TextChoices):
        INVITATIONS_SENT = 'INVITATIONS_SENT', 'Invitations sent'
        STAGE_CHANGED = 'STAGE_CHANGED', 'Stage changed'
        BATCH_SUBMITTED = 'BATCH_SUBMITTED', 'Batch submitted'
        OTHER = 'OTHER', 'Other'

    batch = models.ForeignKey(
        KemenakerBatch,
        on_delete=models.CASCADE,
        related_name='events',
    )
    event_type = models.CharField(
        max_length=24,
        choices=EventType.choices,
    )
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='kemenaker_batch_events',
    )
    details = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return (
            f'{self.batch.reference_code} - '
            f'{self.get_event_type_display()}'
        )


# ============================================================
# CALENDAR EVENTS
# ============================================================

class CalendarEvent(models.Model):
    class Kind(models.TextChoices):
        EXAM = 'EXAM', 'Exam'
        PASSPORT = 'PASSPORT', 'Passport'
        MEDICAL = 'MEDICAL', 'Medical'
        INTERVIEW = 'INTERVIEW', 'Interview'
        OTHER = 'OTHER', 'Other'

    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name='events',
    )
    title = models.CharField(max_length=180)
    kind = models.CharField(
        max_length=12,
        choices=Kind.choices,
        default=Kind.OTHER,
    )
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField(null=True, blank=True)
    location = models.CharField(max_length=180, blank=True)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
    )
    google_event_id = models.CharField(max_length=200, blank=True)
    sync_status = models.CharField(
        max_length=30,
        default='NOT_CONNECTED',
    )
    created_at = models.DateTimeField(auto_now_add=True)


# ============================================================
# SUPPORT TICKETS AND REPLIES
# ============================================================

class SupportTicket(models.Model):
    class Status(models.TextChoices):
        OPEN = 'OPEN', 'Open'
        ASSIGNED = 'ASSIGNED', 'Assigned'
        WAITING = 'WAITING', 'Waiting for student'
        PROGRESS = 'PROGRESS', 'In progress'
        RESOLVED = 'RESOLVED', 'Resolved'
        CLOSED = 'CLOSED', 'Closed'

    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name='tickets',
    )
    subject = models.CharField(max_length=180)
    category = models.CharField(max_length=50, default='DOCUMENT')
    description = models.TextField()
    status = models.CharField(
        max_length=12,
        choices=Status.choices,
        default=Status.OPEN,
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tickets',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class TicketReply(models.Model):
    ticket = models.ForeignKey(
        SupportTicket,
        on_delete=models.CASCADE,
        related_name='replies',
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
    )
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_internal = models.BooleanField(default=False)


# ============================================================
# TSK VISITS AND PLACEMENT COMMUNICATIONS
# ============================================================

class TskVisit(models.Model):
    organization = models.ForeignKey(
        TskKumiai,
        on_delete=models.PROTECT,
    )
    pic_name = models.CharField(max_length=150, blank=True)
    visit_at = models.DateTimeField()
    purpose = models.CharField(max_length=180)
    host_staff = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
    )
    attendees = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    follow_up_due = models.DateField(null=True, blank=True)


class PlacementCommunication(models.Model):
    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name='communications',
    )
    organization = models.ForeignKey(
        TskKumiai,
        on_delete=models.PROTECT,
    )
    company = models.ForeignKey(
        ReceivingCompany,
        on_delete=models.PROTECT,
    )
    recipient_group = models.CharField(max_length=180)
    sent_at = models.DateTimeField(null=True, blank=True)
    sent_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
    )
    summary = models.TextField(blank=True)
    confirmation_status = models.CharField(
        max_length=40,
        default='PENDING',
    )


# ============================================================
# AUDIT LOG
# ============================================================

class AuditLog(models.Model):
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
    )
    action = models.CharField(max_length=100)
    object_type = models.CharField(max_length=100)
    object_id = models.CharField(max_length=80)
    details = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
