import logging

class AppLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # سيتم استدعاء process_view لاحقًا، في حالة وجوده
        response = self.get_response(request)
        # بعد معالجة الطلب، يمكن تسجيل معلومات الاستجابة
        # هنا نستخدم logger الافتراضي إذا لم نتمكن من تحديد التطبيق
        default_logger = logging.getLogger('default')
        default_logger.info("Response sent: status=%s", response.status_code)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        # الحصول على الوحدة التي ينتمي لها الـ view (مثلاً "app1.views")
        module_path = view_func.__module__
        # استخراج اسم التطبيق: نفترض أن اسم التطبيق هو أول جزء من اسم الوحدة
        app_name = module_path.split('.')[0]

        # الحصول على logger الخاص بالتطبيق، وإذا لم يكن موجوداً نستخدم logger الافتراضي
        logger = logging.getLogger(app_name)
        if not logger.handlers:
            logger = logging.getLogger('default')

        user_info = request.user.username if hasattr(request, 'user') and request.user.is_authenticated else "Anonymous"

        # تسجيل تفاصيل الطلب مع معلومات المستخدم
        logger.info("Request received: method=%s, path=%s, user=%s", request.method, request.get_full_path(), user_info)

        return None