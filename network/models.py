from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import models


class User(AbstractUser):
    pass

def validate_image_size(value):
    filesize = value.size
    if filesize > 6 * 1024 * 1024:  # 6 MB
        raise ValidationError("The maximum file size that can be uploaded is 6MB")

class ProfileImage(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='profile_images/', validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png']), validate_image_size])
class Post(models.Model):  
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.CharField(max_length=500, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    like = models.ManyToManyField(User, blank=True, related_name="liked_user")

    def serialize(self):
        profile_image_url = None
        if hasattr(self.user, 'profile_image'):
            profile_image_url = self.user.profile_image.image.url if self.user.profile_image.image else None

        return {
            "id": self.id,
            "user": self.user.username,
            "post": self.post,
            "timestamp": self.timestamp.strftime("%b %d %Y, %H:%M:%S"),
            "likes": self.like.count(),
            "profile_image": profile_image_url
        }
    
class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="likeduser")
    post = models.ForeignKey(Post, on_delete=models.PROTECT, related_name="likedpost")

class Follow(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name="following")  
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name="follower")  