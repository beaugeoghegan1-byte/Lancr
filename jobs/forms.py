from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from .models import Job, Profile

User = get_user_model()

INPUT_CLASS = 'input-dark'

COUNTY_CHOICES = [
    ('', 'Select county...'),
    # Leinster
    ('Carlow', 'Carlow'),
    ('Dublin', 'Dublin'),
    ('Kildare', 'Kildare'),
    ('Kilkenny', 'Kilkenny'),
    ('Laois', 'Laois'),
    ('Longford', 'Longford'),
    ('Louth', 'Louth'),
    ('Meath', 'Meath'),
    ('Offaly', 'Offaly'),
    ('Westmeath', 'Westmeath'),
    ('Wexford', 'Wexford'),
    ('Wicklow', 'Wicklow'),
    # Munster
    ('Clare', 'Clare'),
    ('Cork', 'Cork'),
    ('Kerry', 'Kerry'),
    ('Limerick', 'Limerick'),
    ('Tipperary', 'Tipperary'),
    ('Waterford', 'Waterford'),
    # Connacht
    ('Galway', 'Galway'),
    ('Leitrim', 'Leitrim'),
    ('Mayo', 'Mayo'),
    ('Roscommon', 'Roscommon'),
    ('Sligo', 'Sligo'),
    # Ulster (ROI)
    ('Cavan', 'Cavan'),
    ('Donegal', 'Donegal'),
    ('Monaghan', 'Monaghan'),
]


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

    # Freelancer-only fields
    trade = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': INPUT_CLASS,
            'placeholder': 'e.g. Plumber, Electrician, Carpenter'
        })
    )
    county = forms.ChoiceField(
        choices=COUNTY_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': INPUT_CLASS})
    )
    hourly_rate = forms.DecimalField(
        max_digits=6,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={
            'class': INPUT_CLASS,
            'placeholder': 'e.g. 45'
        })
    )
    years_experience = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': INPUT_CLASS,
            'placeholder': 'e.g. 5'
        })
    )
    is_available = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'accent-teal-500 w-4 h-4'})
    )

    class Meta:
        model = Profile
        fields = ['bio', 'avatar', 'trade', 'county', 'hourly_rate', 'years_experience', 'is_available']
        widgets = {
            'bio': forms.Textarea(attrs={'class': INPUT_CLASS, 'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['username'].initial = user.username

        # If client, remove freelancer-only fields entirely
        if user and hasattr(user, 'profile') and user.profile.role == 'client':
            for field in ['trade', 'county', 'hourly_rate', 'years_experience', 'is_available']:
                self.fields.pop(field)

    def save_with_user(self, user, commit=True):
        profile = super().save(commit=False)
        user.username = self.cleaned_data['username']
        if commit:
            user.save()
            profile.save()
        return profile