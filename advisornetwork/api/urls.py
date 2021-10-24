from django.urls import path
from . import views

urlpatterns = [
    path('', views.apiOverview, name="api-overview"),
    path('admin/advisor/', views.addAdvisor, name="add-advisor"),
    path('user/register/', views.userRegister, name="user-register"),
    path('user/login/', views.userLogin, name="user-login"),
    path('user/<int:uid>/advisor/', views.getAllAdvisors, name="all-advisors"),
    path('user/<int:uid>/advisor/<int:aid>/',
         views.bookAdvisor,
         name="book-advisor"),
    path('user/<int:uid>/advisor/booking/',
         views.getAllBookings,
         name="all-bookings"),
    path('refresh-token/', views.refresh_token_view, name="refresh-token-view"),
]
