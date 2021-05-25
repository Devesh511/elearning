from courses.forms import AddCourseForm
from webinars.forms import AddWebinarForm,CommentForm
from webinars.models import *
from courses.models import *
from .forms import *
from pinax.referrals.models import Referral
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import user_passes_test, login_required
from django.urls import reverse
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.shortcuts import render, redirect
from itertools import chain
from django.http import Http404,JsonResponse, HttpResponseRedirect
from django.template.loader import render_to_string
from .models import UserProfile
import razorpay
import json

import logging

import smtplib
from django.core.mail import EmailMessage
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase 
from email import encoders 

logger = logging.getLogger(__name__)


def home(request):
    context = {
        "title": "eLearning",
    }
    action = Referral.record_response(request, "login")
    
    respo=render(request, "home.html", context)
      
    if action is not None:
        referral = Referral.objects.get(id=action.referral.id)
        respo.set_cookie('parent',referral.user.username)
      

    return respo


def about(request):
    context = {
        "title": "About",
    }
    # tutorial  = request.COOKIES['parent']
    # print(tutorial) 
    return render(request, "users/about.html", context)

def faq(request):
    context = {
        "title": "faq",
    }
    # tutorial  = request.COOKIES['parent']
    # print(tutorial) 
    return render(request, "users/faq.html", context)   

def contact_as_instructor(request):
    contact_form = Contact_as_Instructor(request.POST or None)

    context = {
        "title": "Contact",
        "contact_form": contact_form,
    }

    if contact_form.is_valid():

        sender = contact_form.cleaned_data.get("sender")
        sop = contact_form.cleaned_data.get("sop")
        from_email = contact_form.cleaned_data.get("email")
        title = contact_form.cleaned_data.get("title")
        
        
        message = contact_form.cleaned_data.get("message")

        message = 'Sender:  ' + sender + '\nFrom:  ' + from_email + '\n\nSOP'+ sop + '\n\ntitle' + title
        # send_mail("apply as instructor", message, settings.EMAIL_HOST_USER, [settings.EMAIL_HOST_USER], fail_silently=False)
        
        
        
        
        
        
        success_message = "We appreciate you contacting us, one of our Customer Service colleagues will get back" \
                          " to you within a 24 hours."
        messages.success(request, success_message)

        


        msg = MIMEMultipart() 
        msg['Subject'] = "Apply as an Instructor"
        msg['From'] = settings.EMAIL_HOST_USER
        msg['To'] = settings.EMAIL_HOST_USER

        msg.attach(MIMEText(message, 'plain')) 

        
        # Create server object with SSL option
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        # Perform operations via server
        server.login('contact.getskills@gmail.com', 'getskills1.0')

        server.sendmail(settings.EMAIL_HOST_USER, [settings.EMAIL_HOST_USER], msg.as_string())
        server.quit()

        return redirect(reverse('contact_as_instructor'))

    return render(request, "users/contact_as_instructor.html", context)


def contact(request):
    contact_form = Contact(request.POST or None)

    context = {
        "title": "Contact",
        "contact_form": contact_form,
    }

    if contact_form.is_valid():

        sender = contact_form.cleaned_data.get("sender")
        subject = contact_form.cleaned_data.get("subject")
        from_email = contact_form.cleaned_data.get("email")
        message = contact_form.cleaned_data.get("message")
        message = 'Sender:  ' + sender + '\nFrom:  ' + from_email + '\n\n' + message
        # send_mail(subject, message, settings.EMAIL_HOST_USER, [settings.EMAIL_HOST_USER], fail_silently=False)
        success_message = "We appreciate you contacting us, one of our Customer Service colleagues will get back" \
                          " to you within a 24 hours."
        messages.success(request, success_message)

        


        msg = MIMEText(message)
        msg['Subject'] = subject
        msg['From'] = settings.EMAIL_HOST_USER
        msg['To'] = settings.EMAIL_HOST_USER

        # Create server object with SSL option
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        # Perform operations via server
        server.login('contact.getskills@gmail.com', 'getskills1.0')

        server.sendmail(settings.EMAIL_HOST_USER, [settings.EMAIL_HOST_USER], msg.as_string())
        server.quit()

        return redirect(reverse('contact'))

    return render(request, "users/contact.html", context)


@login_required
def profile(request):
    

    if request.user.is_site_admin:
        
        return redirect(reverse('admin'))

    elif request.user.is_professor:
        return redirect(reverse('professor'))
  

    return redirect(reverse('student'))
        

@login_required
def charged_course(request,course_name):
    razorpay_client = razorpay.Client(auth=("rzp_test_6ChBFF3DEQamI8", "RIn69McAqs35zFjHZOB0jqjM"))
    amount = 50000
    payment_id = request.POST['razorpay_payment_id']
    razorpay_client.payment.capture(payment_id, amount)
    c=Course.objects.get(course_name=course_name)
    c.students.set([request.user])
    c.save()
    user=request.user
    if user.parent:
        user.parent.affamount=user.parent.affamount+1
        print(user.parent)
        print(user.parent.affamount)
        user.parent.save()

    return redirect('profile')

@login_required
def charged_webinar(request,webinar_name):
    razorpay_client = razorpay.Client(auth=("rzp_test_6ChBFF3DEQamI8", "RIn69McAqs35zFjHZOB0jqjM"))
    payment_id = request.POST['razorpay_payment_id']
    # razorpay_client.payment.capture(payment_id, amount)
    c=Webinar.objects.get(webinar_name=webinar_name)
    c.students.set([request.user])
    c.save()
    user=request.user
    if user.parent:
        user.parent.affamount=user.parent.affamount+1
        user.parent.save()

    return redirect('profile')


@login_required
def affiliate(request):
    
    profile = UserProfile.objects.get(username=request.user.username)
    # profile.parent = Profile.objects.get(user=referral.user)
    
          
    referral = Referral.create(
    user=profile,
    redirect_to=reverse("home")
    )
        
    profile.referral=referral
    profile.save()
    context={
        "profile":profile,
        "title":"Affiliate"

    }
    
    return render(request, "users/affiliate.html",context)
    

@login_required
def charge_course(request,course_name):
    c=Course.objects.filter(course_name=course_name)
    q=c[0]
    user=request.user
    context = {
           "title": course_name,
            "user":user,
            "course":course_name,
            "intro":q,
            "text": q.text,
            "queryset":c
            }
    
    return render(request, "courses/charge.html",context)



@login_required
def charge_webinar(request,webinar_name):
    c=Webinar.objects.filter(webinar_name=webinar_name)
    q=c[0]
    user=request.user
    context = {
           "title": webinar_name,
            "user":user,
            "webinar":webinar_name,
            "intro":q,
            "text": q.text_webinar,
            "queryset":q
            }
    
    return render(request, "webinars/charge.html",context)


@user_passes_test(lambda user: user.is_site_admin)
def admin(request):
    add_user_form = AddUser(request.POST or None)
    queryset = UserProfile.objects.all()

    search = request.GET.get("search")
    if search:
        queryset = queryset.filter(username__icontains=search)

    context = {
        "title": "Admin",
        "add_user_form": add_user_form,
        "queryset": queryset,

    }

    if add_user_form.is_valid():
        instance = add_user_form.save(commit=False)
        passwd = add_user_form.cleaned_data.get("password")
        instance.password = make_password(password=passwd,
                                          salt='salt', )
        instance.save()
        reverse('profile')

    return render(request, "users/sysadmin_dashboard.html", context)


@user_passes_test(lambda user: user.is_professor)
def professor(request):
    add_course_form = AddCourseForm(request.POST or None)
    queryset_course = Course.objects.filter(user__username=request.user)
    queryset_webinar = Webinar.objects.filter(user__username=request.user)
    add_webinar_form = AddWebinarForm(request.POST or None)
    context = {
        "title": "Professor",
        "add_course_form": add_course_form,
        "add_webinar_form":add_webinar_form,
        "queryset_course": queryset_course,
        "queryset_webinar": queryset_webinar,
    }

    if add_course_form.is_valid():
        course_name = add_course_form.cleaned_data.get("course_name")
        instance = add_course_form.save(commit=False)
        instance.user = request.user
        instance.text = add_course_form.cleaned_data.get("text")
        key = add_course_form.cleaned_data.get("link")

        if 'embed' not in key and 'youtube' in key:
            key = key.split('=')[1]
            instance.link = 'https://www.youtube.com/embed/' + key

        
        instance.save()
        return redirect(reverse('professor_course', kwargs={'course_name': course_name}))

    if add_webinar_form.is_valid():
        webinar_name = add_webinar_form.cleaned_data.get("webinar_name")
        inst = add_webinar_form.save(commit=False)
        inst.user = request.user
        inst.text_webinar = add_webinar_form.cleaned_data.get("text_webinar")
        key = add_webinar_form.cleaned_data.get("link_webinar")

        if 'embed' not in key and 'youtube' in key:
            key = key.split('=')[1]
            inst.link = 'https://www.youtube.com/embed/' + key

        
        inst.save()
        return redirect(reverse('professor_webinar', kwargs={'webinar_name': webinar_name}))


    return render(request, "users/professor_dashboard.html", context)


@login_required
def student(request):
    queryset1 = Course.objects.filter(students=request.user)
    queryset2 = Webinar.objects.filter(students=request.user)
    context = {
        "queryset1": queryset1,
        "queryset2": queryset2,
        "title": request.user,
    }

    return render(request, "users/student_dashboard.html", context)


@user_passes_test(lambda user: user.is_site_admin)
def update_user(request, username):
    user = UserProfile.objects.get(username=username)
    data_dict = {'username': user.username, 'email': user.email}
    update_user_form = EditUser(initial=data_dict, instance=user)

    path = request.path.split('/')[1]
    redirect_path = path
    path = path.title()

    context = {
        "title": "Edit",
        "update_user_form": update_user_form,
        "path": path,
        "redirect_path": redirect_path,
    }

    if request.POST:
        user_form = EditUser(request.POST, instance=user)

        if user_form.is_valid():
            instance = user_form.save(commit=False)
            passwd = user_form.cleaned_data.get("password")

            if passwd:
                instance.password = make_password(password=passwd,
                                                  salt='salt', )
            instance.save()

            return redirect(reverse('profile'))

    return render(request, "users/edit_user.html", context)


@user_passes_test(lambda user: user.is_site_admin)
def delete_user(request, username):
    user = UserProfile.objects.get(username=username)
    user.delete()
    return redirect(reverse('profile'))


@login_required
def course_homepage(request, course_name):
    chapter_list = Chapter.objects.filter(course__course_name=course_name)
    for i in Course.objects.filter(students=request.user):
        if i.course_name == course_name:
            return redirect(reverse(student_course, kwargs={'course_name': course_name, "slug": chapter_list[0].slug}))
    if chapter_list:
        return redirect( reverse(charge_course,kwargs={'course_name': course_name} ))
        # reverse(student_course, kwargs={'course_name': course_name, "slug": chapter_list[0].slug})
    else:
        warning_message = "Currently there are no videos for this course "
        messages.warning(request, warning_message)
        return redirect(reverse('courses'))

@login_required
def webinar_homepage(request, webinar_name):
    session_list = Session.objects.filter(webinar__webinar_name=webinar_name)
    for i in Webinar.objects.filter(students=request.user):
        if i.webinar_name == webinar_name:
            return redirect(reverse(student_webinar, kwargs={'webinar_name': webinar_name, "slug": session_list[0].slug}))
    if session_list:
        return redirect( reverse(charge_webinar, kwargs={'webinar_name': webinar_name}) )
        # reverse(student_course, kwargs={'course_name': course_name, "slug": chapter_list[0].slug})
    else:
        warning_message = "Currently there are no videos for this webinar "
        messages.warning(request, warning_message)
        return redirect(reverse('webinars'))


@login_required
def student_course(request, course_name, slug=None):
    course = Course.objects.get(course_name=course_name)
    chapter_list = Chapter.objects.filter(course=course)
    chapter = Chapter.objects.get(course__course_name=course_name, slug=slug)
    text = TextBlock.objects.filter(text_block_fk=chapter)
    videos = YTLink.objects.filter(yt_link_fk=chapter)
    files = FileUpload.objects.filter(file_fk=chapter)
    gdlinks = gdlink.objects.filter(gd_link_fk=chapter)
    user = request.user
    
    if user in course.students.all() or user.is_professor or user.is_site_admin or course.for_everybody:
        result_list = sorted(
            chain(text, videos, files, gdlinks),
            key=lambda instance: instance.date_created)

        context = {
            "course_name": course_name,
            "chapter_list": chapter_list,
            "chapter_name": chapter.chapter_name,
            "slug": chapter.slug,
            "result_list": result_list,
            "title": course_name + ' : ' + chapter.chapter_name,
        }
        # print(result_list)
        return render(request, "users/student_courses.html", context)

    else:
        raise Http404




@login_required
def student_webinar(request, webinar_name, slug=None):
    webinar = Webinar.objects.get(webinar_name=webinar_name)
    session_list = Session.objects.filter(webinar=webinar)
    session = Session.objects.get(webinar__webinar_name=webinar_name, slug=slug)
    text = TextBlockW.objects.filter(text_block_fk=session)
    videos = YTLinkW.objects.filter(yt_link_fk=session)
    files = FileUploadW.objects.filter(file_fk=session)
    gdlinks = gdlinkW.objects.filter(gd_link_fk=session)
    user = request.user

    comments = Comment.objects.filter(post=session, reply=None).order_by('-id')
    
    if user in webinar.students.all() or user.is_professor or user.is_site_admin or webinar.for_everybody:
        result_list = sorted(
            chain(text, videos, files, gdlinks),
            key=lambda instance: instance.date_created)
        
        if request.method == 'POST':
            comment_form = CommentForm(request.POST or None)
            if comment_form.is_valid():
                content = request.POST.get('content')
                reply_id = request.POST.get('comment_id')
                comment_qs = None
                if reply_id:
                    comment_qs = Comment.objects.get(id=reply_id)
                comment = Comment.objects.create(post=session, user=request.user, content=content, reply=comment_qs)
                comment.save()

                # return HttpResponseRedirect(session.get_absolute_url())
        else:
            comment_form= CommentForm()    


        context = {
            "webinar_name": webinar_name,
            "session_list": session_list,
            "session_name": session.session_name,
            "slug": session.slug,
            "result_list": result_list,
            "title": webinar_name + ' : ' + session.session_name,
            'comments': comments,
            'comment_form': comment_form,
        }

        if request.is_ajax():
            html = render_to_string('comment.html', context, request=request)
            return JsonResponse({'form': html})

        return render(request, "users/student_webinars.html", context)

    else:
        raise Http404