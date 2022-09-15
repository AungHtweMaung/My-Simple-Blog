import json
from django.shortcuts import render, redirect, get_object_or_404
from django.db import IntegrityError
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from .models import Author, Article, Profile
from .forms import ArticleForm, UpdateUserForm, UpdateProfileForm
from django.contrib import messages
from django.http import HttpResponse, JsonResponse

# Create your views here.

def index(request):
    # It will show only publish true.
    articles = Article.objects.filter(is_publish=True)
    
    return render(request, "home.html", {
        "articles": articles,  
    })

def search(request):
    search_title = request.GET["search_title"]
    
    if search_title == "":
        return render(request, "search.html", {
            "error_message": "You didn't type anything."
        })
    else:
        articles = Article.objects.filter(is_publish=True, title__icontains=search_title)
        
        return render(request, "search.html", {"articles": articles, "search_title": search_title})
    

@login_required
def profile(request):
    author = Author.objects.get(username=request.user.username)
    profile = Profile.objects.get(user=request.user)
    if request.method == "POST":
        u_form = UpdateUserForm(request.POST, instance=author)
        p_form = UpdateProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, f"You have been updated successfully.")
            return redirect("profile")
        else:
            messages.error(request, "Something Wrong")
    else:
        u_form = UpdateUserForm(instance=author)
        p_form = UpdateProfileForm(request.FILES, instance=request.user.profile)
    context = {
        "u_form": u_form,
        "p_form": p_form,
    }
    return render(request, "profile.html", context)


def article(request, id):
    article = get_object_or_404(Article, pk=id)
    is_owner = False
    # article ရဲ့ author id နဲ့ login ဝင်ထားတဲ့ user id တူမှ manage button ကိုပြမယ်။ 
    if article.author.id == request.user.id:
       is_owner = True  

    return render(request, "article.html", {
        "article": article,
        "is_owner": is_owner,
    }) 


def signup(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]
        
        # can't be blank
        if username == '' or email == '' or password == '':
            return render(request, "signup.html", {
                "message": "Username, email and password can't be blank!"
            })
        
        if " " in username:
            return render(request, "signup.html", {
                "message": "Username can't contain space!"
            })

        # email check using filter().all()
        # email_already_exist = Author.objects.filter(email=email).all()
        # if len(email_already_exist) > 0:
        #     return render(request, "signup.html", {
        #         "message": "Email already exists!"
        #     })


        # email check using filter().first()
        email_already_exist = Author.objects.filter(email=email).first()
        if email_already_exist != None:
            return render(request, "signup.html", {
                "message": "Email already exists!"
            })        

        # username check
        try:
            user = Author.objects.create_user(username, email, password)
            user.save()
            return redirect("login")

        except IntegrityError as e:
            return render(request, "signup.html", {
                "message": "Username already exists"
            })
        
        
        

    return render(request, "signup.html")


def logout(request):
    # authenticated ဖြစ်တဲ့ user တွေနဲ့ပဲ ဆက်သွယ်တယ်
    # print(request.user.is_authenticated)
    if request.user.is_authenticated:
        auth_logout(request)
    return redirect("home")

def login(request):
    if request.method == "POST":
        # attempt
        username = request.POST["username"]
        password = request.POST["password"]
        
        # username and password သည် db ထဲမှာ ရှိလားစစ်တာ။ 
        # if user exists, return this username. user represents as a current user.
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # log user in 
            auth_login(request, user) 
            return redirect("home")

        else:
            return render(request, "login.html", {
                "message": "Username or password is invalid!"
            })

    return render(request, "login.html")

@login_required
def dashboard(request):
    # author table သည် article table နဲ့ relationship ချိတ်ထားလို့ queryset
    # request.user.article.all() နဲံခေါ်သုံးလိုက်တဲ့အခါ article ထဲမှာ author objects အားလုံးကို ပြပေးတယ် 
    # အဲ့ဒီ author မှာ related_name (ကြိုက်တာပေး) ပေးထားလို့ ခေါ်သုံးလို့ရတာ 
    articles = request.user.article.all()
    total_article = len(articles)
    total_publish = request.user.article.filter(is_publish=True)
    # print(len(articles), total_publish)

    return render(request, "dashboard.html", {
        "articles": articles,
        "total_article": total_article,
        "total_publish": len(total_publish),
    })


@login_required
def handle_publishing(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST method only"}, status=400)

    # body ထဲမှာ ပါတဲ့ data ကို json နဲ့ပို့ပီး json နဲ့ပြန်ယူမယ်
    # data we requested will be seen in network > handle_publishing > payload (id တွေ့ရမယ်)
    req_data = json.loads(request.body)
    post_id = req_data.get('id', '')

    # post id and owner will be same as request id and request user
    # post owner မဟုတ်ဘဲ အခြား user တွေကနေ id လေးပြောင်းရုံနဲ့ ပြောင်းမရအောင်လို့
    article = Article.objects.filter(pk=post_id, author=request.user).first()
    if article == None:
        return JsonResponse({"error": "Post not found"}, status=404)  

    # button click ရင် publish ဆိုရင် unpublish ပြေင်းချင်တာ, True ဆိုရင် False လိုချင်တာ။ 
    article.is_publish = not article.is_publish
    article.save()
    
    action_msg = "Published" if article.is_publish else "Unpublished"
    msg = "Article was " + action_msg

    return JsonResponse({
        "error": "",
        "msg": msg,
        "operation": action_msg,

    }, status=200)
    
    
    return HttpResponse(request)

@login_required
def create_article(request):
    if request.method == "POST":
        # post method နဲ့ request လုပ််လိုက်မယ်ဆို data တွေကပါလာပီ။ ဘာလို့လည်းဆိုတော့ create ဆိုတဲ့ button ကို နှိပ်လ်ုက်လို့ 
        # မဟုတ်ရင် create article ဆိုတဲ့ page ကို ဒီတိုင်းပဲ ရောက်သွားတယ်ဆိုရင် get method နဲ့ဖြစ်မယ်။ 

        # parameter ထည့်ပေးထားတဲ့ request.POST သည် Author ထည့်လိုက်တဲ့ data တွေအားလုံးပါလာမယ်။
        # request.FILEs သည် ထည့်လိုက်တဲ့ image ရဲ့ file path ကို သိအောင်ထည့်ပေးလိုက်တာ 
        form = ArticleForm(request.POST, request.FILES) 
        if form.is_valid(): # It will return boolean
            # form ကို အရင် save လိုက်တာ၊ required field တွေကို နောက်မှထပ် save မှာမလို့ commit False ပေးထားတာ
            article = form.save(commit=False) 
            article.author_id = request.user.id
            article.save()
            messages.success(request, "Post created")
            return redirect("dashboard")

    else:
        form = ArticleForm()  # get နဲ့ဆို empty form ပြ 
    
    return render(request, "create_article.html", {
        "form": form,
    })

@login_required
def edit_article(request, id):   
    # article ရှိမရှိ စစ်တာ
    article = get_object_or_404(Article, pk=id)
    # owner ဟုတ် မဟုတ် စစ်တာ ၊ article table ထဲကို author နဲ့ foregin key နဲ့ချိတ်ထားလို့ article.author.id ဆိုပီး ခေါ်သုံးလို့ရတာ
    if article.author.id != request.user.id:
       return render(request, "error.html")
    
    else:
        if request.method == "POST":
            # instance can be used to include update data, not creating new article.
            form = ArticleForm(request.POST, request.FILES, instance=article) 

            if form.is_valid(): # It will return boolean
                article = form.save(commit=False) 
                article.author_id = request.user.id
                article.save()
                messages.success(request, "Post edited")
                return redirect("home")

        else:
            # Here, instance is to show the old data from database for editing post
            form = ArticleForm(instance=article)  
    
        context = {
            "form": form, 
            "post_id": article.id,
        }
        return render(request, "edit_article.html", context)

@login_required
def remove_article(request, id):

    article = get_object_or_404(Article, pk=id) 
    print(article.is_publish)
    
    if article.author_id != request.user.id:
        return JsonResponse({"error": "Post not found!"})
    else:
        if request.method == "POST":
            if article.is_publish != True:
                article.delete()
                messages.success(request, "Post deleted")
                return redirect("dashboard")
            else:
                messages.error(request, "Published post can't remove directly, Do unpublish firstly.")
                return redirect("dashboard")
        

    return redirect("dashboard")