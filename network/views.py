from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render,redirect,get_object_or_404
from django.urls import reverse
from .models import User, Follow,Post,UserProfile   
from django.core.paginator import Paginator
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import json
from .forms import ProfileImageForm

def index(request):
    if request.method == "POST":
        post_content = request.POST.get("post")
        if post_content:
            new_post = Post(user=request.user, content=post_content)
            new_post.save()
            return HttpResponseRedirect(reverse("index"))

    posts = Post.objects.all().order_by('-timestamp')
    profile_image = None
    if request.user.is_authenticated:
        try:
            user_profile = request.user.profile 
            profile_image = user_profile.image.url if user_profile.image else None
        except UserProfile.DoesNotExist:
            pass 

    serialized_posts = [post.serialize() for post in posts]

    paginator = Paginator(serialized_posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, "network/index.html", {
        "page_obj": page_obj
    })
    

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")
    
'''++++++++++++====+++++++++++++==============++++++==+++++===++++=+===+++ added code '''  
@login_required
def profile(request, username):
    profile_user = get_object_or_404(User, username=username)
    
    user_profile = profile_user.profile
    posts = Post.objects.filter(user=profile_user).order_by('-timestamp')
    followers_count = Follow.objects.filter(following=profile_user).count()
    following_count = Follow.objects.filter(follower=profile_user).count()

    # Check if the current user is following the profile user
    is_following = False
    if request.user.is_authenticated and request.user != profile_user:
        is_following = Follow.objects.filter(follower=request.user, following=profile_user).exists()
   
    # Render the profile page with all necessary context
    return render(request, 'network/profile.html', {
        'profile_user': profile_user,
        'user_profile': user_profile,
        'posts': posts,
        'followers_count': followers_count,
        'following_count': following_count,
        'is_following': is_following,

    })
@login_required
def toggle_follow(request, username):
    profile_user = get_object_or_404(User, username=username)
    
    if request.user != profile_user:
        # Check if the user is already following this profile
        follow_instance = Follow.objects.filter(follower=request.user, following=profile_user).first()
        
        if follow_instance:
            follow_instance.delete()
        else:

            Follow.objects.create(follower=request.user, following=profile_user)
    
  
    return redirect('profile', username=profile_user.username)

@csrf_exempt
@login_required
def edit(request, post_id):
    post = Post.objects.get(id=post_id)
    if request.method == "POST":
        data = json.loads(request.body)
        print(f'data is {data}')
        if data.get("post") is not None:
            post.post = data["post"]
        post.save()
        return HttpResponse(status=204)

@login_required
def following(request):
    # Get all users the current user is following
    followed_users = request.user.following.values_list('following', flat=True)
    posts = Post.objects.filter(user__in=followed_users).order_by('-timestamp')
    
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, "network/following.html", {
        "page_obj": page_obj
    })


@csrf_exempt
@login_required
def like(request, post_id):
    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return JsonResponse({"error": "Post not found."}, status=404)

    if request.method == "PUT":
        data = json.loads(request.body)
        if data.get("like"):
            post.like.add(request.user)
        else:  # unlike
            post.like.remove(request.user)
        return JsonResponse(post.serialize(), status=200)

    return JsonResponse({"error": "PUT request required."}, status=400)

#  form = ProfileImageForm(instance=user_profile)  
#     if request.method == "POST":
#         form = ProfileImageForm(request.POST, request.FILES, instance=user_profile)  # Update form with posted data
#         if form.is_valid():
#             form.save()
#             messages.success(request, "Profile image uploaded successfully!")
#             return redirect('profile', user_id=user_id)