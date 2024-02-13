from django.shortcuts import render
from django.http import HttpResponse
from .models import Blog, Comment, UserProfile, Category, Tag, Contact, Reply
from .forms import BlogForm, CommentForm, UserProfileForm, CategoryForm, TagForm, UserForm, ContactForm, ReplyForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings


User = get_user_model()

# Create your views here.
def home(request):
    return render(request, 'index.html')

def blog_list(request):
    blogs = Blog.objects.all()
    query = request.GET.get('q')
    if query:
        blogs = blogs.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query)
        ).distinct()
    paginator = Paginator(blogs, 3)
    page = request.GET.get('page')
    blogs = paginator.get_page(page)
    return render(request, 'blog_list.html', {'blogs': blogs})

def blog_detail(request, blog_id):
    blog = Blog.objects.get(id=blog_id)
    comments = Comment.objects.filter(blog=blog)
    return render(request, 'blog_detail.html', {'blog': blog, 'comments': comments})

@login_required
def blog_create(request):
    if request.method == 'POST':
        form = BlogForm(request.POST)
        if form.is_valid():
            blog = form.save(commit=False)
            blog.author = request.user
            blog.save()
            form.save_m2m()
            return redirect('blog_list')
    else:
        form = BlogForm()
    return render(request, 'blog_form.html', {'form': form})

@login_required
def blog_update(request, blog_id):
    blog = Blog.objects.get(id=blog_id)
    if request.method == 'POST':
        form = BlogForm(request.POST, instance=blog)
        if form.is_valid():
            form.save()
            return redirect('blog_list')
    else:
        form = BlogForm(instance=blog)
    return render(request, 'blog_form.html', {'form': form})

@login_required
def blog_delete(request, blog_id):
    blog = Blog.objects.get(id=blog_id)
    blog.delete()
    return redirect('blog_list')

@login_required
def comment_create(request, blog_id):
    blog = Blog.objects.get(id=blog_id)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.blog = blog
            comment.save()
            return redirect('blog_detail', blog_id)
    else:
        form = CommentForm()
    return render(request, 'comment_form.html', {'form': form})

@login_required
def comment_update(request, comment_id):
    comment = Comment.objects.get(id=comment_id)
    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect('blog_detail', comment.blog.id)
    else:
        form = CommentForm(instance=comment)
    return render(request, 'comment_form.html', {'form': form})

@login_required
def comment_delete(request, comment_id):
    comment = Comment.objects.get(id=comment_id)
    blog_id = comment.blog.id
    comment.delete()
    return redirect('blog_detail', blog_id)

@login_required
def category_list(request):
    categories = Category.objects.all()
    return render(request, 'category_list.html', {'categories': categories})

@login_required
def category_detail(request, id):
    category = Category.objects.get(pk=id)
    blogs = Blog.objects.filter(category=category)
    return render(request, 'category_detail.html', {'category': category, 'blogs': blogs})

@login_required
def category_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('categories')
    else:
        form = CategoryForm()
    return render(request, 'category_form.html', {'form': form})

@login_required
def category_update(request, category_id):
    category = Category.objects.get(id=category_id)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            return redirect('category_list')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'category_form.html', {'form': form})

@login_required
def category_delete(request, category_id):
    category = Category.objects.get(id=category_id)
    category.delete()
    return redirect('category_list')

@login_required
def tag_list(request):
    tags = Tag.objects.all()
    return render(request, 'tag_list.html', {'tags': tags})

@login_required
def tag_detail(request, tag_id):
    tag = Tag.objects.get(id=tag_id)
    blogs = Blog.objects.filter(tags=tag)
    return render(request, 'tag_detail.html', {'tag': tag, 'blogs': blogs})

@login_required
def tag_create(request):
    if request.method == 'POST':
        form = TagForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('tag_list')
    else:
        form = TagForm()
    return render(request, 'tag_form.html', {'form': form})

@login_required
def tag_update(request, tag_id):
    tag = Tag.objects.get(id=tag_id)
    if request.method == 'POST':
        form = TagForm(request.POST, instance=tag)
        if form.is_valid():
            form.save()
            return redirect('tag_list')
    else:
        form = TagForm(instance=tag)
    return render(request, 'tag_form.html', {'form': form})

@login_required
def tag_delete(request, tag_id):
    tag = Tag.objects.get(id=tag_id)
    tag.delete()
    return redirect('tag_list')

def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('blog_list')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            return redirect('blog_list')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'registration/login.html')

def logout_view(request):
    logout(request)
    return redirect('blog_list')

@login_required
def profile(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=request.user.userprofile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect('blog_list')
    else:
        user_form = UserForm(instance=request.user)
        profile_form = UserProfileForm(instance=request.user.userprofile)
    return render(request, 'profile.html', {'user_form': user_form, 'profile_form': profile_form})

@login_required
def update_profile(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=request.user.userprofile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect('blog_list')
    else:
        user_form = UserForm(instance=request.user)
        profile_form = UserProfileForm(instance=request.user.userprofile)
    return render(request, 'profile_form.html', {'user_form': user_form, 'profile_form': profile_form})

@login_required
def delete_profile(request):
    UserProfile.objects.get(user=request.user).delete()
    return redirect('blog_list')

def about(request):
    return render(request, 'about.html')

def contact(request):
    return render(request, 'contact.html')

def search(request):
    query = request.GET.get('q')
    blogs = Blog.objects.filter(
        Q(title__icontains=query) |
        Q(content__icontains=query)
    ).distinct()
    return render(request, 'blog_list.html', {'blogs': blogs})

def send_contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')
        send_mail(
            'Contact Form',
            message+'\nFrom:\n'+name+'\n'+email,
            email,
            [settings.EMAIL_HOST_USER],
            fail_silently=False,
        )
        return redirect('contact')
    return redirect('contact')

@login_required
def delete_contact(request, contact_id):
    Contact.objects.get(id=contact_id).delete()
    return redirect('contact')

@login_required
def reply_contact(request, contact_id):
    contact = Contact.objects.get(id=contact_id)
    if request.method == 'POST':
        message = request.POST.get('message')
        send_mail(
            'Contact Form',
            message,
            settings.EMAIL_HOST_USER,
            [contact.email],
            fail_silently=False,
        )
        return redirect('contact')
    return render(request, 'reply_contact.html', {'contact': contact})

@login_required
def delete_reply(request, contact_id):
    Reply.objects.get(id=contact_id).delete()
    return redirect('contact')

@login_required
def update_reply(request, contact_id):
    reply = Reply.objects.get(id=contact_id)
    if request.method == 'POST':
        form = ReplyForm(request.POST, instance=reply)
        if form.is_valid():
            form.save()
            return redirect('contact')
    else:
        form = ReplyForm(instance=reply)
    return render(request, 'reply_form.html', {'form': form})

def user_list(request):
    users = User.objects.all()
    return render(request, 'user_list.html', {'users': users})

