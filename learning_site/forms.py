from django import forms
from django.contrib.auth import authenticate, get_user_model


def must_be_empty(value):
    # validation function for bots
    if value:
        raise forms.ValidationError('is not empty')


class SuggestionForm(forms.Form):
    name = forms.CharField()
    email = forms.EmailField()
    verify_email = forms.EmailField(label="Please verify your email address")
    suggestion = forms.CharField(widget=forms.Textarea)
    honeypot = forms.CharField(required=False,  # check for bots with honeypot
                               widget=forms.HiddenInput,
                               label="Leave empty",
                               validators=[must_be_empty]
                               )

    def clean(self):
        # clean entire form
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        verify = cleaned_data.get('verify_email')

        if email != verify:
            raise forms.ValidationError(
                "You need to enter the same email in both fields")


User = get_user_model()

class UserLoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self, *args, **kwargs):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise forms.ValidationError('This user does not exist')
            if not user.check_password(password):
                raise forms.ValidationError('Incorrect password')
            if not user.is_active:
                raise forms.ValidationError('This user is not active')
        return super(UserLoginForm, self).clean(*args, **kwargs)


class UserRegisterForm(forms.ModelForm):
    IB_DIPLOMA = 'ib'
    A_LEVELS = 'a_levels'
    OTHER = 'other'

    HIGHSCHOOL_DIPLOMA_CHOICES = (
        (IB_DIPLOMA, 'International Baccalaureate'),
        (A_LEVELS, 'A-Levels'),
        (OTHER), 'Other'
    )

    # highschool_diploma = forms.ChoiceField(
    #     choices=HIGHSCHOOL_DIPLOMA_CHOICES,
    # )

    first_name = forms.CharField(label='First Name')
    last_name = forms.CharField(label='Last Name')
    email = forms.EmailField(label='Email Address')
    email2 = forms.EmailField(label='Confirm Email')
    password = forms.CharField(widget=forms.PasswordInput)
    staff_status = forms.BooleanField(label='Staff Status', required=False, initial=False)

    class Meta:
        model = User
        fields = [
            'username',
            'first_name',
            'last_name',
            'email',
            'email2',
            'password',
            'staff_status',
        ]

    def clean(self, *args, **kwargs):
        email = self.cleaned_data.get('email')
        email2 = self.cleaned_data.get('email2')
        if email != email2:
            raise forms.ValidationError('Emails must match')
        email_qs = User.objects.filter(email=email)
        if email_qs.exists():
            raise forms.ValidationError('This email is already taken')
        return super(UserRegisterForm, self).clean(*args, **kwargs)
