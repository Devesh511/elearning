from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import AbstractUser
# from django_mysql.models import ListCharField
from pinax.referrals.models import Referral

class UserProfile(AbstractUser):
    is_professor = models.BooleanField(default=False)
    is_site_admin = models.BooleanField(default=False)
    affamount = models.IntegerField(default=0)
    # user = models.ForeignKey(UserProfile,on_delete=models.CASCADE, default=1)
    parent=models.ForeignKey( "self" ,on_delete=models.CASCADE, related_name='parent_affiliate' , blank=True,null = True)
    referral = models.OneToOneField(Referral,on_delete=models.CASCADE,blank=True,null=True)
    # List_courses = models.ListCharField(
    #     base_field=models.Charfield(maxlength=30),
    #     size=20,
    #     max_length=20*30)
    # is_affiliate = models.BooleanField(default=False)
    # parent=models.CharField(max_length=20)

class Mails(models.Model):
    document = models.FileField(upload_to='documents/')
    sender = models.CharField( max_length=30,default="xyz")
    sop = models.CharField(max_length=300,default="dummy")
    title = models.CharField( max_length=300,default="dummy")
    email = models.EmailField( max_length=30,default="xyz@gmail.com")
    