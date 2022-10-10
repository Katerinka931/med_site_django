from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenObtainSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

from MedApp.models import Doctor


class CustomTokenSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        refresh = self.get_token(self.user)

        data["refresh"] = str(refresh)
        data["access"] = str(refresh.access_token)
        data["role"] = Doctor.objects.get(login=self.user).role

        return data


class CustomTokenView(TokenObtainPairView):
    serializer_class = CustomTokenSerializer
    token_obtain_pair = TokenObtainPairView.as_view()