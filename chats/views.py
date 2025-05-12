from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Q
from django.contrib.contenttypes.models import ContentType
from .models import Thread, DirectMessage
from .forms import MessageForm
from notifications.models import Notification

@login_required
def inbox(request):
    threads = Thread.objects.filter(participants=request.user)
    return render(request, 'messages/inbox.html', {'threads': threads})

@login_required
def thread_detail(request, thread_id):
    thread = get_object_or_404(Thread, id=thread_id, participants=request.user)
  
    messages_list = thread.messages.all()
   
    unread_messages = messages_list.exclude(sender=request.user).exclude(read_by=request.user)
    for message in unread_messages:
        message.read_by.add(request.user)
        message.save() 

    other_user = thread.participants.exclude(id=request.user.id).first()
    print('user data' ,other_user)
  
    if request.method == 'POST':
        form = MessageForm(request.POST, request.FILES)
        if form.is_valid():
         
            message = form.save(commit=False)
            message.thread = thread
            message.sender = request.user
            message.save()
            
      
            notifications = [
                Notification(
                    recipient=participant,
                    sender=request.user,
                    notification_type='message',
                    content_type=ContentType.objects.get_for_model(thread),
                    object_id=thread.id
                )
                for participant in thread.participants.exclude(id=request.user.id)
            ]
            Notification.objects.bulk_create(notifications)
           
            thread.save()
            
          
            return redirect('thread_detail', thread_id=thread.id)
    else:
        
        form = MessageForm()
    
    context = {
        'thread': thread,
        'messages_list': messages_list,
        'form': form,
        'other_user': other_user,  
    }
    
    return render(request, 'messages/thread_detail.html', context)

@login_required
def start_thread(request, username):
 
    recipient = get_object_or_404(User, username=username)
    
 
    threads = Thread.objects.filter(participants=request.user).filter(participants=recipient)
    if threads.exists():
       
        return redirect('thread_detail', thread_id=threads.first().id)
    

    if request.method == 'POST':
        form = MessageForm(request.POST, request.FILES)
        if form.is_valid():
          
            thread = Thread.objects.create()
            thread.participants.add(request.user, recipient)
            
    
            message = form.save(commit=False)
            message.thread = thread
            message.sender = request.user
            message.save()
            
          
            Notification.objects.create(
                recipient=recipient,
                sender=request.user,
                notification_type='message',
                content_type=ContentType.objects.get_for_model(thread),
                object_id=thread.id
            )
            
           
            return redirect('thread_detail', thread_id=thread.id)
    else:
        
        form = MessageForm()
    

    context = {
        'form': form,
        'recipient': recipient,
    }
    
    return render(request, 'messages/start_thread.html', context)
