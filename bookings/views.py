from datetime import datetime, time, timedelta
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils.dateparse import parse_datetime, parse_date
from django.utils import timezone

from .models import Room, Booking
from .serializers import RoomSerializer, BookingSerializer
from .swagger_docs import (
    booking_cancel_schema,
    booking_availability_schema,
    room_availability_schema,
    room_free_slots_schema,
)


class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.all().order_by("name")
    serializer_class = RoomSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    @room_availability_schema
    @action(detail=True, methods=["get"], url_path="availability", permission_classes=[permissions.AllowAny])
    def availability(self, request, pk=None):
        """
        Checks if a given room is available for the provided interval.
        """
        room = self.get_object()
        start_at = parse_datetime(request.query_params.get("start_at"))
        end_at = parse_datetime(request.query_params.get("end_at"))

        if not (start_at and end_at and end_at > start_at):
            return Response({"detail": "Invalid or missing start_at/end_at."}, status=status.HTTP_400_BAD_REQUEST)

        exists = Booking.objects.filter(
            room=room,
            status__in=[Booking.Status.PENDING, Booking.Status.CONFIRMED],
            start_at__lt=end_at,
            end_at__gt=start_at,
        ).exists()

        return Response({"available": not exists})

    @room_free_slots_schema
    @action(detail=True, methods=["get"], url_path="free-slots", permission_classes=[permissions.AllowAny])
    def free_slots(self, request, pk=None):
        """
        Returns free time slots for a given room and date.
        """
        room = self.get_object()
        day = parse_date(request.query_params.get("date") or "")
        if not day:
            return Response({"detail": "Parameter 'date' (YYYY-MM-DD) is required."}, status=status.HTTP_400_BAD_REQUEST)

        def _parse_time(s, fallback):
            try:
                h, m = map(int, (s or "").split(":"))
                return time(h, m)
            except Exception:
                return fallback

        open_t = _parse_time(request.query_params.get("open"), time(8, 0))
        close_t = _parse_time(request.query_params.get("close"), time(20, 0))

        try:
            slot_delta = timedelta(minutes=int(request.query_params.get("slot", "30")))
        except ValueError:
            slot_delta = timedelta(minutes=30)

        day_start = timezone.make_aware(datetime.combine(day, open_t))
        day_end = timezone.make_aware(datetime.combine(day, close_t))

        if day_end <= day_start:
            return Response({"detail": "Invalid open/close window."}, status=status.HTTP_400_BAD_REQUEST)

        bookings = list(
            Booking.objects.filter(
                room=room,
                status__in=[Booking.Status.PENDING, Booking.Status.CONFIRMED],
                start_at__lt=day_end,
                end_at__gt=day_start,
            ).order_by("start_at")
        )

        cursor = day_start
        free = []
        for b in bookings:
            if b.start_at > cursor and (b.start_at - cursor) >= slot_delta:
                free.append({"start": cursor.isoformat(), "end": b.start_at.isoformat()})
            cursor = max(cursor, b.end_at)
        if cursor < day_end and (day_end - cursor) >= slot_delta:
            free.append({"start": cursor.isoformat(), "end": day_end.isoformat()})

        return Response({"free": free})
        

class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all().order_by("-created_at")
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    @booking_cancel_schema
    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated])
    def cancel(self, request, pk=None):
        booking = self.get_object()
        if booking.status == Booking.Status.CANCELLED:
            return Response({"detail": "Booking is already cancelled"}, status=400)
        booking.status = Booking.Status.CANCELLED
        booking.save()
        return Response({"detail": "Booking cancelled successfully"}, status=200)

    @booking_availability_schema
    @action(detail=False, methods=["get"], url_path="availability", permission_classes=[permissions.AllowAny])
    def availability(self, request):
        """
        GET /api/bookings/availability/?room=1&start_at=...&end_at=...
        """
        try:
            room_id = int(request.query_params.get("room"))
            start_at = parse_datetime(request.query_params.get("start_at"))
            end_at = parse_datetime(request.query_params.get("end_at"))
        except Exception:
            return Response({"detail": "Invalid parameters"}, status=400)

        if not (room_id and start_at and end_at and end_at > start_at):
            return Response({"detail": "Specify room, start_at, end_at (ISO), and a valid interval."}, status=400)

        exists = Booking.objects.filter(
            room_id=room_id,
            status__in=[Booking.Status.PENDING, Booking.Status.CONFIRMED],
            start_at__lt=end_at,
            end_at__gt=start_at,
        ).exists()

        return Response({"available": not exists})

    



        


