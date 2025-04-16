from rest_framework import serializers
from .models import Contact, WorkingHours

class WorkingHoursSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkingHours
        fields = ['day_of_week', 'start_time', 'end_time', 'is_active']

class ContactSerializer(serializers.ModelSerializer):
    working_hours = WorkingHoursSerializer(many=True, read_only=True)

    class Meta:
        model = Contact
        fields = ['id', 'phone', 'whatsapp', 'email', 'office_address', 'created_at', 'updated_at', 'working_hours'] 