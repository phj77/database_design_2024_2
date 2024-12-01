from django.db import models
from django_mysql.models import EnumField
from django.db.models import Index

class Genre(models.Model):
    # genre_ID: 기본키, VARCHAR(3), NOT NULL
    genre_ID = models.CharField(max_length=3, primary_key=True)

    # name: VARCHAR(15), NOT NULL
    name = models.CharField(max_length=15)

    # Meta 클래스: 테이블 이름 지정
    class Meta:
        db_table = 'genre'

    # 객체의 문자열 표현
    def __str__(self):
        return self.name

class Author(models.Model):
    # author_ID: 기본키, VARCHAR(10), NOT NULL
    author_ID = models.AutoField(primary_key=True)

    # name: VARCHAR(30), NOT NULL
    name = models.CharField(max_length=30)

    # country: VARCHAR(20), NOT NULL
    country = models.CharField(max_length=20)

    # Meta 클래스: 테이블 이름 지정
    class Meta:
        db_table = 'author'

        indexes = [
            Index(fields=['name'], name='author_name_idx', )
        ]

    # 객체의 문자열 표현
    def __str__(self):
        return self.name
    
class Book(models.Model):
    # bookID: 기본키, VARCHAR(10), NOT NULL
    bookID = models.AutoField(primary_key=True)

    # name: VARCHAR(30), NOT NULL
    name = models.CharField(max_length=30)

    # genre_ID: 외래 키, VARCHAR(3), 참조: Genre 테이블
    genre_ID = models.ForeignKey(
        'Genre',  # 참조할 테이블
        on_delete=models.RESTRICT,  # 삭제 시 제한
        db_column='genre_ID'  # 실제 테이블의 컬럼 이름
    )

    # author_ID: 외래 키, VARCHAR(4), 참조: Author 테이블
    author_ID = models.ForeignKey(
        'Author',  # 참조할 테이블
        on_delete=models.RESTRICT,  # 삭제 시 제한
        db_column='author_ID'  # 실제 테이블의 컬럼 이름
    )

    # is_borrowed: Boolean, 기본값 False
    is_borrowed = models.BooleanField(default=False)

    # Meta 클래스: 테이블 이름 지정
    class Meta:
        db_table = 'book'
        indexes = [
            models.Index(fields=['name'], name='book_name_idx', db_tablespace='FULLTEXT')
        ]

    # 객체의 문자열 표현
    def __str__(self):
        return self.name
    
class User(models.Model):
    # UserID: 기본키, VARCHAR(20), NOT NULL
    UserID = models.CharField(max_length=20, primary_key=True)

    # PW: VARCHAR(20), NOT NULL
    PW = models.CharField(max_length=128)

    # name: VARCHAR(30), NOT NULL
    name = models.CharField(max_length=30)

    # gender: ENUM('M', 'F'), NOT NULL
    gender = EnumField(choices=['M', 'F'], default='M')  # ENUM 필드

    # Meta 클래스: 테이블 이름 지정
    class Meta:
        abstract = True

    # 객체의 문자열 표현
    def __str__(self):
        return f"{self.UserID} ({self.name})"

    
class User_member(User):
    is_overdue = models.BooleanField(default=False)
    class Meta:
        db_table = 'User_member'

class User_manager(User):
    class Meta:
        db_table = 'User_manager'


class Comments(models.Model):
    # comment: VARCHAR(100), NULL 허용
    comment = models.CharField(max_length=100, null=True, blank=True)

    # bookID: 외래키, NOT NULL, 참조: Book 테이블
    bookID = models.ForeignKey(
        'Book',  # 참조할 테이블
        on_delete=models.CASCADE,  # 부모 데이터 삭제 시 자식도 삭제
        db_column='bookID'
    )

    # UserID: 외래키, NOT NULL, 참조: User 테이블
    UserID = models.ForeignKey(
        'User_member',  # 참조할 테이블
        on_delete=models.CASCADE,  # 부모 데이터 삭제 시 자식도 삭제
        db_column='UserID'
    )

    # Meta 클래스: 테이블 이름 지정
    class Meta:
        db_table = 'comments'
        indexes = [
            models.Index(fields=['bookID']),
        ]

    # 객체의 문자열 표현
    def __str__(self):
        return self.comment or "No Comment"
    
class Loan(models.Model):
    # when_borrowed: DATE, NOT NULL
    when_borrowed = models.DateField()

    # UserID: 외래키, NOT NULL, 참조: User 테이블
    UserID = models.ForeignKey(
        'User_member',  # 참조할 테이블
        on_delete=models.RESTRICT,  # 부모(User) 데이터 삭제 제한
        db_column='UserID'
    )

    # bookID: 외래키, NOT NULL, 참조: Book 테이블
    bookID = models.OneToOneField(
        'Book',  # 참조할 테이블
        on_delete=models.CASCADE,  # 부모(Book) 데이터 삭제 시 관련 데이터 삭제
        db_column='bookID'
    )

    # Meta 클래스: 테이블 이름 지정
    class Meta:
        db_table = 'loan'
        indexes = [
            models.Index(fields=['UserID']),
        ]

    # 객체의 문자열 표현
    def __str__(self):
        return f"{self.UserID.UserID} borrowed {self.bookID.name} on {self.when_borrowed}"
    
class LoanHistory(models.Model):
    # when_borrowed: DATE, NOT NULL
    when_borrowed = models.DateField()

    # UserID: 외래키, NOT NULL, 참조: User 테이블
    UserID = models.ForeignKey(
        'User_member',  # 참조할 테이블
        on_delete=models.CASCADE,  # 부모(User) 데이터 삭제 시 관련 데이터 삭제
        db_column='UserID'
    )

    # bookID: 외래키, NOT NULL, 참조: Book 테이블
    bookID = models.ForeignKey(
        'Book',  # 참조할 테이블
        on_delete=models.CASCADE,  # 부모(Book) 데이터 삭제 시 관련 데이터 삭제
        db_column='bookID'
    )

    # Meta 클래스: 테이블 이름 지정
    class Meta:
        db_table = 'loan_history'
        indexes = [
            models.Index(fields=['UserID']),
        ]

    # 객체의 문자열 표현
    def __str__(self):
        return f"{self.UserID.UserID} borrowed {self.bookID.name} on {self.when_borrowed}"
    
#현재 로그인한 유저 구현   
class CurrentSession(models.Model):
    # 세션 ID
    session_id = models.CharField(max_length=40, primary_key=True)

    # 로그인한 유저
    user = models.OneToOneField(
        'User_member',  # 참조: User_member 테이블
        on_delete=models.CASCADE,  # 유저 삭제 시 세션도 삭제
        db_column='user'
    )

    # 로그인 시간
    login_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'current_session'

    def __str__(self):
        return f"Session for {self.user.UserID}"
