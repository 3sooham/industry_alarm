from django.conf import settings
from django.db import models
from django.utils import timezone

# image
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericRelation

class EntryImage(models.Model):
    def productFile(instance, filename):
        return f'EntryImage/{filename}'

    image = models.ImageField(
        upload_to=productFile,
        max_length=254, blank=True, null=True
    )
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

class Post(models.Model):
    # models.ForeignKey - 다른 모델에 대한 링크를 의미합니다.
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    # models.CharField - 글자 수가 제한된 텍스트를 정의할 때 사용합니다. 글 제목같이 짧은 문자열 정보를 저장할 때 사용합니다.
    title = models.CharField(max_length=200)
    # models.TextField - 글자 수에 제한이 없는 긴 텍스트를 위한 속성입니다. 블로그 콘텐츠를 담기 좋겠죠?
    text = models.TextField()
    # models.DateTimeField - 날짜와 시간을 의미합니다.
    created_date = models.DateTimeField(
            default=timezone.now)
    published_date = models.DateTimeField(
            blank=True, null=True)
    image = GenericRelation(EntryImage, related_query_name='post', null=True)

    def publish(self):
        self.published_date = timezone.now()
        self.save()

    # 메서드는 자주 무언가를 되돌려주죠. (return) 그 예로 __str__ 메서드를 봅시다. 
    # 이 시나리오대로라면, __str__를 호출하면 Post 모델의 제목 텍스트(string)를 얻게 될 거에요.
    def __str__(self):
        return self.title

    # <a href="{% url 'post_detail' pk=post.pk %}">Comments: {{ post.approved_comments.count }}</a>
    # 에서 post.approved_comments 함수를 사용해
    @property
    def approved_comments(self):
        return self.comments.filter(approved_comment=True)

    # 원래 functinoo은 동사인데 @property로 명사로 바꿔줌
    # @proporty 안쓰면 get_all_comments ㅇ렇게 이름함
    # 메서드 이름은 동사처럼
    # 프로퍼티 이름은 명사처럼
    # 프로터피는 ()가 안붙으니까 명사로 하는거임 ()는 뭔가 실행한다는 의미여서
    @property
    def all_comments(self):
        return self.comments.all()


# 댓글
class Comment(models.Model):
    # dels.ForeignKey의 related_name 옵션은 Post 모델에서 댓글에 액서스할 수 있게 합니다.
    # 역참조 대상인 Post에서 comment를 접근할 수 있음
    post = models.ForeignKey('blog.Post', on_delete=models.CASCADE, related_name='comments')
    # 이거 help text form에서 쓰나봄 자세히는 모르겠음 일단 admin change page에서는 이거 문구 나옴
    author = models.CharField(max_length=200, help_text="This is the grey text")
    text = models.TextField()
    created_date = models.DateTimeField(default=timezone.now)
    # 이거 나중에 modified_date 추가하기
    # models.BooleanField - 참/거짓(true/false) 필드랍니다.
    # 이거 is_approved로 이름 바꾸기
    approved_comment = models.BooleanField(default=False)

    def approve(self):
        self.approved_comment = True
        self.save()

    def __str__(self):
        return self.text