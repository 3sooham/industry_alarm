from rest_framework import serializers
from .models import Eve

class EveSerializer(serializers.ModelSerializer):

    class Meta:
        model = Eve
        # fieds에 id나 pk로 지정된 필드 꼭 있어야함
        fields = ['typeId', 'typeName', 'iconId', 'marketGroupId']