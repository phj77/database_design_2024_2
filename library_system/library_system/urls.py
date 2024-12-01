"""
URL configuration for library_system project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
from library.views import *

urlpatterns = [
    path("admin/", admin.site.urls),
    path('', loginPage, name='login'),  # 로그인 페이지
    path('register/', registerPage, name='register'),  # 회원가입 페이지
    path('main/', mainPage, name='main_page'),  # 메인 페이지
    path('search/', searchPage, name='search_page'),  # 검색 페이지
    path('member/', memberPage, name='member_page'),  # 회원 페이지
    path('manager/', managerPage, name='manager_page'),  # 관리자 페이지
    path("book_details/<int:book_id>/", book_details, name="book_details"),
    path("borrow_book/<int:book_id>/", borrow_book, name="borrow_book"),
    path("add_comment/<int:book_id>/", add_comment, name="add_comment"),
    path('logout/', logout, name='logout'),
    path('user_info/', get_user_info, name='user_info'),

    path('manage_books/', manage_books, name='manage_books'),
]
