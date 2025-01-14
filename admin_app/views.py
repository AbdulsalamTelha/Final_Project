from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.core.mail import send_mail
from django.http import JsonResponse, HttpResponse
from django.urls import reverse
from django.utils import timezone
from django.utils.dateparse import parse_date
from django.utils.timezone import now
from django.db.models import Q

from .models import (
    File,
    User,
    Instructor,
    Student,
    Course,
    AccountRequest,
    Group,
    OTP
)
from .utils import generate_otp, send_otp_email


def get_groups_view(request):
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
                return redirect('instructor_dashboard')  # Instructor dashboard view
            elif user.role == User.Roles.STUDENT:
                return redirect('library')  # Student dashboard view
            else:
                messages.error(request, "Your role is not recognized.")
                # return redirect('access_denied')
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
    # if request.user.role not in [User.Roles.STUDENT, User.Roles.INSTRUCTOR]:
    #     return redirect('access_denied')

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


def request_account(request):
    if request.method == "POST":
        full_name = request.POST.get("full_name")
        email = request.POST.get("email")
        phone_number = request.POST.get("phone_number")
        profile_image = request.FILES.get("profile_image")

        if not full_name or not email:
            return render(request, "request_account.html", {
                "error": "Please fill all required fields."
            })

        # إنشاء الطلب
        AccountRequest.objects.create(
            full_name=full_name,
            email=email,
            phone_number=phone_number,
            profile_image=profile_image
            
        )

        messages.success(request,"Your request has been sent successfully. We will respond to you soon")
        return redirect('request_account') # إعادة توجيه المستخدم إلى نفس الصفحة بعد الإرسال

    return render(request, "request_account.html")


def check_email_request(request):
    email = request.GET.get('email')
    if email and AccountRequest.objects.filter(email=email).exists():
        return JsonResponse({'exists': True})
    return JsonResponse({'exists': False})

from django.contrib.auth.decorators import user_passes_test


# التحقق إذا كان المستخدم دكتورًا
def is_doctor(user):
    return user.is_authenticated and user.role == "INSTRUCTOR"  # عدّل role حسب جدولك

@login_required
@user_passes_test(is_doctor)
def students_list(request):
    students = Student.objects.all()
    return render(request, 'students_list.html', {'students': students})





def request_otp(request):
    if request.method == "POST":
        username = request.POST.get("username")
        user = User.objects.filter(username=username).first()

        if user:
            OTP.objects.filter(user=user).delete()  # Clear old OTPs
            otp = generate_otp()
            expires_at = timezone.now() + timezone.timedelta(minutes=5)
            OTP.objects.create(user=user, otp=otp, expires_at=expires_at)

            if send_otp_email(user.email, otp):
                return render(request, "verify_otp.html", {
                    "username": username,
                    "message": "OTP sent successfully!"
                })
            else:
                return render(request, "request_otp.html", {
                    "error": "Failed to send OTP. Please try again."
                })
        else:
            return render(request, "request_otp.html", {
                "error": "Username not found."
            })

    return render(request, "request_otp.html")


def verify_otp(request):
    if request.method == "POST":
        username = request.POST.get("username")
        otp = request.POST.get("otp")

        # Check if the user exists
        user = User.objects.filter(username=username).first()
        if not user:
            return render(request, "verify_otp.html", {
                "error": "User not found. Please try again.",
                "username": username,
            })

        # Check if the OTP exists for the user
        otp_record = OTP.objects.filter(user=user, otp=otp).first()
        if not otp_record:
            return render(request, "verify_otp.html", {
                "error": "Invalid OTP. Please try again.",
                "username": username,
            })

        # Check if the OTP is expired
        if otp_record.expires_at and timezone.now() > otp_record.expires_at:
            return render(request, "verify_otp.html", {
                "error": "OTP has expired. Please request a new one.",
                "username": username,
            })

        # OTP is valid; delete the OTP record and redirect to reset password
        otp_record.delete()
        reset_password_url = reverse("reset_password") + f"?username={username}"
        return redirect(reset_password_url)

    # Render the verify OTP page for GET requests
    return render(request, "verify_otp.html")

def reset_password(request):
    if request.method == "POST":
        username = request.POST.get("username")
        new_password = request.POST.get("new_password")
        user = User.objects.filter(username=username).first()

        if user:
            user.set_password(new_password)
            user.save()
            return redirect("login")
        else:
            return render(request, "reset_password.html", {"error": "Username not found."})

    username = request.GET.get("username")
    if username:
        return render(request, "reset_password.html", {"username": username})

    return redirect("request_otp")

def resend_otp(request):
    if request.method == "POST":
        username = request.POST.get("username")
        user = User.objects.filter(username=username).first()

        if user:
            OTP.objects.filter(user=user).delete()

            otp = generate_otp()
            expires_at = timezone.now() + timezone.timedelta(minutes=5)
            OTP.objects.create(user=user, otp=otp, expires_at=expires_at)

            if send_otp_email(user.email, otp):
                return render(request, "verify_otp.html", {
                    "username": username,
                    "message": "A new OTP has been sent to your email."
                })
            else:
                return render(request, "verify_otp.html", {
                    "username": username,
                    "error": "Failed to resend OTP. Please try again."
                })
        else:
            return render(request, "verify_otp.html", {
                "error": "Username not found. Please try again."
            })

    return redirect("request_otp")

@login_required
def group_students(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    department = group.department
    students = group.students.all()  # جلب الطلاب المرتبطين بالجروب
    return render(request, 'group_students.html', {
        'group': group,
        'students': students,
        'department': department,
    })
    
@login_required
def instructor_dashboard(request):
    instructor = Instructor.objects.get(user=request.user)
    groups_with_courses = []
    # الجروبات التي يدرسها الدكتور
    groups = instructor.groups.all()
    courses = instructor.courses.all()
    departments = instructor.departments.all()

    for group in groups:
        # الكورسات المرتبطة بالقسم والمستوى الخاصين بالجروب
        courses_set = Course.objects.filter(
            departments=group.department,
            level=group.level
        ).distinct()

        courses_names = ", ".join(course.name for course in courses_set)
        # إضافة البيانات للجروبات مع رابط
        group_link = reverse('group_students', kwargs={'group_id': group.id})
        groups_with_courses.append({
            'group': group.name,
            'group_link': group_link,
            'level': group.level,
            'department': group.department.name,
            'courses': courses_names,
        })
    # جمع الإحصائيات
    total_groups = groups.count()  # عدد الجروبات
    total_courses = courses.count()  # عدد الكورسات
    total_departments = departments.count()  # عدد الكورسات

    return render(request, 'instructor_dashboard.html', {
        'instructor': instructor,
        'groups_with_courses': groups_with_courses,
        'total_groups': total_groups,
        'total_courses': total_courses,
        'total_departments': total_departments,
    })

@login_required
def instructor_upload_file(request):
    if request.method == 'POST':
        # الحصول على البيانات من الطلب
        file = request.FILES.get('file')
        description = request.POST.get('description')
        course_id = request.POST.get('course')
        # تحقق من أن جميع البيانات تم إرسالها
        if file and description and course_id:
            # إنشاء الكائن وحفظه في قاعدة البيانات
            try:
                file_instance = File(
                    file=file,
                    description=description,
                    course_id=course_id,
                    upload_by=request.user,  # تعيين المستخدم الحالي
                    status='APPROVED'  # الحالة دائمًا Approved للدكتور
                )
                file_instance.save()
                messages.success(request, 'File uploaded successfully!')
                return redirect('instructor_upload_file')  # العودة إلى صفحة الدكتور
            except Instructor.DoesNotExist:
                return messages.error(request,  'You are not registered as an instructor.')
        else:
            # إذا كانت البيانات غير مكتملة، عرض رسالة خطأ
            return messages.error(request,  'All fields are required')
    # جلب كائن Instructor المرتبط بـ request.user
    try:
        instructor = Instructor.objects.get(user=request.user)
        # جلب الكورسات التي يدرسها الدكتور فقط
        courses = instructor.courses.filter(status=True)  # التحقق من حالة الكورس
    except Instructor.DoesNotExist:
        return messages.error(request,  'You are not registered as an instructor.')

    return render(request, 'instructor_upload_file.html', {'courses': courses})





def instructors_list(request):
    # استرجاع جميع المدرسين من قاعدة البيانات
    instructors = Instructor.objects.select_related('user').prefetch_related('departments', 'courses')
    return render(request, 'instructors_list.html', {'instructors': instructors})

