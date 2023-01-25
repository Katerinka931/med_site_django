from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from MedApp.models import User

class CustomTokenSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        refresh = self.get_token(self.user)

        data["refresh"] = str(refresh)
        data["access"] = str(refresh.access_token)
        # todo delete it role
        data["role"] = User.index_to_role_for_old_model(User.objects.get(username=self.user.username).role)

        return data


class CustomTokenView(TokenObtainPairView):
    serializer_class = CustomTokenSerializer
    token_obtain_pair = TokenObtainPairView.as_view()