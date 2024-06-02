from .models import (
    BookListModel,
    Library,
    LibraryUserModel,
    LibraryStaff,
    WishListModel,
)
from .forms import (
    UserLoginForm,
    RegisterUSerForm,
    LibraryBorrowBookForm,
    StaffUserForm,
    AddBookForm,
    WishListForm
)
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView, CreateView
from django.views.generic.list import ListView
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.db import IntegrityError
from datetime import datetime, timedelta
from django.contrib import messages
from django.views.generic import View
from django.urls import reverse
from django.db.models import Count
from django.db.models import Q
from datetime import date
from django.utils.text import slugify


class LibraryIndexView(ListView):
    template_name = "index.html"
    model = BookListModel
    context_object_name = "books"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        book_counts = Library.objects.values('book__name') \
                                     .annotate(count=Count('book')) \
                                     .order_by('-count')

        # Format data for Chart.js
        book_name = [book['book__name'] for book in book_counts]
        borrow_counts = [book['count'] for book in book_counts]

        context['book_name'] = book_name
        context['borrow_counts'] = borrow_counts
        return context


class LibraryHomeView(LoginRequiredMixin, TemplateView):
    template_name = "home.html"

class UserLoginView(View):
    template_name = "login.html"
    form_class = UserLoginForm

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, context={'form':form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('/index/')
            else:
                messages.error(request, "Invalid User Name Or Password!")
                return render(request, self.template_name, context={'form':form, 'message':messages})
        return render(request, self.template_name, context={'form': form})

class UserLogoutView(View):

    def get(self, request):
        logout(request)
        return redirect('/login/')

class RegisterUserView(View):
    form_class = RegisterUSerForm
    template_name = 'register.html'

    def get(self, request):
        form = self.form_class
        return render(request, self.template_name,{'form':form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            login(request, user)
            return redirect('/index/')
        return render(request, self.template_name, {'form': form})

class BorrowBookView(PermissionRequiredMixin,FormView):
    model = Library
    template_name = "borrowbook.html"
    form_class = LibraryBorrowBookForm
    success_url = "/home/"
    permission_required = 'library_app.add_library'

    def handle_no_permission(self):
        return HttpResponseForbidden("You do not have permission to view this page.")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        self.book_name = self.kwargs.get('book_name')
        if self.book_name:
            self.book = get_object_or_404(BookListModel, slug=self.book_name)
            kwargs['book_initial'] = self.book
        return kwargs

    def form_valid(self, form):
        if not self.request.user.has_perm(self.permission_required):
            return HttpResponseForbidden("Staff users are not allowed to borrow books.")
        # Fetch the user from the form
        username = form.cleaned_data["user"]
        user = get_object_or_404(LibraryUserModel, username=username)
        # Check if the user can borrow more books
        if user.book_count >= user.max_books:
            messages.error(self.request, "Already borrowed the maximum number of books. Can't borrow more.")
            return self.form_invalid(form)
        # Create the Library record
        Library.objects.create(user=user, book=self.book, issued=True)
        # Update the user's book count
        user.book_count += 1
        user.save()
        return super().form_valid(form)

class LibraryBooksListView(LoginRequiredMixin, ListView):
    template_name = "librarybooks.html"
    model = BookListModel
    context_object_name = "books"

@login_required
def UserBooks(request):
    user = request.user
    issued_books = Library.objects.filter(user=user, issued=True)
    context = {'issued_books': issued_books}
    return render(request, 'returnbooks.html', context)


def get_default_event_date():
    return datetime.now().date() + timedelta(days=48)


@login_required
@permission_required('library_app.change_library')
def UserReturnBook(request, pk):
    if not request.user.has_perm('library_app.change_library'):
        return HttpResponseForbidden("Staff users are not allowed to return books.")
    book_record = get_object_or_404(Library, pk=pk, user=request.user)
    current_user = request.user
    user = get_object_or_404(LibraryUserModel, username=current_user)
    user.book_count -= 1
    user.save()
    #user returned book after due date
    book_record.returned_on = get_default_event_date()
    #user returned book on date
    #book_record.returned_on = datetime.now()
    book_record.issued = False
    book_record.save()
    return redirect('/userbooks/')

#staff login can be done by site user login view
# class StaffLoginView(FormView):
#     form_class = StaffLoginForm
#     template_name = 'loginstaff.html'
#     success_url = "/home/"# Change 'dashboard' to your desired URL name
#
#     def form_valid(self, form):
#         username = form.cleaned_data['username']
#         password = form.cleaned_data['password']
#         user = authenticate(self.request, username=username, password=password)
#         if user is not None:
#             login(self.request, user)
#             return super().form_valid(form)
#         else:
#             return self.form_invalid(form)


class StaffUserView(CreateView):
    model = LibraryStaff
    template_name = "staffregister.html"
    form_class = StaffUserForm
    success_url = "/home/"

    def form_valid(self, form):
        try:
            # Attempt to create a LibraryStaff instance
            return super().form_valid(form)
        except IntegrityError:
            # If a user with the same ID already exists, redirect to home or any appropriate URL
            return HttpResponseRedirect(reverse('home'))

class StaffAddBooksView(PermissionRequiredMixin, CreateView):
    template_name = "addbook.html"
    model = BookListModel
    success_url = "/index/"
    form_class = AddBookForm
    permission_required = 'library_app.add_booklistmodel'

    def handle_no_permission(self):
        return HttpResponseForbidden("You do not have permission to view this page.")

    def form_valid(self, form):
        form.save()
        return redirect('/librarybooks/')

class DueBookUsers(PermissionRequiredMixin, ListView):
    model = Library
    template_name = "duereturn_book_users.html"
    context_object_name = 'libraries'
    permission_required = 'library_app.view_library'


    def handle_no_permission(self):
        return HttpResponseForbidden("You do not have permission to view this page.")


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        library_object = Library.objects.all()
        due_users = []

        for library_instance in library_object:
            if library_instance.returned_on and library_instance.return_date < library_instance.returned_on:
                rdate = (library_instance.returned_on - library_instance.return_date).days
                user = library_instance.user.username
                book = library_instance.book.name
                due_users.append({
                    'user': user,
                    'book': book,
                    'rdate': rdate,
                })
        context['due_users'] = due_users
        return context

class UserWishedBookView(FormView):
    template_name = "userwish.html"
    form_class = WishListForm
    success_url = "/home/"

    def form_valid(self, form):
        user_name = form.cleaned_data['user_name']
        book_name = form.cleaned_data['book_name']
        author = form.cleaned_data['author']
        publish_date = form.cleaned_data['publish_date']
        try:
            book = BookListModel.objects.get(name=book_name)
            if book.available:
                messages.error(self.request, "Already Exist, Borrow Book From Library Books! ")
                return self.form_invalid(form)
            WishListModel.objects.create(user_name=user_name, book_name=book_name, author=author,
                                         publish_date=publish_date)
            messages.success(self.request, "Book added to  wishlist successfully!")
            return super().form_valid(form)

        except:
            WishListModel.objects.create(user_name=user_name, book_name=book_name, author=author,
                                         publish_date=publish_date)
            messages.success(self.request, "Book added to  wishlist successfully!")
            return super().form_valid(form)

class WishListView(ListView):
    model = WishListModel
    template_name = "wishlist.html"
    context_object_name = 'wishlist'


