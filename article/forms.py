from django.forms import ModelForm
from .models import  Author, Article, Profile 

class ArticleForm(ModelForm):
    class Meta:
        model = Article
        fields = ['image', 'title', 'content', 'category']


class UpdateUserForm(ModelForm):
    class Meta:
        model = Author
        fields = ["username", "email"]


class UpdateProfileForm(ModelForm): 
    class Meta:
        model = Profile
        fields = ['image']

