from rest_framework import serializers
from features.xero.models import ChartOfAccount

class ChartOfAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChartOfAccount
        fields = '__all__'
