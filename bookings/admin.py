from django.contrib import admin

from .models import Room, Booking


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "capacity")
    search_fields = ("name",)

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("id", "room", "start_at", "end_at", "status", "customer_name")
    list_filter = ("status", "room")
    search_fields = ("customer_name",)
