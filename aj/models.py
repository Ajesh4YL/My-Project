from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.search import SearchVectorField, SearchVector

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True)

    def __str__(self):
        return self.user.username
    
class Project(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    owner = models.ForeignKey(User, related_name='owned_projects', on_delete=models.CASCADE)
    team_members = models.ManyToManyField(User, related_name='projects', blank=True)
    search_vector = SearchVectorField(null=True)

    class Meta:
        permissions = [
            ("can_manage_team", "Can manage team members"),
            ("can_view_project", "Can view project"),
            ("can_edit_project", "Can edit project"),
        ]

    def save(self, *args, **kwargs):
        self.search_vector = SearchVector('name', 'description')
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Task(models.Model):
    STATUS_CHOICES = [
        ('TODO', 'To Do'),
        ('INPROGRESS', 'In Progress'),
        ('DONE', 'Done'),
    ]

    PRIORITY_CHOICES = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='TODO')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='MEDIUM')
    due_date = models.DateField()
    assigned_to = models.ForeignKey(User, related_name='tasks', on_delete=models.SET_NULL, null=True, blank=True)
    project = models.ForeignKey(Project, related_name='tasks', on_delete=models.CASCADE)
    search_vector = SearchVectorField(null=True)

    class Meta:
        permissions = [
            ("can_view_task", "Can view task"),
            ("can_edit_task", "Can edit task"),
        ]

    def save(self, *args, **kwargs):
        self.search_vector = SearchVector('title', 'description')
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
