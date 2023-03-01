from django.shortcuts import render, redirect

# Create your views here.
from django.http import HttpResponse
from .models import Room, Topic, Message, User
from .forms import RoomForm, UserForm, MyUserCreationForm
from django.db.models import Q
#from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login , logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
#rooms = [
#    {'id':1 , 'name':'lets learn python'},
#    {'id':2, 'name':'Design with me'},
#    {'id':3, 'name':'Code Challenge'}
#]

def loginPage(request):
    page= 'login'
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        email = request.POST['email'].lower()
        password = request.POST['password']

        try:
            user = User.objects.get(email = email)
        except:
            messages.error(request, 'User Does not exist!')

        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Bad Credentials!, try again.')
        
            
    context = {
        'page':page

    }
    return render (request, 'base/login_register.html' , context)

def registerPage(request):
    page = 'register'
    form = MyUserCreationForm()
    if request.method == 'POST':
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'error occurred during registration, check fields again.')

    return render(request, 'base/login_register.html' , {'page':page, 'form':form})


def logoutPage(request):
    logout(request)
    return redirect('home')

def home(request ):
    #return HttpResponse('this is the home page')
    q = request.GET.get('q') if request.GET.get('q')!= None else''
    rooms = Room.objects.filter(Q(topic__name__icontains=q) | 
                                Q(name__icontains=q) |
                                Q(description__icontains =q))[0:2]   #i is for making it case insensitive.
    topics = Topic.objects.all()[0:3]
    room_count = rooms.count()
    room_messages = Message.objects.filter(Q(room__topic__name__icontains = q)).order_by('-created')[0:2]
    context ={'rooms':rooms, 'topics':topics, 'room_count':room_count, 'room_messages':room_messages}
    return render(request, 'base/home_new.html' ,context)

def room(request, pk):
    #return HttpResponse('this is the rooms page')
    room = Room.objects.get(id=pk)
    topics = Topic.objects.all()
    room_messages = room.message_set.all().order_by ('-created')[0:2]
    participants = room.participants.all()
    if request.method == 'POST':
        message = Message.objects.create(
            user = request.user,
            room = room,
            body = request.POST.get('body')
        )
        room.participants.add(request.user)
        return redirect('room' , pk = room.id)
    #room = None
    #for i in rooms:
    #    if i['id'] == int(pk):
    #        room = i
    context = {
        'participants':participants,
        'room_messages':room_messages,
        'room': room,
        'topics':topics
    }
    return render(request, 'base/room.html' , context)

def userProfile(request ,pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()
    context = { 'user':user, 'rooms':rooms, 'room_messages':room_messages, 'topics':topics}
    return render(request, 'base/profile.html' ,context)
@login_required(login_url='loginpage')
def createRoom(request):
    topics = Topic.objects.all()
    
    form = RoomForm()
    if request.method == 'POST':
        topic_name = request.POST['topic']
        topic, created = Topic.objects.get_or_create(name=topic_name)
        Room.objects.create(
            host = request.user,
            topic = topic,
            name = request.POST['room_name'],
            description = request.POST['room_description']
        )
        #print(request.POST)
        #form = RoomForm(request.POST)
        #if form.is_valid():
        #    room= form.save(commit=False)
        #    room.host = request.user
        #    room.save()
        return redirect('home')

    context = { 'form':form , 'topics':topics}
    return render(request, 'base/room_form.html', context)
@login_required(login_url='loginpage')
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    topics = Topic.objects.all()
    form = RoomForm(instance=room)
    if request.user != room.host:
        return HttpResponse('You are not allowed here!')
    if request.method == 'POST':
            topic_name = request.POST['topic']
            topic, created = Topic.objects.get_or_create(name = topic_name)
            room.name = request.POST['room_name']
            room.topic = topic
            room.description = request.POST['room_description']
            room.save()
    #    form = RoomForm(request.POST, instance=room)
    #    if form.is_valid():
    #        form.save()
            return redirect('home')
    context= {
        'topics':topics,
        'form':form,
        'room':room
    }
    return render(request, 'base/room_form.html' , context)
@login_required(login_url='loginpage')
def deleteRoom(request, pk):
    room = Room.objects.get(id = pk)
    if request.user != room.host:
        return HttpResponse('You are not allowed here!')
    if request.method == 'POST':
        room.delete()
        return redirect('home')
    context = {
        'obj':room
    }
    return render(request, 'base/delete.html', context)

@login_required(login_url='loginpage')
def deleteMessage(request, pk):
    message = Message.objects.get(id = pk)
    if request.user != message.user:
        return HttpResponse('You are not allowed here!')
    if request.method == 'POST':
        message.delete()
        return redirect('home')
    context = {
        'obj':message
    }
    return render(request, 'base/delete.html', context)

@login_required(login_url='loginpage')
def updateUser(request):
    user = request.user
    form = UserForm(instance=user)
    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('userprofile' , pk=user.id)
    context = { 'form':form}
    return render (request, 'base/update-user.html' , context)


def mobile_topic(request):
    q = request.GET.get('q') if request.GET.get('q')!= None else''
    topics = Topic.objects.filter(name__icontains = q)
    rooms = Room.objects.all()
    room = Room.objects.all()

    rooms_count = rooms.count()

    context= {'topics':topics , 'rooms_count':rooms_count, 'room':room}
    return render (request, 'base/topics.html', context)


def mobile_activity(request):
    room = Room.objects.all().order_by('-created')
    all_messages = Message.objects.all()
    context = {'all_messages': all_messages}

    return render(request, 'base/activity.html' , context)
