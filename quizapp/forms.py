from .models import Blog, Comment, UserProfile, Category, Tag, Contact, Reply
from django.contrib.auth.models import User
from django import forms
from django_ckeditor_5.widgets import CKEditor5Widget

# Create your forms here.
class BlogForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
          super().__init__(*args, **kwargs)
          self.fields["text"].required = False
    # content = forms.CharField(widget=CKEditor5Widget())
    class Meta:
        model = Blog
        fields = ['title', 'content', 'category', 'tags']
        widgets = {
            'content': CKEditor5Widget(
                attrs={"class": "django_ckeditor_5"}, config_name="blog"
            ),
        }

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password']

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['bio', 'profile_picture']

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']

class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = ['name']

class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['name', 'email', 'subject', 'message']
    
class ReplyForm(forms.ModelForm):
    class Meta:
        model = Reply
        fields = ['message']