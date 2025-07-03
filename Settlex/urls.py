from django.contrib import admin
from django.urls import path, include
from two_factor import urls as tf_urls
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from settlements_app.views import (
    SettlexTwoFactorLoginView,
    SettlexTwoFactorSetupView,
)

settlex_two_factor_patterns = [
    path("login/", SettlexTwoFactorLoginView.as_view(), name="login"),
    path("setup/", SettlexTwoFactorSetupView.as_view(), name="setup"),
]

urlpatterns = [
    path("admin/login/", auth_views.LoginView.as_view(template_name="admin/login.html"), name="admin_login"),
    path("admin/", admin.site.urls),
    # ✅ This must come **before** your app's urls to register the namespace and avoid overrides
    path(
        "two_factor/",
        include(
            (
                settlex_two_factor_patterns
                + tf_urls.core
                + tf_urls.profile
                + tf_urls.plugin_urlpatterns,
                "two_factor",
            ),
            namespace="two_factor",
        ),
    ),

    # 🧾 Include your app routes last
    path("", include(("settlements_app.urls", "settlements_app"), namespace="settlements_app")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)