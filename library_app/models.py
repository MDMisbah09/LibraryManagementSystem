from typing import re
from django.contrib.auth.models import User
from django.db import models
from datetime import datetime, timedelta
from django.template.defaultfilters import slugify

def create_slug(text):
    # Preprocess text (optional)
    text = text.lower()  # Ensure lowercase
    text = re.sub(r"[^\w\s-]", "", text)  # Remove non-alphanumeric characters and spaces
    return slugify(text)

def get_default_event_date():
    return datetime.now().date() + timedelta(days=45)

class LibraryUserModel(User):
    max_books = models.PositiveIntegerField(default=3)
    book_count = models.PositiveIntegerField(default=0)


    def __str__(self):
        return self.username

class AuthorModel(models.Model):
    author = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return self.author

class BookListModel(models.Model):
    name = models.CharField(max_length=50)
    authors = models.ManyToManyField(AuthorModel)
    publish_date = models.DateField()
    release_date = models.DateField()
    slug = models.SlugField(unique=True)
    available = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = create_slug(self.name)
        super().save(*args, **kwargs)

class Library(models.Model):
    user = models.ForeignKey(LibraryUserModel, on_delete=models.CASCADE)
    book = models.ForeignKey(BookListModel, on_delete=models.CASCADE, unique=False)
    borrow_date = models.DateField(auto_now=True)
    return_date = models.DateField(default=get_default_event_date)
    returned_on = models.DateField(null=True, blank=True)
    issued = models.BooleanField()

    class Meta:
        permissions = [
            ("view_due_books_users", "Can view due books users")
        ]

class LibraryStaff(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username

class WishListModel(models.Model):
    user_name = models.CharField(max_length=50)
    book_name = models.CharField(max_length=50)
    author = models.CharField(max_length=50)
    publish_date = models.DateField()

    def __str__(self):
        return self.user_name
