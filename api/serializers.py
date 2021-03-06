# -*- coding: utf-8  -*-
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import authenticate
from rest_framework import serializers, exceptions
from rest_framework.authtoken.serializers import AuthTokenSerializer
from activities.models import Activity, Episode
from activities.models import Category as ActivityCategory
from clubs.models import Club
from media.models import Buzz, BuzzView
from niqati.models import Code, Category, Collection, Order

class ModifiedAuthTokenSerializer(AuthTokenSerializer):
    def validate(self, attrs):
        """Allow both usernames and emails."""
        identification = attrs.get('username')
        password = attrs.get('password')

        if identification and password:
            if '@' in identification:
                username = identification.split('@')[0]
            else:
                username = identification

            user = authenticate(username=username, password=password)

            if user:
                if not user.is_active:
                    msg = _('User account is disabled.')
                    raise exceptions.ValidationError(msg)

                # Currently, the app is only available for students.
                try:
                    college = user.common_profile.college
                except (ObjectDoesNotExist, AttributeError):
                    raise exceptions.ValidationError(u"لم تسجل في بوابة إنجاز كطالب!")
            else:
                msg = _('Unable to log in with provided credentials.')
                raise exceptions.ValidationError(msg)
        else:
            msg = _('Must include "username" and "password".')
            raise exceptions.ValidationError(msg)

        attrs['user'] = user
        return attrs

class EpisodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Episode
        fields = ('pk', 'start_datetime', 'end_datetime', 'location')

class ClubSerializer(serializers.ModelSerializer):
    class Meta:
        model = Club
        fields = ('pk', 'name', 'english_name', 'email', 'coordinator', 'gender', 'city')

class ActivityCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityCategory
        fields = ('pk', 'ar_name')

class ActivitySerializer(serializers.ModelSerializer):
    primary_club = ClubSerializer(read_only=True)
    category = ActivityCategorySerializer(read_only=True)
    secondary_clubs = ClubSerializer(many=True, read_only=True)
    episode_set = EpisodeSerializer(many=True, read_only=True)
    class Meta:
        model = Activity
        fields = ('pk', 'name', 'primary_club', 'secondary_clubs', 'public_description', 'episode_set', 'gender', 'category')

class BuzzSerializer(serializers.ModelSerializer):
    class Meta:
        model = Buzz
        fields = ('pk', 'title', 'body', 'image', 'is_push')

class BuzzViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = BuzzView
        fields = ('pk', 'viewer', 'buzz', 'off_date')

class NiqatiActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Activity
        fields = ('name',)


class NiqatiEpisodeSerializer(serializers.ModelSerializer):
    activity = NiqatiActivitySerializer(read_only=True)
    class Meta:
        model = Episode
        fields = ('activity',)

class OrderSerializer(serializers.ModelSerializer):
    episode = NiqatiEpisodeSerializer(read_only=True)
    class Meta:
        model = Order
        fields = ('episode',)

class NiqatiCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('ar_label',)

class CollectionSerializer(serializers.ModelSerializer):
    order = OrderSerializer(read_only=True)
    category = NiqatiCategorySerializer(read_only=True)
    class Meta:
        model = Collection
        fields = ('category', 'order')

class CodeSerializer(serializers.ModelSerializer):
    collection = CollectionSerializer(read_only=True)
    class Meta:
        model = Code
        fields = ('pk', 'points', 'redeem_date', 'collection')
