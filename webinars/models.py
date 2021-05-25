from __future__ import unicode_literals
import os
from users.models import UserProfile 

from django.db import models
from users.models import UserProfile
from django.urls import reverse
from django.db.models.signals import pre_save
from django.utils.text import slugify
from django.dispatch import receiver
from six import python_2_unicode_compatible
from django.utils.translation import ugettext as _

# Create your models here.
class Webinar(models.Model):
    webinar_name = models.CharField(unique=True, max_length=20)
    webinar_author_name = models.CharField(max_length=20,default=" ")
    webinar_created_date = models.DateTimeField(auto_now_add=True)
    text_webinar = models.TextField(default=None,null=True)
    link_webinar = models.URLField(default=None,null=True,blank=True)
    user = models.ForeignKey(UserProfile,on_delete=models.CASCADE, default=1)
    # students = models.ManyToManyField(UserProfile, related_name='students_to_course')
    cost_webinar=models.IntegerField(null=True,default=0)
    image_webinar=models.IntegerField(null=True,default=0)
    students = models.ManyToManyField(UserProfile,through="join", related_name='students_to_webinars')

    for_everybody_webinar = models.BooleanField(default=True)
    def __unicode__(self):
        return self.course_name

class join(models.Model):
    user=models.ForeignKey(UserProfile ,on_delete=models.CASCADE)
    webinar=models.ForeignKey(Webinar , on_delete=models.CASCADE)
    

class Session(models.Model):
    session_name = models.CharField(max_length=20)
    session_created_date = models.DateTimeField(auto_now_add=True)
    webinar = models.ForeignKey(Webinar, on_delete=models.CASCADE, default=1)
    slug = models.SlugField(unique=True)

    def __unicode__(self):
        return self.chapter_name

    def get_absolute_url(self):
        return reverse("session", kwargs={"webinar_name": self.webinar.webinar_name,
                                          "slug": self.slug})

    def slug_default(self):
        slug = create_slug(new_slug=self.session_name)
        return slug


def create_slug(instance=None, new_slug=None):
    slug = slugify(instance.session_name)

    if new_slug is not None:
        slug = new_slug

    qs = Session.objects.filter(slug=slug).order_by("-id")
    exists = qs.exists()

    if exists:
        new_slug = "%s-%s" % (slug, qs.first().id)
        return create_slug(instance, new_slug=new_slug)

    return slug


def pre_save_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = create_slug(instance)

pre_save.connect(pre_save_receiver, sender=Session)


class TextBlockW(models.Model):
    lesson = models.TextField()
    text_block_fk = models.ForeignKey(Session,  on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True)


class YTLinkW(models.Model):
    link = models.URLField(max_length=200)
    yt_link_fk = models.ForeignKey(Session,  on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True)

class gdlinkW(models.Model):
    link = models.URLField(max_length=200)
    gd_link_fk = models.ForeignKey(Session,  on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True)


class FileUploadW(models.Model):
    file = models.FileField(null=False, blank=False, default='')
    date_created = models.DateTimeField(auto_now_add=True)
    file_fk = models.ForeignKey(Session,  on_delete=models.CASCADE)

class Comment(models.Model):
    post = models.ForeignKey(Session, on_delete = models.CASCADE)
    user = models.ForeignKey(UserProfile, on_delete = models.CASCADE)
    reply = models.ForeignKey('Comment', null=True, related_name="replies",on_delete = models.CASCADE)
    content = models.TextField(max_length=160)
    timestamp = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return '{}-{}'.format(self.post.session_name, str(self.user.username))

# class Quiz(models.Model):
#     quiz_name = models.CharField(max_length=20)
#     quiz_created_date = models.DateTimeField(auto_now_add=True)
#     session = models.ForeignKey(Session, on_delete=models.CASCADE, default=1)
#     marks = models.IntegerField(max_length=10)
#     marks_to_show = models.BooleanField(blank=False,default=False)
#     user=models.ForeignKey(UserProfile ,on_delete=models.CASCADE)


# @python_2_unicode_compatible
# class Question(models.Model):
#     content = models.CharField(max_length=1000,
#                                blank=False,
#                                help_text=_("Enter the question text that "
#                                            "you want displayed"),
#                                verbose_name=_('Question'))
#     quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, default=1)                           

#     attempted = models.BooleanField(blank=False,default=False)
#     def __str__(self):
#         return self.content



# @python_2_unicode_compatible
# class Answer(models.Model):
#     question = models.ForeignKey(Question)

#     content = models.CharField(max_length=1000,
#                                blank=False,
#                                help_text=_("Enter the answer text that "
#                                            "you want displayed"),
#                                verbose_name=_("Content"))

#     correct = models.BooleanField(blank=False,
#                                   default=False,
#                                   help_text=_("Is this a correct answer?"),
#                                   verbose_name=_("Correct"))

#     def __str__(self):
#         return self.content




@receiver(models.signals.post_delete, sender=FileUploadW)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    if instance.file:
        if os.path.isfile(instance.file.path):
            os.remove(instance.file.path)
