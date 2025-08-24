from drf_spectacular.utils import (
    extend_schema, OpenApiParameter, OpenApiTypes, OpenApiExample, OpenApiResponse
)
from .serializers import BookingSerializer

# --- BOOKINGS ---

booking_cancel_schema = extend_schema(
    summary="Cancel a booking",
    description="Sets status to `CANCELED`. If already canceled, returns 400.",
    tags=["bookings"],
    responses={
        200: BookingSerializer,
        400: OpenApiResponse(description="Booking already canceled"),
        404: OpenApiResponse(description="Not found"),
    },
    examples=[
        OpenApiExample(
            "Success response",
            value={
                "id": 1, "room": 1, "room_name": "Blue Room",
                "start_at": "2025-08-26T10:00:00Z", "end_at": "2025-08-26T11:00:00Z",
                "status": "CANCELED", "customer_name": "Karina",
                "created_at": "2025-08-24T12:00:00Z"
            },
            response_only=True,
        ),
        OpenApiExample(
            "Already canceled",
            value={"detail": "Booking already canceled."},
            response_only=True,
        ),
    ],
)

booking_availability_schema = extend_schema(
    summary="Check availability (global)",
    description="Checks if a room is available for a given interval.",
    tags=["bookings"],
    parameters=[
        OpenApiParameter(name="room", type=OpenApiTypes.INT, required=True, description="Room ID"),
        OpenApiParameter(name="start_at", type=OpenApiTypes.DATETIME, required=True),
        OpenApiParameter(name="end_at", type=OpenApiTypes.DATETIME, required=True),
    ],
    responses={200: OpenApiTypes.OBJECT, 400: OpenApiResponse(description="Invalid parameters")},
    examples=[
        OpenApiExample("Available", value={"available": True}, response_only=True),
        OpenApiExample("Not available", value={"available": False}, response_only=True),
    ],
)

# --- ROOMS ---

room_availability_schema = extend_schema(
    summary="Room availability for interval",
    description="Returns whether the given room is free for the requested time interval.",
    tags=["rooms"],
    parameters=[
        OpenApiParameter(name="start_at", type=OpenApiTypes.DATETIME, required=True),
        OpenApiParameter(name="end_at", type=OpenApiTypes.DATETIME, required=True),
    ],
    responses={200: OpenApiTypes.OBJECT, 400: OpenApiResponse(description="Invalid parameters")},
    examples=[
        OpenApiExample("Free", value={"available": True}, response_only=True),
        OpenApiExample("Busy", value={"available": False}, response_only=True),
    ],
)

room_free_slots_schema = extend_schema(
    summary="Free time slots for a day",
    description=(
        "Calculates free gaps within a daily working window.\n"
        "- `date` is required (YYYY-MM-DD)\n"
        "- `open`/`close` are optional (HH:MM)\n"
        "- `slot` is the minimal free interval length in minutes"
    ),
    tags=["rooms"],
    parameters=[
        OpenApiParameter(name="date", type=OpenApiTypes.DATE, required=True),
        OpenApiParameter(name="open", type=OpenApiTypes.STR, required=False, description="HH:MM (default 08:00)"),
        OpenApiParameter(name="close", type=OpenApiTypes.STR, required=False, description="HH:MM (default 20:00)"),
        OpenApiParameter(name="slot", type=OpenApiTypes.INT, required=False, description="Minutes (default 30)"),
    ],
    responses={200: OpenApiTypes.OBJECT, 400: OpenApiResponse(description="Invalid parameters")},
    examples=[
        OpenApiExample(
            "Example response",
            value={"free": [
                {"start": "2025-08-26T09:00:00+02:00", "end": "2025-08-26T10:00:00+02:00"},
                {"start": "2025-08-26T11:00:00+02:00", "end": "2025-08-26T12:30:00+02:00"},
            ]},
            response_only=True,
        ),
    ],
)
