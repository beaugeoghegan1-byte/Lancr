from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from .models import Article, Message
from jobs.models import Job as JobModel
from django.contrib.auth.decorators import login_required
from .forms import MessageForm


def about(request):
    return HttpResponse("This is the About page.")


def article_list(request):
    return HttpResponse("This is the list of articles.")


def article_detail(request, id):
    article = get_object_or_404(Article, id=id)
    return render(request, 'article_detail.html', {'article': article})


@login_required
def job_messages(request, job_id):
    job = get_object_or_404(JobModel, id=job_id)
    messages_qs = Message.objects.filter(job=job).order_by('timestamp')

    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            msg = form.save(commit=False)
            msg.job = job
            msg.sender = request.user
            msg.receiver = job.client
            msg.save()
            return redirect('job_messages', job_id=job.id)
    else:
        form = MessageForm()

    return render(request, 'my_app/job_messages.html', {
        'job': job,
        'messages': messages_qs,
        'form': form
    })










