from django.contrib import admin
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from .models import LibraryUserModel, AuthorModel, BookListModel, Library, LibraryStaff
# Register your models here.
admin.site.register(LibraryUserModel)
admin.site.register(AuthorModel)
admin.site.register(BookListModel)
admin.site.register(Library)
admin.site.register(LibraryStaff)
#
# class CanAddBook(Permission):
#     name = "Can add book"
#     content_type = ContentType.objects.get_for_model(BookListModel)
#     codename = 'can_add_book'
#
# class CanBorrowBook(Permission):
#     name = "Can borrow book"
#     content_type = ContentType.objects.get_for_model(Library)
#     codename = 'can_borrow_book'
#
# class CanReturnBook(Permission):
#     name = "Can return book"
#     content_type = ContentType.objects.get_for_model(Library)
#     codename = 'can_return_book'
#
