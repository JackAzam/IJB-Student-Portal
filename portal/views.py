import mimetypes
from pathlib import Path
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from .forms import RegistrationForm, ProfileForm, EventForm, TicketForm
from .models import StudentProfile, CalendarEvent, SupportTicket, StudentDocument, AuditLog

class PortalLoginView(LoginView):
    template_name = 'portal/login.html'
    redirect_authenticated_user = True

class PortalLogoutView(LogoutView):
    pass

def is_staff_user(user):
    return user.is_authenticated and (user.is_superuser or user.role in {'STAFF','MANAGER'})

def get_student_profile(user):
    profile, _ = StudentProfile.objects.get_or_create(user=user)
    return profile


def get_accessible_students(user):
    if user.is_superuser or user.role == 'MANAGER':
        return StudentProfile.objects.all()

    if user.role == 'STAFF':
        return StudentProfile.objects.filter(
            staff_assignments__staff=user,
            staff_assignments__active=True,
        ).distinct()

    return StudentProfile.objects.none()

def register(request):
    if request.user.is_authenticated: return redirect('dashboard')
    form = RegistrationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        if user.role == UserRole.STUDENT:
            StudentProfile.objects.create(user=user)
        login(request, user)
        messages.success(request, 'Akun berhasil dibuat. Selamat datang di IJB Student Portal.')
        return redirect('dashboard')
    return render(request, 'portal/register.html', {'form': form})

# Kept as a string to avoid importing the model enum in view conditionals.
class UserRole:
    STUDENT = 'STUDENT'

@login_required
def dashboard(request):
    if is_staff_user(request.user):
        students = get_accessible_students(request.user)

        context = {
            'staff_mode': True,
            'student_count': students.count(),
            'open_tickets': SupportTicket.objects.filter(
                student__in=students
            ).exclude(
                status__in=['RESOLVED', 'CLOSED']
            ).count(),
            'upcoming_events': CalendarEvent.objects.filter(
                student__in=students,
                starts_at__gte=timezone.now(),
            ).order_by('starts_at')[:8],
            'pending_documents': StudentDocument.objects.filter(
                student__in=students,
                status__in=['REQUESTED', 'UPLOADED', 'REVIEW'],
            ).count(),
            'recent_tickets': SupportTicket.objects.filter(
                student__in=students
            ).select_related(
                'student__user'
            ).order_by('-created_at')[:6],
        }
    else:
        profile = get_student_profile(request.user)
        context = {
            'staff_mode': False, 'profile': profile,
            'upcoming_events': profile.events.filter(starts_at__gte=timezone.now()).order_by('starts_at')[:8],
            'tickets': profile.tickets.order_by('-created_at')[:5],
            'documents': profile.documents.filter(visible_to_student=True).order_by('-uploaded_at')[:6],
            'interviews': profile.interviews.select_related('order','order__company').order_by('-created_at')[:5],
        }
    return render(request, 'portal/dashboard.html', context)

@login_required
def profile(request):
    if is_staff_user(request.user):
        messages.info(request, 'Profil staf dikelola melalui menu akun.')
        return redirect('dashboard')
    student = get_student_profile(request.user)
    form = ProfileForm(request.POST or None, instance=student)
    if request.method == 'POST' and form.is_valid():
        form.save(); messages.success(request, 'Profil berhasil diperbarui.'); return redirect('profile')
    return render(request, 'portal/profile.html', {'form': form})

@login_required
def events(request):
    if is_staff_user(request.user):
        students = get_accessible_students(request.user)
        items = CalendarEvent.objects.filter(
            student__in=students
        ).select_related(
            'student__user'
        ).order_by('starts_at')
    else:
        items = get_student_profile(request.user).events.order_by('starts_at')

    return render(
        request,
        'portal/events.html',
        {
            'items': items,
            'staff_mode': is_staff_user(request.user),
        },
    )

@login_required
def event_create(request):
    if is_staff_user(request.user):
        messages.info(request, 'Staf dapat membuat jadwal melalui Django Admin pada tahap awal.')
        return redirect('events')
    form = EventForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        event = form.save(commit=False); event.student = get_student_profile(request.user); event.created_by = request.user; event.save()
        AuditLog.objects.create(actor=request.user, action='EVENT_CREATED', object_type='CalendarEvent', object_id=str(event.pk))
        messages.success(request, 'Jadwal berhasil ditambahkan.'); return redirect('events')
    return render(request, 'portal/form_page.html', {'form': form, 'heading': 'Tambah jadwal'})

@login_required
def tickets(request):
    if is_staff_user(request.user):
        students = get_accessible_students(request.user)
        items = SupportTicket.objects.filter(
            student__in=students
        ).select_related(
            'student__user',
            'assigned_to',
        )
    else:
        items = get_student_profile(request.user).tickets.all()

    return render(
        request,
        'portal/tickets.html',
        {
            'items': items.order_by('-created_at'),
            'staff_mode': is_staff_user(request.user),
        },
    )

@login_required
def ticket_create(request):
    if is_staff_user(request.user): return redirect('tickets')
    form = TicketForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        ticket = form.save(commit=False); ticket.student = get_student_profile(request.user); ticket.save()
        AuditLog.objects.create(actor=request.user, action='TICKET_CREATED', object_type='SupportTicket', object_id=str(ticket.pk))
        messages.success(request, 'Tiket bantuan berhasil dikirim.'); return redirect('tickets')
    return render(request, 'portal/form_page.html', {'form': form, 'heading': 'Buat tiket bantuan'})

@login_required
def documents(request):
    if is_staff_user(request.user):
        students = get_accessible_students(request.user)
        items = StudentDocument.objects.filter(
            student__in=students
        ).select_related(
            'student__user',
            'requirement',
        ).order_by('-uploaded_at')
    else:
        items = get_student_profile(request.user).documents.filter(
            visible_to_student=True
        ).select_related('requirement')

    return render(
        request,
        'portal/documents.html',
        {
            'items': items,
            'staff_mode': is_staff_user(request.user),
        },
    )

@login_required
def document_download(request, pk):
    document = get_object_or_404(
        StudentDocument.objects.select_related('student__user'),
        pk=pk,
    )
    if is_staff_user(request.user):
        if not get_accessible_students(request.user).filter(
            pk=document.student_id
        ).exists():
            raise PermissionDenied
    elif (
        document.student.user_id != request.user.id
        or not document.visible_to_student
    ):
        raise PermissionDenied
    if not document.file: raise Http404('File belum tersedia.')
    path = Path(document.file.path).resolve()
    root = Path(settings.MEDIA_ROOT).resolve()
    if root not in path.parents or not path.is_file(): raise Http404('File tidak ditemukan.')
    AuditLog.objects.create(actor=request.user, action='DOCUMENT_DOWNLOADED', object_type='StudentDocument', object_id=str(document.pk))
    content_type = mimetypes.guess_type(path.name)[0] or 'application/octet-stream'
    return FileResponse(open(path, 'rb'), as_attachment=True, filename=path.name, content_type=content_type)
