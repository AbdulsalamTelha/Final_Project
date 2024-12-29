from django import forms
from django.contrib import admin
from .models import Student, Course, StudentCourse
class CombinedStudentForm(forms.ModelForm):
    """نموذج مخصص لدمج حقول الطالب والدورات الدراسية"""
    # الحقول من StudentCourse
    course = forms.ModelChoiceField(queryset=Course.objects.all(), widget=forms.CheckboxSelectMultiple, required=False, label="Course")
    status = forms.BooleanField(required=False, label="Status")
    semester = forms.ChoiceField(choices=[('1', 'First'), ('2', 'Second')], required=False, label="Semester")
    year = forms.IntegerField(required=False, label="Year")

    class Meta:
        model = Student
        fields = ['level', 'group', 'department', 'course']  # الحقول من Student

class CombinedStudentInline(admin.StackedInline):
    """نموذج إداري مخصص لدمج حقول الطالب والدورات"""
    model = Student
    form = CombinedStudentForm
    extra = 1
    verbose_name_plural = 'Student Details and Courses'

    def save_formset(self, request, form, formset, change):
        """حفظ البيانات المدمجة"""
        obj = form.save(commit=False)
        obj.save()

        # حفظ بيانات الجدول الوسيط StudentCourse
        selected_courses = form.cleaned_data.get('course', [])
        for course in selected_courses:  # التعامل مع قائمة الدورات
            StudentCourse.objects.update_or_create(
                student=obj,
                course=course,
                defaults={
                    'status': form.cleaned_data['status'],
                    'semester': form.cleaned_data['semester'],
                    'year': form.cleaned_data['year'],
                }
            )
