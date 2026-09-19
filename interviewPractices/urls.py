from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

from application1.views import EmployeeList, Login, get_public_key

urlpatterns = [
    path("admin/", admin.site.urls),
    path("login/", Login.as_view(), name="login"),
    path("employees/", EmployeeList.as_view(), name="employee_list"),
    path("public-key/", get_public_key, name="get_public_key"),
]

urlpatterns += static(
    settings.STATIC_URL,
    document_root=settings.STATICFILES_DIRS[0],
)

urlpatterns += static(
    settings.MEDIA_URL,
    document_root=settings.MEDIA_ROOT,
)
