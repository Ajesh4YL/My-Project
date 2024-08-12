from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Project, Task
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'start_date', 'end_date', 'owner')
    search_fields = ('name', 'description')
    list_filter = ('start_date', 'end_date')
    filter_horizontal = ('team_members',)

class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'status', 'priority', 'due_date', 'assigned_to', 'project')
    search_fields = ('title', 'description', 'assigned_to__username', 'project__name')
    list_filter = ('status', 'priority', 'due_date', 'assigned_to', 'project')
    raw_id_fields = ('assigned_to', 'project')

class UserCreationFormWithEmail(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        fields = UserCreationForm.Meta.fields + ('email',)

class UserChangeFormWithEmail(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        fields = UserChangeForm.Meta.fields + ('email',)

class UserAdmin(BaseUserAdmin):
    form = UserChangeFormWithEmail
    add_form = UserCreationFormWithEmail

    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username',)
    filter_horizontal = ()

admin.site.register(Project, ProjectAdmin)
admin.site.register(Task, TaskAdmin)
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
