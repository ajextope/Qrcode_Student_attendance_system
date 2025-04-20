from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView
from .forms import UserRegistrationForm, CustomAuthenticationForm, UserProfileForm
from .models import User
from core.models import Course
from django.contrib.auth.views import LoginView, LogoutView

class RegisterView(CreateView):
    """
    View for user registration
    """
    template_name = 'accounts/register.html'
    form_class = UserRegistrationForm
    success_url = reverse_lazy('login')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Account created successfully. You can now log in.')
        return response

class CustomLoginView(LoginView):
    """
    Custom login view with Bootstrap styling
    """
    template_name = 'accounts/login.html'
    authentication_form = CustomAuthenticationForm
    redirect_authenticated_user = True
    
    def get_success_url(self):
        user_type = self.request.user.user_type
        if user_type == 'admin':
            return reverse_lazy('admin_dashboard')
        elif user_type == 'lecturer':
            return reverse_lazy('lecturer_dashboard')
        else:
            return reverse_lazy('student_dashboard')

class CustomLogoutView(LogoutView):
    """
    Custom logout view
    """
    next_page = 'login'

@login_required
def profile_view(request):
    """
    View for user profile
    """
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=request.user)
    
    return render(request, 'accounts/profile.html', {'form': form})

@login_required
def dashboard_view(request):
    """
    View for dashboard based on user type
    """
    user_type = request.user.user_type
     # Get statistics
    total_students = User.objects.filter(user_type='student').count()
    total_lecturers = User.objects.filter(user_type='lecturer').count()
    total_courses = Course.objects.count()  # Assuming you have a Course model

    context = {
        'total_students': total_students,
        'total_lecturers': total_lecturers,
        'total_courses': total_courses,
    }
    if user_type == 'admin':
        return render(request, 'accounts/admin_dashboard.html', context)
    elif user_type == 'lecturer':
        return render(request, 'accounts/lecturer_dashboard.html')
    else:
        return render(request, 'accounts/student_dashboard.html')

