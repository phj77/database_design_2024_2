from django.contrib import admin
from .models import *
# Register your models here.

admin.site.register(Genre)
admin.site.register(Author)
admin.site.register(Book)
admin.site.register(User_member)
admin.site.register(User_manager)
admin.site.register(Comments)
admin.site.register(Loan)
admin.site.register(LoanHistory)