from datetime import date
from django.test import TestCase, Client
from django.urls import reverse
from .models import User, StudentProfile, ExamRule, ExamAttempt, TskKumiai, ReceivingCompany, JobType, Order, Interview, Offer, StaffRegistrationCode
from .services import select_offer

class PortalAccessTests(TestCase):
    def setUp(self):
        self.student = User.objects.create_user(username='student1', password='Strong-test-pass-123', role='STUDENT')
        self.profile = StudentProfile.objects.create(user=self.student)
        self.other = User.objects.create_user(username='student2', password='Strong-test-pass-123', role='STUDENT')
        self.other_profile = StudentProfile.objects.create(user=self.other)
    def test_student_dashboard_only_shows_own_scope(self):
        self.client.login(username='student1', password='Strong-test-pass-123')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['profile'].pk, self.profile.pk)
    def test_staff_registration_code_is_required(self):
        response = self.client.post(reverse('register'), {'username':'badstaff','first_name':'Staff','email':'staff@example.com','role':'STAFF','staff_code':'wrong','password1':'Strong-test-pass-123!','password2':'Strong-test-pass-123!'})
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username='badstaff').exists())

    def test_valid_staff_invitation_is_one_time_and_never_superuser(self):
        raw = 'IJB-ABCD-2345'
        admin_user = User.objects.create_superuser(username='root', email='root@example.com', password='Strong-test-pass-123!')
        StaffRegistrationCode.objects.create(code_hash=StaffRegistrationCode.hash_code(raw), created_by=admin_user)
        response = self.client.post(reverse('register'), {'username':'newstaff','first_name':'New','email':'newstaff@example.com','role':'STAFF','staff_code':raw,'password1':'Strong-test-pass-123!','password2':'Strong-test-pass-123!'})
        self.assertEqual(response.status_code, 302)
        staff = User.objects.get(username='newstaff')
        self.assertTrue(staff.is_staff)
        self.assertFalse(staff.is_superuser)
        invitation = StaffRegistrationCode.objects.get(used_by=staff)
        self.assertIsNotNone(invitation.used_at)

class OfferSelectionTests(TestCase):
    def setUp(self):
        self.staff = User.objects.create_user(username='staff', password='Strong-test-pass-123', role='STAFF')
        self.student = User.objects.create_user(username='candidate', password='Strong-test-pass-123', role='STUDENT')
        self.profile = StudentProfile.objects.create(user=self.student)
        org = TskKumiai.objects.create(name='Test Kumiai')
        company = ReceivingCompany.objects.create(organization=org, name='Test Company')
        job = JobType.objects.create(name='Test Job')
        order = Order.objects.create(code='TO-001', title='Test role', kind='TO', pathway='INTERNSHIP', organization=org, company=company, job_type=job)
        self.i1 = Interview.objects.create(student=self.profile, order=order, status='PASSED', created_by=self.staff)
        self.i2 = Interview.objects.create(student=self.profile, order=order, status='PASSED', created_by=self.staff)
        self.o1 = Offer.objects.create(interview=self.i1)
        self.o2 = Offer.objects.create(interview=self.i2)
    def test_selecting_another_offer_preserves_history(self):
        select_offer(offer_id=self.o1.pk, actor=self.staff)
        select_offer(offer_id=self.o2.pk, actor=self.staff, reason='Student choice')
        self.o1.refresh_from_db(); self.o2.refresh_from_db()
        self.assertEqual(self.o1.status, Offer.Status.NOT_SELECTED)
        self.assertEqual(self.o2.status, Offer.Status.SELECTED)
        self.assertEqual(Interview.objects.filter(student=self.profile).count(), 2)
    def test_failed_interview_cannot_be_selected(self):
        self.i2.status = 'FAILED'; self.i2.save()
        with self.assertRaises(ValueError): select_offer(offer_id=self.o2.pk, actor=self.staff)
