import django
django.setup()

from django.shortcuts import render, redirect
from .models import *
from django.contrib.auth.decorators import login_required
from .forms import *

# bobby account credentials
# bobby - username
# bobbydeol123@ - password


# Create your views here.
@login_required
def chat_view(request):
    chat_group = ChatGroup.objects.get(group_name = 'public-chat')
    chat_messages = GroupMessage.objects.filter(group = chat_group)[:30]
    
    form = ChatMessageCreateForm()
    
    if request.htmx:
        form = ChatMessageCreateForm(request.POST)

        if form.is_valid():

            group_message_obj = form.save(commit = False)
            group_message_obj.author = request.user
            group_message_obj.group = chat_group
            group_message_obj.save()

            context = {
                'message': group_message_obj,
                'user': request.user
            }
            return render(request, "partials/chat_message_p.html", context)


    return render(request, 'chat.html', {'chat_messages': chat_messages, 'form': form})