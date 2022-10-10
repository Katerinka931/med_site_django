from . import views
from django.conf.urls.static import static
from django.conf import settings
from django.urls import re_path
from rest_framework_simplejwt.views import token_refresh

from .CustomTokenSerializer.TokenSerializer import CustomTokenView

urlpatterns = [
                  re_path(r'^login', CustomTokenView.as_view(), name='token_obtain_pair'),  # token_obtain_pair),
                  re_path(r'^refresh_token', token_refresh),
                  re_path(r'^logout$', views.user_logout),

                  re_path(r'^main$', views.main),
                  re_path(r'^patients$', views.patients_list),

                  re_path(r'^profile$', views.profile),
                  re_path(r'^create_user$', views.create_user),
                  re_path(r'^edit_user/(?P<usr>\d+)$', views.edit_user),
                  re_path(r'^user/(?P<usr>\d+)$', views.doctors_info),

                  re_path(r'^create_patient$', views.create_patient),
                  re_path(r'^edit_patient/(?P<pat>\d+)$', views.edit_patient),
                  re_path(r'^patient/(?P<pat>\d+)$', views.patients_info),

                  re_path(r'^load_image$', views.load_image),

              ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
