from django.apps import AppConfig

class AdminAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'admin_app'
    verbose_name = 'Services'  # اسم الكارد الذي سيظهر في لوحة التحكم

    def ready(self):
        import admin_app.signals # تأكد من استيراد ملف الإشارات