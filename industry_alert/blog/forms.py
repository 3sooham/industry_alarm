from django import forms

from .models import Post, Comment

# PostForm 은 이미 다들 예상 하셨듯이 우리가 만들 폼의 이름이에요.
# 리고 장고에 이 폼이 ModelForm이라는 것을 알려줘야해요. (그러면 장고가 뭔가 마술을 부릴 거에요) - forms.ModelForm은 ModelForm이라는 것을 알려주는 구문이에요.
class PostForm(forms.ModelForm):

    # 자, 이제 다음으로 class Meta가 나오는데요, 
    class Meta:
        # 이 구문은 이 폼을 만들기 위해서 어떤 model이 쓰여야 하는지 장고에 알려주는 구문입니다. (model = Post).
        model = Post
        # 이번 폼에서는 title과 text만 보여지게 해 봅시다
        fields = ('title', 'text',)

class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('author', 'text',)