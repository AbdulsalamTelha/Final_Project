from django import forms
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
from django.db.models import Q, F, Value, CharField
from django.contrib.auth.decorators import user_passes_test
from django.db.models.functions import Concat
from django.http import Http404

from .models import *
from .utils import generate_otp, send_otp_email
from django.core.paginator import Paginator
from django.core.exceptions import FieldDoesNotExist, FieldError
from itertools import groupby
from operator import attrgetter
import re
import mimetypes
from django.core.files.uploadedfile import InMemoryUploadedFile
import socket
from django.db.models import Count


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


def home_view(request):
    if request.user.is_authenticated:
        # Redirect user based on role
        if request.user.role == User.Roles.ADMIN:
            return redirect('admin_dashboard')  # Admin dashboard view
        elif request.user.role == User.Roles.INSTRUCTOR:
            return redirect('instructor_dashboard')  # Instructor dashboard view
        elif request.user.role == User.Roles.STUDENT:
            return redirect('library_list')  # Student dashboard view
        else:
            messages.error(request, "Your role is not recognized.")
            return redirect('access_denied')
    else:
        return redirect('login')  # Redirect to login page if user is not authenticated
    

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if not username or not password:
            messages.warning(request, 'Please fill all required fields.')
            return redirect('login')
        
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            # Redirect user based on role
            if user.role == User.Roles.ADMIN:
                return redirect('admin_dashboard')  # Admin dashboard view
            elif user.role == User.Roles.INSTRUCTOR:
                return redirect('instructor_dashboard')  # Instructor dashboard view
            elif user.role == User.Roles.STUDENT:
                return redirect('student_dashboard')  # Student dashboard view
            else:
                messages.error(request, "Your role is not recognized.")
                return redirect('access_denied')
        else:
            messages.error(request, "Invalid username or password.")

    
    return render(request, 'login.html', {
        'is_login_page': True,  # إضافة متغير للإشارة إلى أن هذه صفحة تسجيل الدخول
    })

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')

def access_denied(request):
    return render(request, 'access_denied.html')


def custom_400(request, exception=None): # 400: طلب غير صالح.
    return render(request, '400.html', status=400)

def custom_403(request, exception=None): # 403: ممنوع الوصول.
    return render(request, '403.html', status=403)

def custom_404(request, exception=None): # 404: الصفحة غير موجودة.
    return render(request, '404.html', status=404)

def custom_405(request, exception=None): # 405: طريقة غير مسموحة.
    return render(request, '405.html', status=405)

def custom_500(request, exception=None): # 500: خطأ في الخادم.
    return render(request, '500.html', status=500)


@login_required
def library_view(request):

    # Get search and filter parameters
    category_filter = request.GET.get('category', '').strip()
    course_filter = request.GET.get('course', '').strip()
    type_filter = request.GET.get('type', '').strip()
    uploader_filter = request.GET.get('uploader', '').strip()
    search_query = request.GET.get('search', '').strip()
    ordering = request.GET.get('ordering', 'name').strip().lower()

    # Base query
    files = File.objects.filter(status="APPROVED").select_related('upload_by')

    # Fetch distinct data for filters
    categories = File.objects.values_list('category', flat=True).distinct()
    courses = Course.objects.filter(
        id__in=files.values_list('course__id', flat=True)
    ).distinct()
    types = File.objects.values_list('type', flat=True).distinct()
    uploaders = User.objects.filter(
        id__in=files.values_list('upload_by__id', flat=True)
    ).distinct()

    # Apply filters
    if category_filter and category_filter in categories:
        files = files.filter(category=category_filter)

    if course_filter and course_filter.isdigit() and Course.objects.filter(id=course_filter).exists():
        files = files.filter(course__id=course_filter)

    if type_filter and type_filter in types:
        files = files.filter(type=type_filter)

    if uploader_filter and uploader_filter.isdigit() and User.objects.filter(id=uploader_filter).exists():
        files = files.filter(upload_by__id=uploader_filter)

    if search_query:
        files = files.filter(name__icontains=search_query)

    valid_ordering_fields = [
        "name", "course__name", "category", "type", "size",
        "upload_date", "upload_by__first_name",
        "-name", "-course__name", "-category", "-type", "-size",
        "-upload_date", "-upload_by__first_name",
    ]

    if ordering not in valid_ordering_fields:
        ordering = "name"  # ترتيب افتراضي
    files = files.order_by(ordering)

    total_count = files.count()

    show_all = request.GET.get('show_all', 'false').lower() == 'true'

    view_mode = request.GET.get('view', 'list').strip().lower()

    if show_all:
        page_obj = files  # عرض جميع السجلات
    else:
        paginator = Paginator(files, 10)  # عدد السجلات في كل صفحة
        page_number = request.GET.get('page')  # الحصول على رقم الصفحة من الطلب
        page_obj = paginator.get_page(page_number)

    return render(request, 'library_list.html', {
        'page_obj': page_obj,
        'category_filter': category_filter,
        'course_filter': course_filter,
        'type_filter': type_filter,
        'uploader_filter': uploader_filter,
        'search_query': search_query,
        'categories': categories,
        'courses': courses,
        'types': types,
        'uploaders': uploaders,
        'actual_ordering': ordering,
        'total_count': total_count,
        'show_all': show_all,
        'view_mode': view_mode,
    })


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
            messages.success(request, "Password changed successfully ...")
            return redirect('profile')
    else:
        form = PasswordChangeForm(user=request.user)
    return render(request, 'change_password.html', {'form': form})

@login_required
def edit_profile_view(request):    
    if request.method == 'POST':
        username = request.POST.get('username')

        if not username:
            messages.error(request, "Username can't be empty.")
            return redirect('edit_profile')
        
        user = request.user
        user.username = username

        if 'file' in request.FILES:
            user.image = request.FILES['file']

        user.save()
        messages.success(request, "Profile updated successfully!")
        return redirect('profile')
    
    return render(request, 'edit_profile.html')

def is_valid_phone_number(phone_number):
    # التعبير النمطي للتحقق من أن الرقم يبدأ بـ 70 أو 71 أو 73 أو 77 أو 78 ويتكون من 9 أرقام
    if not re.match(r'^(70|71|73|77|78)\d{7}$', phone_number):
        return False, "Please enter a valid Yemeni phone number (e.g., 7xxxxxxxx)."
    
    # استثناء الأرقام التي تكون الخانات السبعة الأخيرة متشابهة (مثل 711111111)
    last_seven_digits = phone_number[2:]  # نأخذ الأرقام السبعة الأخيرة
    if all(digit == last_seven_digits[0] for digit in last_seven_digits):
        return False, "This phone number is not allowed (company number)."
    
    return True, None  # الرقم صالح ولا توجد أخطاء

def request_account(request):
    errors = {}
    full_name = request.POST.get("full_name", '').strip()
    email = request.POST.get("email", '').strip()
    phone_number = request.POST.get("phone_number", '').strip()

    if request.method == "POST":
        profile_image = request.FILES.get("profile_image")

        # التحقق من الاسم الكامل (حروف ومسافات فقط)
        if not full_name:
            errors['full_name'] = 'Full name is required.'
        elif not re.match(r'^[A-Za-z\s]+$', full_name):
            errors['full_name'] = 'Full name should contain only letters and spaces.'

        # التحقق من صحة الإيميل
        if not email:
            errors['email'] = 'Email is required.'
        elif not re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', email):
            errors['email'] = 'Please enter a valid email address.'
        else:
            # التحقق من وجود الإيميل في الطلبات السابقة
            if AccountRequest.objects.filter(email=email).exists():
                errors['email'] = 'An account request with this email already exists.'
                messages.warning(request, 'An account request with this email already exists.')
        
        # التحقق من رقم الهاتف (يبدأ بـ 70 أو 71 أو 73 أو 77 أو 78 ويتكون من 9 أرقام)
        if not phone_number:
            errors['phone_number'] = 'Phone number is required.'
        else:
            is_valid, phone_error = is_valid_phone_number(phone_number)
            if not is_valid:
                errors['phone_number'] = phone_error  # عرض رسالة الخطأ المخصصة
            else:
                # التحقق من وجود رقم الهاتف في الطلبات السابقة
                if AccountRequest.objects.filter(phone_number=phone_number).exists():
                    errors['phone_number'] = 'An account request with this phone number already exists.'
                    messages.warning(request, 'An account request with this phone number already exists.')

        # التحقق من أن الملف المرفوع هو صورة
        if not profile_image:
            errors['profile_image'] = 'Profile image is required.'
        elif not isinstance(profile_image, InMemoryUploadedFile):
            errors['profile_image'] = 'Invalid file type.'
        else:
            # التحقق من نوع الملف باستخدام mimetypes
            file_type, _ = mimetypes.guess_type(profile_image.name)
            if not file_type or not file_type.startswith('image'):
                errors['profile_image'] = 'Only image files are allowed.'
        
        # إذا لم تكن هناك أخطاء، قم بإنشاء الطلب
        if not errors and not messages.get_messages(request):
            AccountRequest.objects.create(
                full_name=full_name,
                email=email,
                phone_number=phone_number,
                profile_image=profile_image  
            )

            messages.success(request,"Your request has been sent successfully. We will respond to you soon ...")
            return redirect('login')

    return render(request, "request_account.html", {
        'is_request_account_page': True, 
        'errors': errors,
        'full_name': full_name,
        'email': email,
        'phone_number': phone_number,
    })


@login_required
def students_list(request):
    if request.user.role == User.Roles.ADMIN or request.user.role == User.Roles.INSTRUCTOR:
        students = Student.objects.filter(user__is_active=True).select_related('user').prefetch_related('department', 'group')
    elif request.user.role == User.Roles.STUDENT:
        students = Student.objects.filter(user__is_active=True, user__gender=request.user.gender).select_related('user').prefetch_related('department', 'group')

    # الحصول على معايير الفلترة من الطلب
    department_filter = request.GET.get('department', '').strip().lower()
    group_filter = request.GET.get('group', '').strip().lower()
    level_filter = request.GET.get('level', '').strip()
    gender_filter = request.GET.get('gender', '').strip()
    search_query = request.GET.get('search', '').strip()
    ordering = request.GET.get('ordering', 'user__first_name').strip().lower()  # افتراضي الترتيب حسب الاسم

    # جلب القيم لقوائم الفلترة بناءً على السجلات الحالية
    departments = Department.objects.filter(
        id__in=students.values_list('department__id', flat=True)
    ).distinct()

    groups = Group.objects.annotate(
        display_name=Concat(
            F('name'),
            Value(' - '),
            F('level'),
            Value(' - '),
            F('department__name'),
            output_field=CharField()
        )
    ).filter(
        id__in=students.values_list('group__id', flat=True)
    ).distinct()
    levels = students.values_list('level', flat=True).distinct()
    genders = students.values_list('user__gender', flat=True).distinct()

    # تطبيق الفلترة
    if department_filter and department_filter.isdigit() and Department.objects.filter(id=department_filter).exists():
        students = students.filter(department__id=department_filter)

    if group_filter and group_filter.isdigit() and Group.objects.filter(id=group_filter).exists():
        students = students.filter(group__id=group_filter)

    if level_filter and level_filter.isdigit():
        students = students.filter(level=level_filter)

    if gender_filter and gender_filter in genders:
        students = students.filter(user__gender=gender_filter)

    if search_query:
        # تقسيم النص المدخل إلى كلمات بناءً على المسافات
        search_words = search_query.split()
        
        # إنشاء استعلام للبحث عن الأسماء
        search_filter = Q()
        
        # البحث عن أي كلمة (OR)
        for word in search_words:
            search_filter |= (
                Q(user__first_name__icontains=word) |
                Q(user__last_name__icontains=word)
            )

        # البحث عن جميع الكلمات معًا (AND)
        for word in search_words:
            search_filter &= (
                Q(user__first_name__icontains=word) |
                Q(user__last_name__icontains=word)
            )

        # إضافة البحث في بقية الحقول
        search_filter |= Q(user__id__icontains=search_query) | \
                         Q(user__email__icontains=search_query) | \
                         Q(user__phone__icontains=search_query) | \
                         Q(level__icontains=search_query) | \
                         Q(department__name__icontains=search_query) | \
                         Q(user__birth_date__icontains=search_query) | \
                         Q(group__name__icontains=search_query)

        # تطبيق الفلتر على قائمة المدرسين
        students = students.filter(search_filter).distinct()

    # قائمة الحقول المسموح بها للترتيب
    valid_ordering_fields = [
        "user__id",
        "user__first_name",
        "user__email",
        "user__phone",
        "user__gender",
        "user__birth_date",
        "level",
        "department__name",
        "group__name",
        "-user__id",
        "-user__first_name",
        "-user__email",
        "-user__phone",
        "-user__gender",
        "-user__birth_date",
        "-level",
        "-department__name",
        "-group__name",
    ]

    # التحقق من صحة حقل الترتيب
    if ordering not in valid_ordering_fields:
        ordering = "user__id"  # ترتيب افتراضي
    students = students.order_by(ordering)
    
    # حساب العدد الإجمالي للسجلات
    total_count = students.count()

     # التحقق من عرض جميع السجلات
    show_all = request.GET.get('show_all', 'false').lower() == 'true'

    # التبديل بين القائمة والكروت
    view_mode = request.GET.get('view', 'list').strip().lower()  # الوضع الافتراضي هو القائمة

    # تطبيق التقسيم (Pagination) إذا لم يتم طلب عرض جميع السجلات
    if show_all:
        page_obj = students  # عرض جميع السجلات
    else:                   # instructors, 10 if view_mode == 'list' else len(instructors)
        paginator = Paginator(students, 10)  # عدد السجلات في كل صفحة
        page_number = request.GET.get('page')  # الحصول على رقم الصفحة من الطلب
        page_obj = paginator.get_page(page_number)  # البيانات الخاصة بالصفحة الحالية

    return render(request, 'students_list.html', {
        'page_obj': page_obj,
        'department_filter': department_filter,
        'group_filter': group_filter,
        'level_filter': level_filter,
        'gender_filter': gender_filter,
        'search_query': search_query,
        'departments': departments,
        'groups': groups,
        'levels': levels,
        'genders': genders,
        'actual_ordering': ordering,
        'total_count': total_count,
        'show_all': show_all,
        'view_mode': view_mode,
    })

def request_otp(request):
    errors = {}
    username = request.POST.get("username", '').strip()

    if request.method == "POST":
        if not username:
            errors["username"] = "Username is required."

        if not errors:
            user = User.objects.filter(username=username).first()

            if not user:
                messages.error(request, "Username not found.")
                return render(request, "request_otp.html", {
                    'is_request_otp': True,
                })
            
            # حذف أي رموز سابقة وإرسال OTP جديد
            OTP.objects.filter(user=user).delete()  # Clear old OTPs
            otp = generate_otp()
            expires_at = timezone.now() + timezone.timedelta(minutes=5)
            OTP.objects.create(user=user, otp=otp, expires_at=expires_at)

            try:
                # محاولة إرسال البريد الإلكتروني
                if send_otp_email(user.email, otp):
                    request.session['username'] = username
                    messages.success(request, "OTP sent successfully!")
                    return redirect(reverse('verify_otp'))
                else:
                    messages.error(request, "Failed to send OTP. Please try again.")
                
            except socket.gaierror:
                # في حالة عدم وجود اتصال بالإنترنت
                messages.warning(request, "You are not connected to the internet. Please check your connection and try again.")
                return render(request, "request_otp.html", {
                    'is_request_otp': True,
                })

            except Exception as e:
                # معالجة أي استثناء آخر قد يحدث أثناء الإرسال
                messages.error(request, "An error occurred while sending the OTP. Please try again later.")
                return render(request, "request_otp.html", {
                    'is_request_otp': True,
                })

    return render(request, "request_otp.html", {
        'is_request_otp': True,
        'errors': errors,
    })


def verify_otp(request):
    errors = {}

    # الحصول على اسم المستخدم من الجلسة
    username = request.session.get('username', '').strip()
    if not username:
        messages.warning(request, "No username provided. Please request OTP again.")
        return redirect("request_otp")
    
    # جلب سجل OTP الخاص بالمستخدم وحساب الوقت المتبقي
    otp_record = OTP.objects.filter(user__username=username).first()
    time_left = (otp_record.expires_at - now()).total_seconds() if otp_record else 0
    
    if request.method == "POST":    
        otp = request.POST.get("otp", '').strip()

        # التحقق من أن القيم ليست فارغة
        if not otp:
            errors['otp'] = "OTP is required."
            return render(request, "verify_otp.html", {
                "username": username,
                "is_verify_otp": True,
                "errors": errors,
                "time_left": int(time_left),
            })

        # # Check if the OTP exists for the user
        # otp_record = OTP.objects.filter(user=user, otp=otp).first()
        # if not otp_record:
        #     messages.error(request, "Invalid OTP. Please try again.")
        #     return render(request, "verify_otp.html", {
        #         "username": username,
        #         "is_verify_otp" : True,
        #         "time_left": int(time_left),
        #     })

        # التحقق من الرمز OTP
        if not otp_record or otp_record.otp != otp:
            messages.error(request, "Invalid OTP. Please try again.")
            # return redirect(f"{reverse('verify_otp')}?username={username}")
            return redirect(reverse('verify_otp'))

        # Check if the OTP is expired
        if otp_record.expires_at and timezone.now() > otp_record.expires_at:
            messages.error(request, "OTP has expired. Please request a new one.")
            return redirect("request_otp")

        # حذف سجل OTP وحفظ حالة التحقق
        otp_record.delete()

        # حذف اسم المستخدم من الجلسة
        # del request.session['username']

        request.session['otp_verified'] = True
        request.session['username_verified'] = username

        return redirect(reverse("reset_password"))
    
    return render(request, "verify_otp.html", {
        "username": username,
        "is_verify_otp" : True,
        "time_left": int(time_left),
    })


def reset_password(request):
    # التحقق من الجلسة
    username_verified = request.session.get('username_verified')
    if not username_verified or not request.session.get('otp_verified', False):
        messages.warning(request, "You must verify OTP before resetting your password.")
        return redirect("request_otp")

    errors = {}
    if request.method == "POST":
        new_password = request.POST.get("new_password", '').strip()

        if not new_password:
            errors["new_password"] = "Password is required."
            return render(request, "reset_password.html", {
                "username": username_verified, 
                "errors": errors,
                'is_reset_password': True,
            })

        user = User.objects.filter(username=username_verified).first()
        if user:
            user.set_password(new_password)
            user.save()

            # إزالة بيانات الجلسة بعد نجاح العملية
            del request.session['otp_verified']
            del request.session['username_verified']
            del request.session['username']

            messages.success(request, "Password reset successfully!")
            return redirect("login")
        else:
            messages.error(request, "User not found.")
            return redirect("request_otp")

    return render(request, "reset_password.html", {
        "username": username_verified,
        'is_reset_password': True,
    })

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
                messages.success(request, 'A new OTP has been sent to your email.')
                return render(request, "verify_otp.html", {
                    "username": username,
                    "is_verify_otp" : True,
                })
            else:
                messages.error(request, 'Failed to resend OTP. Please try again.')
                return render(request, "verify_otp.html", {
                    "username": username,
                    "is_verify_otp" : True,
                })
        else:
            messages.error(request, "Username not found. Please try again.")
            return render(request, "verify_otp.html", {
                "is_verify_otp" : True,
            })

    return redirect("request_otp")

@login_required
def group_students(request, group_id):
    error_message = None  # متغير لتخزين رسالة الخطأ
    group = None
    department = None
    students = []

    if not group_id.isdigit():
        error_message = "Invalid group ID. Please enter a valid number."
    else:
        try:
            # محاولة جلب المجموعة بناءً على المعرف
            group = get_object_or_404(Group, id=int(group_id))
            department = group.department
            students = group.students.all()  # جلب الطلاب المرتبطين بالجروب
        except Http404:
            # إذا لم يتم العثور على المجموعة
            error_message = "The requested group does not exist."

    # تمرير رسالة الخطأ إلى القالب، بجانب البيانات الأخرى
    return render(request, 'group_students.html', {
        'group': group,
        'students': students,
        'department': department,
        'error_message': error_message,
    })

# التحقق إذا كان المستخدم دكتورًا
# def is_instructor(user):
#     return user.is_authenticated and user.role == User.Roles.INSTRUCTOR
 
@login_required
# @user_passes_test(is_instructor)
def instructor_dashboard(request):
    if request.user.role != User.Roles.INSTRUCTOR:
        return redirect('403')

    instructor = get_object_or_404(Instructor, user=request.user)
    groups_with_courses = []
    # الجروبات التي يدرسها الدكتور
    groups = instructor.groups.all()
    courses = instructor.courses.all()
    departments = instructor.departments.all()
    instructors = Instructor.objects.all().filter(user__is_active=True).count()
    students = Student.objects.all().filter(user__is_active=True).count()

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
        'total_instructors': instructors,
        'total_students': students,
    })

@login_required
def admin_dashboard(request):
    if request.user.role != User.Roles.ADMIN:
        return redirect('403')  # صفحة مخصصة لرفض الوصول

     # إحصائيات
    total_users = User.objects.count()
    total_students = Student.objects.count()
    total_instructors = Instructor.objects.count()
    total_account_requests = AccountRequest.objects.count()

    # قوائم سريعة
    recent_account_requests = AccountRequest.objects.order_by('-created_at')[:5]
    recent_files = File.objects.order_by('-upload_date')[:5]

    context = {
        'total_users': total_users,
        'total_students': total_students,
        'total_instructors': total_instructors,
        'total_account_requests': total_account_requests,
        'recent_account_requests': recent_account_requests,
        'recent_files': recent_files,
    }
    return render(request, 'admin_dashboard.html', context)


@login_required
def student_dashboard(request):
    if request.user.role != User.Roles.STUDENT:
        return redirect('403')

    student = Student.objects.get(user=request.user)
    student_courses = student.student_courses.all()

    recent_files = File.objects.filter(upload_by=request.user).order_by('-upload_date')[:5]

    return render(request, "student_dashboard.html", {
        "student": student,
        "student_courses": student_courses,
        "recent_files": recent_files,
    })

@login_required
def instructors_list(request):
    # استرجاع جميع المدرسين من قاعدة البيانات
    # instructors = Instructor.objects.all().filter(user__is_active=True)
    instructors = Instructor.objects.filter(user__is_active=True).select_related('user').prefetch_related('departments', 'courses')

    # الحصول على معايير الفلترة من الطلب
    department_filter = request.GET.get('department', '').strip()
    course_filter = request.GET.get('course', '').strip()
    gender_filter = request.GET.get('gender', '').strip()
    search_query = request.GET.get('search', '').strip()
    ordering = request.GET.get('ordering', 'user__first_name').strip()  # افتراضي الترتيب حسب الاسم

    # جلب القيم لقوائم الفلترة بناءً على السجلات الحالية
    departments = Department.objects.filter(
        id__in=instructors.values_list('departments__id', flat=True)
    ).distinct()
    courses = Course.objects.filter(
        id__in=instructors.values_list('courses__id', flat=True)
    ).distinct()
    genders = instructors.values_list('user__gender', flat=True).distinct()

    # تطبيق الفلترة
    if department_filter and department_filter.isdigit() and Department.objects.filter(id=department_filter).exists():
        instructors = instructors.filter(departments__id=department_filter)

    if course_filter and course_filter.isdigit() and Course.objects.filter(id=course_filter).exists():
        instructors = instructors.filter(courses__id=course_filter)

    if gender_filter and gender_filter in genders:
        instructors = instructors.filter(user__gender=gender_filter)

    if search_query:
        # تقسيم النص المدخل إلى كلمات بناءً على المسافات
        search_words = search_query.split()
        
        # إنشاء استعلام للبحث عن الأسماء
        search_filter = Q()

        # البحث عن أي كلمة (OR)
        for word in search_words:
            search_filter |= (
                Q(user__first_name__icontains=word) |
                Q(user__last_name__icontains=word)
            )
        
        # البحث عن جميع الكلمات معًا (AND)
        for word in search_words:
            search_filter &= (
                Q(user__first_name__icontains=word) |
                Q(user__last_name__icontains=word)
            )

        # إضافة البحث في بقية الحقول
        search_filter |= Q(user__id__icontains=search_query) | \
                         Q(user__email__icontains=search_query) | \
                         Q(user__phone__icontains=search_query) | \
                         Q(departments__name__icontains=search_query) | \
                         Q(courses__name__icontains=search_query)

        # تطبيق الفلتر على قائمة المدرسين
        instructors = instructors.filter(search_filter).distinct()

    # قائمة الحقول المسموح بها للترتيب
    valid_ordering_fields = [
        "user__id",
        "user__first_name",
        "user__email",
        "user__phone",
        "user__gender",
        "-user__id",
        "-user__first_name",
        "-user__email",
        "-user__phone",
        "-user__gender",
    ]

    # التحقق من صحة حقل الترتيب
    if ordering not in valid_ordering_fields:
        ordering = "user__id"  # ترتيب افتراضي
    instructors = instructors.order_by(ordering)
    
    # حساب العدد الإجمالي للسجلات
    total_count = instructors.count()

     # التحقق من عرض جميع السجلات
    show_all = request.GET.get('show_all', 'false').lower() == 'true'

    # التبديل بين القائمة والكروت
    view_mode = request.GET.get('view', 'list').strip().lower()  # الوضع الافتراضي هو القائمة

    # تطبيق التقسيم (Pagination) إذا لم يتم طلب عرض جميع السجلات
    if show_all:
        page_obj = instructors  # عرض جميع السجلات
    else:                   # instructors, 10 if view_mode == 'list' else len(instructors)
        paginator = Paginator(instructors, 10)  # عدد السجلات في كل صفحة
        page_number = request.GET.get('page')  # الحصول على رقم الصفحة من الطلب
        page_obj = paginator.get_page(page_number)  # البيانات الخاصة بالصفحة الحالية

    return render(request, 'instructors_list.html', {
        'page_obj': page_obj,
        'department_filter': department_filter,
        'course_filter': course_filter,
        'gender_filter': gender_filter,
        'search_query': search_query,
        'departments': departments,
        'courses': courses,
        'genders': genders,
        'actual_ordering': ordering,
        'total_count': total_count,
        'show_all': show_all,
        'view_mode': view_mode,
    })

@login_required
def departments_with_groups(request):
    departments = Department.objects.prefetch_related('groups')
    context = {'departments': departments}
    return render(request, 'departments_with_groups.html', context)

@login_required
def library_my_uploaded_files(request):
    # if not request.user.is_authenticated:
    #     return redirect('login')  # توجيه المستخدم إذا لم يكن مسجلاً للدخول

    # جلب الملفات التي قام المستخدم برفعها مع حالتها "APPROVED"
    files = File.objects.filter(
        status="APPROVED", 
        upload_by__id=request.user.id
    ).select_related('course').order_by('course__name', 'name')

    # تجميع الملفات حسب المادة
    grouped_files = []
    for course, group in groupby(files, key=attrgetter('course')):
        grouped_files.append({
            'course': course,
            'files': list(group)
        })
    
    show_all = request.GET.get('show_all', 'false').lower() == 'true'

    if show_all:
        page_obj = grouped_files
    else:
        paginator = Paginator(grouped_files, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

    total_count = files.count()

    return render(request, 'library_my_uploaded_files.html', {
        'page_obj': page_obj,
        'show_all': show_all,
        'total_count': total_count,
    })

@login_required
def upload_file(request):
    errors = {}  # لتخزين الأخطاء لكل حقل
    description = request.POST.get('description', '') # القيمة الافتراضية فارغة
    course_id = request.POST.get('course', '') # القيمة الافتراضية فارغة
    
    if request.method == 'POST':
        # الحصول على البيانات من الطلب
        file = request.FILES.get('file')

        # التحقق من الحقول
        if not file:
            errors['file'] = 'File is required.'
        if not description:
            errors['description'] = 'Description is required.'
        elif len(description) > 100:
            errors['description'] = 'Description must be at least 100 characters.'
        if not course_id:
            errors['course'] = 'You must select a course.'

        # إذا لم تكن هناك أخطاء، احفظ الملف
        if not errors:
                file_instance = File(
                    file=file,
                    description=description,
                    course_id=course_id,
                    upload_by=request.user,  # تعيين المستخدم الحالي
                    status= 'APPROVED' if request.user.role == User.Roles.INSTRUCTOR or request.user.role == User.Roles.ADMIN else 'PENDING'   # الحالة دائمًا Approved للدكتور
                )
                file_instance.save()

                if request.user.role == User.Roles.ADMIN or request.user.role == User.Roles.INSTRUCTOR:
                    messages.success(request, 'File uploaded successfully!')
                elif request.user.role == User.Roles.STUDENT:
                    messages.success(request, 'Your file has been sent for approval or rejected by the administrator!')
                
                return redirect('library_my_uploaded_files')

    # جلب الكورسات المرتبطة بالمستخدم الحالي
    if request.user.role == User.Roles.ADMIN:
        courses = Course.objects.filter(status=True)
    elif request.user.role == User.Roles.INSTRUCTOR:
        instructor = Instructor.objects.get(user=request.user)
        courses = instructor.courses.filter(status=True)
    elif request.user.role == User.Roles.STUDENT:
        student = Student.objects.get(user=request.user)
        student_courses = StudentCourse.objects.filter(student=student, status='STUDY')
        courses = Course.objects.filter(id__in=student_courses.values('course_id'))

    return render(request, 'upload_file.html', {
        'courses': courses, 
        'errors': errors,
        'description': description,
        'course_id': course_id,
    })


@login_required
def edit_file(request, file_id):
    errors = {}
    if request.user.role == User.Roles.ADMIN:
        courses = Course.objects.filter(status=True)
    elif request.user.role == User.Roles.INSTRUCTOR:
        courses = request.user.instructors.courses.all()
    elif request.user.role == User.Roles.STUDENT:
        student = Student.objects.get(user=request.user)
        student_courses = StudentCourse.objects.filter(student=student, status='STUDY')
        courses = Course.objects.filter(id__in=student_courses.values('course_id'))

        # التحقق مما إذا كان file_id رقمًا
    if not file_id.isdigit():
        messages.error(request, "Invalid file ID. Please provide a valid file identifier.")
        return render(request, 'edit_file.html', {'file': None, 'courses': courses})
    
    try:
        # محاولة جلب الملف بناءً على المعرّف
        file_instance = File.objects.get(id=file_id)
    except File.DoesNotExist:
        # إذا لم يتم العثور على الملف
        messages.error(request, "The requested file does not exist.")
        return render(request, 'edit_file.html', {'file': None, 'courses': courses})


    if request.method == 'POST':
        # الحصول على البيانات المُرسلة
        description = request.POST.get('description')
        course_id = request.POST.get('course')
        uploaded_file = request.FILES.get('file')

        # التحقق من الحقول
        if not description:
            errors['description'] = "Description is required."
            messages.error(request, "Description is required.")
            return render(request, 'edit_file.html', {'file': file_instance, 'courses': courses})
        if not course_id:
            errors['course'] = "You must select a course."
            messages.error(request, "You must select a course.")
            return render(request, 'edit_file.html', {'file': file_instance, 'courses': courses})

        # إذا لم تكن هناك أخطاء
        if not errors:
            file_instance.description = description
            file_instance.course_id = course_id
            if uploaded_file:
                file_instance.file = uploaded_file
            file_instance.save()

            messages.success(request, "File updated successfully!")
            return redirect('library_my_uploaded_files')

    return render(request, 'edit_file.html', {
        'file': file_instance,
        'courses': courses,
        'errors': errors
    })

@login_required
def delete_file(request, file_id):
    file = get_object_or_404(File, id=file_id)
    file.file.delete()  # حذف الملف المرفوع من السيرفر
    file.delete()       # حذف السجل من قاعدة البيانات
    messages.success(request, "File deleted successfully.")
    return redirect('library_my_uploaded_files')  

@login_required
def departments_list(request):
    departments = Department.objects.filter(status=True)

    # الحصول على معايير الفلترة من الطلب
    search_query = request.GET.get('search', '').strip()
    ordering = request.GET.get('ordering', 'name').strip()  # افتراضي الترتيب حسب الاسم

    if search_query:
        departments = departments.filter(
            Q(id__icontains=search_query) |
            Q(name__icontains=search_query)
        ).distinct()

    # قائمة الحقول المسموح بها للترتيب
    valid_ordering_fields = ["id", "name", "-id", "-name",]
    # التحقق من صحة حقل الترتيب
    if ordering not in valid_ordering_fields:
        ordering = "name"  # ترتيب افتراضي
    departments = departments.order_by(ordering)
    
    # حساب العدد الإجمالي للسجلات
    total_count = departments.count()

    return render(request, 'departments_list.html', {
        'departments': departments,
        'search_query': search_query,
        'actual_ordering': ordering,
        'total_count': total_count,
    })