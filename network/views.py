from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render,redirect
from django.urls import reverse
from .models import User, Follow, ProfileImage, Post
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import json
from .forms import ProfileImageForm

def index(request):
    if request.method == "POST":
        post_content = request.POST.get("post")
        if post_content:
            new_post = Post(user=request.user, post=post_content)
            new_post.save()
            return HttpResponseRedirect(reverse("index"))

    posts = Post.objects.all().order_by('-timestamp')

    serialized_posts = [post.serialize() for post in posts]

    paginator = Paginator(serialized_posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, "network/index.html", {"page_obj": page_obj})

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

@csrf_exempt
@login_required
def follow(request, user_id):
    current_user = request.user
    try:
        profile_user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return JsonResponse({"error": "User not found."}, status=404)

    if request.method == "GET":
        is_following = Follow.objects.filter(follower=current_user, following=profile_user).exists()
        followers_count = Follow.objects.filter(following=profile_user).count()
        return JsonResponse({
            "is_following": is_following,
            "followers_count": followers_count
        }, status=200)

    elif request.method == "POST":
        is_following = Follow.objects.filter(follower=current_user, following=profile_user).exists()
        if is_following:
            Follow.objects.filter(follower=current_user, following=profile_user).delete()
            action = "Follow"
        else:
            Follow.objects.create(follower=current_user, following=profile_user)
            action = "Unfollow"
        
        followers_count = Follow.objects.filter(following=profile_user).count()
        return JsonResponse({
            "action": action,
            "followers_count": followers_count
        }, status=200)

    return JsonResponse({"error": "GET or POST request required."}, status=400)

@login_required
def profile(request, user_id):
    current_user = request.user
    profile_user = User.objects.get(id=user_id)

    if request.method == "POST":
        form = ProfileImageForm(request.POST, request.FILES)
        if form.is_valid():
            profile_image, created = ProfileImage.objects.get_or_create(user=profile_user)
            profile_image.image = form.cleaned_data['image']
            profile_image.save()
            return redirect('profile', user_id=user_id)
        else:
            return JsonResponse({"error": "Invalid form submission."}, status=400)

    is_following = Follow.objects.filter(follower=current_user, following=profile_user).exists()
    posts = Post.objects.filter(user=profile_user).order_by('-timestamp')
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, "network/profile.html", {
        "current_user": current_user,
        "profile_user": profile_user,
        "is_following": is_following,
        # "followers": Follow.objects.filter(following=profile_user).count(),
        # "following": Follow.objects.filter(follower=profile_user).count(),
        "page_obj": page_obj,
        "form": ProfileImageForm()  # Pass the form to the template
    })