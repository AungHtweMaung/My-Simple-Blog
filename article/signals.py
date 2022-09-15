# user created လုပ်လိုက်တာနဲ့ profile ဆိုတဲ့ဟာကို profile model ထဲမှာ သွားsave ချင်တာ  
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Profile, Author

# sender က ကိုယ်ဘယ် model ကနေ signal ပို့ချင်လည်းဆိုတာရေး
@receiver(post_save, sender=Author)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance) # instance က Author ကနေ register လုပ်လိုက်တဲ့ user ကို return ပြန်မယ်။ user row ကို ရတဲ့အတွက် (instance.id ဘာညာခေါ်သုံးလို့ရတယ်)

@receiver(post_save, sender=Author)
def save_profile(sender, instance, **kwargs):
    instance.profile.save()