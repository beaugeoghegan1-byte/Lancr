from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, HttpResponse, HttpResponseBadRequest
from django.template.loader import render_to_string
from django.db import models
from django.db.models import Avg, Q 
from .models import Job, Application, JobImage , Notification, Review
from .forms import JobForm, RegisterForm, ProfileEditForm
from .models import Message
from django.contrib.auth import get_user_model


def home(request):
    User = get_user_model()
    total_jobs = Job.objects.count()
    total_freelancers = User.objects.filter(profile__role='freelancer').count()
    total_hired = Job.objects.filter(status='closed').count()

    return render(request, 'jobs/home.html', {
        'total_jobs': total_jobs,
        'total_freelancers': total_freelancers,
        'total_hired': total_hired,
    })


def job_list(request):
    jobs = Job.objects.filter(status="open").order_by("-created_at")
    query = request.GET.get("q")
    category = request.GET.get("category")
    remote = request.GET.get("remote")
    location = request.GET.get("location")  # add this

    if query:
        jobs = jobs.filter(title__icontains=query)
    if category:
        jobs = jobs.filter(category=category)
    if remote:
        jobs = jobs.filter(remote=True)
    if location:                                      # add this
        jobs = jobs.filter(location__icontains=location)  # and this

    return render(request, "jobs/job_list.html", {
        "jobs": jobs,
        "categories": Job.CATEGORY_CHOICES
    })


def job_detail(request, id):
    job = get_object_or_404(Job, id=id)
    user_has_applied = False
    if request.user.is_authenticated:
        user_has_applied = Application.objects.filter(
            job=job, freelancer=request.user
        ).exists()
    return render(request, 'jobs/job_detail.html', {
        'job': job,
        'user_has_applied': user_has_applied
    })


def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("login")
    else:
        form = RegisterForm()
    return render(request, "jobs/register.html", {"form": form})

def profile_view(request, username):
    User = get_user_model()
    viewed_user = get_object_or_404(User, username=username)
    profile = viewed_user.profile

    posted_jobs = None
    if profile.role == 'client':
        posted_jobs = Job.objects.filter(client=viewed_user, status='open')

    # Reviews received
    reviews = viewed_user.reviews_received.select_related('reviewer', 'job')
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg']

    # Jobs where current user can leave a review
    reviewable_jobs = []
    if request.user.is_authenticated and request.user != viewed_user:
        # Jobs where both users were involved and job is in_progress or closed
        completed_jobs = Job.objects.filter(
            status__in=['in_progress', 'closed']
        ).filter(
            models.Q(client=request.user, hired_freelancer=viewed_user) |
            models.Q(client=viewed_user, hired_freelancer=request.user)
        )
        # Filter to jobs not already reviewed by current user
        already_reviewed = Review.objects.filter(
            reviewer=request.user,
            reviewee=viewed_user
        ).values_list('job_id', flat=True)

        reviewable_jobs = completed_jobs.exclude(id__in=already_reviewed)

    return render(request, 'jobs/profile_view.html', {
        'viewed_user': viewed_user,
        'profile': profile,
        'posted_jobs': posted_jobs,
        'reviews': reviews,
        'avg_rating': avg_rating,
        'reviewable_jobs': reviewable_jobs,
    })

# ------------------------
# POST JOB
# ------------------------
@login_required
def job_create(request):
    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description")
        budget = request.POST.get("budget")
        category = request.POST.get("category")

        job = Job.objects.create(
            title=title,
            description=description,
            budget=budget,
            category=category,
            client=request.user
        )
        html = render_to_string(
            "jobs/partials/job_card.html",
            {"job": job},
            request=request
        )
        return HttpResponse(html)

    return redirect("job_list")


# ------------------------
# APPLY TO JOB
#

@login_required
def apply_job(request, id):
    if request.user.profile.role != 'freelancer':
        return HttpResponseForbidden("Only freelancers can apply.")

    job = get_object_or_404(Job, id=id)

    if job.client == request.user:
        return HttpResponseForbidden("You cannot apply to your own job.")

    if Application.objects.filter(job=job, freelancer=request.user).exists():
        return redirect('job_detail', id=id)

    if request.method == 'POST':
        cover_letter = request.POST.get('cover_letter', '')
        Application.objects.create(
            job=job,
            freelancer=request.user,
            cover_letter=cover_letter
        )
        Notification.objects.create(
            user=job.client,
            type='application',
            message=f"{request.user.username} applied to your job: {job.title}",
            link=f"/jobs/{job.id}/applications/"
        )
        return redirect('job_detail', id=id)

    return redirect('job_detail', id=id)


# ------------------------
# EDIT JOB
# ------------------------
@login_required
def job_edit(request, id):
    job = get_object_or_404(Job, id=id, client=request.user)
    if request.method == 'POST':
        form = JobForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            return redirect('job_detail', id=id)
    else:
        form = JobForm(instance=job)
    return render(request, 'jobs/job_form.html', {
        'form': form,
        'edit_mode': True
    })


# ------------------------
# DELETE JOB
# ------------------------
@login_required
def job_delete(request, id):
    job = get_object_or_404(Job, id=id, client=request.user)
    if request.method == 'POST':
        job.delete()
        return redirect('job_list')
    return render(request, 'jobs/job_confirm_delete.html', {'job': job})


# ------------------------
# VIEW APPLICATIONS (client only)
# ------------------------
@login_required
def job_applications(request, id):
    job = get_object_or_404(Job, id=id)

    if request.user.profile.role != 'client' or job.client != request.user:
        return HttpResponseForbidden("Not allowed.")

    applications = Application.objects.filter(job=job).select_related('freelancer')
    return render(request, "jobs/job_applications.html", {
        "job": job,
        "applications": applications
    })


# ------------------------
# HIRE FREELANCER — FIXED
# ------------------------
@login_required
def hire_freelancer(request, id):
    application = get_object_or_404(Application, id=id)
    job = application.job

    if job.client != request.user:
        return HttpResponseForbidden("Not allowed.")

    if job.status != "open":
        return redirect("job_applications", id=job.id)

    # Reject all other applications for this job
    Application.objects.filter(job=job).exclude(id=application.id).update(status="rejected")

    # Accept this one
    application.status = "accepted"
    application.save()

    # Update the job itself
    job.hired_freelancer = application.freelancer
    job.status = "in_progress"
    job.save()

    Notification.objects.create(
        user=application.freelancer,
        type='accepted',
        message=f"Your application for '{job.title}' was accepted!",
        link=f"/jobs/{job.id}/chat/"
    )

    # Notify rejected freelancers
    rejected = Application.objects.filter(job=job).exclude(id=application.id)
    for rejected_app in rejected:
        Notification.objects.create(
            user=rejected_app.freelancer,
            type='rejected',
            message=f"Your application for '{job.title}' was not selected.",
            link=f"/jobs/{job.id}/"
        )

    return redirect("job_applications", id=job.id)


# ------------------------
# DASHBOARDS
# ------------------------
@login_required
def client_dashboard(request):
    profile = request.user.profile

    if profile.role == "client":
        jobs = Job.objects.filter(client=request.user)
        return render(request, "jobs/client_dashboard.html", {
            "jobs": jobs
        })

    elif profile.role == "freelancer":
        applications = Application.objects.filter(
            freelancer=request.user
        ).select_related("job")

        active_jobs = Job.objects.filter(
            hired_freelancer=request.user,
            status="in_progress"
        )
        return render(request, "jobs/freelancer_dashboard.html", {
            "applications": applications,
            "active_jobs": active_jobs
        })


# ------------------------
# JOB CHAT
# ------------------------
@login_required
def job_chat(request, job_id):
    job = get_object_or_404(Job, id=job_id)

    accepted_app = job.applications.filter(status="accepted").first()
    if not accepted_app:
        return redirect("job_list")

    if request.user != job.client and request.user != accepted_app.freelancer:
        return redirect("job_list")

    messages = job.messages.all().order_by("created_at")
    return render(request, "jobs/job_chat.html", {
        "job": job,
        "messages": messages
    })


# ------------------------
# SEND MESSAGE
# ------------------------
@login_required
def send_message(request, job_id):
    if request.method == "POST":
        job = get_object_or_404(Job, id=job_id)

        accepted_app = job.applications.filter(status="accepted").first()
        if not accepted_app:
            return HttpResponse(status=403)

        if request.user != job.client and request.user != accepted_app.freelancer:
            return HttpResponse(status=403)

        content = request.POST.get("content")
        message = Message.objects.create(
            job=job,
            sender=request.user,
            content=content
        )

        # Notify the other person in the chat
        other_user = accepted_app.freelancer if request.user == job.client else job.client
        Notification.objects.create(
            user=other_user,
            type='message',
            message=f"{request.user.username} sent a message on: {job.title}",
            link=f"/jobs/{job.id}/chat/"
        )
        return render(request, "jobs/partials/message.html", {
            "message": message,
            "user": request.user
        })


@login_required
def profile_edit(request):
    profile = request.user.profile
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES, instance=profile, user=request.user)
        if form.is_valid():
            form.save_with_user(request.user)
            return redirect('profile_view', username=request.user.username)
    else:
        form = ProfileEditForm(instance=profile, user=request.user)
    return render(request, 'jobs/profile_edit.html', {'form': form})


@login_required
def job_create(request):
    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description")
        budget = request.POST.get("budget")
        category = request.POST.get("category")
        location = request.POST.get("location", "")
        remote = request.POST.get("remote") == "on"
        currency = request.POST.get("currency", "EUR")

        job = Job.objects.create(
            title=title,
            description=description,
            budget=budget,
            category=category,
            location=location,
            remote=remote,
            currency=currency,
            client=request.user
        )

        for image in request.FILES.getlist('images'):
            JobImage.objects.create(job=job, image=image)

        if request.headers.get("HX-Request") == "true":
            job_card_html = render_to_string(
                "jobs/_job_card.html",
                {"job": job, "user": request.user},
                request=request
            )
            # Return confirmation banner + job card
            return HttpResponse(f"""
                <li id="job-confirm-banner"
                    class="bg-teal-900/40 border border-teal-600 rounded-2xl p-4
                           flex items-center justify-between gap-4 mb-2"
                    _="on load wait 4s then remove me">
                  <div class="flex items-center gap-3">
                    <span class="text-2xl">✅</span>
                    <div>
                      <p class="text-teal-300 font-semibold text-sm">Job posted successfully!</p>
                      <p class="text-teal-400/70 text-xs mt-0.5">"{job.title}" is now live and visible to freelancers.</p>
                    </div>
                  </div>
                </li>
                {job_card_html}
            """)

        return redirect('job_list')

    return redirect('job_list')

@login_required
def mark_notifications_read(request):
    notification = get_object_or_404(Notification, id=id, user=request.user)
    notification.is_read = True
    notification.save()
    return redirect(notification.link)


@login_required
def leave_review(request, username):
    if request.method != 'POST':
        return HttpResponseBadRequest("Only POST allowed")

    User = get_user_model()
    reviewee = get_object_or_404(User, username=username)
    job_id = request.POST.get('job_id')
    rating = request.POST.get('rating')

    if not job_id or not rating:
        return HttpResponseBadRequest("Missing fields")

    job = get_object_or_404(Job, id=job_id)

    # Security — must be client or hired freelancer on this job
    if request.user != job.client and request.user != job.hired_freelancer:
        return HttpResponseForbidden()

    # Prevent self-review
    if request.user == reviewee:
        return HttpResponseForbidden()

    # Prevent duplicate reviews
    if Review.objects.filter(job=job, reviewer=request.user).exists():
        return redirect('profile_view', username=username)

    Review.objects.create(
        job=job,
        reviewer=request.user,
        reviewee=reviewee,
        rating=int(rating)
    )

    # Notify the reviewee
    Notification.objects.create(
        user=reviewee,
        type='application',
        message=f"{request.user.username} left you a {rating}★ review.",
        link=f"/profile/{reviewee.username}/"
    )

    return redirect('profile_view', username=username)

@login_required
def notification_read(request, id):
    notification = get_object_or_404(Notification, id=id, user=request.user)
    notification.is_read = True
    notification.save()
    return redirect(notification.link)

@login_required
def delete_notification(request, id):
    notification = get_object_or_404(Notification, id=id, user=request.user)
    notification.delete()
    return HttpResponse("")


@login_required
def mark_complete(request, id):
    job = get_object_or_404(Job, id=id)

    # Security — only client or hired freelancer can mark complete
    if request.user != job.client and request.user != job.hired_freelancer:
        return HttpResponseForbidden()

    if request.user == job.client:
        job.completed_by_client = True
    elif request.user == job.hired_freelancer:
        job.completed_by_freelancer = True

    # If both have confirmed — mark as closed
    if job.completed_by_client and job.completed_by_freelancer:
        job.status = 'closed'

        # Notify both parties
        Notification.objects.create(
            user=job.client,
            type='accepted',
            message=f"'{job.title}' has been marked as complete!",
            link=f"/profile/{job.hired_freelancer.username}/"
        )
        Notification.objects.create(
            user=job.hired_freelancer,
            type='accepted',
            message=f"'{job.title}' has been marked as complete!",
            link=f"/profile/{job.client.username}/"
        )

    job.save()
    return redirect('job_chat', job_id=job.id)