from django.db import models

class Conversation(models.Model):
    user_message = models.TextField()
    bot_response = models.TextField()
    language = models.CharField(max_length=10, default='swahili')
    session_id = models.CharField(max_length=100, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.user_message[:50]}..."

class Lead(models.Model):
    STATUS_CHOICES = [
        ('new', 'New'),
        ('contacted', 'Contacted'),
        ('converted', 'Converted'),
        ('lost', 'Lost'),
    ]
    
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    location = models.CharField(max_length=100)
    current_provider = models.CharField(max_length=50, blank=True)
    interest = models.CharField(max_length=50)
    budget = models.CharField(max_length=50, blank=True)
    needs = models.TextField(blank=True)
    language = models.CharField(max_length=10, default='swahili')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.name} - {self.interest}"