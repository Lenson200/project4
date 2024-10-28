from django import template
from network.models import Follow

register = template.Library()

@register.filter(name='user_is_following')
def user_is_following(current_user, profile_user):
    return Follow.objects.filter(follower=current_user, following=profile_user).exists()
