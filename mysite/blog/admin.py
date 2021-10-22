
from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from .models import EntryImage, Post, Comment, User
from django.db.models.functions import Concat
from django.db.models import Value

# 관리자 페이지에서 만든 모델을 보려면 admin.site.register(Post)로 모델을 등록해야 해요.
class CommentAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {
            'fields': ('post', 'author', 'text')
        }),
        ('Date information', {
            # 이거 튜플 ,없으면 튜플로 인식못함 파이썬 버그임
            'fields': ('created_date',)
        }),
        (None, {
            'fields': ('approved_comment',),
            # A string of optional extra text to be displayed at the top of each fieldset,
            # under the heading of the fieldset.
            'description':("1asdasdsa1"),
        }),
    ]

    list_filter = (
        ('approved_comment', admin.BooleanFieldListFilter),
        # Assuming post is a ForeignKey to a Comment model,
        # 모든 post 말고 댓글달린거만 가져옴
        ('post', admin.RelatedOnlyFieldListFilter),
        'post',
    )

    date_hierarchy = 'created_date'

    # By default, the admin uses a select-box interface (<select>) for those fields.
    # Sometimes you don’t want to incur the overhead of selecting all the related instances to display in the dropdown.
    # You must define search_fields on the related object’s ModelAdmin because the autocomplete search uses it.
    autocomplete_fields = ['post']
    # search_fields = ['author__email', 'title']
    # 밑의 post admin에서 seracrh_fields = ['title']을 사용함


class EntryImageInline(GenericTabularInline):
    model = EntryImage

from datetime import date
from django.utils.translation import gettext_lazy as _
class PostListFilter(admin.SimpleListFilter):
    title = _('2021/09 및 2021/10')
    parameter_name = 'created_date'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return (
            ('month9', _('9월')),
            ('month10', _('10월')),
        )

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        # Compare the requested value (either '80s' or '90s')
        # to decide how to filter the queryset.
        if self.value() == 'month9':
            # gte -> greater than or equal
            # lte -> less than or equal
            return queryset.filter(created_date__gte=date(2021, 9, 1),
                                   created_date__lte=date(2021, 9, 30))
        if self.value() == 'month10':
            return queryset.filter(created_date__gte=date(2021, 10, 1),
                                   created_date__lte=date(2021, 10, 31))

# Also as a convenience, the ModelAdmin object is passed to the lookups method,
# for example if you want to base the lookups on the available data:
class AdvancedDecadeBornListFilter(PostListFilter):
    title = ('2021/1 ~ 2021/3 AND 2021/10')

    def lookups(self, request, model_admin):
        """
        Only show the lookups if there actually is
        anyone born in the corresponding decades.
        """
        qs = model_admin.get_queryset(request)
        if qs.filter(created_date__gte=date(2021, 1, 1),
                                   created_date__lte=date(2021, 3, 30)).exists():
            yield ('month9', _('in the eighties'))
        if qs.filter(created_date__gte=date(2021, 10, 1),
                                   created_date__lte=date(2021, 10, 31)).exists():
            yield ('month10', _('10월달'))

class PostAdmin(admin.ModelAdmin):
    inlines = [
        EntryImageInline,
    ]

    # If you don’t set list_display,
    # the admin site will display a single column that displays the __str__() representation of each object.
    # Set list_display to control which fields are displayed on the change list page of the admin.
    # list_display = ('title', 'author', 'published_date')

    # list_display = ('upper_case_name',)
    # @admin.display(description='Title')
    # def upper_case_name(self, obj):
    #     return ("%s %s" % (obj.title, obj.text)).upper()

    # If the value of a field is None, an empty string,
    # or an iterable without elements, Django will display - (a dash)
    # empty_value_display = 'unknown'

    # list_display = ('name', 'birth_date_view')
    #
    # @admin.display(empty_value='unknown')
    # def birth_date_view(self, obj):
    #     return obj.birth_date

    list_display = ('default_title_view',
                    'author_email',
                    'published_date_view',
                    'default_created_view',
                    'title_and_text',)

    # Field names in list_filter can also span relations using the __ lookup
    # list_filter = ['author', 'published_date', 'author__name']
    list_filter = (PostListFilter,
                   AdvancedDecadeBornListFilter,
                   'author', 'published_date', 'author__name',
                   ('text', admin.EmptyFieldListFilter),
                   ('author', admin.RelatedOnlyFieldListFilter),)

    # Set list_per_page to control how many items appear on each paginated admin change list page.
    # By default, this is set to 100.
    list_per_page = 5

    # Set ordering to specify how lists of objects should be ordered in the Django admin views.
    # This should be a list or tuple in the same format as a model’s ordering parameter.
    ordering = ('-published_date',)

    # By default, Django’s admin uses a select-box interface (<select>) for fields that are ForeignKey or have choices set.
    # If a field is present in radio_fields, Django will use a radio-button interface instead.
    # radio_fields = {"author": admin.VERTICAL}
    # By default, Django’s admin uses a select-box interface (<select>) for fields that are ForeignKey.
    # Sometimes you don’t want to incur the overhead of having to select all the related instances to display in the drop-down.
    raw_id_fields = ("author",)

    # Normally, objects have three save options: “Save”, “Save and continue editing”, and “Save and add another”.
    # If save_as is True, “Save and add another” will be replaced by a “Save as new” button that creates a new object (with a new ID) rather than updating the existing object.
    save_as = True

    # By default the admin shows all fields as editable.
    # Any fields in this option (which should be a list or tuple) will display its data as-is and non-editable
    readonly_fields = ('published_date',)
    # The same field can’t be listed in both list_editable and list_display_links
    # – a field can’t be both a form and a link.
    # list_display = ('text', )
    # 이거 하면 change 페이지에서 field 값 수정가능함
    # list_editable = ('text', )

    search_fields = ['author__email', 'title']

    # default로 chage list page에서 모델의 모든 field에 대해서 sorting 가능함
    # 이거로 sorting 하는거 필드 설정할 수 있음(list_display의 subset으로)
    sortable_by = ['author_email',
                    'published_date_view',
                    'default_created_view']

    # save_model method를 override 하면 doing pre- or post-save operations 할 수 있음
    # 아래 코드에서는 어드민페이지에서 수정하면서 저장하면 유저를 뭘 고르던간에
    # 포스트의 author를 현재 admin 페이지에 로그인한 유저로 바꿔줌
    # def save_model(self, request, obj, form, change):
    #     obj.author = request.user
    #     super().save_model(request, obj, form, change)

    # 이거도 마찬가지로 pre- or post delete operation 할 수 있음
    # 아래는 그냥 지우기전에 폴더하나 생성하는거임
    def delete_model(self, request, obj):
        import os
        os.mkdir("C:\\Users\\Home\\Desktop\\djangotestfolder")
        super().delete_model(request, obj)

    # 이거 링크는 링크 눌러서 들어가는거를 설정해주는거임
    # By default, the change list page will link the first column
    # list_display = ('text', )
    # list_display_links = ('text', )
    @admin.display(description='title')
    def default_title_view(self, obj):
        return obj.title
    # @admin.display(description='author')
    # def default_author_view(self, obj):
    #     return obj.author
    # description 안쓰면 method 이름이 들어감
    @admin.display(ordering='published_date', description='published date',empty_value='unknown')
    def published_date_view(self, obj):
        return obj.published_date

    # descending으로 정렬하려면 '-first_name'으로 하면됨
    @admin.display(description='created_date', ordering='created_date')
    def default_created_view(self, obj):
        return obj.created_date

    # The ordering argument supports query lookups to sort by values on related models.
    @admin.display(ordering='author__email')
    def author_email(self, obj):
        return obj.author.email

    # value()는 값을 넣어주는거임
    # concat()
    # Accepts a list of at least two text fields or expressions and returns the concatenated text.
    # Each argument must be of a text or char type.
    # 이거 뭐 기준으로 정렬이 되는거임? 알파벳 순인 아닌거같은데
    # Concat이거 뭐하는건지 알아내야함
    # https://docs.djangoproject.com/en/1.8/ref/models/database-functions/
    @admin.display(ordering=Concat('title', Value(' '), 'text'))
    def title_and_text(self, obj):
        return obj.title + ' / ' + obj.text


# ModelAdmin class를 define하지 않으면 default admin interface가 제공됨
admin.site.register(Post, PostAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(User)
admin.site.register(EntryImage)