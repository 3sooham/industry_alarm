from django.db import models

class Eve(models.Model):
    typeId = models.IntegerField(primary_key=True )
    groupId = models.IntegerField()
    typeName = models.CharField(max_length=255)
    description = models.TextField()
    mass = models.FloatField()
    volume = models.FloatField()
    capacity = models.FloatField()
    portionsize = models.IntegerField()
    raceId = models.IntegerField()
    basePrice = models.DecimalField(max_digits=19, decimal_places=4)
    published = models.IntegerField()
    marketGroupId = models.IntegerField()
    iconId = models.IntegerField()
    soundId = models.IntegerField()
    graphicId = models.IntegerField()

    class Meta:
        # managed
        # - https://docs.djangoproject.com/en/4.0/ref/models/options/#managed
        # - 장고가 db를 관리하는게 아니라 외부에서 만든 db 테이블에 장고를 연결한거라서 
        # false로 해야함. default는 true임. 
        # false면 이 모델에서는 장고가 db 테이블 생성, 수정, 삭제를 안함.
        managed = False
        # 이 모델이 있는 db 테이블 이름임
        # 원래는 자동으로 생성해주는데 지금은 있는 테이블에 있는 데이터를 사용하니 이렇게 명시해줘야함
        db_table = 'invTypes'