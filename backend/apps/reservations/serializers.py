from rest_framework import serializers
from django.utils import timezone
from .models import Reservation


class ReservationSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source="user.username")
    total_price_eur = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Reservation
        fields = "__all__"
        read_only_fields = (
            "user",
            "created_at",
            "updated_at",
            "is_deleted",
            "deleted_at",
            "total_price_eur",
        )

    def validate(self, data):
        """
        Глобальная валидация дат и пересечений бронирований.
        """
        start_date = data.get("start_date")
        end_date = data.get("end_date")
        rental_property = data.get("rental_property")

        if start_date and start_date < timezone.now().date():
            raise serializers.ValidationError("Дата начала не может быть в прошлом.")

        if start_date and end_date and end_date < start_date:
            raise serializers.ValidationError("Дата окончания не может быть раньше даты начала.")

        # Проверка пересечений бронирований
        if rental_property and start_date and end_date:
            overlapping = Reservation.objects.filter(
                rental_property=rental_property,
                start_date__lt=end_date,
                end_date__gt=start_date,
                is_deleted=False,
            )
            if self.instance:
                overlapping = overlapping.exclude(pk=self.instance.pk)

            if overlapping.exists():
                raise serializers.ValidationError("Этот объект уже забронирован на выбранные даты.")

        return data