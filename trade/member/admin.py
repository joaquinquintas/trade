from trade.member.models import *
from django.contrib import admin


class MemberAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name', )
    search_fields = ['first_name', 'last_name', 'email', 'user__username']

admin.site.register(Member, MemberAdmin)
