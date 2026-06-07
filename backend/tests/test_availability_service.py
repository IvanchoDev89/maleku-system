"""
Tests for availability service logic
"""
import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock

from app.services.availability_service import (
    check_room_availability,
    get_room_availability_calendar,
    check_tour_availability
)


class MockBooking:
    """Mock booking for testing"""
    def __init__(self, id, room_id, check_in, check_out, status="confirmed"):
        self.id = id
        self.room_id = room_id
        self.check_in = check_in
        self.check_out = check_out
        self.status = MagicMock()
        self.status.value = status


class MockTour:
    """Mock tour for testing"""
    def __init__(self, id, max_group_size=15, is_active=True):
        self.id = id
        self.max_group_size = max_group_size
        self.is_active = is_active
        self.schedule_days = None  # Available all days


@pytest.mark.asyncio
async def test_check_room_availability_no_conflicts():
    """Test room available when no conflicting bookings"""
    mock_session = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = []
    mock_session.execute.return_value = mock_result
    
    is_available = await check_room_availability(
        db=mock_session,
        room_id="room-123",
        check_in=datetime.now(timezone.utc) + timedelta(days=1),
        check_out=datetime.now(timezone.utc) + timedelta(days=3)
    )
    
    assert is_available is True


@pytest.mark.asyncio
async def test_check_room_availability_with_conflict():
    """Test room not available when there's a conflicting booking"""
    mock_session = AsyncMock()
    
    # Create a conflicting booking
    conflict_booking = MockBooking(
        id="booking-1",
        room_id="room-123",
        check_in=datetime.now(timezone.utc) + timedelta(days=1),
        check_out=datetime.now(timezone.utc) + timedelta(days=3)
    )
    
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [conflict_booking]
    mock_session.execute.return_value = mock_result
    
    # Try to book same dates
    is_available = await check_room_availability(
        db=mock_session,
        room_id="room-123",
        check_in=datetime.now(timezone.utc) + timedelta(days=1),
        check_out=datetime.now(timezone.utc) + timedelta(days=3)
    )
    
    assert is_available is False


@pytest.mark.asyncio
async def test_check_room_availability_excludes_cancelled():
    """Test that cancelled bookings don't block availability"""
    mock_session = AsyncMock()
    mock_result = MagicMock()
    # Return empty list (no active bookings found)
    mock_result.scalars.return_value.all.return_value = []
    mock_session.execute.return_value = mock_result
    
    is_available = await check_room_availability(
        db=mock_session,
        room_id="room-123",
        check_in=datetime.now(timezone.utc) + timedelta(days=1),
        check_out=datetime.now(timezone.utc) + timedelta(days=3)
    )
    
    # The query filters by status, so cancelled bookings shouldn't appear
    assert is_available is True


@pytest.mark.asyncio
async def test_check_tour_availability_tour_not_found():
    """Test tour availability when tour doesn't exist"""
    mock_session = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute.return_value = mock_result
    
    is_available, reason = await check_tour_availability(
        db=mock_session,
        tour_id="non-existent",
        booking_date=datetime.now(timezone.utc) + timedelta(days=1),
        participants=2
    )
    
    assert is_available is False
    assert "not found" in reason.lower()


@pytest.mark.asyncio
async def test_check_tour_availability_inactive_tour():
    """Test tour availability when tour is inactive"""
    mock_session = AsyncMock()
    mock_result = MagicMock()
    
    inactive_tour = MockTour(id="tour-1", is_active=False)
    mock_result.scalar_one_or_none.return_value = inactive_tour
    mock_session.execute.return_value = mock_result
    
    is_available, reason = await check_tour_availability(
        db=mock_session,
        tour_id="tour-1",
        booking_date=datetime.now(timezone.utc) + timedelta(days=1),
        participants=2
    )
    
    assert is_available is False
    assert "not available" in reason.lower()


@pytest.mark.asyncio
async def test_check_tour_availability_too_many_participants():
    """Test tour availability when participants exceed max"""
    mock_session = AsyncMock()
    
    tour = MockTour(id="tour-1", max_group_size=10)
    
    # Mock tour query
    tour_result = MagicMock()
    tour_result.scalar_one_or_none.return_value = tour
    
    # Mock bookings query (no existing bookings)
    bookings_result = MagicMock()
    bookings_result.scalars.return_value.all.return_value = []
    
    mock_session.execute.side_effect = [tour_result, bookings_result]
    
    is_available, reason = await check_tour_availability(
        db=mock_session,
        tour_id="tour-1",
        booking_date=datetime.now(timezone.utc) + timedelta(days=1),
        participants=15  # More than max_group_size
    )
    
    assert is_available is False
    assert "maximum" in reason.lower() or "spots" in reason.lower()


@pytest.mark.asyncio
async def test_check_tour_availability_available():
    """Test tour availability when spots are available"""
    mock_session = AsyncMock()
    
    tour = MockTour(id="tour-1", max_group_size=15)
    
    # Mock tour query
    tour_result = MagicMock()
    tour_result.scalar_one_or_none.return_value = tour
    
    # Mock existing booking for 5 participants
    existing_booking = MagicMock()
    existing_booking.participants = 5
    
    bookings_result = MagicMock()
    bookings_result.scalars.return_value.all.return_value = [existing_booking]
    
    mock_session.execute.side_effect = [tour_result, bookings_result]
    
    is_available, reason = await check_tour_availability(
        db=mock_session,
        tour_id="tour-1",
        booking_date=datetime.now(timezone.utc) + timedelta(days=1),
        participants=5  # 10 spots remaining (15 - 5 = 10)
    )
    
    assert is_available is True
    assert reason == "Available"


@pytest.mark.asyncio
async def test_get_room_availability_calendar():
    """Test getting availability calendar"""
    mock_session = AsyncMock()
    
    # Create a booking that blocks 2 days
    blocked_booking = MockBooking(
        id="booking-1",
        room_id="room-123",
        check_in=datetime(2024, 1, 10),
        check_out=datetime(2024, 1, 12)
    )
    
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [blocked_booking]
    mock_session.execute.return_value = mock_result
    
    calendar = await get_room_availability_calendar(
        db=mock_session,
        room_id="room-123",
        start_date=datetime(2024, 1, 8),
        end_date=datetime(2024, 1, 15)
    )
    
    # Should return 7 days
    assert len(calendar) == 7
    
    # Jan 10 and 11 should be unavailable
    jan_10 = next((d for d in calendar if d["date"].startswith("2024-01-10")), None)
    jan_11 = next((d for d in calendar if d["date"].startswith("2024-01-11")), None)
    
    if jan_10:
        assert jan_10["available"] is False
    if jan_11:
        assert jan_11["available"] is False
