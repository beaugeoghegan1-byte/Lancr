from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from accounts.forms import CustomUserCreationForm
from django.contrib.auth.forms import AuthenticationForm

# --- Login ---
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)  # ✅ sets session cookie
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect("job_list")  # or redirect to dashboard_view if preferred
        else:
            messages.error(request, "Invalid username or password.")
            return redirect("home")

    return render(request, "accounts/login.html")

# --- Logout ---
def logout_view(request):
    logout(request)
    messages.info(request, "You've been logged out successfully.")
    return redirect("home")

# --- Dashboard (role-based) ---
def dashboard_view(request):
    user = request.user
    if user.is_authenticated:
        if hasattr(user, "is_client") and user.is_client():
            return render(request, "accounts/client_dashboard.html")
        elif hasattr(user, "is_freelancer") and user.is_freelancer():
            return render(request, "accounts/freelancer_dashboard.html")
    return redirect("home")


def register_view(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("home")
    else:
        form = CustomUserCreationForm()

    return render(request, "accounts/register.html", {"form": form})
