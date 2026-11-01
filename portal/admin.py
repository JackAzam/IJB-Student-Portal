import secrets
from django.contrib import admin, messages
from django.utils import timezone
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from . import models
from .services import select_offer

@admin.register(models.User)
class UserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (('IJB Portal', {'fields': ('role','phone','staff_code_used')}),)
    add_fieldsets = BaseUserAdmin.add_fieldsets + (('IJB Portal', {'fields': ('role','phone')}),)
    list_display = ('username','email','first_name','last_name','role','is_active')
    list_filter = ('role','is_active')


@admin.register(models.StaffRegistrationCode)
class StaffRegistrationCodeAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_by', 'created_at', 'expires_at', 'used_at', 'used_by', 'revoked', 'status')
    list_filter = ('revoked', 'created_at', 'expires_at', 'used_at')
    readonly_fields = ('code_hash', 'created_by', 'created_at', 'used_at', 'used_by')
    fields = ('expires_at', 'revoked', 'code_hash', 'created_by', 'created_at', 'used_at', 'used_by')

    def has_module_permission(self, request):
        return request.user.is_superuser

    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_add_permission(self, request):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    @admin.display(description='Status')
    def status(self, obj):
        if obj.used_at: return 'Used'
        if obj.revoked: return 'Revoked'
        if obj.expires_at and obj.expires_at <= timezone.now(): return 'Expired'
        return 'Available'

    def save_model(self, request, obj, form, change):
        if not change:
            # Show the raw secret once. Only its SHA-256 hash is persisted.
            alphabet = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'
            raw = 'IJB-' + ''.join(secrets.choice(alphabet) for _ in range(4)) + '-' + ''.join(secrets.choice(alphabet) for _ in range(4))
            obj.code_hash = models.StaffRegistrationCode.hash_code(raw)
            obj.created_by = request.user
            super().save_model(request, obj, form, change)
            self.message_user(request, f'Kode staf baru: {raw} — salin sekarang dan berikan kepada staf. Kode tidak dapat ditampilkan lagi.', messages.SUCCESS)
        else:
            super().save_model(request, obj, form, change)

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields
        return ('code_hash', 'created_by', 'created_at', 'used_at', 'used_by')

@admin.register(models.StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('user','origin','program','updated_at')
    search_fields = ('user__username','user__first_name','user__last_name','user__email')
    list_filter = ('origin','program')

@admin.register(models.StudentDocument)
class StudentDocumentAdmin(admin.ModelAdmin):
    list_display = ('student','requirement','version','status','visible_to_student','due_date','uploaded_at')
    list_filter = ('status','visible_to_student','requirement__pathway')
    search_fields = ('student__user__username','student__user__first_name','requirement__name')
    readonly_fields = ('version','uploaded_at')

@admin.register(models.ExamAttempt)
class ExamAttemptAdmin(admin.ModelAdmin):
    list_display = ('student','rule','exam_date','status','earliest_retake_date')
    list_filter = ('status','rule')
    search_fields = ('student__user__username','student__user__first_name')

@admin.register(models.Interview)
class InterviewAdmin(admin.ModelAdmin):
    list_display = ('student','order','scheduled_at','status')
    list_filter = ('status','order__pathway','order__job_type')
    search_fields = ('student__user__username','order__code','order__company__name')

@admin.register(models.Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = ('interview','status','selected_at')
    list_filter = ('status','interview__order__pathway')
    actions = ['select_selected_offers']
    @admin.action(description='Select the chosen passed offer (audit logged)')
    def select_selected_offers(self, request, queryset):
        selected = 0
        for offer in queryset.select_related('interview__student'):
            try:
                select_offer(offer_id=offer.pk, actor=request.user, reason='Selected by staff in Admin')
                selected += 1
            except ValueError:
                self.message_user(request, f'Offer #{offer.pk} tidak berasal dari interview Passed.')
        self.message_user(request, f'{selected} offer berhasil dipilih.')

@admin.register(models.SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    list_display = ('subject','student','category','status','assigned_to','created_at')
    list_filter = ('status','category')
    search_fields = ('subject','student__user__username','description')

@admin.register(models.CalendarEvent)
class CalendarEventAdmin(admin.ModelAdmin):
    list_display = ('title','student','kind','starts_at','location')
    list_filter = ('kind','starts_at')
    search_fields = ('title','student__user__username')

# Register the operational models with the standard, searchable admin UI.
for model in [models.JobType, models.TskKumiai, models.TskContact, models.ReceivingCompany,
              models.Order, models.StudentOrderAssignment, models.ExamRule, models.MedicalCheckup,
              models.PassportCase, models.DocumentRequirement, models.TicketReply,
              models.TskVisit, models.PlacementCommunication, models.AuditLog]:
    try:
        admin.site.register(model)
    except admin.sites.AlreadyRegistered:
        pass

admin.site.site_header = 'IJB Student Portal'
admin.site.site_title = 'IJB Portal Admin'
admin.site.index_title = 'Manajemen Operasional LPK'
