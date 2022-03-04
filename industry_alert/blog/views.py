from django.shortcuts import render, get_object_or_404
from django.utils import timezone # timezone.now() 사용하기 위함임
from rest_framework.exceptions import ParseError

from .models import Post, Comment # Post모델, Comment모델을 불러오기 위함임
from .serializers import PostSerializer, CommentSerializer
from .forms import PostForm, CommentForm
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

# 여기부터 drf viewset 적용위한거임
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import serializers
from rest_framework import status
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.authtoken.models import Token

# CELERY TASK
from blog.tasks import count_widgets

# 뷰(view) 는 애플리케이션의 "로직"을 넣는 곳이에요.
# 뷰는 이전 장에서 만들었던 모델에서 필요한 정보를 받아와서 템플릿에 전달하는 역할을 합니다.

# 방금 post_list라는 함수(def)를 만들었습니다. 
# 이 함수는 요청(request)을 넘겨받아 render메서드를 호출합니다. 
# 이 함수는 render 메서드를 호출하여 받은(return) blog/post_list.html템플릿을 보여줍니다.

# 이미지 테스트
from .models import EntryImage
from .serializers import ImageSerializer
from django.contrib.contenttypes.models import ContentType

# drf viewset
class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [AllowAny]

# view는 들어온 요청을
# 적절한 serializer를 가져다가 serializer의 매서드를 실행하는거지
# 직접 뭘 하는부분은 아님

class PostViewSet2(viewsets.GenericViewSet):
    # 기본 설정이 is_authenticaed여서 이거 해줘야함
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    # http GET http://127.0.0.1:8000/api/v1/post "Authorization: Token 65b51c4fbf5914eda00efdeb7828842dd0d4dcc6"
    def list(self, request):
        print("쿼리 패러미터 : ", request.query_params)
        queryset = self.get_queryset().filter(published_date__lte=timezone.now()).order_by('published_date')
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    # http GET http://127.0.0.1:8000/api/v1/post/<int:pk>
    def retrieve(self, request, pk):
        post = self.get_object()
        serializer = self.serializer_class(post)
        return Response(serializer.data)

    # 내 published 된 post 검색
    # http GET http://127.0.0.1:8000/api/v1/post/published "Authorization: Token 65b51c4fbf5914eda00efdeb7828842dd0d4dcc6"
    # 이거 /api/v1/post/published로 등록됨
    # 그리고 이전에 했던 것 처럼 cur_user = UserSerializer(request.user) 이렇게 시리얼라이져 탈 필요없음
    # 왜냐면 request.user가 실제 User 인스턴스라서 걍 바로 넣어도 됨
    @action(methods=['get'], detail=False, url_path='published')
    def get_users_published_posts(self, request):
        # lte = less than equal
        # __ 이거는 역으로 접근하는거임
        queryset = self.get_queryset().filter(author=request.user, published_date__lte=timezone.now())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    # 이거도 위에 것 처럼 바꾸기
    # http GET http://127.0.0.1:8000/api/v1/post/get_users_posts "Authorization: Token bf8bf34417deb3cbd2bfa502d37013243cd9f5eb"
    @action(methods=['get'], detail=False)
    def get_users_posts(self, request):
        cur_user = UserSerializer(request.user)
        cur_user_name = cur_user.data['email']
        # 이거 왜 name=cur_user_name이렇게는 안됨?
        # 이거 모델 수정해서 name != email이라서 안대는거임
        asd = User.objects.get(email=cur_user_name)
        print(asd.id)
        # 일단 유저 id 출력하는거 까지는 했음
        # lte = lees than or equal
        queryset = self.get_queryset().filter(author=asd.id)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    # author가 id로 들어가야함 지금 post모델에서 author가 아래와 같이 있음
    # author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    # http POST http://127.0.0.1:8000/api/v1/post "Authorization: Token bf8bf34417deb3cbd2bfa502d37013243cd9f5eb" title="asddf" text="포스트내용2"

    def add_image(self, instance, request):
        try:
            #  fields = ['id', 'image', 'content_type', 'object_id']
            # import pdb; pdb.set_trace()
            # verbose_name 옵션을 지정하지 않으면 CamelCase 클래스 이름을 기준으로 camel case 이와 같이 모두 소문자로 변경한다.
            # https://wikidocs.net/6667#verbose_name
            # user_type = ContentType.objects.get(app_label='blog', model='post')
            image = request.data['image']
            data = {'image':request.data['image'],
                    'content_type':ContentType.objects.get_for_model(Post).id,
                    'object_id':instance.id}
            image_serializer = ImageSerializer(data=data)
            image_serializer.is_valid(raise_exception=True)
            image_serializer.save()
        # exception KeyError
        # Raised when a mapping (dictionary) key is not found in the set of existing keys.
        except KeyError:
            pass
        except serializers.ValidationError:
            return Response({"status": "failed", "errors": image_serializer.errors})

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
            post_instance = serializer.save()
            result = self.add_image(post_instance, request)
            if result:
                return result
            # 이거 pw는 write_only라서 안보임
            print(serializer.data)
        except serializers.ValidationError:
            return Response({"status": "failed", "errors": serializer.errors})

        return Response(serializer.data)


    # http DELETE http://127.0.0.1:8000/api/v1/post/12 "Authorization: Token bf8bf34417deb3cbd2bfa502d37013243cd9f5eb"
    #  get_object() looks for a pk_url_kwarg argument in the arguments to the view;
    #  if this argument is found, this method performs a primary-key based lookup using that value.
    # https://docs.djangoproject.com/en/3.2/ref/class-based-views/mixins-single-object/#django.views.generic.detail.SingleObjectMixin.get_object
    def delete(self, request, pk):
        print("in delete")
        instance = self.get_object()
        print(instance)
        instance.delete()
        # 이거 왜 resoponse가 안나오는거임?
        # https://developer.mozilla.org/ko/docs/Web/HTTP/Status/204
        return Response({'success': True}, status=status.HTTP_204_NO_CONTENT)

    # http POST http://127.0.0.1:8000/api/v1/post/20/publish "Authorization: Token bf8bf34417deb3cbd2bfa502d37013243cd9f5eb"
    @action(methods=['post'], detail=True)
    def publish(self, request, pk):
        post = self.get_object()
        print(post.text)
        post.publish()
        return Response({"status": "succsess"})

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

    # 코멘트 달기
    # http POST http://127.0.0.1:8000/api/v1/post/21/create_comment "Authorization: Token bf8bf34417deb3cbd2bfa502d37013243cd9f5eb" text="댓ㅁㄴㅇㅁㄴㅇd글내용1"
    # get_serializer_context(self) - Returns a dictionary containing any extra context that should be supplied to the serializer.
    # Defaults to including 'request', 'view' and 'format' keys.
    # 추가로 뭘 넘겨줄 수 있음
    @action(methods=['post'], detail=True)
    def create_comment(self, request, pk):
        context = self.get_serializer_context()
        context['post_id'] = pk
        serializer = CommentSerializer(data=request.data, context=context)
        try:
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        except serializers.ValidationError:
            return Response({"status": "failed", "errors": serializer.errors})


    # 질문할거
    # 이거 로갓 안하면 토큰 계속 남아있는데 이 토큰 계속 사용할 수 있는지 확인해보기
    # 저번에 질문한거랑은 약간 다른건데 그래도 확인해서 좀 더 괜찮은 질문으로 바꾸기
    # 이거 그리고 이전의 토큰이 남아있으면 그거를 그냥 써버리면 접근이 가능한데 이거 어케 수정함?

    # 코멘트 승인하기
    # http POST http://127.0.0.1:8000/api/v1/post/25/approve_comment "Authorization: Token 65b51c4fbf5914eda00efdeb7828842dd0d4dcc6"
    @action(methods=['post'], detail=True)
    def approve_comment(self, request, pk):
        comment = get_object_or_404(Comment, pk=pk)
        comment.approve()
        return Response({"status": "success"})

    # 포스트에 해당하는 전체 코멘트 가져오기
    # http POST http://127.0.0.1:8000/api/v1/post/25/comment "Authorization: Token 65b51c4fbf5914eda00efdeb7828842dd0d4dcc6"
    @action(methods=['post'], detail=True, serializer_class=CommentSerializer)
    def comment(self, request, pk):
        post = self.get_object()
        comments = post.all_comments
        serializer = self.get_serializer(comments, many=True)
        return Response(serializer.data)

    # 포스트에 해당하는 승인된 코멘트 가져오기
    # http POST http://127.0.0.1:8000/api/v1/post/25/approved_comment "Authorization: Token 65b51c4fbf5914eda00efdeb7828842dd0d4dcc6"
    # @action에다가
    @action(methods=['post'], detail=True, serializer_class=CommentSerializer)
    def approved_comment(self, request, pk):
        post = self.get_object()
        comments = post.approved_comments
        serializer = self.get_serializer(comments, many=True)
        return Response(serializer.data)

class CommentViewSet(viewsets.GenericViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    # 전체 코멘트
    # http GET http://127.0.0.1:8000/api/v1/comment "Authorization: Token 65b51c4fbf5914eda00efdeb7828842dd0d4dcc6"
    def list(self, request):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    # 코멘트 삭제
    # http DELETE http://127.0.0.1:8000/api/v1/comment/17 "Authorization: Token 65b51c4fbf5914eda00efdeb7828842dd0d4dcc6"
    def delete(self, request, pk):
        instance = self.get_object()
        instance.delete()
        return Response({'success': True}, status=status.HTTP_204_NO_CONTENT)

    # 특정 코멘트 가져오기
    # http GET http://127.0.0.1:8000/api/v1/comment/17 "Authorization: Token 65b51c4fbf5914eda00efdeb7828842dd0d4dcc6"
    def retrieve(self, request, pk):
        post = self.get_object()
        serializer = self.serializer_class(post)
        return Response(serializer.data)

    # comment 수정
    # http PUT http://127.0.0.1:8000/api/v1/comment/16 "Authorization: Token 65b51c4fbf5914eda00efdeb7828842dd0d4dcc6" text="올암"
    def update(self, request, pk):
        instance = self.get_object()
        # context로 comment가 들어간 post의 id를 넘겨줘야함
        context = self.get_serializer_context()
        context['post_id'] = instance.post_id
        serializer = self.get_serializer(instance, data=request.data, context=context, partial=True)
        try:
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        except serializers.ValidationError:
            return Response({"status": "failed", "errors": serializer.errors})

def post_list(request):
    # 쿼리를 만들어서 html로 보냄
    posts = Post.objects.filter(published_date__lte=timezone.now()).order_by('published_date')
    # {}이 보일 텐데, 이곳에 템플릿을 사용하기 위해 매개변수를 추가할 거에요. (이 매개변수를'posts'라고 할거에요)
    # {}으로 QuerySet을 템플릿 컨텍스트에 전달하는 것입니다. 걱정하지 마세요. 맨 마지막에 이 부분을 다룰 거에요.
    return render(request, 'blog/post_list.html', {'posts': posts})

def post_detail(request, pk):
    # 블로그 게시글 한 개만 보려면, 아래와 같이 쿼리셋(queryset)을 작성해야해요
    # 하지만 이 코드에는 문제가 있어요. 
    # 만약 해당 primary key(pk)의 Post를 찾지 못하면 오류가 나올 거에요!
    # Post.objects.get(pk=pk)
    post = get_object_or_404(Post, pk=pk)
    return render(request, 'blog/post_detail.html', {'post': post})

@login_required
def post_new(request):
    # 새 Post 폼을 추가하기 위해 PostForm() 함수를 호출하도록 하여 템플릿에 넘깁니다. 
    # 폼을 제출할 때, 같은 뷰를 불러옵니다. 
    # 이때 request에는 우리가 입력했던 데이터들을 가지고 있는데, request.POST가 이 데이터를 가지고 있습니다. 
    # (POST는 글 데이터를 "등록하는(posting)"하는 것을 의미합니다. 블로그 "글"을 의미하는 "post"와 관련이 없어요) 
    # HTML에서 <form>정의에 method="POST"라는 속성이 있던 것이 기억나나요? 
    # 이렇게 POST로 넘겨진 폼 필드의 값들은 이제 request.POST에 저장됩니다.
    # POST로 된 값을 다른 거로 바꾸면 안 돼요. method 속성의 값으로 넣을 수 있는 유효한 값 중에 GET같은 것도 있지만, 
    # post와 어떤 차이점이 있는지 등에 대해서 다루기에는 너무 길어질 것 같아 생략할게요)
    # form = PostForm()

    # 이제 view 에서 두 상황으로 나누어 처리해볼게요.
    # 첫 번째: 처음 페이지에 접속했을 때입니다. 당연히 우리가 새 글을 쓸 수 있게 폼이 비어있어야겠죠.
    # 두 번째: 폼에 입력된 데이터를 view 페이지로 가지고 올 때입니다. 여기서 조건문을 추가시켜야 해요. (if를 사용하세요)
    if request.method == "POST":
        # method가 POST라면, 폼에서 받은 데이터를 PostForm으로 넘겨줘야겠죠? 
        form = PostForm(request.POST)
        # (모든 필드에는 값이 있어야하고 잘못된 값이 있다면 저장하면 되지 않아야해요) 이를 위해 form.is_valid()을 사용할거에요.
        if form.is_valid():
            # commit=False란 넘겨진 데이터를 바로 Post 모델에 저장하지는 말라는 뜻입니다. 
            # 왜냐하면, 작성자를 추가한 다음 저장해야 하니까요. 
            # 대부분의 경우에는 commit=False를 쓰지 않고 바로 form.save()를 사용해서 저장해요. 
            # 다만 여기서는 작성자 정보를 추가하고 저장해야 하므로 commit=False를 사용하는 거예요
            post = form.save(commit=False)
            # 작성자를 추가하는 작업입니다. (PostForm에는 작성자(author) 필드가 없지만, 필드 값이 필요하죠!) 
            post.author = request.user
            # post.published_date = timezone.now() 미리 보기로 블로그 글 저장하기 위함
            # post.save()는 변경사항(작성자 정보를 포함)을 유지할 것이고 새 블로그 글이 만들어질 거에요!
            post.save()
            # 새 블로그 글을 작성한 다음에 post_detail페이지로 이동할 수 있으면 좋겠죠? 
            # post_detail은 우리가 이동해야 할 뷰의 이름이에요
            # post_detail 뷰 는 pk변수가 필요한 거 기억하고 있겠죠? pk=post.pk를 사용해서 뷰에게 값을 넘겨줄 거에요.
            # 여기서 post는 새로 생성한 블로그 글이에요.
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm()
    return render(request, 'blog/post_edit.html', {'form': form})

# 첫 번째: url로부터 추가로 pk 매개변수를 받아서 처리합니다.
@login_required
def post_edit(request, pk):
    # get_object_or_404(Post, pk=pk)를 호출하여 수정하고자 하는 글의 Post 모델 인스턴스(instance)로 가져옵니다. 
    # (pk로 원하는 글을 찾습니다) 이렇게 가져온 데이터를 폼을 만들 때와(글을 수정할 때 폼에 이전에 입력했던 데이터가 있어야 하겠죠?) 
    # 폼을 저장할 때 사용하게 됩니다.
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        form = PostForm(request.POST, instance=post)
        # print("asdddddddddddd", request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            # 이거 강의에서는 form = PostForm(instance=post) 이렇게 하라는데 이렇게 하면 작동을 안함 왜그런거임?
            post.author = request.user
            # 이거 있어서 글 수정하면 published_date 바뀜
            # 수정 날짜 보여주도록 model에 수정된 날짜도 넣어야할듯
            # post.published_date = timezone.now() 미리 보기로 블로그 글 저장하기 위함
            post.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm(instance=post)
    return render(request, 'blog/post_edit.html', {'form': form})

@login_required
def post_draft_list(request):
    posts = Post.objects.filter(published_date__isnull=True).order_by('created_date')
    return render(request, 'blog/post_draft_list.html', {'posts': posts})

@login_required
def post_publish(request, pk):
    post = get_object_or_404(Post, pk=pk)
    post.publish()
    return redirect('post_detail', pk=pk)

@login_required
def post_remove(request, pk):
    post = get_object_or_404(Post, pk=pk)
    # 장고 모델을 삭제할 때는 단순히.delete()를 호출하면 됩니다. 
    post.delete()
    return redirect('post_list')

def add_comment_to_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = CommentForm()
    return render(request, 'blog/add_comment_to_post.html', {'form': form})

@login_required
def comment_approve(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    comment.approve()
    return redirect('post_detail', pk=comment.post.pk)

@login_required
def comment_remove(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    comment.delete()
    return redirect('post_detail', pk=comment.post.pk)
