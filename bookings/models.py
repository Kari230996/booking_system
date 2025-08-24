from enum import unique
from django.db import models, transaction
from django.core.exceptions import ValidationError
from django.db.models import F, Q, Func, constraints, expressions
from django.contrib.postgres.fields import DateTimeRangeField, RangeOperators
from django.contrib.postgres.constraints import ExclusionConstraint
from django.conf import settings

class TsTzRange(Func):
    function = "tstzrange"
    output_field = DateTimeRangeField()

    def __init__(self, start, end, bounds="[)"):
        super().__init__(start, end, bounds=bounds)

class Room(models.Model):
    name = models.CharField(max_length=120, unique=True)
    capacity = models.PositiveBigIntegerField(default=1)

    def __str__(self):
        return self.name

class Booking(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        CONFIRMED = "confirmed", "Confirmed"
        CANCELLED = "cancelled", "Cancelled"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="bookings"
    )
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="bookings")
    start_at = models.DateTimeField()
    end_at = models.DateTimeField()
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.CONFIRMED)
    customer_name = models.CharField(max_length=120, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    
    def clean(self): 
        if self.end_at <= self.start_at:
            raise ValidationError({"end_at": "End date must be after start date"})

        conflict = Booking.objects.filter(
            room=self.room,
            status__in=[self.Status.PENDING, self.Status.CONFIRMED],
            start_at__lt=self.end_at,
            end_at__gt=self.start_at,
        ).exclude(pk=self.pk).exists()

        if conflict:
            raise ValidationError("A booking already exists for this time interval.")

    def save(self, *args, **kwargs):
        with transaction.atomic():
            self.full_clean()
            super().save(*args, **kwargs)

    
    class Meta:
        indexes = []
        constraints = [
            ExclusionConstraint(
                name="exclude_overlapping_bookings",
                expressions=[
                    (TsTzRange("start_at", "end_at"), RangeOperators.OVERLAPS),
                    (F("room_id"), RangeOperators.EQUAL)
                ],
                condition=Q(status__in=["pending", "confirmed"])
            )
        ]
    
    def __str__(self):
        return f"{self.room} | {self.start_at:%Y-%m-%d %H:%M}–{self.end_at:%H:%M} | {self.status}"
    
    
    
    


