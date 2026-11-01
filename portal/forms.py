from django import forms
from django.db import transaction
from django.utils import timezone
from django.contrib.auth.forms import UserCreationForm
from .models import User, StudentProfile, CalendarEvent, SupportTicket, StaffRegistrationCode

class RegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=150, label='Nama depan')
    last_name = forms.CharField(max_length=150, required=False, label='Nama belakang')
    email = forms.EmailField(label='Email')
    phone = forms.CharField(max_length=30, required=False, label='Nomor telepon')
    role = forms.ChoiceField(choices=[('STUDENT','Siswa'),('STAFF','Staf LPK')], label='Jenis akun')
    staff_code = forms.CharField(required=False, label='Kode pendaftaran staf', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('username','first_name','last_name','email','phone','role','password1','password2')

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('role') == 'STAFF':
            raw_code = cleaned.get('staff_code', '')
            if not raw_code or not StaffRegistrationCode.objects.filter(
                code_hash=StaffRegistrationCode.hash_code(raw_code), revoked=False,
                used_at__isnull=True,
            ).exists():
                self.add_error('staff_code', 'Kode staf tidak valid, sudah digunakan, atau sudah dicabut.')
            else:
                invitation = StaffRegistrationCode.objects.get(code_hash=StaffRegistrationCode.hash_code(raw_code))
                if invitation.expires_at and invitation.expires_at <= timezone.now():
                    self.add_error('staff_code', 'Kode staf sudah kedaluwarsa.')
        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        user.phone = self.cleaned_data['phone']
        user.role = self.cleaned_data['role']
        user.is_staff = user.role == 'STAFF'
        user.is_superuser = False
        if commit:
            with transaction.atomic():
                user.save()
                if user.role == 'STAFF':
                    if not StaffRegistrationCode.consume(self.cleaned_data.get('staff_code', ''), user):
                        from django.core.exceptions import ValidationError
                        raise ValidationError('Kode staf sudah tidak berlaku. Minta kode baru kepada Superuser.')
                    user.staff_code_used = True
                    user.save(update_fields=['staff_code_used'])
                    from django.contrib.auth.models import Group
                    group = Group.objects.filter(name='LPK Staff').first()
                    if group:
                        user.groups.add(group)
        return user

class ProfileForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = ['origin','origin_lpk_name','program','date_of_birth','address','emergency_contact']
        widgets = {'date_of_birth': forms.DateInput(attrs={'type':'date'}), 'address': forms.Textarea(attrs={'rows':3})}

class EventForm(forms.ModelForm):
    class Meta:
        model = CalendarEvent
        fields = ['title','kind','starts_at','ends_at','location','notes']
        widgets = {'starts_at': forms.DateTimeInput(attrs={'type':'datetime-local'}), 'ends_at': forms.DateTimeInput(attrs={'type':'datetime-local'}), 'notes': forms.Textarea(attrs={'rows':3})}

class TicketForm(forms.ModelForm):
    class Meta:
        model = SupportTicket
        fields = ['subject','category','description']
        widgets = {'description': forms.Textarea(attrs={'rows':5})}
