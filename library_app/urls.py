from django.urls import path
from . import views
# app name
app_name = "library_app"

urlpatterns = [
    path("index/", views.LibraryIndexView.as_view(), name="index"),
    path('home/', views.LibraryHomeView.as_view(),name="home"),
    path('login/', views.UserLoginView.as_view(),name="login"),
    path('logout/', views.UserLogoutView.as_view(),name="logout"),
    path('register/', views.RegisterUserView.as_view(),name="register"),
    path('librarybooks/',views.LibraryBooksListView.as_view(),name="librarybooks"),
    path('borrowbook/<slug:book_name>/', views.BorrowBookView.as_view(),name="borrowbook"),
    path('userbooks/', views.UserBooks,name="userbooks"),
    path('return/<int:pk>/', views.UserReturnBook, name="return"),
    path('staffregister/', views.StaffUserView.as_view(),name="staffregister"),
    # staff login url doesn't require because it's done by site user login view
    #path("staff/login/", views.StaffLoginView.as_view(), name="staff"),
    path('addbook/', views.StaffAddBooksView.as_view(),name="addbook"),
    path('duebookusers/', views.DueBookUsers.as_view(),name="duebookusers"),
    path('wishlist/', views.WishListView.as_view(),name="wishlist"),
    path('userwishbook/', views.UserWishedBookView.as_view(),name="userwishbook"),
]

