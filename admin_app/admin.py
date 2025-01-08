from django.contrib import admin
from import_export.admin import ExportMixin, ImportExportModelAdmin, ImportExportMixin
from import_export.resources import ModelResource
from import_export import resources, fields
from import_export.widgets import ManyToManyWidget, ForeignKeyWidget
from .models import File, Department, Course, Group, User, Admin, Instructor, Student, StudentCourse
from django.contrib.auth.hashers import make_password
from django.utils.html import format_html
from django import forms
from django.forms import BaseInlineFormSet
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


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
    list_display = ('name', 'course__name' ,'category', 'type', 'size', 'display_upload_by', 'status', 'upload_date', 'view_file')
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
    display_upload_by.short_description = "Upload_By"
    
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
        js = ('js/admin/select_group.js',)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        department = self.data.get('department') or self.initial.get('department')
        level = self.data.get('level') or self.initial.get('level')

        if department and level:
            self.fields['group'].queryset = Group.objects.filter(department=department, level=level)
        else:
            self.fields['group'].queryset = Group.objects.none()

class StudentResource(ModelResource):
    # الحقول الأساسية للطالب
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

    # الحقول الإضافية المرتبطة بالمواد الدراسية
    # course_status = fields.Field(
    #     column_name='course_status',
    #     attribute='student_courses',
    #     widget=ForeignKeyWidget(StudentCourse, 'status'),
    # )
    # course_semester = fields.Field(
    #     column_name='course_semester',
    #     attribute='student_courses',
    #     widget=ForeignKeyWidget(StudentCourse, 'semester'),
    # )
    # course_year = fields.Field(
    #     column_name='course_year',
    #     attribute='student_courses',
    #     widget=ForeignKeyWidget(StudentCourse, 'year'),
    # )


    class Meta:
        model = Student
        fields = ('id', 'first_name', 'last_name', 'department', 'level', 'group', 'courses',)
        # fields = ('id', 'first_name', 'last_name', 'department', 'level', 'group', 'courses', 'course_status', 'course_semester', 'course_year',)
        # export_order = (
        #     'id', 'first_name', 'last_name', 'department', 'level', 'group',
        #     *(f'course_{i}' for i in range(1, 11)),
        #     *(f'course_{i}_semester' for i in range(1, 11)),
        #     *(f'course_{i}_year' for i in range(1, 11)),
        #     *(f'course_{i}_status' for i in range(1, 11)),
        # )

    # def dehydrate(self, student):
    #     # Fetch related courses
    #     student_courses = StudentCourse.objects.filter(student=student).select_related('course')

    #     # Prepare course data
    #     for idx, student_course in enumerate(student_courses[:10], start=1):
    #         self.fields[f'course_{idx}'].attribute = student_course.course.name
    #         self.fields[f'course_{idx}_semester'].attribute = student_course.semester
    #         self.fields[f'course_{idx}_year'].attribute = student_course.year
    #         self.fields[f'course_{idx}_status'].attribute = student_course.status

    #     return super().dehydrate(student)

    
    
    # # Validate data before importing
    # def before_import_row(self, row, **kwargs):
    #     department = row.get('department')
    #     level = row.get('level')
    #     courses = []

    #     # Collect course data
    #     for i in range(1, 11):  # يدعم حتى 10 مواد لكل طالب
    #         course_name = row.get(f'course_{i}')
    #         if course_name:
    #             courses.append({
    #                 'name': course_name.strip(),
    #                 'semester': row.get(f'course_{i}_semester'),
    #                 'year': row.get(f'course_{i}_year'),
    #                 'status': row.get(f'course_{i}_status'),
    #             })
        
    #     # Validate course data
    #     if department and level:
    #         for course in courses:
    #             try:
    #                 course_obj = Course.objects.get(name=course['name'])
    #                 # Check department and level match
    #                 if not course_obj.departments.filter(name=department).exists():
    #                     raise ValueError(f"Course '{course['name']}' does not belong to department '{department}'.")
    #                 if course_obj.level != int(level):
    #                     raise ValueError(f"Course '{course['name']}' does not match the student's level '{level}'.")
    #             except Course.DoesNotExist:
    #                 raise ValueError(f"Course '{course['name']}' does not exist.")
        
    #     # التحقق من الحقول الإضافية
    #     for course in courses:
    #         if not course['semester'] or not course['year'] or not course['status']:
    #             raise ValueError(f"All fields (semester, year, status) are required for course '{course['name']}'.")

    # # Save related courses in the intermediary table
    # def save_m2m(self, instance, data):
    #     super().save_m2m(instance, data)
        
    #     # حفظ المواد الدراسية في الجدول الوسيط
    #     for i in range(1, 11):  # يدعم حتى 10 مواد لكل طالب
    #         course_name = data.get(f'course_{i}')
    #         if course_name:
    #             course = Course.objects.get(name=course_name.strip())
    #             StudentCourse.objects.update_or_create(
    #                 student=instance,
    #                 course=course,
    #                 defaults={
    #                     'semester': data.get(f'course_{i}_semester'),
    #                     'year': data.get(f'course_{i}_year'),
    #                     'status': data.get(f'course_{i}_status'),
    #                 }
    #             )

## Dynamic fields for courses and their related attributes
# def add_course_fields(cls):
#     for i in range(1, 11):  # Assuming up to 10 courses per student
#         cls.declared_fields[f'course_{i}'] = fields.Field(
#             column_name=f'course_{i}',
#             attribute='',
#             readonly=True,
#         )
#         cls.declared_fields[f'course_{i}_semester'] = fields.Field(
#             column_name=f'course_{i}_semester',
#             attribute='',
#             readonly=True,
#         )
#         cls.declared_fields[f'course_{i}_year'] = fields.Field(
#             column_name=f'course_{i}_year',
#             attribute='',
#             readonly=True,
#         )
#         cls.declared_fields[f'course_{i}_status'] = fields.Field(
#             column_name=f'course_{i}_status',
#             attribute='',
#             readonly=True,
#         )
# # Call the method to dynamically add fields during class definition
# add_course_fields(StudentResource)

@admin.register(Student)
class StudentAdmin(ImportExportMixin, admin.ModelAdmin):
    resource_class = StudentResource
    form = StudentForm
    list_display = ('user__id', 'user', 'department', 'level', 'group', 'list_courses', )
    list_filter = ('department', 'level', 'group',)    
    search_fields = ('user__first_name', 'user__last_name')
    inlines = [StudentCourseInline]
    fieldsets = (
        ('Student Details', {'fields': ('user', 'department', 'level', 'group',)}),
    )

    def list_courses(self, obj): # إرجاع أسماء الكورسات المرتبطة بالقسم
        return ", ".join(course.name for course in obj.course.all())
    list_courses.short_description = 'Courses'

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

        

        
