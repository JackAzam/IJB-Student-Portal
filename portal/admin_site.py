
from django.contrib.admin import AdminSite


class IJBAdminSite(AdminSite):
    site_header = 'IJB Student Portal'
    site_title = 'IJB Portal Admin'
    index_title = 'Manajemen Operasional LPK'

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


ijb_admin_site = IJBAdminSite(name='ijb_admin')
