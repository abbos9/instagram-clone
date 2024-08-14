from django.db import models

from general_dj.models import BaseModel
from users.models import User

# Create your models here.



class Post(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.TextField()
    file = models.FileField(upload_to='media/post/video')

    class Meta:
        verbose_name = "Post"
        verbose_name_plural = "Posts"

    def __str__(self) -> str:
        return f"user:{self.user.username}, post:{self.description} "

class PostComment(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post,on_delete=models.CASCADE)
    comment = models.TextField()

    class Meta:
        verbose_name = "Comment"
        verbose_name_plural = "Comments"

    def __str__(self) -> str:
        return f"user:{self.user.username}, post:{self.post.description} "

class PostLike(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post,on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'post')
        verbose_name = "Like"
        verbose_name_plural =  "Likes"

    def __str__(self) -> str:
        return f"user:{self.user.username}, post:{self.post.description} "