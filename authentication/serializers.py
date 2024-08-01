from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from .models import CustomUser, Company
from django.core.validators import validate_email
from django.core.exceptions import ValidationError



class UserRegisterSerializer(serializers.ModelSerializer):
    # email = serializers.EmailField(required=True,validators=[UniqueValidator(queryset=CustomUser.objects.all())])
    email = serializers.EmailField(required=True)
    username = serializers.CharField(max_length=20, required=True, allow_blank=False)
    password = serializers.CharField(write_only=True, required=True)
    confirm_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'first_name', 'last_name', 'password', 'confirm_password',
                  'email', 'role','company')
        
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
            'confirm_password': {'read_only': True},
            'id': {'read_only': True},
            'role': {'required': True}
        }







class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ('id', 'name')

class CustomUserSerializer(serializers.ModelSerializer):
    company = CompanySerializer()  # Nested serializer for Company

    class Meta:
        model = CustomUser
        fields = '__all__'








class RegisterSerializer(serializers.ModelSerializer):
    # email = serializers.EmailField(required=True,validators=[UniqueValidator(queryset=CustomUser.objects.all())])
    email = serializers.EmailField(required=True)
    username = serializers.CharField(max_length=20, required=True, allow_blank=False)
    password = serializers.CharField(write_only=True, required=True)
    confirm_password = serializers.CharField(write_only=True, required=True)


    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'first_name', 'last_name', 'password', 'confirm_password',
                  'email', 'role', 'is_true')
        
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
            'confirm_password': {'read_only': True},
            'id': {'read_only': True},
            'role': {'required': True}
        }


    def validate_password(self, value):
        # Custom validation logic for field1
        if len(value) < 7:
            raise serializers.ValidationError("password must have at least 7 characters.")
        
        # Return the validated value
        return value

    # Object Level Validation
    def validate(self, data):
        user_name = data.get('username')
        email = data.get('email')
        if CustomUser.objects.filter(username__iexact=user_name).exists() and CustomUser.objects.filter(
                email__iexact=email).exists():
            raise serializers.ValidationError("User Name and email must be unique")
        if CustomUser.objects.filter(username__iexact=user_name).exists():
            raise serializers.ValidationError("User Name already taken")
        if CustomUser.objects.filter(email__iexact=email).exists():
            raise serializers.ValidationError("Email already exist")
        return data
    
   

class RegisterUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        fields = ('username', 'first_name', 'last_name', 'password', 'email', 'role', 'company', 'is_true')
       
        extra_kwargs = {
            'username': {'required': False},
            'password': {'required': False},
        }

class RegisterGetSerializer(serializers.ModelSerializer):

     class Meta:
        model = CustomUser
        fields = ('id', 'username', 'first_name', 'last_name',
                  'email', 'role', 'company')
        
        # depth = 1


class UserSerializer(serializers.ModelSerializer):
    email = serializers.CharField(required=True) 

    class Meta:
        model = CustomUser
        fields = ["email", "password"]
        extra_kwargs = {
            'password': {'write_only': True}
        }

class CompanySerializer(serializers.ModelSerializer):

    class Meta:
        model = Company
        fields = '__all__'

class SendForgotEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

class ChangePasswordSerializer(serializers.Serializer):
    password = serializers.CharField(max_length=200, required=True)
    confirm_password = serializers.CharField(max_length=200, required=True)



# 
    # ________________________________________________________code_by_davinder_rajput_______________________________________________



from invoice.models import Transaction, Item, Calculation, CloseDate, CalculationMonths, ArrGracePeriod



class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'

class GetAllUserRoleSerializer(serializers.ModelSerializer):
    transactions = TransactionSerializer(many=True, read_only=True)  # Include this line

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'email_verified', 'forget_password_token', 'role', 'company', 'transactions']





class CompanyUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ('id', 'name')





class UserUpdateSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(required=False)
    company = CompanySerializer(read_only=True)

    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'first_name', 'last_name', 'email', 'role', 'company', 'company_name', 'is_true')
        extra_kwargs = {
            'username': {'required': False},
            'first_name': {'required': False},
            'last_name': {'required': False},
            'email': {'required': False},
            'role': {'required': False},
            'company': {'required': False},
        }






        

    # def update(self, instance, validated_data):
    #     company_name = validated_data.pop('company_name', None)
        
    #     if company_name:
    #         try:
    #             # Check if a company with the given name already exists
    #             existing_company = Company.objects.get(name=company_name)
    #             # If the existing company is not the same as the instance being updated,
    #             # it means a company with this name already exists, so we should not proceed.
    #             if existing_company != instance.company:
    #                 # Raise an exception or handle the case as per your requirement.
    #                 raise ValidationError("Company with this name already exists.")
    #         except Company.DoesNotExist:
    #             pass
        
    #     return super().update(instance, validated_data)    



    def update(self, instance, validated_data):
        company_name = validated_data.pop('company_name', None)
        
        if company_name:
            try:
                company = Company.objects.get(pk=instance.company.pk)
                company.name = company_name
                company.save()
            except Company.DoesNotExist:
                # Handle case where company doesn't exist
                pass
        
        return super().update(instance, validated_data)
  