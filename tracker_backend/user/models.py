from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal
from django.conf import settings
from cloudinary.models import CloudinaryField



class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class Expense(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="expenses")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    notes = models.TextField(blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.category or 'Uncategorized'} - ${self.amount}"


class Income(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="incomes")
    source = models.CharField(max_length=150)  # e.g. Salary, Freelance, Investment
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    notes = models.TextField(blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.source} - ${self.amount}"


class Budget(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='budgets')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='budget')
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    spent = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    icon = models.CharField(max_length=10, default="🏷️")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'category')
        ordering = ('-created_at',)

    def __str__(self):
        return f"{self.user.username} - {self.category.name} : ${self.amount}"
    
    @property
    def name(self):
        return self.category.name if self.category else "Unknown"
    
    @property
    def percentage_used(self):
        if self.amount > 0:
            return (self.spent / self.amount) * 100
        return 0

    @property
    def remaining(self):
        return self.amount - self.spent

    @property
    def is_over_budget(self):
        return self.spent > self.amount



class Transaction(models.Model):
    TRANSACTION_TYPES = (
        ("income", "Income"),
        ("expense", "Expense"),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="transactions")
    type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.TextField(blank=True)
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    class Meta:
        ordering = ("-date", "-created_at")

    def __str__(self):
        return f"{self.user.username} - {self.get_type_display()} - {self.amount}"
    

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    bio= models.TextField(blank=True, null=True)
    avatar = CloudinaryField('avatar', blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s profile"
    
    def get_avatar_url(self):
        if self.avatar:
            return self.avatar.url
        return None



class SavingsGoal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='savings_goals')
    name = models.CharField(max_length=100)
    target = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    current = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    deadline = models.DateField()
    icon = models.CharField(max_length=10, default="🎯")
    color = models.CharField(max_length=20, default="blue")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.name}: ${self.current}/${self.target}"

    @property
    def percentage_complete(self):
        if self.target > 0:
            return (self.current / self.target) * 100
        return 0

    @property
    def remaining(self):
        return self.target - self.current

    @property
    def is_completed(self):
        return self.current >= self.target
    




