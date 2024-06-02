from django.contrib.auth.forms import AuthenticationForm
from library_app.models import Library, LibraryUserModel, BookListModel
from crispy_forms.layout import Layout, Submit, Field, Row, Column
from django.contrib.auth.models import User
from crispy_forms.helper import FormHelper
from library_app.models import LibraryStaff
from django import forms


class UserLoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'username'}),label="", max_length=100, required=True)
    password = forms.CharField(label="", widget=forms.PasswordInput(attrs={'placeholder': 'password'}))

    def __init__(self, *args, **kwargs):
        super(UserLoginForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Column(
                Row('username', css_class='col-md-14', placeholder="username"),
                Row('password', css_class='col-md-14', placeholder="Password"),
            )
        )
        self.helper.add_input(Submit('submit','login'))


class RegisterUSerForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'ConForm Password'}), label="Confirm password")

    class Meta:
        model = LibraryUserModel
        fields = ['username','password']
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'username'}),
        }

    def clean_password2(self):
        password = self.cleaned_data
        if password['password'] == password['password2']:
            return password['password2']
        else:
            raise forms.ValidationError('password does not match')

    def __init__(self, *args, **kwargs):
        super(RegisterUSerForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Column(
                Row('username', css_class='col-md-3', placeholder="username"),
                Row('password', css_class='col-md-3', placeholder="Password"),
                Row('password2', css_class='col-md-3', placeholder="Password2"),
            )
        )
        self.helper.add_input(Submit('submit','Register'))

# class LibraryBorrowBookForm(forms.ModelForm):
#     user = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
#
#     class Meta:
#         model = Library
#         fields = ['book']
#         widgets = {
#             'book': forms.Select(attrs={'class': 'form-control'}),
#         }
#
#     def __init__(self, *args, **kwargs):
#         book = kwargs.pop('book_initial', None)
#         super(LibraryBorrowBookForm, self).__init__(*args, **kwargs)
#         if book:
#             self.fields['book'].initial = book


class LibraryBorrowBookForm(forms.Form):
    user = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'username', 'class': 'form-control'}))
    book = forms.ModelChoiceField(queryset=BookListModel.objects.all(), widget=forms.Select(attrs={'class': 'form-control'}))

    def __init__(self, *args, **kwargs):
        book = kwargs.pop('book_initial', None)
        super(LibraryBorrowBookForm, self).__init__(*args, **kwargs)
        if book:
            self.fields['book'].initial = book

#Normal User authentication is enough for login staff user
# class StaffLoginForm(AuthenticationForm):
#     username = forms.CharField(label='Username', max_length=254)
#     password = forms.CharField(label='Password', widget=forms.PasswordInput)

# Staff Model register form
class StaffUserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    password_confirm = forms.CharField(widget=forms.PasswordInput, label='Confirm Password')

    class Meta:
        model = User
        fields = ["username","password"]

    def clean_password2(self):
        password = self.cleaned_data
        if password['password'] == password['password_confirm']:
            return password['password_confirm']
        else:
            raise forms.ValidationError('password does not match')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])  # This line hashes the password
        if commit:
            user.save()
            LibraryStaff.objects.create(user=user)
        return user

    def __init__(self, *args, **kwargs):
        super(StaffUserForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Column(
                Row('username', css_class='col-md-3', placeholder="username"),
                Row('password', css_class='col-md-3', placeholder="Password"),
                Row('password_confirm', css_class='col-md-3', placeholder="password_confirm"),
            )
        )
        self.helper.add_input(Submit('submit','Register'))


class AddBookForm(forms.ModelForm):
    class Meta:
        model = BookListModel
        fields = ["name","authors","publish_date","release_date","slug", "available"]

    def __init__(self,*args, **kwargs):
        super(AddBookForm,self).__init__(*args,**kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Column(
                Row('name', css_class='col-md-3', placeholder="username"),
                Row('authors', css_class='col-md-3'),
                Row('publish_date', css_class='col-md-3'),
                Row('release_date', css_class='col-md-3'),
                Row('slug', css_class='col-md-3'),
                Row('available', css_class='col-md-3'),
            )
        )
        self.helper.add_input(Submit('submit','Register'))


class WishListForm(forms.Form):
    user_name = forms.CharField(max_length=100)
    book_name = forms.CharField(max_length=100)
    author = forms.CharField(max_length=50)
    publish_date = forms.DateField()

