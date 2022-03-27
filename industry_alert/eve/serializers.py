from rest_framework import serializers
from .models import InvTypes, SolarSystem

class EveSerializer(serializers.ModelSerializer):

    class Meta:
        model = InvTypes
        # fieds에 id나 pk로 지정된 필드 꼭 있어야함
        fields = ['typeId', 'typeName', 'iconId', 'marketGroupId']

class SolarSystemSerializer(serializers.ModelSerializer):

    class Meta:
        model = SolarSystem
        fields = ['solarSystemID', 'solarSystemName', 'regionID', 'constellationID', 'securityClass']