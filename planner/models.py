from django.db import models

class StudyTask(models.Model):
    PRIORITY_CHOICES = [
        ('High', 'High'),
        ('Medium', 'Medium'),
        ('Low', 'Low'),
    ]

    DIFFICULTY_CHOICES = [
        ('Easy', 'Easy'),
        ('Medium', 'Medium'),
        ('Hard', 'Hard'),
    ]

    subject = models.CharField(max_length=100)
    hours = models.FloatField()
    deadline = models.DateField()
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES)
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, default='Medium')
    preferred_time = models.CharField(max_length=20, default='Evening')
    completed = models.BooleanField(default=False)

    def __str__(self):
        return self.subject
