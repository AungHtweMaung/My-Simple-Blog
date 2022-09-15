from django.contrib.auth.models import AbstractUser
from django.db import models
from ckeditor.fields import RichTextField
from django.forms import ModelForm

# Create your models here.

class Author(AbstractUser):
    def __str__(self):
        return self.username

class Category(models.Model):
    name = models.CharField(max_length=40)

    def __str__(self):
        return self.name
  
class Article(models.Model):
    id = models.BigAutoField(primary_key=True, editable=False)
    image = models.ImageField(upload_to="blog/")
    title = models.CharField(max_length=60)
    content = RichTextField()
    is_publish = models.BooleanField(default=False)
    # author တစ်ယောက်ထဲရေးထားတဲ့ article အားလုံးကို ကြည့်လို့ရအောင် related_name ကိုပေးထားတာ
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name="article")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="article")

    def __str__(self):
        return f"{self.title} (Author - {self.author})"

class Profile(models.Model): 
    user = models.OneToOneField(Author, on_delete=models.CASCADE)
    image = models.ImageField(default="default-profile.png", upload_to="profile_images")
    def __str__(self):
        return f"{self.user.username} Profile"
    
