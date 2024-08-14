from django.contrib import admin
from blogs.models import PostComment, PostLike, Post
# Register your models here.


admin.site.register(PostLike)
admin.site.register(PostComment)
admin.site.register(Post)