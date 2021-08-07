from django.shortcuts import render, get_object_or_404
from django.utils import timezone # timezone.now() 사용하기 위함임
from .models import Post, Comment # Post모델, Comment모델을 불러오기 위함임
from .forms import PostForm, CommentForm
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

# 여기부터 drf viewset 적용위한거임
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from blog.models import Post, Comment
from blog.serializers import PostSerializer, CommentSerializer, RegistrationSerializer, LoginSerializer

# curl 확인용
#from django.views.decorators.csrf import csrf_exempt, csrf_protect
#@csrf_exempt

# 뷰(view) 는 애플리케이션의 "로직"을 넣는 곳이에요. 
# 뷰는 이전 장에서 만들었던 모델에서 필요한 정보를 받아와서 템플릿에 전달하는 역할을 합니다.

# 방금 post_list라는 함수(def)를 만들었습니다. 
# 이 함수는 요청(request)을 넘겨받아 render메서드를 호출합니다. 
# 이 함수는 render 메서드를 호출하여 받은(return) blog/post_list.html템플릿을 보여줍니다.

# drf viewset
class PostViewSet(viewsets.ViewSet):
    def list(self, request):
        queryset = Post.objects.filter(published_date__lte=timezone.now()).order_by('published_date')
        serializer = PostSerializer(queryset, many=True)
        return Response(serializer.data)
    
    def retrieve(self, request, pk):
        queryset = Post.objects.all()
        post = get_object_or_404(queryset, pk=pk)
        serializer = PostSerializer(post)
        return Response(serializer.data)

# drf login
class AccountViewSet(viewsets.GenericViewSet):
    @action(detail=True, methods=['post']) 
    def registration(self, request):
        serializer = RegistrationSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()

        return Response('Registered')
    
    @action(detail=True, methods=['post'])
    def login(self, request, pk):
        serializer = LoginSerializer(data=request.data)

        if serializer.is_valid():
            result = serializer.authenticate()
            # 이메일에 대해서 비밀번호가 일치하면
            if result == True:
                return Response('Login Success')
            return Response('Login Failure')

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