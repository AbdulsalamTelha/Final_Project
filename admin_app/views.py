from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import File, User, Instructor, Student,Course
from django.db.models import Q
from django.utils.dateparse import parse_date
from django.shortcuts import render, redirect
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.http import JsonResponse
from .models import Group

def get_groups(request):
    department_id = request.GET.get('department')
    level = request.GET.get('level')

    if not department_id or not level:
        return JsonResponse({'groups': []})  # لا توجد بيانات إذا لم يتم تحديد القسم أو المستوى
    groups = Group.objects.filter(department_id=department_id, level=level)
    formatted_groups = [
        {
            'id': group.id,
            'display': f"{group.name} - {group.level} - {group.department.name}"
        }
        for group in groups
    ]
    return JsonResponse({'groups': formatted_groups})



# Login view
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            # Redirect user based on role
            if user.role == User.Roles.ADMIN:
                return redirect('admin_dashboard')  # Admin dashboard view
            elif user.role == User.Roles.INSTRUCTOR:
                return redirect('library')  # Instructor dashboard view
            elif user.role == User.Roles.STUDENT:
                return redirect('library')  # Student dashboard view
            else:
                messages.error(request, "Your role is not recognized.")
                return redirect('access_denied')
        else:
            messages.error(request, "Invalid username or password.")
    return render(request, 'login.html')

# Logout view
@login_required
def logout_view(request):
    logout(request)
    return redirect('login')

# Access denied view
def access_denied(request):
    return render(request, 'access_denied.html')

# Library view for students and instructors


@login_required
def library_view(request):
    # Ensure the user has the correct role
    if request.user.role not in [User.Roles.STUDENT, User.Roles.INSTRUCTOR]:
        return redirect('access_denied')

    # Get search and filter parameters
    search_query = request.GET.get('search', '').strip()
    category_filter = request.GET.get('category', '').strip()
    course_filter = request.GET.get('course', '').strip()
    type_filter = request.GET.get('type', '').strip()

    # Base query
    files = File.objects.all()

    # Apply filters
    if search_query:
        files = files.filter(name__icontains=search_query)

    if category_filter:
        files = files.filter(category=category_filter)

    if course_filter:
        files = files.filter(course__id=course_filter)

    if type_filter:
        files = files.filter(type=type_filter)

    # Fetch distinct data for filters
    categories = File.objects.values_list('category', flat=True).distinct()
    courses = Course.objects.filter(status=True).values('id', 'name')  # Assuming 'Course' model has 'name' and 'status' fields
    file_types = File.objects.values_list('type', flat=True).distinct()

    return render(request, 'library.html', {
        'files': files,
        'search_query': search_query,
        'category_filter': category_filter,
        'course_filter': course_filter,
        'type_filter': type_filter,
        'categories': categories,
        'courses': courses,
        'file_types': file_types,
    })

# Instructor dashboard view
@login_required
def instructor_dashboard_view(request):
    if request.user.role != User.Roles.INSTRUCTOR:
        return redirect('access_denied')

    instructor = get_object_or_404(Instructor, user=request.user)
    courses = instructor.course.all()

    return render(request, 'instructor_dashboard.html', {'file': File, 'courses': courses})

# Student dashboard view
@login_required
def student_library_view(request):
    if request.user.role != User.Roles.STUDENT:
        return redirect('access_denied')

    student = get_object_or_404(Student, user=request.user)
    courses = student.course.all()

    return render(request, 'student_library_view.html', {'student': student, 'courses': courses})

@login_required
def profile_view(request):
    return render(request,'profile.html')


@login_required
def change_password_view(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # الحفاظ على تسجيل الدخول بعد تغيير كلمة المرور
            return redirect('profile')
        else:
            messages.error(request, "هناك خطأ في تغيير كلمة المرور. الرجاء المحاولة مرة أخرى.")
    else:
        form = PasswordChangeForm(user=request.user)
    return render(request, 'change_password.html', {'form': form})

@login_required
def edit_profile_view(request):
    if request.method == 'POST':
        user = request.user
        user.username = request.POST.get('username', user.username)
        if 'image' in request.FILES:
            user.image = request.FILES['image']
        user.save()
        return redirect('profile')
    return render(request, 'edit_profile.html')
