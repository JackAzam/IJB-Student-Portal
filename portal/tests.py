from django.contrib.auth.models import Group, Permission
from django.test import TestCase
from django.urls import reverse

from .models import (
    User,
    StudentProfile,
    StudentStaffAssignment,
    ExamRule,
    ExamAttempt,
    TskKumiai,
    ReceivingCompany,
    JobType,
    Order,
    Interview,
    Offer,
    StaffRegistrationCode,
    DocumentRequirement,
    StudentDocument,
    CalendarEvent,
    SupportTicket,
)

from .services import select_offer


class PortalAccessTests(TestCase):

    def setUp(self):
        self.student = User.objects.create_user(
            username='student1',
            password='Strong-test-pass-123',
            role='STUDENT',
        )
        self.profile = StudentProfile.objects.create(
            user=self.student
        )

        self.other = User.objects.create_user(
            username='student2',
            password='Strong-test-pass-123',
            role='STUDENT',
        )
        self.other_profile = StudentProfile.objects.create(
            user=self.other
        )

    def test_student_dashboard_only_shows_own_scope(self):
        self.client.login(
            username='student1',
            password='Strong-test-pass-123',
        )

        response = self.client.get(reverse('dashboard'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context['profile'].pk,
            self.profile.pk,
        )

    def test_staff_registration_code_is_required(self):
        response = self.client.post(
            reverse('register'),
            {
                'username': 'badstaff',
                'first_name': 'Staff',
                'email': 'staff@example.com',
                'role': 'STAFF',
                'staff_code': 'wrong',
                'password1': 'Strong-test-pass-123!',
                'password2': 'Strong-test-pass-123!',
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            User.objects.filter(username='badstaff').exists()
        )

    def test_valid_staff_invitation_is_one_time_and_never_superuser(self):
        raw = 'IJB-ABCD-2345'

        admin_user = User.objects.create_superuser(
            username='root',
            email='root@example.com',
            password='Strong-test-pass-123!',
        )

        StaffRegistrationCode.objects.create(
            code_hash=StaffRegistrationCode.hash_code(raw),
            created_by=admin_user,
        )

        response = self.client.post(
            reverse('register'),
            {
                'username': 'newstaff',
                'first_name': 'New',
                'email': 'newstaff@example.com',
                'role': 'STAFF',
                'staff_code': raw,
                'password1': 'Strong-test-pass-123!',
                'password2': 'Strong-test-pass-123!',
            },
        )

        self.assertEqual(response.status_code, 302)

        staff = User.objects.get(username='newstaff')

        self.assertEqual(staff.role, 'STAFF')
        self.assertTrue(staff.is_staff)
        self.assertFalse(staff.is_superuser)

        invitation = StaffRegistrationCode.objects.get(
            used_by=staff
        )
        self.assertIsNotNone(invitation.used_at)

    def test_superuser_automatically_gets_manager_role(self):
        manager = User.objects.create_superuser(
            username='root',
            email='root@example.com',
            password='Strong-test-pass-123!',
        )

        manager.refresh_from_db()

        self.assertEqual(manager.role, 'MANAGER')
        self.assertTrue(manager.is_staff)
        self.assertTrue(manager.is_superuser)

    def test_student_registration_automatically_creates_profile(self):
        response = self.client.post(
            reverse('register'),
            {
                'username': 'newstudent',
                'first_name': 'New',
                'last_name': 'Student',
                'email': 'newstudent@example.com',
                'phone': '08123456789',
                'role': 'STUDENT',
                'password1': 'Strong-test-pass-123!',
                'password2': 'Strong-test-pass-123!',
            },
        )

        self.assertEqual(response.status_code, 302)

        student = User.objects.get(username='newstudent')

        self.assertEqual(student.role, 'STUDENT')
        self.assertTrue(
            StudentProfile.objects.filter(user=student).exists()
        )

    def test_student_document_download_permissions(self):
        requirement = DocumentRequirement.objects.create(
            code='PASSPORT_TEST',
            name='Passport Test',
        )

        # Document belonging to another student.
        other_document = StudentDocument.objects.create(
            student=self.other_profile,
            requirement=requirement,
            uploaded_by=self.other,
            visible_to_student=True,
        )

        # Own document, but not visible to the student.
        hidden_document = StudentDocument.objects.create(
            student=self.profile,
            requirement=requirement,
            uploaded_by=self.student,
            visible_to_student=False,
        )

        # Own document, visible to the student.
        visible_document = StudentDocument.objects.create(
            student=self.profile,
            requirement=requirement,
            uploaded_by=self.student,
            visible_to_student=True,
        )

        self.client.login(
            username='student1',
            password='Strong-test-pass-123',
        )

        # Cannot access another student's document.
        response = self.client.get(
            reverse('document_download', args=[other_document.pk])
        )
        self.assertEqual(response.status_code, 403)

        # Cannot access own hidden document.
        response = self.client.get(
            reverse('document_download', args=[hidden_document.pk])
        )
        self.assertEqual(response.status_code, 403)

        # Visible own document passes permission checks,
        # but has no uploaded file in this test.
        response = self.client.get(
            reverse('document_download', args=[visible_document.pk])
        )
        self.assertEqual(response.status_code, 404)


class OfferSelectionTests(TestCase):

    def setUp(self):
        self.staff = User.objects.create_user(
            username='staff',
            password='Strong-test-pass-123',
            role='STAFF',
        )

        self.student = User.objects.create_user(
            username='candidate',
            password='Strong-test-pass-123',
            role='STUDENT',
        )

        self.profile = StudentProfile.objects.create(
            user=self.student
        )

        org = TskKumiai.objects.create(
            name='Test Kumiai'
        )

        company = ReceivingCompany.objects.create(
            organization=org,
            name='Test Company',
        )

        job = JobType.objects.create(
            name='Test Job'
        )

        order = Order.objects.create(
            code='TO-001',
            title='Test role',
            kind='TO',
            pathway='INTERNSHIP',
            organization=org,
            company=company,
            job_type=job,
        )

        self.i1 = Interview.objects.create(
            student=self.profile,
            order=order,
            status='PASSED',
            created_by=self.staff,
        )

        self.i2 = Interview.objects.create(
            student=self.profile,
            order=order,
            status='PASSED',
            created_by=self.staff,
        )

        self.o1 = Offer.objects.create(
            interview=self.i1
        )

        self.o2 = Offer.objects.create(
            interview=self.i2
        )

    def test_selecting_another_offer_preserves_history(self):
        select_offer(
            offer_id=self.o1.pk,
            actor=self.staff,
        )

        select_offer(
            offer_id=self.o2.pk,
            actor=self.staff,
            reason='Student choice',
        )

        self.o1.refresh_from_db()
        self.o2.refresh_from_db()

        self.assertEqual(
            self.o1.status,
            Offer.Status.NOT_SELECTED,
        )

        self.assertEqual(
            self.o2.status,
            Offer.Status.SELECTED,
        )

        self.assertEqual(
            Interview.objects.filter(
                student=self.profile
            ).count(),
            2,
        )

    def test_failed_interview_cannot_be_selected(self):
        self.i2.status = 'FAILED'
        self.i2.save()

        with self.assertRaises(ValueError):
            select_offer(
                offer_id=self.o2.pk,
                actor=self.staff,
            )
class StaffAssignmentAccessTests(TestCase):

    def setUp(self):
        from django.utils import timezone
        from datetime import timedelta

        self.staff = User.objects.create_user(
            username='assigned_staff',
            password='Strong-test-pass-123',
            role='STAFF',
        )
        self.manager = User.objects.create_user(
            username='manager',
            password='Strong-test-pass-123',
            role='MANAGER',
        )

        self.student = User.objects.create_user(
            username='assigned_student',
            password='Strong-test-pass-123',
            role='STUDENT',
        )
        self.profile = StudentProfile.objects.create(user=self.student)

        self.other_student = User.objects.create_user(
            username='unassigned_student',
            password='Strong-test-pass-123',
            role='STUDENT',
        )
        self.other_profile = StudentProfile.objects.create(
            user=self.other_student,
        )

        self.assignment = StudentStaffAssignment.objects.create(
            student=self.profile,
            staff=self.staff,
            assigned_by=self.manager,
        )

        self.requirement = DocumentRequirement.objects.create(
            code='TEST-DOC',
            name='Test Document',
        )

        self.assigned_event = CalendarEvent.objects.create(
            student=self.profile,
            title='Assigned student event',
            starts_at=timezone.now() + timedelta(days=2),
            created_by=self.manager,
        )
        self.other_event = CalendarEvent.objects.create(
            student=self.other_profile,
            title='Other student event',
            starts_at=timezone.now() + timedelta(days=2),
            created_by=self.manager,
        )

        self.assigned_ticket = SupportTicket.objects.create(
            student=self.profile,
            subject='Assigned student ticket',
            description='Test ticket',
        )
        self.other_ticket = SupportTicket.objects.create(
            student=self.other_profile,
            subject='Other student ticket',
            description='Test ticket',
        )

        self.assigned_document = StudentDocument.objects.create(
            student=self.profile,
            requirement=self.requirement,
            uploaded_by=self.manager,
        )
        self.other_document = StudentDocument.objects.create(
            student=self.other_profile,
            requirement=self.requirement,
            uploaded_by=self.manager,
        )

    def login_staff(self):
        self.client.login(
            username='assigned_staff',
            password='Strong-test-pass-123',
        )

    def test_staff_dashboard_counts_only_assigned_students(self):
        self.login_staff()
        response = self.client.get(reverse('dashboard'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['student_count'], 1)

    def test_staff_sees_only_assigned_student_events(self):
        self.login_staff()
        response = self.client.get(reverse('events'))

        self.assertEqual(response.status_code, 200)
        visible_ids = set(
            response.context['items'].values_list('id', flat=True)
        )
        self.assertIn(self.assigned_event.id, visible_ids)
        self.assertNotIn(self.other_event.id, visible_ids)

    def test_staff_sees_only_assigned_student_tickets(self):
        self.login_staff()
        response = self.client.get(reverse('tickets'))

        self.assertEqual(response.status_code, 200)
        visible_ids = set(
            response.context['items'].values_list('id', flat=True)
        )
        self.assertIn(self.assigned_ticket.id, visible_ids)
        self.assertNotIn(self.other_ticket.id, visible_ids)

    def test_staff_sees_only_assigned_student_documents(self):
        self.login_staff()
        response = self.client.get(reverse('documents'))

        self.assertEqual(response.status_code, 200)
        visible_ids = set(
            response.context['items'].values_list('id', flat=True)
        )
        self.assertIn(self.assigned_document.id, visible_ids)
        self.assertNotIn(self.other_document.id, visible_ids)

    def test_inactive_assignment_revokes_staff_access(self):
        self.assignment.active = False
        self.assignment.save(update_fields=['active'])

        self.login_staff()
        response = self.client.get(reverse('dashboard'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['student_count'], 0)
    def test_staff_cannot_download_unassigned_student_document(self):
        self.login_staff()

        response = self.client.get(
            reverse(
                'document_download',
                kwargs={'pk': self.other_document.pk},
            )
        )

        self.assertEqual(response.status_code, 403)

    def test_manager_can_see_all_students_and_their_records(self):
        self.client.login(
            username='manager',
            password='Strong-test-pass-123',
        )

        dashboard_response = self.client.get(reverse('dashboard'))
        events_response = self.client.get(reverse('events'))
        tickets_response = self.client.get(reverse('tickets'))
        documents_response = self.client.get(reverse('documents'))

        self.assertEqual(dashboard_response.status_code, 200)
        self.assertEqual(
            dashboard_response.context['student_count'],
            2,
        )

        self.assertIn(
            self.other_event.id,
            events_response.context['items'].values_list('id', flat=True),
        )
        self.assertIn(
            self.other_ticket.id,
            tickets_response.context['items'].values_list('id', flat=True),
        )
        self.assertIn(
            self.other_document.id,
            documents_response.context['items'].values_list('id', flat=True),
        )

    def test_student_can_be_assigned_to_multiple_staff(self):
        second_staff = User.objects.create_user(
            username='second_staff',
            password='Strong-test-pass-123',
            role=User.Role.STAFF,
        )

        second_assignment = StudentStaffAssignment.objects.create(
            student=self.profile,
            staff=second_staff,
            assigned_by=self.manager,
        )

        assignments = StudentStaffAssignment.objects.filter(
            student=self.profile,
            active=True,
        )

        self.assertEqual(assignments.count(), 2)

        self.assertTrue(
            assignments.filter(staff=self.staff).exists()
        )
        self.assertTrue(
            assignments.filter(staff=second_staff).exists()
        )

class AdminRoleAccessTests(TestCase):

    def setUp(self):
        self.manager = User.objects.create_user(
            username='admin_manager',
            password='Strong-test-pass-123',
            role='MANAGER',
        )

        self.staff = User.objects.create_user(
            username='admin_staff',
            password='Strong-test-pass-123',
            role='STAFF',
            is_staff=True,
        )

        self.superuser = User.objects.create_superuser(
            username='admin_root',
            email='root@example.com',
            password='Strong-test-pass-123!',
        )

        manager_group = Group.objects.get(name='LPK Managers')

        student_profile_permission = Permission.objects.get(
            content_type__app_label='portal',
            codename='view_studentprofile',
        )

        manager_group.permissions.add(student_profile_permission)

    def test_manager_can_access_admin_and_operational_records(self):
        self.client.force_login(self.manager)

        index_response = self.client.get(
            reverse('ijb_admin:index')
        )
        records_response = self.client.get(
            reverse('ijb_admin:portal_studentprofile_changelist')
        )

        self.assertEqual(index_response.status_code, 200)
        self.assertEqual(records_response.status_code, 200)

    def test_manager_cannot_manage_users(self):
        self.client.force_login(self.manager)

        response = self.client.get(
            reverse('ijb_admin:portal_user_changelist')
        )

        self.assertEqual(response.status_code, 403)

    def test_manager_cannot_manage_staff_registration_codes(self):
        self.client.force_login(self.manager)

        response = self.client.get(
            reverse('ijb_admin:portal_staffregistrationcode_changelist')
        )

        self.assertEqual(response.status_code, 403)

    def test_staff_cannot_access_admin(self):
        self.client.force_login(self.staff)

        response = self.client.get(
            reverse('ijb_admin:index')
        )

        self.assertNotEqual(response.status_code, 200)

    def test_superuser_can_manage_users_and_registration_codes(self):
        self.client.force_login(self.superuser)

        user_response = self.client.get(
            reverse('ijb_admin:portal_user_changelist')
        )
        code_response = self.client.get(
            reverse('ijb_admin:portal_staffregistrationcode_changelist')
        )

        self.assertEqual(user_response.status_code, 200)
        self.assertEqual(code_response.status_code, 200)

    def test_student_cannot_access_admin(self):
        student = User.objects.create_user(
            username='admin_student',
            password='Strong-test-pass-123',
            role='STUDENT',
        )

        self.client.force_login(student)

        response = self.client.get(
            reverse('ijb_admin:index')
        )

        self.assertNotEqual(response.status_code, 200)

    def test_manager_has_read_only_audit_log_permission(self):
        audit_view_permission = Permission.objects.get(
            content_type__app_label='portal',
            codename='view_auditlog',
        )

        manager_group = Group.objects.get(name='LPK Managers')
        manager_group.permissions.add(audit_view_permission)

        self.assertTrue(
            self.manager.has_perm('portal.view_auditlog')
        )
        self.assertFalse(
            self.manager.has_perm('portal.add_auditlog')
        )
        self.assertFalse(
            self.manager.has_perm('portal.change_auditlog')
        )
        self.assertFalse(
            self.manager.has_perm('portal.delete_auditlog')
        )

class UserGroupSynchronizationTests(TestCase):

    def test_role_transitions_synchronize_groups(self):
        Group.objects.get_or_create(name='LPK Staff')
        Group.objects.get_or_create(name='LPK Managers')

        user = User.objects.create_user(
            username='role_transition',
            password='Strong-test-pass-123',
            role=User.Role.STAFF,
        )
        staff_group = Group.objects.get(name='LPK Staff')
        manager_group = Group.objects.get(name='LPK Managers')

        # STAFF belongs to LPK Staff.
        self.assertTrue(
            user.groups.filter(pk=staff_group.pk).exists()
        )
        self.assertFalse(
            user.groups.filter(pk=manager_group.pk).exists()
        )

        # Changing to MANAGER moves the user to LPK Managers.
        user.role = User.Role.MANAGER
        user.save()

        self.assertFalse(
            user.groups.filter(pk=staff_group.pk).exists()
        )
        self.assertTrue(
            user.groups.filter(pk=manager_group.pk).exists()
        )

        # Changing to STUDENT removes both operational groups.
        user.role = User.Role.STUDENT
        user.save()

        self.assertFalse(
            user.groups.filter(pk=staff_group.pk).exists()
        )
        self.assertFalse(
            user.groups.filter(pk=manager_group.pk).exists()
        )