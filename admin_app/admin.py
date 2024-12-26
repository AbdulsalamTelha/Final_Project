from django.contrib import admin
from import_export.admin import ExportMixin, ImportExportModelAdmin, ImportExportMixin
from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget
from import_export.resources import ModelResource
from .models import File, Department, Course, Group

# Register your models here.

# File Resource for Import-Export
class FileResource(ModelResource):
    class Meta:
        model = File
        fields = ('id', 'name', 'category', 'type', 'size', 'upload_by__username', 'status', 'upload_date')

# File Admin with Import-Export and Filters
@admin.register(File)
class FileAdmin(ExportMixin, admin.ModelAdmin):
    resource_class = FileResource
    list_display = ('name', 'course__name' ,'category', 'type', 'size', 'upload_by', 'status', 'upload_date')
    list_filter = ('status', 'type', 'upload_date', 'category')
    search_fields = ('name', 'upload_by__username', 'type', 'category')
    readonly_fields = ('name', 'category', 'size', 'type', 'upload_by', 'upload_date')

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.upload_by = request.user
        super().save_model(request, obj, form, change)

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields
        return ()


# Course Resource
class CourseResource(ModelResource):
    class Meta:
        model = Course
        fields = ('id', 'name', 'level', 'status')

@admin.register(Course)
class CourseAdmin(ImportExportMixin, admin.ModelAdmin):
    resource_class = CourseResource
    list_display = ('id', 'name', 'name_initials' , 'level',  'list_departments', 'status',)
    list_filter = ('level', 'status')
    search_fields = ('name',)
    list_display_links = ('id', 'name', 'name_initials')

    def list_departments(self, obj):
        # إرجاع أسماء الأقسام المرتبطة بالكورس
        return ", ".join(department.name for department in obj.departments.all())
    list_departments.short_description = 'Departments'  # تغيير عنوان العمود في الجدول

    def name_initials(self, obj):
        # أخذ أول حرف من كل كلمة في اسم القسم
        return ''.join([word[0].upper() for word in obj.name.split()])
    name_initials.short_description = 'Abb.'  # تغيير عنوان العمود في الجدول

# Department Resource
class DepartmentResource(ModelResource):
    class Meta:
        model = Department
        fields = ('id', 'name', 'status')

@admin.register(Department)
class DepartmentAdmin(ImportExportMixin, admin.ModelAdmin):
    resource_class = DepartmentResource
    list_display = ('id', 'name', 'name_initials', 'list_courses', 'status') # إضافة دالة لعرض الكورسات
    list_filter = ('status',)
    search_fields = ('name',)
    list_display_links = ('id', 'name', 'name_initials')

    def list_courses(self, obj):
        # إرجاع أسماء الكورسات المرتبطة بالقسم
        return ", ".join(course.name for course in obj.courses.all())
    list_courses.short_description = 'Courses'  # تغيير عنوان العمود في الجدول

    def name_initials(self, obj):
        # أخذ أول حرف من كل كلمة في اسم القسم
        return ''.join([word[0].upper() for word in obj.name.split()])
    name_initials.short_description = 'Abb.'  # تغيير عنوان العمود في الجدول


# Group Resource
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
        # ('Department Information', {
        #     'fields': ('department',),
        #     'classes': ('collapse',)  # يمكنك استخدام collapse لجعل القسم قابلاً للطي
        # }),
        # ('Status', {
        #     'fields': ('status',),
        #     'classes': ('wide',)  # يمكنك استخدام wide لتوسيع هذا القسم
        # }),
    )