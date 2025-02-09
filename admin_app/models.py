from django.db import models
from django.contrib.auth.models import AbstractUser  # Use Django's built-in User model
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator, RegexValidator
import os
import re
from datetime import date
from django.templatetags.static import static
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.timezone import now, timedelta
from django.db.models import Count
from datetime import date
import logging

# Create your models here.

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


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
                'pdf', 'doc', 'docx', 'txt', 'rtf', 'odt', 'xls', 'xlsx', 'csv', 'ppt', 'pptx','eddx',
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
    size = models.BigIntegerField(editable=False, default=0) # حجم الملف بالبايت فقط
    type = models.CharField(max_length=10, editable=False)  # Auto-detected
    upload_date = models.DateTimeField(auto_now_add=True,)  # Auto-detected
    upload_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='files' ,on_delete=models.CASCADE, limit_choices_to={'is_staff': True}, editable=False)
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
            logger.error("File size exceeds limit for file: %s", self.file.name)
            raise ValidationError(_("File size must be less than 80MB."))
                # تحقق من وصف الملف
        if self.description:
            valid_pattern = re.compile(r'^[a-zA-Z0-9(),."\'\s]*$')
            if not valid_pattern.match(self.description):
                logger.error("Invalid description detected for file: %s", self.file.name if self.file else "No file")
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

            self.size = self.file.size  # تحويل الحجم إلى تنسيق قابل للقراءة
            self.type = self.get_file_extension()  # Detect file extension/type
            self.category = self.detect_category()  # Detect and set the category

        super().save(*args, **kwargs)
        if hasattr(self, 'upload_by') and self.upload_by:
            logger.info("File '%s' saved by user '%s'.", self.name, self.upload_by)
        else:
            logger.info("File '%s' saved.", self.name)

    def delete(self, *args, **kwargs):
        # حذف الملف المخزن عند حذف الكائن
        logger.warning("Initiating delete process for File: %s", self.file.name if self.file else "No file")
        if self.file and os.path.isfile(self.file.path):
            os.remove(self.file.path)  # حذف الملف الفعلي من نظام الملفات
        super().delete(*args, **kwargs)
        logger.info("File deleted from database: %s", self.file.name if self.file else "No file")

    def get_file_extension(self):
        _, ext = os.path.splitext(self.file.name)
        ext = ext.lower().replace('.', '')
        return ext if ext else "unknown"

    def detect_category(self):
        doc_ext = {'pdf', 'doc', 'docx', 'txt', 'rtf', 'odt', 'xls', 'xlsx', 'csv', 'ppt', 'pptx','eddx'}
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
    
    def get_human_readable_size(self):
        size = self.size
        #  تحويل الحجم إلى تنسيق قابل للقراءة (KB, MB, GB)
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0
        return f"{size:.2f} PB"
    
    def __str__(self):
        return f"{self.name}"
    
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
            valid_pattern = re.compile(r'^[a-zA-Z\s]*$')
            if not valid_pattern.match(self.name):
                logger.error("Invalid Department name: %s", self.name)
                raise ValidationError({
                    'name': _("Name can only contain letters.")
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
                logger.error("Invalid Course name: %s", self.name)
                raise ValidationError({
                    'name': _("Name can only contain letters and numbers.")
                })
        logger.info("Clean completed for Course: %s", self.name)
            
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
                regex=r'^[a-zA-Z\s]+$',  # يسمح فقط بالأحرف الإنجليزية
                message='First name must contain letters only.'
            )
        ],)
    last_name = models.CharField(
        max_length=150,
        validators=[
            RegexValidator(
                regex=r'^[a-zA-Z\s]+$',  # يسمح فقط بالأحرف الإنجليزية
                message='Last name must contain letters only.'
            )
        ],)
    email = models.EmailField(
        verbose_name='email address',
        unique=True,  # يضمن عدم تكرار الإيميلات
    )
    phone = models.PositiveIntegerField(
        verbose_name='phone number',
        unique=True,
        help_text='Digits only.',
        validators=[
            RegexValidator(
                regex=r'^\d{9}$',  # يسمح فقط بتسعة أرقام
                message='Phone number must contain exactly 9 digits without any letters or special characters.'
            )
        ],)
    gender = models.CharField(max_length=1, choices=[('M', 'Male'), ('F', 'Female')],)
    birth_date = models.DateField(null=False, blank=False)
    role = models.CharField(max_length=10, choices=Roles.choices,)
    image = models.ImageField(upload_to='user_images/%y/%m/%d',)

    class Meta:
        unique_together = ('first_name', 'last_name',)
        
    def clean(self):
        super().clean()  # استدعاء التحقق الأساسي للنموذج
        self.first_name = self.first_name.strip().title()
        self.last_name = self.last_name.strip().title()
        
        less_age = date.today().year - 18
        if self.birth_date.year >= less_age:
            raise ValidationError({
                'birth_date':_('Your age must be greater than 18 years')
            })
        
        if self.phone:
            valid_range = (
                (770000000 <= self.phone <= 789999999) or
                (710000000 <= self.phone <= 719999999) or
                (730000000 <= self.phone <= 739999999)
            )
            # استبعاد الأرقام الممنوعة
            excluded_numbers = {777777777}
            
            if not valid_range or self.phone in excluded_numbers:
                logger.error("Invalid phone number for User: %s", self.phone)
                raise ValidationError({
                    'phone': _(
                        'Phone number must be in the allowed ranges: '
                        '77*******, 78*******, 71*******, or 73*******, '
                        'and must not include restricted numbers like 777777777.'
                    )
                })
        logger.info("Clean completed for User: %s %s", self.first_name, self.last_name)
    
    
    def get_profile_image_url(self):
        """
        Returns the URL of the user's profile image if it exists, otherwise the default logo.
        """
        if self.image and os.path.isfile(self.image.path):  # تحقق من وجود الملف فعليًا
            return self.image.url
        return static('img/user_black.svg')  # الصورة الافتراضية
    
    def get_formatted_number_birth_date(self):
        return self.birth_date.strftime('%d-%m-%Y')
    
    def get_formatted_letter_birth_date(self):
        return self.birth_date.strftime('%b. %d, %Y')
    
    def get_age(self):
        """
        حساب عمر المستخدم بناءً على تاريخ الميلاد.
        """
        logger.info("Calculating age for User: %s", self.username)
        today = date.today()
        age = today.year - self.birth_date.year

        # التحقق من إذا كان عيد الميلاد لهذا العام قد حدث أم لا
        if (today.month < self.birth_date.month) or (today.month == self.birth_date.month and today.day < self.birth_date.day):
            age -= 1  # لم يحن عيد الميلاد بعد هذا العام
        
        return f"{age} years"
                
    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Admin(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="admins")
    
    def __str__(self):
        return f"{self.user.get_full_name()}"

class Instructor(models.Model):
    departments = models.ManyToManyField('Department', related_name='instructors', limit_choices_to={'status': True}, blank=True,)
    courses = models.ManyToManyField('Course', related_name="instructors", limit_choices_to={'status': True}, blank=True,)
    groups = models.ManyToManyField('Group', related_name='instructors', limit_choices_to={'status': True}, blank=True,)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="instructors")
            
    def __str__(self):
        logger.info("Returning string representation for Instructor: %s", self.user.get_full_name())
        return f"{self.user.get_full_name()}"

class  Student(models.Model):
    class Levels(models.IntegerChoices):
        ONE = 1, _('1')
        TWO = 2, _('2')
        THREE = 3, _('3')
        FOUR = 4, _('4')

    department = models.ForeignKey('Department', on_delete=models.CASCADE, related_name='students', limit_choices_to={'status': True},)
    level = models.IntegerField(choices=Levels.choices, default=Levels.ONE,)
    group = models.ForeignKey('Group', on_delete=models.CASCADE, related_name='students', limit_choices_to={'status': True},)
    course = models.ManyToManyField('Course', through='StudentCourse', limit_choices_to={'status': True}, related_name="students",)    
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="students", limit_choices_to={'role': 'STUDENT', 'is_active': True},)
    
    def clean(self):
        super().clean()
        try:
            if self.group:
                if self.group.level != self.level:
                    logger.error("Student level and Group level mismatch for user: %s", self.user.get_full_name() if self.user else "No user")
                    raise ValidationError({
                        'group': _("Student's level should match the group's level.")
                    })
                if self.group.department != self.department:
                    logger.error("Student department and Group department mismatch for user: %s", self.user.get_full_name() if self.user else "No user")
                    raise ValidationError({
                        'group': _("Student's department should match the group's department.")
                    })
        except self.__class__.group.RelatedObjectDoesNotExist:
            logger.warning("Group not set for Student: %s", self.user.get_full_name() if self.user else "No user")
            pass  # Ignore if the group is not set
        logger.info("Clean completed for Student: %s", self.user.get_full_name() if self.user else "No user")


    def __str__(self):
        return f"{self.user.get_full_name()}"

class StudentCourse(models.Model):
    class Levels(models.TextChoices):
        STUDY = 'STUDY', _('Study')
        SUSPENDED = 'SUSPENDED', _('Suspended')
        COMPLETED = 'COMPLETED', _('Completed')
    student = models.ForeignKey("Student", on_delete=models.CASCADE, related_name='student_courses', limit_choices_to={'user__is_active': True},)
    course = models.ForeignKey("Course", on_delete=models.CASCADE, related_name='student_courses', limit_choices_to={'status': True},)
    status = models.CharField(choices=Levels.choices, default=Levels.STUDY, max_length=10, )
    semester = models.CharField(max_length=10, choices=[('1', _('First')), ('2', _('Second'))], default='1')
    year = models.PositiveIntegerField(default=date.today().year, editable=False,)
    
    class Meta:
        unique_together = ('student', 'course',)

    def clean(self):
        super().clean()
        try:
            # التحقق من مستوى الطالب ومادة الكورس
            if self.student.level != self.course.level:
                logger.error("Student level and Course level mismatch for student: %s", self.student.user.get_full_name() if self.student and self.student.user else "No student")
                raise ValidationError({
                    'course': _("The student's level must match the course's level.")
                })

            # التحقق من تخصص الطالب ومادة الكورس
            if not self.course.departments.filter(id=self.student.department.id).exists():
                logger.error("Student department and Course department mismatch for student: %s", self.student.user.get_full_name() if self.student and self.student.user else "No student")
                raise ValidationError({
                    'course': _("The student's department must match the course's department.")
                })

            # التحقق من السنة
            current_year = date.today().year
            if self.year < current_year or self.year > current_year:
                logger.error("Invalid year for StudentCourse for student: %s", self.student.user.get_full_name() if self.student and self.student.user else "No student")
                raise ValidationError({
                    'year': _("The year must be equal to the current year.")
                })
        except self.__class__.student.RelatedObjectDoesNotExist:
            logger.warning("Student not set for StudentCourse")
            pass
        

    def __str__(self):
        return f"{self.student.user.first_name} - {self.course.name}"

class AccountRequest(models.Model):
    full_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20)
    profile_image = models.ImageField(upload_to="account_requests/%y/%m/%d/", null=True, blank=True)
    is_approved = models.BooleanField(default=False)
    status = models.CharField(max_length=10, choices=[('APPROVED', 'Approved'), ('REJECTED', 'Rejected'), ('PENDING', 'Pending')], default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name
    
    class Meta:
        verbose_name = "Account Request"
        verbose_name_plural = "Account Requests"

def default_expiry():
     return now() + timedelta(minutes=5)

class OTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(default=default_expiry)

    def is_expired(self):
        return now() > self.expires_at

    def __str__(self):
        return f"{self.user.username} - {self.otp}"