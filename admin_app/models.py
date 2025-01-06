from django import forms
from django.db import models
from django.contrib.auth.models import AbstractUser  # Use Django's built-in User model
from django.conf import settings
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.core.validators import FileExtensionValidator, RegexValidator, MinValueValidator, MaxValueValidator, MaxLengthValidator
import os
import re

# Create your models here.


class File(models.Model):
    choices = (
        ('PENDING', _('Pending')),
        ('APPROVED', _('Approved')),
        ('REJECTED', _('Rejected')),
    )

    file = models.FileField(
        max_length=255,
        upload_to="uploaded_files/%y/%m/%d",
        validators=[
            FileExtensionValidator([
                # Documents
                'pdf', 'doc', 'docx', 'txt', 'rtf', 'odt', 'xls', 'xlsx', 'csv', 'ppt', 'pptx',
                # Images
                'jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff', 'webp', 'svg',
                # Audio
                'mp3', 'wav', 'aac', 'ogg', 'wma', 'flac',
                # Video
                'mp4', 'avi', 'mkv', 'mov', 'wmv', 'flv', 'webm',
                # Archives
                'zip', 'rar', '7z', 'tar', 'gz', 'bz2',
                # Code and Markup
                'html', 'css', 'js', 'json', 'xml', 'yaml', 'py', 'java', 'cpp', 'c', 'h', 'php', 'sql',
                # Miscellaneous
                'md', 'epub', 'mobi', 'exe', 'apk', 'iso', 'dmg'
            ])
        ]
  # Validate file extensions
    )
    name = models.CharField(max_length=255, editable=False)  # Auto-detected
    size = models.CharField(max_length=50, editable=False)  # تحديث الحقل ليكون نصيًا
    type = models.CharField(max_length=10, editable=False)  # Auto-detected
    upload_date = models.DateTimeField(auto_now_add=True,)  # Auto-detected
    upload_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, limit_choices_to={'is_staff': True}, editable=False)
    description = models.TextField(max_length=500)  # Limit description length
    status = models.CharField(
        max_length=10,
        choices=choices,
        default=choices[0]
    )
    category = models.CharField(max_length=20, editable=False)
    course = models.ForeignKey(
        'Course',  # الربط مع كلاس Course
        on_delete=models.CASCADE,  # حذف الملفات عند حذف الدورة
        related_name="files",  # اسم العلاقة العكسية (للوصول إلى الملفات من الدورة)
        limit_choices_to={'status': True}
    )

    def clean(self):
        super().clean()
        self.description = self.description.strip().capitalize()
        # Validate file size (max 80MB)
        if self.file and self.file.size > 80 * 1024 * 1024:
            raise ValidationError(_("File size must be less than 80MB."))
                # تحقق من وصف الملف
        if self.description:
            valid_pattern = re.compile(r'^[a-zA-Z0-9(),."\'\s]*$')
            if not valid_pattern.match(self.description):
                raise ValidationError({
                    'description': _("Description can only contain letters, numbers, and parentheses.")
                })

    def save(self, *args, **kwargs):
        # Auto-detect file name, size, and type on save
        if self.file:
            original_name = os.path.basename(self.file.name) # Get file name
            if len(original_name) > 100:
                self.name = original_name[:97] + '...'  # تقصير الاسم مع إضافة "..."
            else:
                self.name = original_name

            self.size = self.get_human_readable_size(self.file.size)  # تحويل الحجم إلى تنسيق قابل للقراءة
            self.type = self.get_file_extension()  # Detect file extension/type
            self.category = self.detect_category()  # Detect and set the category

            try:
                # إذا كان الكائن موجودًا مسبقًا وكان الملف قد تغير
                old_instance = File.objects.get(pk=self.pk)
                if old_instance.file and old_instance.file != self.file:
                    # حذف الملف القديم
                    if os.path.isfile(old_instance.file.path):
                        os.remove(old_instance.file.path)
            except ObjectDoesNotExist:
                pass  # الكائن جديد، لذا لا يوجد ملف قديم لحذفه
    
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # حذف الملف المخزن عند حذف الكائن
        if self.file and os.path.isfile(self.file.path):
            os.remove(self.file.path)  # حذف الملف الفعلي من نظام الملفات
        super().delete(*args, **kwargs)

    def get_file_extension(self):
        _, ext = os.path.splitext(self.file.name)
        ext = ext.lower().replace('.', '')
        return ext if ext else "unknown"

    def detect_category(self):
        doc_ext = {'pdf', 'doc', 'docx', 'txt', 'rtf', 'odt', 'xls', 'xlsx', 'csv', 'ppt', 'pptx'}
        img_ext = {'jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff', 'webp', 'svg'}
        audio_ext = {'mp3', 'wav', 'aac', 'ogg', 'wma', 'flac'}
        video_ext = {'mp4', 'avi', 'mkv', 'mov', 'wmv', 'flv', 'webm'}
        archive_ext = {'zip', 'rar', '7z', 'tar', 'gz', 'bz2'}
        code_ext = {'html', 'css', 'js', 'json', 'xml', 'yaml', 'py', 'java', 'cpp', 'c', 'h', 'php', 'sql'}
        misc_ext = {'md', 'epub', 'mobi', 'exe', 'apk', 'iso', 'dmg'}

        ext = self.get_file_extension()

        if ext in doc_ext:
            return "Documents"
        elif ext in img_ext:
            return "Images"
        elif ext in audio_ext:
            return "Audio"
        elif ext in video_ext:
            return "Video"
        elif ext in archive_ext:
            return "Archives"
        elif ext in code_ext:
            return "Code and Markup"
        elif ext in misc_ext:
            return "Miscellaneous"
        else:
            return "Unknown"
    
    def get_human_readable_size(self, size):
        #  تحويل الحجم إلى تنسيق قابل للقراءة (KB, MB, GB)
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0
        return f"{size:.2f} PB"
    
    def __str__(self):
        return f"{self.name} ({self.get_status_display()})"
    
    class Meta:
        verbose_name = "File"
        verbose_name_plural = "Library Files"

class ParentAll(models.Model):
    name = models.CharField(max_length=100, unique=True)  # Common name field for all entities
    status = models.BooleanField(default=True)  # Common status field (active/inactive)

    class Meta:
        abstract = True  # This is an abstract model; no table will be created for this class

    def clean(self):
        super().clean()
        self.name = self.name.strip().title()

    def __str__(self):
        return self.name  # String representation of the object

class Department(ParentAll):
    def clean(self):
        super().clean()
        if self.name:
            valid_pattern = re.compile(r'^[a-zA-Z0-9\s]*$')
            if not valid_pattern.match(self.name):
                raise ValidationError({
                    'name': _("Name can only contain letters and numbers.")
                })

class Course(ParentAll):
    class Levels(models.IntegerChoices):
        ONE = 1, _('1')
        TWO = 2, _('2')
        THREE = 3, _('3')
        FOUR = 4, _('4')

    level = models.IntegerField(choices=Levels.choices)
    departments = models.ManyToManyField('Department', related_name='courses', limit_choices_to={'status': True})

    def clean(self):
        super().clean()
        if self.name:
            valid_pattern = re.compile(r'^[a-zA-Z0-9\s]*$')
            if not valid_pattern.match(self.name):
                raise ValidationError({
                    'name': _("Name can only contain letters and numbers.")
                })
            
    def __str__(self):
        return f"{self.name} ({self.get_level_display()})"

class Group(ParentAll):
    class Levels(models.IntegerChoices):
        ONE = 1, _('1')
        TWO = 2, _('2')
        THREE = 3, _('3')
        FOUR = 4, _('4')

    name = models.CharField(max_length=100)
    level = models.IntegerField(choices=Levels.choices)
    department = models.ForeignKey('Department', on_delete=models.CASCADE, related_name='groups', limit_choices_to={'status': True})

    class Meta:
        unique_together = ('name', 'level', 'department')  # Ensure uniqueness based on these fields

    def clean(self):
        super().clean()
        if self.name:
            valid_pattern = re.compile(r'^[a-zA-Z0-9\s-]*$')
            if not valid_pattern.match(self.name):
                raise ValidationError({
                    'name': _("Name can only contain letters, numbers and - .")
                })
            
    def __str__(self):
        return f"{self.name} - {self.level} - {self.department}"

class User(AbstractUser):
    class Roles(models.TextChoices):
        ADMIN = 'ADMIN', _('Admin')
        INSTRUCTOR = 'INSTRUCTOR', _('Instructor')
        STUDENT = 'STUDENT', _('Student')

    first_name = models.CharField(
        max_length=150,
        validators=[
            RegexValidator(
                regex=r'^[a-zA-Z]+$',  # يسمح فقط بالأحرف الإنجليزية
                message='First name must contain letters only.'
            )
        ],)
    last_name = models.CharField(
        max_length=150,
        validators=[
            RegexValidator(
                regex=r'^[a-zA-Z]+$',  # يسمح فقط بالأحرف الإنجليزية
                message='Last name must contain letters only.'
            )
        ],)
    email = models.EmailField(
        verbose_name='email address',
        unique=True,  # يضمن عدم تكرار الإيميلات
    )
    phone = models.PositiveIntegerField(
        verbose_name='phone number',
        help_text='Digits only.',
        validators=[
            RegexValidator(
                regex=r'^\d{9}$',  # يسمح فقط بتسعة أرقام
                message='Phone number must contain exactly 9 digits without any letters or special characters.'
            )
        ],)
    gender = models.CharField(max_length=1, choices=[('M', 'Male'), ('F', 'Female')],)
    birth_date = models.DateField()
    role = models.CharField(max_length=10, choices=Roles.choices,)
    image = models.ImageField(upload_to='user_images/%y/%m/%d')

    def clean(self):
        super().clean()  # استدعاء التحقق الأساسي للنموذج
        self.first_name = self.first_name.strip().title()
        self.last_name = self.last_name.strip().title()
        if self.phone:
            valid_range = (
                (770000000 <= self.phone <= 789999999) or
                (710000000 <= self.phone <= 719999999) or
                (730000000 <= self.phone <= 739999999)
            )
            # استبعاد الأرقام الممنوعة
            excluded_numbers = {777777777}
            
            if not valid_range or self.phone in excluded_numbers:
                raise ValidationError({
                    'phone': _(
                        'Phone number must be in the allowed ranges: '
                        '77*******, 78*******, 71*******, or 73*******, '
                        'and must not include restricted numbers like 777777777.'
                    )
                })
                
    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Admin(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="admins")
    
    def __str__(self):
        return f"{self.user.get_full_name()}"

class Instructor(models.Model):
    department = models.ManyToManyField('Department', related_name='instructors', limit_choices_to={'status': True})
    course = models.ManyToManyField('Course', related_name="instructors", limit_choices_to={'status': True})
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="instructors")

    def __str__(self):
        return f"{self.user.get_full_name()}"

class Student(models.Model):
    class Levels(models.IntegerChoices):
        ONE = 1, _('1')
        TWO = 2, _('2')
        THREE = 3, _('3')
        FOUR = 4, _('4')

    department = models.ForeignKey('Department', on_delete=models.CASCADE, related_name='students', limit_choices_to={'status': True},)
    level = models.IntegerField(choices=Levels.choices, default=Levels.ONE,)
    group = models.ForeignKey('Group', on_delete=models.CASCADE, related_name='students',)
    course = models.ManyToManyField('Course', through='StudentCourse', limit_choices_to={'status': True}, related_name="students",)    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="students", limit_choices_to={'role': 'STUDENT', 'is_active': True},)
    
    # def clean(self):
    #     if self.group:
    #         if self.group.level != self.level:
    #             raise ValidationError({
    #                 'group': _("Student's level should match the group's level.")
    #             })
    #         if self.group.department != self.department:
    #             raise ValidationError({
    #                 'group': _("Student's department should match the group's department.")
    #             })

    def __str__(self):
        return f"Student: {self.user.first_name} {self.user.last_name} (L:{self.level}) (D: {self.department})"

class StudentCourse(models.Model):
    student = models.ForeignKey("Student", on_delete=models.CASCADE, related_name='student_courses')
    course = models.ForeignKey("Course", on_delete=models.CASCADE, limit_choices_to={'status': True}, related_name='student_courses')
    status = models.BooleanField(default=True)
    semester = models.CharField(max_length=50, choices=[('1', _('First')), ('2', _('Second'))], default='1')
    year = models.PositiveIntegerField()
    
    def __str__(self):
        return f"{self.student.user.first_name} - {self.course.name}"


class AccountRequest(models.Model):
    full_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20)
    profile_image = models.ImageField(upload_to="account_requests/%y/%m/%d/", null=True, blank=True)
    is_approved = models.BooleanField(default=False)
    status = models.CharField(max_length=50, choices=[('approved', 'Approved'), ('rejected', 'Rejected')], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name
    
class AccountRequestForm(forms.ModelForm):
    class Meta:
        model = AccountRequest
        fields = ['full_name', 'email', 'phone_number', 'profile_image']
