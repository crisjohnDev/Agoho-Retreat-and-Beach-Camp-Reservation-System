
from datetime import date

from django.db.models import Q

from .models import Room, Reservation


# =========================================================
# AI ASSISTANT
# =========================================================

def generate_ai_response(user, message):

    message = message.lower().strip()

    # =====================================================
    # GET USER RESERVATIONS
    # =====================================================

    reservations = Reservation.objects.filter(
        customer=user
    ).select_related("room")


    # =====================================================
    # GREETING
    # =====================================================

    if any(word in message for word in [
        "hello",
        "hi",
        "hey",
        "good morning",
        "good afternoon",
        "good evening",
    ]):

        return (
            f"Hello {user.username}! 👋 "
            "I'm your reservation assistant. "
            "I can help you find rooms, check prices, "
            "check availability, and view your reservations."
        )


    # =====================================================
    # HELP
    # =====================================================

    if "help" in message or "what can you do" in message:

        return (
            "I can help you with:\n\n"
            "• Available rooms\n"
            "• Room prices\n"
            "• Room capacity\n"
            "• Rooms and cottages\n"
            "• Your reservations\n"
            "• Reservation status\n"
            "• Check-in and check-out dates\n"
            "• Reservation total amount\n\n"
            "Try asking: "
            "\"What rooms are available?\""
        )


    # =====================================================
    # AVAILABLE ROOMS
    # =====================================================

    if (
        "available room" in message
        or "available rooms" in message
        or "what rooms are available" in message
        or "show available" in message
    ):

        rooms = Room.objects.filter(
            status="AVAILABLE"
        ).order_by("price")

        if not rooms.exists():

            return (
                "I'm sorry, there are currently "
                "no available rooms."
            )

        response = "Here are the available rooms:\n\n"

        for room in rooms:

            response += (
                f"• {room.name}\n"
                f"  Type: {room.get_type_display()}\n"
                f"  Price: ₱{room.price} per night\n"
                f"  Capacity: {room.capacity} guests\n\n"
            )

        return response.strip()


    # =====================================================
    # COTTAGES
    # =====================================================

    if "cottage" in message or "cottages" in message:

        cottages = Room.objects.filter(
            type="COTTAGE",
            status="AVAILABLE"
        ).order_by("price")

        if not cottages.exists():

            return "There are currently no available cottages."

        response = "Available cottages:\n\n"

        for room in cottages:

            response += (
                f"• {room.name}\n"
                f"  ₱{room.price} per night\n"
                f"  Capacity: {room.capacity} guests\n"
            )

            if room.description:
                response += (
                    f"  {room.description}\n"
                )

            response += "\n"

        return response.strip()


    # =====================================================
    # CHEAPEST ROOM
    # =====================================================

    if any(word in message for word in [
        "cheapest",
        "lowest price",
        "least expensive",
        "most affordable",
    ]):

        room = Room.objects.filter(
            status="AVAILABLE"
        ).order_by("price").first()

        if not room:

            return "There are currently no available rooms."

        return (
            f"The most affordable available option is "
            f"{room.name}.\n\n"
            f"Type: {room.get_type_display()}\n"
            f"Price: ₱{room.price} per night\n"
            f"Capacity: {room.capacity} guests"
        )


    # =====================================================
    # MOST EXPENSIVE ROOM
    # =====================================================

    if any(word in message for word in [
        "most expensive",
        "highest price",
        "premium room",
    ]):

        room = Room.objects.filter(
            status="AVAILABLE"
        ).order_by("-price").first()

        if not room:

            return "There are currently no available rooms."

        return (
            f"The highest-priced available option is "
            f"{room.name}.\n\n"
            f"Type: {room.get_type_display()}\n"
            f"Price: ₱{room.price} per night\n"
            f"Capacity: {room.capacity} guests"
        )


    # =====================================================
    # ROOM CAPACITY
    # =====================================================

    if any(word in message for word in [
        "capacity",
        "how many people",
        "how many guests",
        "can accommodate",
    ]):

        rooms = Room.objects.filter(
            status="AVAILABLE"
        ).order_by("-capacity")

        if not rooms.exists():

            return "There are currently no available rooms."

        response = "Available rooms by capacity:\n\n"

        for room in rooms:

            response += (
                f"• {room.name} — "
                f"up to {room.capacity} guests\n"
            )

        return response.strip()


    # =====================================================
    # MY RESERVATIONS
    # =====================================================

    if (
        "my reservation" in message
        or "my reservations" in message
        or "my booking" in message
        or "my bookings" in message
    ):

        if not reservations.exists():

            return (
                "You don't have any reservations yet."
            )

        response = "Your reservations:\n\n"

        for reservation in reservations:

            response += (
                f"• Reservation #{reservation.id}\n"
                f"  Room: {reservation.room.name}\n"
                f"  Check-in: {reservation.check_in}\n"
                f"  Check-out: {reservation.check_out}\n"
                f"  Status: {reservation.get_status_display()}\n"
                f"  Payment: {reservation.get_payment_status_display()}\n"
                f"  Total: ₱{reservation.total_amount}\n\n"
            )

        return response.strip()


    # =====================================================
    # NEXT RESERVATION
    # =====================================================

    if (
        "next reservation" in message
        or "upcoming reservation" in message
        or "upcoming booking" in message
    ):

        reservation = (
            reservations
            .filter(
                check_in__gte=date.today(),
                status__in=["PENDING", "CONFIRMED"]
            )
            .order_by("check_in")
            .first()
        )

        if not reservation:

            return "You don't have any upcoming reservations."

        return (
            f"Your next reservation is "
            f"Reservation #{reservation.id}.\n\n"
            f"Room: {reservation.room.name}\n"
            f"Check-in: {reservation.check_in}\n"
            f"Check-out: {reservation.check_out}\n"
            f"Guests: {reservation.adults} adults, "
            f"{reservation.children} children\n"
            f"Status: {reservation.get_status_display()}\n"
            f"Payment: {reservation.get_payment_status_display()}\n"
            f"Total: ₱{reservation.total_amount}"
        )


    # =====================================================
    # RESERVATION STATUS
    # =====================================================

    if (
        "reservation status" in message
        or "booking status" in message
        or "status of my reservation" in message
    ):

        if not reservations.exists():

            return "You don't have any reservations."

        reservation = reservations.order_by(
            "-created_at"
        ).first()

        return (
            f"Your latest reservation is "
            f"Reservation #{reservation.id}.\n\n"
            f"Room: {reservation.room.name}\n"
            f"Reservation status: "
            f"{reservation.get_status_display()}\n"
            f"Payment status: "
            f"{reservation.get_payment_status_display()}"
        )


    # =====================================================
    # PAYMENT
    # =====================================================

    if any(word in message for word in [
        "payment",
        "paid",
        "unpaid",
        "receipt",
    ]):

        if not reservations.exists():

            return "You don't have any reservations yet."

        reservation = reservations.order_by(
            "-created_at"
        ).first()

        return (
            f"For your latest reservation "
            f"(#{reservation.id}):\n\n"
            f"Total amount: ₱{reservation.total_amount}\n"
            f"Payment status: "
            f"{reservation.get_payment_status_display()}"
        )


    # =====================================================
    # CHECK-IN
    # =====================================================

    if (
        "check in" in message
        or "check-in" in message
        or "checkin" in message
    ):

        if not reservations.exists():

            return "You don't have any reservations yet."

        reservation = reservations.order_by(
            "-check_in"
        ).first()

        return (
            f"Your check-in date for "
            f"Reservation #{reservation.id} is "
            f"{reservation.check_in}."
        )


    # =====================================================
    # CHECK-OUT
    # =====================================================

    if (
        "check out" in message
        or "check-out" in message
        or "checkout" in message
    ):

        if not reservations.exists():

            return "You don't have any reservations yet."

        reservation = reservations.order_by(
            "-check_out"
        ).first()

        return (
            f"Your check-out date for "
            f"Reservation #{reservation.id} is "
            f"{reservation.check_out}."
        )


    # =====================================================
    # DEFAULT RESPONSE
    # =====================================================

    return (
        "I'm not sure how to answer that yet. "
        "You can ask me about available rooms, "
        "room prices, cottages, room capacity, "
        "or your reservations."
    )

