from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render,redirect,get_object_or_404
from django.urls import reverse
from .models import User, Follow,Post,UserProfile,Like  
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
    liked_posts = []

    # Only fetch liked posts if the user is authenticated
    if request.user.is_authenticated:
        liked_posts = list(Like.objects.filter(user=request.user).values_list('post_id', flat=True))
        print("Liked Posts:", liked_posts)  # Debug print to check liked posts

    liked_posts_json = json.dumps(liked_posts)
    print("Liked Posts JSON:", liked_posts_json)  # Debug print for JSON data

    serialized_posts = [post.serialize(current_user=request.user) for post in posts]

    paginator = Paginator(serialized_posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, "network/index.html", {
        "page_obj": page_obj,
        "liked_posts_json": liked_posts_json,
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
    # Get the user whose profile is being viewed
    profile_user = get_object_or_404(User, username=username)
    user_profile = None
    try:
        user_profile = profile_user.profile
    except UserProfile.DoesNotExist:
        pass
    if request.user == profile_user:
        if user_profile is None:
            # If no profile exists, the user can create one
            if request.method == "POST":
                form = ProfileImageForm(request.POST, request.FILES)
                if form.is_valid():
                    # Create the user's profile and save the form data
                    new_profile = form.save(commit=False)
                    new_profile.user = profile_user
                    new_profile.save()
                    messages.success(request, "Your profile has been created!")
                    return redirect('profile', username=username)
            else:
                form = ProfileImageForm()
        else:
            # If the profile exists, allow the user to update it
            if request.method == "POST":
                form = ProfileImageForm(request.POST, request.FILES, instance=user_profile)
                if form.is_valid():
                    form.save()
                    messages.success(request, "Your profile has been updated!")
                    return redirect('profile', username=username)
            else:
                form = ProfileImageForm(instance=user_profile)
    else:
        form = None

    # Get posts of the profile user
    posts = Post.objects.filter(user=profile_user).order_by('-timestamp')

    # Get followers and following count
    followers_count = Follow.objects.filter(following=profile_user).count()
    following_count = Follow.objects.filter(follower=profile_user).count()

    # Check if the current user is following the profile user
    is_following = False
    if request.user.is_authenticated and request.user != profile_user:
        is_following = Follow.objects.filter(follower=request.user, following=profile_user).exists()

    # Render the profile page with all necessary stuff
    return render(request, 'network/profile.html', {
        'profile_user': profile_user,
        'user_profile': user_profile,  
        'posts': posts,
        'followers_count': followers_count,
        'following_count': following_count,
        'is_following': is_following,
        'form': form,
    })

@login_required
def toggle_follow(request, username):
    profile_user = get_object_or_404(User, username=username)

    if request.user != profile_user:
        
        follow_instance = Follow.objects.filter(follower=request.user, following=profile_user).first()

        if follow_instance:
            follow_instance.delete()
            is_following = False
        else:
            Follow.objects.create(follower=request.user, following=profile_user)
            is_following = True

        # Return a JSON response indicating success
        return JsonResponse({"success": True, "is_following": is_following})
    return redirect('profile', username=profile_user.username)   

@csrf_exempt
@login_required
def edit(request, post_id):
    try:
        post = Post.objects.get(id=post_id)

        # Check if the logged-in user is the owner of the post
        if post.user != request.user:
            return JsonResponse({"error": "You are not authorized to edit this post."}, status=403)

        # Handle the POST request for editing the post
        if request.method == "POST":
            data = json.loads(request.body)
            if "post" in data:
                post.content = data["post"]
                post.save()
                return JsonResponse({"message": "Post updated successfully!", "content": post.content}, status=200)

        return JsonResponse({"error": "Invalid request method."}, status=400)
    except Post.DoesNotExist:
        return JsonResponse({"error": "Post not found."}, status=404)

@login_required
def following(request):
    # Get all users the current user is following
    followed_users = request.user.following.values_list('following', flat=True)
    posts = Post.objects.filter(user__in=followed_users).order_by('-timestamp')
    profile_image = None
    serialized_posts = [post.serialize() for post in posts]
    paginator = Paginator(serialized_posts, 10)
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
        else: 
            post.like.remove(request.user)
        return JsonResponse(post.serialize(), status=200)

    return JsonResponse({"error": "PUT request required."}, status=400)