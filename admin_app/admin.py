from django.contrib import admin
from import_export.admin import ExportMixin, ImportExportMixin
from import_export.resources import ModelResource
from import_export import fields
from import_export.widgets import ManyToManyWidget, ForeignKeyWidget
from .models import AccountRequest, File, Department, Course, Group, User, Admin, Instructor, Student, StudentCourse
from django.contrib.auth.hashers import make_password
from django.utils.html import format_html
from django.contrib import messages
from django import forms
from django.core.mail import send_mail
import random

# Register your models here.
admin.site.site_title = "SSS Admin"
admin.site.site_header = 'Student Services System'

class FileAdminForm(forms.ModelForm):
    class Meta:
        model = File
        fields = '__all__'
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3, 'cols': 40}),  # تعديل الحجم
        }

    # def __init__(self, *args, **kwargs): ## if you want to use a validation in front-end.
    #     super().__init__(*args, **kwargs)
    #     self.fields['description'].widget.attrs.update({'class': 'validate-letters-numbers'})  # إضافة فئة CSS


class FileResource(ModelResource):
    class Meta:
        model = File
        fields = ('id', 'name', 'category', 'type', 'size', 'upload_by', 'upload_by__username', 'status', 'upload_date', 'course__name', 'file')

@admin.register(File)
class FileAdmin(ExportMixin, admin.ModelAdmin):
    form = FileAdminForm
    resource_class = FileResource
    list_display = ('name', 'course__name' ,'category', 'type', 'get_human_readable_size', 'display_upload_by', 'status', 'upload_date', 'view_file')
    list_filter = ('status', 'type', 'upload_date', 'category')
    search_fields = ('name', 'upload_by__username', 'type', 'category')
    readonly_fields = ('name', 'category', 'size', 'type', 'upload_by', 'upload_date')

    class Media:
        js = ('js/validation.js',)
        css = {
            'all': ('css/admin_app/download_and_view_buttons.css',)  # إضافة ملف CSS
        }

    def display_upload_by(self, obj):
        return obj.upload_by.username if obj.upload_by else "N/A"
    display_upload_by.short_description = "Upload By"
    
    def view_file(self, obj):    # دالة لاستعراض الملف
        if obj.file and obj.file.url:  # التحقق من وجود الملف والرابط
            view_link = format_html('<a href="{}" target="_blank" class="custom-button view-button">View</a>', obj.file.url)
            download_link = format_html('<a href="{}" download class="custom-button download-button">Download</a>', obj.file.url)
            return format_html('{}{}', view_link, download_link)
        return "No file"
    view_file.short_description = "Action"

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.upload_by = request.user
        super().save_model(request, obj, form, change)

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields
        return ()

class CourseResource(ModelResource):
    departments = fields.Field(
        attribute='departments',
        widget=ManyToManyWidget(Department, field='name'),  # استخدام الاسم لتحديد القسم
        column_name='departments'
    )

    class Meta:
        model = Course
        fields = ('id', 'name', 'level', 'status', 'departments')

@admin.register(Course)
class CourseAdmin(ImportExportMixin, admin.ModelAdmin):
    resource_class = CourseResource
    list_display = ('id', 'name', 'name_initials' , 'level',  'list_departments', 'status',)
    list_filter = ('level', 'status')
    search_fields = ('name',)
    list_display_links = ('id', 'name', 'name_initials')
    ordering = ('id',)

    def list_departments(self, obj): # إرجاع أسماء الأقسام المرتبطة بالكورس
        return ", ".join(department.name for department in obj.departments.all())
    list_departments.short_description = 'Departments'  # تغيير عنوان العمود في الجدول

    def name_initials(self, obj):  # أخذ أول حرف من كل كلمة في اسم القسم
        return ''.join([word[0].upper() for word in obj.name.split()])
    name_initials.short_description = 'Abb.'  # تغيير عنوان العمود في الجدول

# class DepartmentAdminForm(forms.ModelForm): ## if you want to use a validation in front-end.
#     class Meta:
#         model = Department
#         fields = '__all__'

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.fields['name'].widget.attrs.update({'class': 'validate-field'})

class DepartmentResource(ModelResource):
    class Meta:
        model = Department
        fields = ('id', 'name', 'status')

@admin.register(Department)
class DepartmentAdmin(ImportExportMixin, admin.ModelAdmin):
    resource_class = DepartmentResource
    list_display = ('id', 'name', 'name_initials', 'list_courses', 'status') # إضافة دالة لعرض الكورسات
    list_filter = ('status',)
    search_fields = ('name', 'id')
    list_display_links = ('id', 'name', 'name_initials')
    ordering = ('id',)

    def list_courses(self, obj): # إرجاع أسماء الكورسات المرتبطة بالقسم
        return ", ".join(course.name for course in obj.courses.all())
    list_courses.short_description = 'Courses'  # تغيير عنوان العمود في الجدول

    def name_initials(self, obj): # أخذ أول حرف من كل كلمة في اسم القسم
        return ''.join([word[0].upper() for word in obj.name.split()])
    name_initials.short_description = 'Abb.'  # تغيير عنوان العمود في الجدول

class GroupResource(ModelResource):
    # استخدام ForeignKeyWidget لربط القسم باستخدام اسم القسم
    department = fields.Field(
        column_name='department',  # اسم العمود في ملف الاستيراد
        attribute='department',    # الحقل في نموذج Group الذي يجب ربطه
        widget=ForeignKeyWidget(Department, 'name')  # ربط بواسطة اسم القسم\
    )
    class Meta:
        model = Group
        fields = ('id', 'name', 'status', 'level', 'department')

@admin.register(Group)
class GroupAdmin(ImportExportMixin, admin.ModelAdmin):
    resource_class = GroupResource
    list_display = ('name', 'level', 'department', 'status')
    list_filter = ('department', 'level', 'status')
    search_fields = ('name',)
    fieldsets = (
        (None, {
            'fields': ('name', 'level', 'department', 'status',),
        }),
    )

class StudentCourseInline(admin.TabularInline):
    model = StudentCourse
    extra = 1
    can_delete = True

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = '__all__'

    class Media:
        js = ('js/admin_app/select_group.js',)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        department = self.data.get('department') or self.initial.get('department')
        level = self.data.get('level') or self.initial.get('level')

        if department and level:
            self.fields['group'].queryset = Group.objects.filter(department=department, level=level)
        else:
            self.fields['group'].queryset = Group.objects.none()

class StudentResource(ModelResource):
    first_name = fields.Field(
        column_name='first_name',
        attribute='user',
        widget=ForeignKeyWidget(User, 'first_name'),
    )
    last_name = fields.Field(
        column_name='last_name',
        attribute='user',
        widget=ForeignKeyWidget(User, 'last_name'),
    )
    department = fields.Field(
        attribute='department',
        widget=ForeignKeyWidget(Department, 'name'),
        column_name='department',
    )

    # Custom ForeignKeyWidget for groups
    class GroupForeignKeyWidget(ForeignKeyWidget):
        def clean(self, value, row=None, *args, **kwargs):
            # الحصول على اسم القسم من الصف
            department_name = row.get('department')
            level = row.get('level')
            if not department_name:
                raise ValueError("Department is required to identify the group.")
            
            try:
                # البحث عن المجموعة المرتبطة بالقسم المحدد
                return self.model.objects.get(name=value, department__name=department_name, level=level)
            except self.model.MultipleObjectsReturned:
                raise ValueError(f"Multiple groups found for name '{value}' in department '{department_name}' for level '{level}'.")
            except self.model.DoesNotExist:
                raise ValueError(f"No group found for name '{value}' in department '{department_name}' for level '{level}'.")
            
    group = fields.Field(
        attribute='group',
        widget=GroupForeignKeyWidget(Group, 'name'),
        column_name='group',
    )
    courses = fields.Field(
        attribute='course',
        widget=ManyToManyWidget(Course, field='name'),  # استخدام الاسم لتحديد القسم
        column_name='courses'
    )
   
    class Meta:
        model = Student
        fields = ('id', 'first_name', 'last_name', 'department', 'level', 'group', 'courses',) 
    
    # Validate data before importing
    def before_import_row(self, row, **kwargs):
        courses_data = row.get('courses')
        department = row.get('department')
        level = row.get('level')
        first_name = row.get('first_name')
        last_name = row.get('last_name')

        # التحقق مما إذا كان الطالب بنفس الاسم الأول والأخير موجودًا
        if first_name and last_name:
            if Student.objects.filter(user__first_name=first_name.strip(), user__last_name=last_name.strip()).exists():
                raise ValueError(f"Student with the name '{first_name.strip()} {last_name.strip()}' already exists.")
        
        if not department or not level:
            raise ValueError("Both 'department' and 'level' fields are required.")
        elif not Department.objects.filter(name=department.strip()).exists():
            raise ValueError(f"Department '{department.strip()}' does not exist.")
        elif not level.isdigit() or not (1 <= int(level) <= 4):
            raise ValueError("The 'level' must be a number between 1 and 4.")

        if courses_data:
            courses = courses_data.split(',') # فصل المواد باستخدام الفاصلة
            validated_courses = []
            
            for course_name in courses:
                try:
                    course_obj = Course.objects.get(name=course_name)
                    
                    # التحقق من أن المادة تنتمي إلى القسم نفسه
                    if not course_obj.departments.filter(name=department).exists():
                        raise ValueError(f"Course '{course_name}' does not belong to department '{department}'.")
                    
                    # التحقق من أن المادة تتطابق مع مستوى الطالب
                    if course_obj.level != int(level):
                        raise ValueError(f"Course '{course_name}' does not match the student's level '{level}'.")
                    
                    validated_courses.append(course_name)
                except Course.DoesNotExist:
                    raise ValueError(f"Course '{course_name}' does not exist.")
            
            row['courses_list'] = validated_courses  # نستخدم قائمة منفصلة للتخزين المؤقت
        else:
            row['courses_list'] = []
   
    # Save related courses in the intermediary table after importing
    def save_m2m(self, instance, data, **kwargs):
        """حفظ العلاقات Many-to-Many في الجدول الوسيط."""
        super().save_m2m(instance, data)
        
        # حذف العلاقات القديمة
        StudentCourse.objects.filter(student=instance).delete()

        # إضافة الكورسات الجديدة
        courses = data.get('courses_list', [])
        for course_name in courses:
            try:
                course = Course.objects.get(name=course_name)
                StudentCourse.objects.create(
                    student=instance,
                    course=course,
                )
            except Course.DoesNotExist:
                raise ValueError(f"Course '{course_name}' does not exist.")

@admin.register(Student)
class StudentAdmin(ImportExportMixin, admin.ModelAdmin):
    resource_class = StudentResource
    form = StudentForm
    list_display = ('student_id', 'student_user', 'department', 'level', 'group', 'list_courses', 'edit_user_link')
    list_filter = ('department', 'level', 'group',)
    search_fields = ('student_user__first_name', 'student_user__last_name')
    list_display_links = ('student_id', 'student_user',)
    inlines = [StudentCourseInline]
    fieldsets = (
        ('Student Details', {'fields': ('user', 'department', 'level', 'group',)}),
    )

    def list_courses(self, obj):  # إرجاع أسماء الكورسات المرتبطة بالقسم
        return ", ".join(course.name for course in obj.course.all())
    list_courses.short_description = 'Courses'

    def student_id(self, obj):
        return obj.user.id
    student_id.short_description = "ID"

    def student_user(self, obj):
        return obj.user
    student_user.short_description = "Student"

    def edit_user_link(self, obj): # رابط تعديل المستخدم
        return format_html('<a href="/admin/admin_app/user/{}/change/">Edit</a>', obj.user.id)
    edit_user_link.short_description = 'Edit User'

class InstructorInline(admin.StackedInline):
    model = Instructor
    extra = 1
    verbose_name_plural = 'Instructor Details'
    verbose_name = 'Instructor Details'
    fk_name = 'user'
    can_delete = False

class UserResource(ModelResource):
    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'username', 'password', 'email', 'phone', 'gender', 'birth_date', 'role', 'is_superuser', 'is_staff', 'is_active', 'image')
        
@admin.register(User)
class UserAdmin(ImportExportMixin, admin.ModelAdmin):
    resource_class = UserResource
    list_display = ('user_image', 'id', 'first_name', 'last_name', 'username', 'email', 'phone', 'gender', 'role', 'birth_date', 'date_joined', 'is_active', 'is_staff', 'is_superuser')
    list_filter = ('is_staff', 'is_superuser', 'role', 'gender', 'is_active')    
    search_fields = ('id', 'first_name', 'last_name', 'username', 'email', 'phone')
    list_display_links = ('id', 'username', 'first_name', 'last_name', 'user_image',)
    fieldsets = (
        (None, {'fields': ('username', 'password', 'role')}),
        ('Personal Information', {
            'fields': ('first_name', 'last_name', 'email', 'phone', 'gender', 'birth_date', 'image'),
            'classes': ('collapse',)
        }),
        ('Permissions', {
            'fields': ('user_permissions', 'is_staff', 'is_active', 'is_superuser'),
            'classes': ('collapse',)
        }),
    )
    inlines = [InstructorInline]   # الحقول المضمنة ستتم إضافتها ديناميكيًا

    class Media:
        js = ('js/admin_app/user_role.js',)
    
    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        # ------------------------Admin ---------------------
        if not request.user.is_superuser and request.user.role == 'ADMIN':
            # إذا كان المستخدم الحالي ليس superuser وكان له role=Admin
            # إخفاء حقل is_superuser من الـ fieldsets
            for fieldset in fieldsets:
                if 'is_superuser' in fieldset[1]['fields']:
                    fieldset[1]['fields'] = tuple(
                        field for field in fieldset[1]['fields'] if field != 'is_superuser'
                    )
        return fieldsets
    
    def user_image(self, obj):
        if obj.image:  # التحقق إذا كان للمستخدم صورة
            return format_html('<img src="{}" style="width: 40px; height: 40px; border-radius: 50%;" />', obj.image.url)
        return "No Image"
    user_image.short_description = 'Image'  # تغيير عنوان العمود

    def save_model(self, request, obj, form, change):
        if change: # إذا كان السجل موجودًا (تعديل المستخدم)
            # التحقق من الدور القديم
            old_user = User.objects.get(pk=obj.pk)
            old_role = old_user.role
            
            # إذا تم تغيير الدور، نحذف البيانات المرتبطة بالدور القديم
            if old_role != obj.role:
                print("Inside If Statement, Old_Role = {0}".format(old_role))
                if old_role == 'STUDENT':
                    Student.objects.filter(user=old_user).delete()
                elif old_role == 'INSTRUCTOR':
                    Instructor.objects.filter(user=old_user).delete()
                elif old_role == 'ADMIN':
                    print("ADMIN Delete: ....")
                    Admin.objects.filter(user=old_user).delete()
                    obj.is_staff = False
                    obj.is_superuser = False

                obj.save()

        if not change:
            obj.save()  # حفظ السجل الجديد
            if obj.role == 'ADMIN':
                Admin.objects.create(user=obj)
            elif obj.role == 'STUDENT' or obj.role == 'INSTRUCTOR':
                obj.is_staff = False
                obj.is_superuser = False
        

        # تأكد من أن كلمة المرور مشفرة إذا تم تغييرها
        if 'password' in form.changed_data:
            obj.password = make_password(obj.password)

        super().save_model(request, obj, form, change)
     
class AccountRequestForm(forms.ModelForm):
    class Meta:
        model = AccountRequest
        fields = ['full_name', 'email', 'phone_number', 'profile_image']

@admin.register(AccountRequest)
class AccountRequestAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'phone_number', 'is_approved', 'created_at', 'status')
    list_filter = ('is_approved', 'status', 'created_at')
    search_fields = ('full_name', 'email', 'phone_number')
    exclude = ('status',)
    actions = ['check_users', 'approve_requests', 'reject_requests']

    @admin.action(description='Check if users exist in the system')
    def check_users(self, request, queryset):
        """
        تحقق إذا كان المستخدم موجودًا في جدول User وأظهر رسالة للإدمن.
        """
        for account_request in queryset:
            user = User.objects.filter(email=account_request.email, phone=account_request.phone_number).first()
            if user:
                messages.success(
                    request, 
                    f"User with email {account_request.email} and phone {account_request.phone_number} exists. "
                    f"Username: {user.username}. Role: {user.role}."
                )
            else:
                messages.error(
                    request, 
                    f"User with email {account_request.email} and phone {account_request.phone_number} does not exist."
                )

    @admin.action(description='Approve selected account requests')
    def approve_requests(self, request, queryset):
        """
        إرسال رسالة الموافقة مع توليد كلمة مرور عشوائية من 8 أرقام.
        """
        for account_request in queryset:
            if account_request.is_approved:
                user = User.objects.filter(email=account_request.email).first()
                if user:
                    if user.role in ['STUDENT', 'INSTRUCTOR']:  # التحقق من الدور
                        try:
                            # توليد كلمة مرور عشوائية من 8 أرقام
                            temp_password = ''.join(random.choices('0123456789', k=8))

                            # تحديث كلمة المرور للمستخدم
                            user.set_password(temp_password)
                            user.save()

                            # إرسال رسالة الموافقة عبر الإيميل
                            send_mail(
                                'Account Approved',
                                f'Hello {account_request.full_name},\n\nYour account has been approved.\n\nUsername: {user.username}\nPassword: {temp_password}\n\nPlease log in and change your password immediately.',
                                'ytrudtrfjd@gmail.com',
                                [account_request.email],
                                fail_silently=False,
                            )

                            # تحديث حالة الطلب
                            account_request.is_approved = True
                            account_request.status = 'approved'
                            account_request.save()

                            messages.success(request, f"Approval email sent to {account_request.full_name}.")
                        except Exception as e:
                            messages.warning(request, f"Error while sending email to {account_request.email}: {str(e)}")
                    else:
                        messages.error(
                            request,
                            f"Cannot approve. User with email {account_request.email} has an invalid role: {user.role}."
                        )
                else:
                    messages.error(request, f"Cannot approve. User with email {account_request.email} does not exist.")
            else:
                messages.error(request,"Must be verified by admin and must check is_approved equal true")

    @admin.action(description='Reject selected account requests')
    def reject_requests(self, request, queryset):
        """
        إرسال رسالة الرفض فقط إذا كان المستخدم غير موجود في جدول User.
        """
        for account_request in queryset:
            if not account_request.is_approved:
                # تحقق من عدم وجود المستخدم
                user = User.objects.filter(email=account_request.email).first()
                if not user:
                    try:
                        # إرسال رسالة الرفض عبر الإيميل
                        send_mail(
                            'Account Request Denied',
                            f'Dear {account_request.full_name},\n\nWe regret to inform you that your account request has been denied as you are not registered in our system.',
                            'ytrudtrfjd@gmail.com',
                            [account_request.email],
                            fail_silently=False,
                        )

                        # تحديث حالة الطلب
                        account_request.is_approved = False
                        account_request.status = 'rejected'
                        account_request.save()

                        messages.success(request, f"Rejection email sent to {account_request.full_name}.")
                    except Exception as e:
                        messages.error(request, f"Error while sending email to {account_request.email}: {str(e)}")
                else:
                    messages.error(request, f"Cannot reject. User with email {account_request.email} exists.")
            else:
                messages.error(request,"Must be verified by admin and must check is_approved equal false")