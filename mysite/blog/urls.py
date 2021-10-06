from django.urls import path
from django.urls import include, re_path # re_path용
#  blog 애플리케이션에서 사용할 모든 views를 가져왔어요
from . import views

# drf
from rest_framework.routers import DefaultRouter

router = DefaultRouter(trailing_slash=False)
# 이 baseanem에 넣은거 기준으로
# basename='post'면
# list api는 post-list
# create api는 post-create
router.register(r'post', views.PostViewSet2, basename='posts')
router.register(r'comment', views.CommentViewSet, basename='comments')
router.register(r'user', views.AccountViewSet, basename='logins')

urlpatterns = [
    # drf
    path('api/v1/', include(router.urls)),

    # post_list라는 view가 루트 URL에 할당되었습니다.
    # 이 URL 패턴은 빈 문자열에 매칭이 되며, 
    # 장고 URL 확인자(resolver)는 전체 URL 경로에서 접두어(prefix)에 
    # 포함되는 도메인 이름(i.e. http://127.0.0.1:8000/)을 무시하고 받아들입니다.
    # 이 패턴은 장고에게 누군가 웹사이트에 'http://127.0.0.1:8000/' 주소로 들어왔을 때 views.post_list를 보여주라고 말해줍니다.
    # 마지막 부분인 name='post_list'는 URL에 이름을 붙인 것으로 뷰를 식별합니다.
    # 뷰의 이름과 같을 수도 완전히 다를 수도 있습니다. 이름을 붙인 URL은 프로젝트의 후반에 사용할 거예요. 
    # 그러니 앱의 각 URL마다 이름 짓는 것은 중요합니다. 
    # URL에 고유한 이름을 붙여, 외우고 부르기 쉽게 만들어야 해요.
    path('', views.post_list, name='post_list'),
    # 첫 게시물의 상세 페이지 URL이 http://127.0.0.1:8000/post/1/가 되게 만들 거에요.
    # post/<int:pk/>/는 URL 패턴을 나타내요
    # post/란 URL이 post 문자를 포함해야 한다는 것을 말합니다.
    # <int:pk>는 조금 까다롭습니다. 
    # 장고는 정수 값을 기대하고 이를 pk라는 변수로 뷰로 전송하는 것을 말합니다.
    # /은 다음에 / 가 한 번 더 와야 한다는 의미입니다.
    # 브라우저에 http://127.0.0.1:8000/post/5/라고 입력하면, 
    # 장고는 post_detail 뷰를 찾아 매개변수 pk가 5인 값을 찾아 뷰로 전달합니다.
    path('post/<int:pk>/', views.post_detail, name='post_detail'),
    path('post/new', views.post_new, name='post_new'),
    path('post/<int:pk>/edit/', views.post_edit, name='post_edit'),
    # ^ 메타 문자는 문자열의 맨 처음과 일치함을 의미한다. 
    # $는 문자열의 끝과 매치함을 의미한다.
    path('drafts/', views.post_draft_list, name='post_draft_list'),
    re_path(r'^post/(?P<pk>\d+)/publish/$', views.post_publish, name='post_publish'),
    path('post/<int:pk>)/remove', views.post_remove, name='post_remove'),
    re_path(r'^post/(?P<pk>\d+)/comment/$', views.add_comment_to_post, name='add_comment_to_post'),
    re_path(r'^comment/(?P<pk>\d+)/approve/$', views.comment_approve, name='comment_approve'),
    # Here r'' specifies that the string is a raw string. '^' signifies the start, and $ marks the end.
    # Now 'pk' (when inside <>) stands for a primary key. A primary key can be anything eg. it can be a string, number etc. 
    # A primary key is used to differentiate different columns of a table.
    # \d matches [0-9] and other digit characters.
    # +' signifies that there must be at least 1 or more digits in the number
    # re_path(r'^comment/(?P<pk>\d+)/remove/$', views.comment_remove, name='comment_remove'),
    # 'comment/<int:pk>/remove/'와 'comment/<int:pk>/remove'는 같지만
    # 이론적으로는 url뒤에 슬러쉬 붙이는게 정석입니다 - Rest Api에서는 /를 붙이지 않지만 질문해주신 분의 url에서는 remove라는게 붙어있다는 자체가 
    # restful한 API가 아니어서 저렇게 답변드렸는데 트레일링 슬래시에 대해 검색해보시면 뒤에 /를 왜 붙여야 하는지 언제 붙여야 하는지 감을 잡을 수 있을것 같습니다 
    # django url은 깔끔해야한다고 뒤에 /를 넣는 관습이 있는데, RestAPI에서는 뒤에 /를 빼는게 유명하죠.ㅎㅎ
    # RestApi 에서는 마지막에 /를 붙이지 않아용. 
    # RESTAPI 는 분명한 URI를 만들어 통신을 해야하기 때문에 혼동을 주지 않도록 URI 경로 마지막에는 / 사옹하지 않습니다.
    # 위에 말씀하시는 것처럼 굳이 지키지는 않아도 되지만 안지키면 눈살 살짝 찌그러지는 느낌?
    # https://www.google.com/example/ -> 디렉토리입니다.
    # https://www.google.com/example -> 파일입니다.
    path('comment/<int:pk>/remove/', views.comment_remove, name='comment_remove'),
]