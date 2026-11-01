from django.contrib import admin
from django.urls import path
from portal import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.dashboard, name='dashboard'),
    path('register/', views.register, name='register'),
    path('login/', views.PortalLoginView.as_view(), name='login'),
    path('logout/', views.PortalLogoutView.as_view(), name='logout'),
    path('profile/', views.profile, name='profile'),
    path('events/', views.events, name='events'),
    path('events/new/', views.event_create, name='event_create'),
    path('tickets/', views.tickets, name='tickets'),
    path('tickets/new/', views.ticket_create, name='ticket_create'),
    path('documents/', views.documents, name='documents'),
    path('documents/<int:pk>/download/', views.document_download, name='document_download'),
]
