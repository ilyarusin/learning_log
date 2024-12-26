from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Topic, Entry
from .forms import TopicForm, EntryForm
from django.http import Http404

# Create your views here.

def index(request):
    '''Домашняя страница приложения Learning Log'''
    return render(request, 'learning_logs/index.html')


def topics(request):
    '''Выводит список тем'''

    # Get all appropriate topics.
    # If a user is logged in, we get all of their topics, and all public topics
    #   from other users.
    # If a user is not logged in, we get all public topics.
    if request.user.is_authenticated:
        topics = Topic.objects.filter(owner=request.user).order_by('date_added')
        # Get all public topics not owned by the current user.
        # Note: Wrapping the query in parentheses lets you break the long query
        #   up across multiple lines.
        public_topics = (Topic.objects.filter(public=True).exclude(owner=request.user).order_by('date_added'))
    else:
        # User is not authenticated; return all public topics.
        topics = None
        public_topics = Topic.objects.filter(public=True).order_by('date_added')

    context = {'topics': topics, 'public_topics': public_topics}
    return render(request, 'learning_logs/topics.html', context)


def topic(request, topic_id):
    '''Выводит одну тему и все её записи'''
    topic = Topic.objects.get(id=topic_id)

     # We only want to show new_entry and edit_entry links if the current
    #   user owns this topic.
    is_owner = False
    if request.user == topic.owner:
            is_owner = True

    # If the topic belongs to someone else, and it is not public,
    #   show an error page.
    if (topic.owner != request.user) and (not topic.public):
        raise Http404
    
    # Проверка того что тема принадлежит текущему пользователю
    #check_topic_owner(request, topic)

    entries = topic.entry_set.order_by('-date_added')
    context = {'topic': topic, 'entries': entries, 'is_owner': is_owner}
    return render(request, 'learning_logs/topic.html', context)

def check_topic_owner(request, topic):
    '''Проверяет что тема принадлежит текущему пользователю'''
    if topic.owner != request.user:
        raise Http404

@login_required
def new_topic(request):
    '''Определяет новую тему'''
    if request.method != 'POST':
        # Данные не отправлялись. Создается пустая форма.
        form = TopicForm()
    else:
        # Отправлены данные POST; обработать данные.
        form = TopicForm(data=request.POST)
        if form.is_valid():
            new_topic = form.save(commit=False)
            new_topic.owner = request.user
            new_topic.save()
            #form.save()
            return redirect('learning_logs:topics')
    
    # Вывести пустую или недействительную форму
    context = {'form': form}
    return render(request, 'learning_logs/new_topic.html', context)

@login_required
def new_entry(request, topic_id):
    '''Добавляет новую запись по конкретной теме'''
    topic = Topic.objects.get(id=topic_id)

    check_topic_owner(request, topic)
    if request.method != 'POST':
        # Данные не отправлялись. Создается пустая форма.
        form = EntryForm()
    else:
        # Отправлены данные POST; обработать данные.
        form = EntryForm(data=request.POST)
        if form.is_valid():
            new_entry = form.save(commit=False)
            new_entry.topic = topic
            new_entry.save()
            return redirect('learning_logs:topic', topic_id=topic_id)
    
    # Вывести пустую или недействительную форму
    context = {'topic': topic, 'form': form}
    return render(request, 'learning_logs/new_entry.html', context)

@login_required
def edit_entry(request, entry_id):
    '''Редактирует существующую запись'''
    entry = Entry.objects.get(id=entry_id)
    topic = entry.topic

    check_topic_owner(request, topic)

    if request.method != 'POST':
        # Исходный запрос; форма заполняется данными текущей записи.
        form = EntryForm(instance=entry)
    else:
        # Отправка данных POST; обработать данные.
        form = EntryForm(instance=entry, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('learning_logs:topic', topic_id=topic.id)
    
    context = {'entry': entry, 'topic': topic, 'form': form}
    return render(request, 'learning_logs/edit_entry.html', context)