from django.contrib.auth import get_user_model
from .models import Post, Comment, EntryImage
from account.models import User

# drf
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import ValidationError
# get_user_model() : 클래스이다.
# >>> get_user_model()
# <class 'accounts.models.User'>
# settings.AUTH_USER_MODEL : 문자열이다.
# >>> settings.AUTH_USER_MODEL
# >>> settings.AUTH_USER_MODEL
# 'accounts.User'

# 이미지 테스트
from .models import EntryImage

class ImageSerializer(serializers.ModelSerializer):
    image = serializers.ImageField()

    class Meta:
        model = EntryImage
        # 'content_object' 이거는 db에 실제로 써지는게 아니라서 없어도 됨
        fields = ['id', 'image', 'content_type', 'object_id']

class PostSerializer(serializers.ModelSerializer):
    # https://github.com/encode/django-rest-framework/blob/fdb49314754ff13d91c6eec7ccdb8ece52bea9eb/rest_framework/fields.py#L286
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())
    # post instance에서 이미지가 있는데 image는 image instance여서 seralize해줘야지 json으로 보여줄 수 있는거니까 image=ImageSerializer로 중첩해서 함
    # one to many realation 이어서 many=True 해줘야함
    image = ImageSerializer(read_only=True, allow_null=True, many=True)

    class Meta:
        model = Post
        # fieds에 id나 pk로 지정된 필드 꼭 있어야함
        fields = ['id', 'author', 'title', 'image', 'text', 'created_date', 'published_date']

# 이게 해야하는 일
# 1. post에 딸린 comment list가져오는거
# 2. comment 생성하는거
# 3. comment 업데이트하는거
class CommentSerializer(serializers.ModelSerializer):
    # 이거 read_only는 이걸 serialize 했을때 
    # [
    #   {
    #     "id": number,
    #     "post": number
    #   }
    # ]
    # 위와 같은 결과물을 만들고 싶다는 거임
    # post = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    # 이 두 필드를 requests로 받는게 아니라 강제로 지정할 거기 때문에 required=False로 함함
    author = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False)
    # 이거 post로 하면 Post 인스턴스라서 안돼고
    # 이렇게 _id 붙여서 id int로 바꿔야함
    # 이 related field들은 다 이럼
    # django 기본 queryset이 걍 이런거임
    # 이 related field들이 fk constraint말고도 실제로 칼럼이름이 post_id로 저장되어 있음
    # post_id같이 (related_field이름)_id 이런식으로 실제 db에 기록대고
    # 이게 본체인거고 저런 post 같은게 장고가 알아서 해주는 부분인데
    post_id = serializers.PrimaryKeyRelatedField(queryset=Post.objects.all(), required=False)

    class Meta:
        model = Comment
        fields = ['id', 'post_id', 'author', 'text', 'created_date', 'approved_comment']

    #  is_valid가 3가지 검사를 함
    # model에 정의된거랑 타입이 맞는지 필드별로 검사 한 번 다 하고
    # serializer에 validate_필드이름 이렇게 정의한 함스들 코드에서 파싱해서 저 함수들 한번씩 다 돌려주고
    # 각 필드에 대한 추가적인 validation임
    # 그 다음에 validate() 한번 실행하고 결과값을 validated_data로 
    # create나 update 메서드에 넘겨줌
    # def validate(self, attr):
    #        return attr
    # 이거는 원래 비어있음
    def validate(self, attr):
        # 이거는 request 전부가 serializer로 감
        # self.context['view'].action 이거로 더 자세한 정보 볼 수 있음
        # 어떤 함수 불러온지 알 수 있기 때문임
        author = self.context['request'].user
        if author.is_anonymous:
            raise ValidationError('anonymous user cannot create comment')
        attr['author'] = self.context['request'].user.id
        attr['post_id'] = self.context['post_id']
        return attr

    # Field-level validation
    # 이게 is_valid안에서 완벽히 일치하는거는 아닌데 대충 이런게 돌아감
    # def is_valid(self):
    #     ...
    #     for field in self.Meta.fields:
    #         validate_func = getattr(self, f'validate_{field}')
    #         validate_func(self.initial_data.get(field))
    # 여기서 value는 text임
    def validate_text(self, value):
        if '시벌' in value:
            raise ValidationError('욕하지마라')
        return value
