from rest_framework import serializers

from core.models import (
    BankInfo,
    BankAccountInfo,
    BankAccountRequest,
)

class BankInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankInfo
        fields = '__all__'


class BankAccountInfoSerializer(serializers.ModelSerializer):
    bank_info = BankInfoSerializer(source="bank", many=False, read_only=True)

    class Meta:
        model = BankAccountInfo
        fields = '__all__'


class BankAccountRequestSerializer(serializers.ModelSerializer):
    state_display = serializers.SerializerMethodField()
    full_name= serializers.CharField(source="employee.full_name", read_only=True)
    bank_name = serializers.SerializerMethodField()

    class Meta:
        model = BankAccountRequest
        fields = (
            "id",
            "full_name",
            "state_display",
            "bank_name",
            "org",
            "sub_org",
            "salbar",
            "employee",
            "bank",
            "number",
            "state",
            "bank_account",
            "created_at",
        )

    def get_state_display(self, obj):
        return obj.state_display

    def get_full_name(self, obj):
        return obj.full_name

    def get_bank_name(self, obj):
        return obj.bank_name
