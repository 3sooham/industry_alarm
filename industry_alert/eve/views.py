from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from .serializers import EveSerializer
from .models import Eve

from rest_framework.response import Response

class EveViewSet(viewsets.GenericViewSet):
    permission_classes = [AllowAny]
    queryset = Eve.objects.all()
    serializer_class = EveSerializer

    def list(self, request):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

        print("나는 뷰")
        print(serializer.data)

        return Response(serializer.data)
