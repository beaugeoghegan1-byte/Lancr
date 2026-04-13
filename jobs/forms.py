from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from .models import Job, Profile

User = get_user_model()

INPUT_CLASS = 'input-dark'


class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ['title', 'description', 'budget', 'category', 'location', 'remote']


class RegisterForm(UserCreationForm):
    role = forms.ChoiceField(
        choices=Profile.ROLE_CHOICES,
        widget=forms.Select(attrs={'class': INPUT_CLASS})
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'role', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name != 'role':
                field.widget.attrs.update({'class': INPUT_CLASS})
        # Remove verbose Django help text
        self.fields['username'].help_text = None
        self.fields['password1'].help_text = None
        self.fields['password2'].help_text = None

    def save(self, commit=True):
        user = super().save(commit)
        user.profile.role = self.cleaned_data['role']
        user.profile.save()
        return user


class ProfileEditForm(forms.ModelForm):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': INPUT_CLASS})
    )

    class Meta:
        model = Profile
        fields = ['bio', 'avatar']
        widgets = {
            'bio': forms.Textarea(attrs={'class': INPUT_CLASS, 'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['username'].initial = user.username

    def save_with_user(self, user, commit=True):
        profile = super().save(commit=False)
        user.username = self.cleaned_data['username']
        if commit:
            user.save()
            profile.save()
        return profile