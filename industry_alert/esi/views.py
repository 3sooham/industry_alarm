from django.shortcuts import render, get_object_or_404
from django.utils import timezone # timezone.now() 사용하기 위함임

from .models import IndustryJobs
from .serializers import IndustryJobsSerializer

# 여기부터 drf viewset 적용위한거임
from rest_framework import viewsets, serializers, status
from rest_framework.decorators import action
from rest_framework.response import Response


class IndustryJobViewSet(viewsets.GenericViewSet):
    queryset = IndustryJobs.objects.all()
    serializer_class = IndustryJobsSerializer

    # http GET http://127.0.0.1:8000/api/v1/post "Authorization: Token 65b51c4fbf5914eda00efdeb7828842dd0d4dcc6"
    def list(self, request):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    # http GET http://127.0.0.1:8000/api/v1/post/<int:pk>
    def retrieve(self, request, pk):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    # http GET http://127.0.0.1:8000/api/v1/post/published "Authorization: Token 65b51c4fbf5914eda00efdeb7828842dd0d4dcc6"
    # 이거 /api/v1/post/published로 등록됨
    # 그리고 이전에 했던 것 처럼 cur_user = UserSerializer(request.user) 이렇게 시리얼라이져 탈 필요없음
    # 왜냐면 request.user가 실제 User 인스턴스라서 걍 바로 넣어도 됨
    @action(methods=['get'], detail=False, url_path='users_jobs')
    def get_users_industry_jobs(self, request):
        queryset = self.get_queryset().filter(user=request.user)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    # 아직 완료안된 job 가져오기

    # bulk create
    def create(self, request):
        # 이거 하면
        # def get_serializer(self):
        #     context = self.get_serializer_context()
        #     serializer = self.get_serializer_class(self.validated_data, context=context)
        #     return serializer
        # 대충 이렇게 생김 자세한 코드는 찾아보기
        # import pdb; pdb.set_trace()
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            # 이거 save()했을때 불려오는 method는
            # serializer = UserSerializer(data=request.data)에서 data앞에 뭐가 없으면
            # UserSerializer.create()를 불러오는거임
            # 일단 post를 생성하고
            serializer.save()
        except serializers.ValidationError:
            return Response({"status": "failed", "errors": serializer.errors})

        return Response(serializer.data)


    # http DELETE http://127.0.0.1:8000/api/v1/post/12 "Authorization: Token bf8bf34417deb3cbd2bfa502d37013243cd9f5eb"
    #  get_object() looks for a pk_url_kwarg argument in the arguments to the view;
    #  if this argument is found, this method performs a primary-key based lookup using that value.
    # https://docs.djangoproject.com/en/3.2/ref/class-based-views/mixins-single-object/#django.views.generic.detail.SingleObjectMixin.get_object
    def delete(self, request, pk):
        instance = self.get_object()
        instance.delete()
        # 이거 왜 resoponse가 안나오는거임?
        # https://developer.mozilla.org/ko/docs/Web/HTTP/Status/204
        return Response({'success': True}, status=status.HTTP_204_NO_CONTENT)

    # http PUT http://127.0.0.1:8000/api/v1/post/21 "Authorization: Token bf8bf34417deb3cbd2bfa502d37013243cd9f5eb" text="올암"
    def update(self, request, pk):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        try:
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        except serializers.ValidationError:
            return Response({"status": "failed", "errors": serializer.errors})