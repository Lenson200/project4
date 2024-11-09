from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import models


class User(AbstractUser):
    pass

def validate_image_size(value):
    filesize = value.size
    if filesize > 6 * 1024 * 1024:  
        raise ValidationError("The maximum file size that can be uploaded is 6MB")

class UserProfile(models.Model):
     user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
     image = models.ImageField(upload_to='profile_images/', validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png']), validate_image_size])
     about=models.TextField(blank=True, null=True)
     date_of_birth = models.DateField(blank=True, null=True)

class Post(models.Model):  
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.CharField(max_length=500, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    like = models.ManyToManyField(User, blank=True, related_name="liked_user")
    images=models.ImageField(upload_to='post_images/', validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png']), validate_image_size])
    
    def serialize(self,current_user=None):
        user_profile = self.user.profile
        profile_image_url = user_profile.image.url if user_profile.image else None
        is_liked = self.like.filter(id=current_user.id).exists() if current_user else False
        return {
            "id": self.id,
            "user_id": self.user.id,
            "user": self.user.username,
            "post": self.content,
            "timestamp": self.timestamp.strftime("%b %d %Y, %H:%M:%S"),
            "likes": self.like.count(),
           "post_image": self.images.url if self.images else None,
           "profile_image": profile_image_url,
            "is_liked": is_liked,
         
        }
    
class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="likeduser")
    post = models.ForeignKey(Post, on_delete=models.PROTECT, related_name="likedpost")

    def __str__(self):
        return f"{self.user.username} liked post {self.post.id}"

class Follow(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name="following")  
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name="follower")

    def __str__(self):
        return f"{self.follower.username} follows {self.following.username}" 