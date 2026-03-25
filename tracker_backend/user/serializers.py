from django.contrib.auth.models import User
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import Category, Expense, Income, Budget, Transaction, Budget, UserProfile


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class ExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expense
        fields = '__all__'


class IncomeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Income
        fields = '__all__'


class BudgetSerializer(serializers.ModelSerializer):
    percentage_used = serializers.ReadOnlyField()
    remaining = serializers.ReadOnlyField()
    is_over_budget = serializers.ReadOnlyField()
    category_name = serializers.CharField(source='category.name', read_only=True)
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())


    class Meta:
        model = Budget
        fields = ['id', 'category', 'category_name', 'amount', 'spent', 'icon', 'percentage_used', 'remaining', 'is_over_budget', 'created_at', 'updated_at']   
        read_only_fields = ['spent', 'created_at', 'updated_at']
    
    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Budget amount must be greated than 0")
        return value 
        
    def create(self, validated_data):
        validated_data['user']= self.context['request'].user
        return super().create(validated_data)


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'
        read_only_fields =['user']


class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True) 
    email = serializers.EmailField(source='user.email', read_only=True)
    first_name = serializers.CharField(source='user.first_name', required=False)
    last_name = serializers.CharField(source='user.last_name', required=False)
    # phone = serializers.CharField(source='phone-number', required=False, allow_blank=True)
    avatar = serializers.SerializerMethodField()
    avatar_upload = serializers.ImageField(write_only=True, required=False, allow_null=True)

    class Meta :
        model = UserProfile
        fields = [
        'id', 'username', 'email', 'first_name', 'last_name',
        'phone_number', 'bio', 'avatar', 'avatar_upload',
        'date_of_birth', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_avatar(self,obj):
        try:
            if obj.avatar:
                return obj.avatar.url
        except Exception:
            pass
        return None

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', {})

        avatar_upload = validated_data.pop('avatar_upload', None)
        if avatar_upload:
            instance.avatar = avatar_upload
        
        if 'first_name' in user_data:
            instance.user.first_name = user_data['first_name']
        if 'last_name' in user_data:
            instance.user.last_name = user_data['last_name']
        instance.user.save()
        
        return super().update(instance, validated_data)


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Extends JWT tokens to include username & email
    """
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username
        token['email'] = user.email
        return token
    


class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True)
    confirm_password = serializers.CharField(required=True, write_only=True)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Current password is incorrect")
        return value

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match"})
        
        validate_password(data['new_password'], self.context['request'].user)
        return data

    def save(self):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user
    

class AnalyticsSerializer(serializers.Serializer):
    total_income = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_expenses = serializers.DecimalField(max_digits=10, decimal_places=2)
    balance = serializers.DecimalField(max_digits=10, decimal_places=2)
    spending_rate = serializers.FloatField()
    budget_adherence = serializers.FloatField()
    avg_monthly_expenses = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_budget = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_spent = serializers.DecimalField(max_digits=10, decimal_places=2)
    categories_on_track = serializers.IntegerField()
    categories_over_budget = serializers.IntegerField()
