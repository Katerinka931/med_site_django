from . import views
from django.conf.urls.static import static
from django.conf import settings
from django.urls import re_path
from rest_framework_simplejwt.views import token_refresh


from .CustomTokenSerializer.TokenSerializer import CustomTokenView
from .views import DoctorsInfoClass, MainListClass, PatientsListClass, ProfileClass, CreateUserClass, EditUserClass, \
    CreatePatientClass, EditPatientClass, PatientsInfoClass

urlpatterns = [
                  re_path(r'^login', CustomTokenView.as_view(), name='token_obtain_pair'),  # token_obtain_pair),
                  re_path(r'^refresh_token', token_refresh),
                  re_path(r'^logout$', views.user_logout),

                  re_path(r'^main$', MainListClass.as_view()),
                  re_path(r'^patients$', PatientsListClass.as_view()),
                  re_path(r'^profile$', ProfileClass.as_view()),

                  re_path(r'^create_user$', CreateUserClass.as_view()),
                  re_path(r'^edit_user/(?P<usr>\d+)$', EditUserClass.as_view()),
                  re_path(r'^user/(?P<usr>\d+)$', DoctorsInfoClass.as_view()),

                  re_path(r'^create_patient$', CreatePatientClass.as_view()),
                  re_path(r'^edit_patient/(?P<pat>\d+)$', EditPatientClass.as_view()),
                  re_path(r'^patient/(?P<pat>\d+)$', PatientsInfoClass.as_view()),

                  re_path(r'^load_image$', views.LoadImageClass.as_view()),

              ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
