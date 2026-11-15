
from django.contrib.admin import AdminSite

from . import models


class IJBAdminSite(AdminSite):
    site_header = 'IJB Student Portal'
    site_title = 'IJB Portal Admin'
    index_title = 'Manajemen Operasional LPK'

    index_template = 'admin/ijb_index.html'

    MODULE_GROUPS = {
        'StudentProfile': 'Student Management',
        'StudentDocument': 'Student Management',
        'DocumentRequirement': 'Student Management',
        'StudentOrderAssignment': 'Student Management',
        'StudentStaffAssignment': 'Student Management',

        'Order': 'Training & Placement',
        'JobType': 'Training & Placement',
        'ReceivingCompany': 'Training & Placement',
        'Interview': 'Training & Placement',
        'Offer': 'Training & Placement',
        'ExamAttempt': 'Training & Placement',
        'ExamRule': 'Training & Placement',
        'MedicalCheckup': 'Training & Placement',
        'PassportCase': 'Training & Placement',
        'PlacementCommunication': 'Training & Placement',
        'TskKumiai': 'Training & Placement',
        'TskContact': 'Training & Placement',
        'TskVisit': 'Training & Placement',

        'User': 'Administration & Support',
        'StaffRegistrationCode': 'Administration & Support',
        'SupportTicket': 'Administration & Support',
        'TicketReply': 'Administration & Support',
        'CalendarEvent': 'Administration & Support',
        'AuditLog': 'Administration & Support',
    }

    MODULE_DESCRIPTIONS = {
        'Student Management': (
            'Manage student profiles, documents, requirements, '
            'and staff assignments.'
        ),
        'Training & Placement': (
            'Manage training orders, companies, examinations, '
            'interviews, and placement.'
        ),
        'Administration & Support': (
            'Manage users, staff access, support requests, '
            'calendar events, and audit records.'
        ),
        'Other Management': (
            'Other registered operational modules.'
        ),
    }

    def has_permission(self, request):
        user = request.user

        return (
            user.is_active
            and user.is_authenticated
            and (
                user.is_superuser
                or user.role == 'MANAGER'
            )
        )

    def index(self, request, extra_context=None):
        extra_context = extra_context or {}

        extra_context.update({
            'student_count': models.User.objects.filter(
                role='STUDENT',
                is_active=True,
            ).count(),

            'staff_count': models.User.objects.filter(
                role='STAFF',
                is_active=True,
            ).count(),

            'document_count': models.StudentDocument.objects.count(),

            'order_count': models.Order.objects.count(),

            'interview_count': models.Interview.objects.count(),

            'ticket_count': models.SupportTicket.objects.count(),
        })

        # Build module groups from models Django says this user can access.
        app_list = self.get_app_list(request)

        group_order = [
            'Student Management',
            'Training & Placement',
            'Administration & Support',
            'Other Management',
        ]

        groups = {
            name: {
                'title': name,
                'description': self.MODULE_DESCRIPTIONS[name],
                'models': [],
            }
            for name in group_order
        }

        for app in app_list:
            for model_admin in app['models']:
                object_name = model_admin['object_name']

                group_name = self.MODULE_GROUPS.get(
                    object_name,
                    'Other Management',
                )

                model_admin['icon'] = '▦'

                groups[group_name]['models'].append(model_admin)

        extra_context['management_groups'] = [
            groups[name]
            for name in group_order
            if groups[name]['models']
        ]

        return super().index(request, extra_context)


ijb_admin_site = IJBAdminSite(name='ijb_admin')
