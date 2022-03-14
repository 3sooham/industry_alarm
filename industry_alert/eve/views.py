from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from .serializers import EveSerializer
from .models import Eve

from rest_framework.response import Response

class EveViewSet(viewsets.ModelViewSet):
    queryset = Eve.objects.all()
    serializer_class = EveSerializer
    permission_classes = [AllowAny]

    def list(self, request):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

        print("asddddddddd")

        return Response(serializer.data)