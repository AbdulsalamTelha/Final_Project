from django.contrib import admin
from import_export.admin import ExportMixin, ImportExportModelAdmin, ImportExportMixin
from import_export.resources import ModelResource
from import_export import resources, fields
from import_export.widgets import ManyToManyWidget
from .models import File, Department, Course, Group, User, Admin, Instructor, Student, StudentCourse
from django.contrib.auth.hashers import make_password
from django.utils.html import format_html
from django import forms
# Register your models here.

class FileAdminForm(forms.ModelForm):
    class Meta:
        model = File
        fields = '__all__'
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3, 'cols': 40}),  # تعديل الحجم
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['description'].widget.attrs.update({'class': 'validate-letters-numbers'})  # إضافة فئة CSS


class FileResource(ModelResource):
    class Meta:
        model = File
        fields = ('id', 'name', 'category', 'type', 'size', 'upload_by', 'upload_by__username', 'status', 'upload_date', 'course__name', 'file')

@admin.register(File)
class FileAdmin(ExportMixin, admin.ModelAdmin):
    form = FileAdminForm
    resource_class = FileResource
    list_display = ('name', 'course__name' ,'category', 'type', 'size', 'display_upload_by', 'status', 'upload_date', 'view_file')
    list_filter = ('status', 'type', 'upload_date', 'category')
    search_fields = ('name', 'upload_by__username', 'type', 'category')
    readonly_fields = ('name', 'category', 'size', 'type', 'upload_by', 'upload_date')

    class Media:
        js = ('js/validation.js',)

    def display_upload_by(self, obj):
        return obj.upload_by.username if obj.upload_by else "N/A"
    display_upload_by.short_description = "Upload_By"
    
    def view_file(self, obj):    # دالة لاستعراض الملف
        if obj.file and obj.file.url:  # التحقق من وجود الملف والرابط
            return format_html('<a href="{}" target="_blank">View File</a>', obj.file.url)
        return "No file"
    view_file.short_description = "View File"

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


class DepartmentAdminForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({'class': 'validate-field'})

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
    class Meta:
        model = Group
        fields = ('id', 'name', 'status', 'level')

@admin.register(Group)
class GroupAdmin(ExportMixin, admin.ModelAdmin):
    resource_class = GroupResource
    list_display = ('name', 'level', 'department', 'status')
    list_filter = ('department', 'level', 'status')
    search_fields = ('name',)
    fieldsets = (
        (None, {
            'fields': ('name', 'level', 'department', 'status',),
        }),
    )

class StudentCourseResource(ModelResource):
    class Meta:
        model = StudentCourse
        fields = ('student', 'course','status','semester', 'year')

@admin.register(StudentCourse)
class StudentCourseAdmin(admin.ModelAdmin):
    resource_class = StudentCourseResource
    list_display = ('student', 'course','status','semester', 'year')

class StudentInline(admin.StackedInline):
    model = Student
    extra = 1  # عدد النماذج الإضافية التي تظهر
    verbose_name_plural = 'Student Details'
    verbose_name = 'Student Details'
    fields = ['level', 'group', 'department']  # الحقول التي ستظهر
    fk_name = 'user'  # الحقل الذي يربط Student بـ User
    classes = ('collapse',)  # تقليص النموذج

class InstructorInline(admin.StackedInline):
    model = Instructor
    extra = 1
    verbose_name_plural = 'Instructor Details'
    verbose_name = 'Instructor Details'
    fk_name = 'user'
    classes = ('collapse',)

class AdminInline(admin.StackedInline):
    model = Admin
    extra = 1
    verbose_name_plural = 'Admin Details'
    verbose_name = 'Admin Details'
    fk_name = 'user'
    classes = ('collapse',)

class UserResource(ModelResource):
    class Meta:
        model = User
        fields = ('id', 'first_name', 'status', 'last_name')

@admin.register(User)
class UserAdmin(ExportMixin, admin.ModelAdmin):
    resource_class = UserResource
    list_display = ('first_name', 'last_name', 'username', 'email', 'phone', 'gender', 'role', 'date_joined', 'is_active', 'is_staff', 'is_superuser')
    list_filter = ('is_staff', 'is_superuser', 'role', 'gender', 'is_active')    
    search_fields = ('first_name', 'last_name', 'username', 'email', 'phone')
    ordering = ('username',)
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
    inlines = [StudentInline, InstructorInline, AdminInline]   # الحقول المضمنة ستتم إضافتها ديناميكيًا

    class Media:
        js = ('js/admin/user_role.js',)
    
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
    
    def save_model(self, request, obj, form, change):
        # تأكد من أن كلمة المرور مشفرة
        if 'password' in form.changed_data:
            obj.password = make_password(obj.password)  
        super().save_model(request, obj, form, change)
