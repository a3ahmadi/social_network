from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework.validators import UniqueValidator
from .models import Profile
from apps.follows.models import Follow

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password_1 = serializers.CharField(required=True, write_only=True)
    password_2 = serializers.CharField(required=True, write_only=True)

    class Meta:
        model = User
        fields = (
            'email', 'username', 'password_1', 'password_2',
            'first_name', 'last_name'
        )
        extra_kwargs = {
            'first_name' : {'required': False},
            'last_name' : {'required': False},
        }

    def validate(self, attrs):
        if attrs['password_1'] != attrs['password_2']:
            raise serializers.ValidationError({
                'password': 'password did not match.'
            })
        return super(RegisterSerializer, self).validate(attrs)
    
    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name = validated_data.get('first_name', ''),
            last_name = validated_data.get('last_name', ''),
            password=validated_data['password_1'],
        )
        return user
    

class ProfileSerializer(serializers.ModelSerializer):
    is_owner = serializers.SerializerMethodField()
    username = serializers.SerializerMethodField()
    is_following = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        exclude = [
            'updated_at', 'user'
            ]
        
    def get_is_owner(self, obj):
        request = self.context.get("request")
        return obj.user == request.user
    
    def get_username(self, obj):
        return obj.user.username
    
    def get_is_following(self, obj):
        request = self.context.get("request")
        return Follow.objects.filter(follower=request.user, following=obj.user).exists()
    
