from . import views
from django.conf.urls.static import static
from django.conf import settings
from django.urls import re_path
from rest_framework_simplejwt.views import token_refresh

from .serializers.TokenSerializer import CustomTokenView
from .views import UserInfoClass, MainListClass, PatientsListClass, ProfileClass, CreateUserClass, EditUserClass, \
    CreatePatientClass, EditPatientClass, PatientsInfoClass

urlpatterns = [
                  re_path(r'^login', CustomTokenView.as_view(), name='token_obtain_pair'),
                  re_path(r'^refresh_token', token_refresh),
                  re_path(r'^logout$', views.user_logout),

                  re_path(r'^main$', MainListClass.as_view(), name='main-page'),
                  re_path(r'^patients$', PatientsListClass.as_view(), name='patients-list'),
                  re_path(r'^profile$', ProfileClass.as_view(), name='profile'),

                  re_path(r'^create_user$', CreateUserClass.as_view(), name='create-user'),
                  re_path(r'^edit_user/(?P<usr>\d+)$', EditUserClass.as_view(), name='edit-user'),
                  re_path(r'^user/(?P<usr>\d+)$', UserInfoClass.as_view(), name='users-data'),

                  re_path(r'^create_patient$', CreatePatientClass.as_view(), name='create-patient'),

                  re_path(r'^edit_patient/(?P<pat>\d+)$', EditPatientClass.as_view({'get': 'get', 'put': 'put'}),
                          name='edit-patient'),
                  re_path(r'^edit_patient/(?P<pat>\d+)/photo$',
                          EditPatientClass.as_view({'post': 'post_photo_instance'}), name='edit-photo'),

                  re_path(r'^patient/(?P<pat>\d+)$', PatientsInfoClass.as_view({'get': 'get', 'delete': 'delete'}),
                          name='patients-data'),
                  re_path(r'^patient/(?P<pat>\d+)/history$', PatientsInfoClass.as_view({'get': 'get_photos_history'}),
                          name='patients-data'),
                  re_path(r'^patient/(?P<pat>\d+)/download/(?P<type>\w+)$',
                          PatientsInfoClass.as_view({'get': 'download'}), name='patients-data'),

                  re_path(r'^load_image$', views.LoadImageClass.as_view({'get': 'get', 'post': 'post_predict'}),
                          name='load-image'),
                  re_path(r'^load_image/save$', views.LoadImageClass.as_view({'post': 'post_save'}),
                          name='load-image-save'),

              ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
