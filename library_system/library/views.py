from gc import get_objects
from django.db import IntegrityError
from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.views.generic import View
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Book, Comments, CurrentSession, Loan, LoanHistory, User_manager, User_member
from django.db.models import Count
from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import check_password
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction

#page rendering
def loginPage(request):
   return render(request, "login.html")

def mainPage(request):
   return render(request, "main.html")

def searchPage(request):
   return render(request, "search.html")

def memberPage(request):
   return render(request, "member.html")

def managerPage(request):
   return render(request, "manager.html")

#도서관리
def add_book(request):
    if request.method == "POST":
        name = request.POST.get('name')
        genre_id = request.POST.get('genre_ID')
        author_id = request.POST.get('author_ID')

        if not (name and genre_id and author_id):
            return JsonResponse({"error": "All fields are required"}, status=400)

        try:
            # 도서 추가
            book = Book.objects.create(
                name=name,
                genre_ID_id=genre_id,
                author_ID_id=author_id
            )
            return JsonResponse({"message": "Book added successfully", "bookID": book.bookID}, status=201)
        except IntegrityError:
            return JsonResponse({"error": "Invalid genre_ID or author_ID. Please check the references."}, status=400)
        
def delete_book(request, bookID):
    if request.method == "POST":
        try:
            book = get_objects(Book, bookID=bookID)
            # 도서 삭제
            book.delete()
            return JsonResponse({"message": f"Book with ID {bookID} deleted successfully"}, status=200)
        except:
            return JsonResponse({"error": f"Book with ID {bookID} does not exist."}, status=404)
        
def get_books(request):
    # 검색 쿼리 가져오기
    query = request.GET.get('q')
    author = request.GET.get('author')

    # 검색 조건 생성
    books = Book.objects.all()
    if query:
        books = books.filter(name__icontains=query)  # 도서 이름 검색
    if author:
        books = books.filter(author_ID__name__icontains=author)  # 작가 이름 검색

    # 검색 결과가 없을 때
    if not books.exists():
        return JsonResponse({
            "message": "No books found matching your query." if query or author else "No books available.",
            "books": [],
            "count": 0
        }, status=404)

    # 검색 결과 반환
    books_list = list(books.values('bookID', 'name', 'genre_ID__name', 'author_ID__name', 'is_borrowed'))
    return JsonResponse({
        "books": books_list,
        "count": books.count()
    }, status=200)


# 도서 관리 메인 함수
def manage_books(request):
    action = request.GET.get('action')  # 쿼리 파라미터로 동작 구분
    if action == "add":
        return add_book(request)
    elif action == "delete":
        bookID = request.GET.get('bookID')
        if not bookID:
            return JsonResponse({"error": "bookID is required for deletion"}, status=400)
        return delete_book(request, bookID)
    elif action == "get":
        return get_books(request)
    else:
        return JsonResponse({"error": "Invalid action"}, status=400)
    

# 로그인 뷰
def loginPage(request):
    if request.method == "POST":
        user_id = request.POST.get('UserID')
        password = request.POST.get('PW')

        try:
            user = User_member.objects.get(UserID=user_id)  # 기본은 member 검색
            if check_password(password, user.PW):
                # 세션 생성 및 저장
                with transaction.atomic():
                    request.session['user_id'] = user.UserID
                    CurrentSession.objects.create(
                        session_id=request.session.session_key,
                        user=user
                    )
                return redirect('/search')
            else:
                return render(request, 'login.html', {"error": "Invalid password"})
        except User_member.DoesNotExist:
            return render(request, 'login.html', {"error": "User does not exist"})

    return render(request, 'login.html')


# 로그아웃 뷰
# 로그아웃 뷰
def logout(request):
    session_id = request.session.session_key
    try:
        # 현재 세션 삭제
        CurrentSession.objects.filter(session_id=session_id).delete()
        request.session.flush()  # Django 세션 정보 삭제
    except CurrentSession.DoesNotExist:
        pass
    return redirect('/login')  # 로그인 페이지로 리다이렉트


# 회원가입 뷰
def registerPage(request):
    if request.method == "POST":
        print(request.POST)  # 전달된 데이터 출력
        user_id = request.POST.get('UserID')
        password = request.POST.get('PW')
        name = request.POST.get('name')
        gender = request.POST.get('gender')
        user_type = request.POST.get('type')  # member 또는 manager

        if not (user_id and password and name and gender and user_type):
            return JsonResponse({"error": "All fields are required for registration"}, status=400)

        if User_member.objects.filter(UserID=user_id).exists() or User_manager.objects.filter(UserID=user_id).exists():
            return JsonResponse({"error": "UserID already exists"}, status=400)

        if user_type == "member":
            User_member.objects.create(
                UserID=user_id,
                PW=make_password(password),
                name=name,
                gender=gender
            )
        elif user_type == "manager":
            User_manager.objects.create(
                UserID=user_id,
                PW=make_password(password),
                name=name,
                gender=gender
            )
        else:
            return JsonResponse({"error": "Invalid user type"}, status=400)

        return JsonResponse({"success": "Registration successful! Please log in."}, status=201)

    return render(request, 'login.html')

#대출,코멘트 추가
def book_details(request, book_id):
    try:
        book = Book.objects.get(pk=book_id)
        comments = Comments.objects.filter(bookID=book).values_list("comment", flat=True)
        can_comment = LoanHistory.objects.filter(bookID=book, UserID=request.session.get("user_id")).exists()
        return JsonResponse({
            "name": book.name,
            "author": book.author_ID.name,
            "genre": book.genre_ID.name,
            "is_borrowed": book.is_borrowed,
            "comments": list(comments),
            "can_comment": can_comment,
        })
    except Book.DoesNotExist:
        return JsonResponse({"error": "Book not found"}, status=404)

@csrf_exempt
def borrow_book(request, book_id):
    if request.method == "POST":
        user = get_logged_in_user(request)
        if not user:
            return JsonResponse({"error": "User not logged in"}, status=403)

        try:
            book = Book.objects.get(pk=book_id)
            if book.is_borrowed:
                return JsonResponse({"error": "Book already borrowed"}, status=400)

            # 대출 처리
            book.is_borrowed = True
            book.save()

            Loan.objects.create(UserID=user, bookID=book, when_borrowed=timezone.now())
            LoanHistory.objects.create(UserID=user, bookID=book, when_borrowed=timezone.now())

            return JsonResponse({"success": "Book borrowed successfully!"})
        except Book.DoesNotExist:
            return JsonResponse({"error": "Book not found"}, status=404)


@csrf_exempt
def add_comment(request, book_id):
    if request.method == "POST":
        user = get_logged_in_user(request)
        if not user:
            return JsonResponse({"error": "User not logged in"}, status=403)

        comment = request.POST.get("comment")
        if not comment:
            return JsonResponse({"error": "Comment cannot be empty"}, status=400)

        # 유저가 해당 책을 빌린 기록 확인
        if not LoanHistory.objects.filter(bookID_id=book_id, UserID=user).exists():
            return JsonResponse({"error": "You cannot comment on this book"}, status=403)

        Comments.objects.create(bookID_id=book_id, UserID=user, comment=comment)
        return JsonResponse({"success": "Comment added!"})

    
#로그인한 유저 정보 조회
def get_logged_in_user(request):
    session_id = request.session.session_key
    try:
        current_session = CurrentSession.objects.get(session_id=session_id)
        return current_session.user
    except CurrentSession.DoesNotExist:
        return None
    

def get_user_info(request):
    user = get_logged_in_user(request)
    if not user:
        return JsonResponse({"error": "User not logged in"}, status=403)

    # Loan history 데이터
    loans = LoanHistory.objects.filter(UserID=user).values("bookID__name", "when_borrowed")

    # Currently borrowed 데이터
    current_loans = Loan.objects.filter(UserID=user).values("bookID__name")

    return JsonResponse({
        "UserID": user.UserID,
        "name": user.name,
        "loan_history": [{"book": loan["bookID__name"], "when_borrowed": loan["when_borrowed"]} for loan in loans],
        "current_loans": [{"book": loan["bookID__name"]} for loan in current_loans],
    })
