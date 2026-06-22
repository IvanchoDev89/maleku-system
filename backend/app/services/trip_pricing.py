from datetime import datetime, timezone

from typing import Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import (
    Room,
    Tour,
    Transportation,
    Vehicle,
    BoatEquipment,
    Flight,
    Property,
    Vendor,
)
from app.services.pricing_service import calculate_room_price
from app.core.config import settings


PACKAGE_DISCOUNT_RULES = [
    {
        "name": "hotel_tour_combo",
        "label": "Combo Hotel + Tour 10%",
        "min_items": 2,
        "item_types": ["accommodation", "tour"],
        "same_destination": True,
        "discount_percent": 10,
    },
    {
        "name": "multi_tour",
        "label": "2+ Tours 5% descuento",
        "min_items": 2,
        "item_types": ["tour"],
        "same_destination": False,
        "discount_percent": 5,
    },
    {
        "name": "weekly_stay",
        "label": "7+ noches descuento semanal",
        "min_items": 7,
        "item_types": ["accommodation"],
        "same_destination": False,
        "discount_percent": 5,
    },
    {
        "name": "full_package",
        "label": "Paquete completo (Hotel + Tour + Transporte) 15%",
        "min_item_types": 3,
        "required_types": ["accommodation", "tour", "transport"],
        "discount_percent": 15,
    },
]


async def fetch_item_price(
    db: AsyncSession,
    item_type: str,
    reference_type: str,
    reference_id: UUID,
    quantity: int,
    travelers: int = 1,
    check_date: Optional[datetime] = None,
) -> dict:
    check_date = check_date or datetime.now(timezone.utc)

    if item_type == "accommodation":
        result = await db.execute(select(Room).where(Room.id == reference_id))
        room = result.scalar_one_or_none()
        if not room:
            raise ValueError(f"Room not found: {reference_id}")

        check_in = check_date
        check_out = check_date.replace(hour=0, minute=0, second=0)
        check_out = check_out.replace(day=check_out.day + quantity)

        pricing = calculate_room_price(
            room=room,
            check_in=check_in,
            check_out=check_out,
            guests=travelers,
        )
        unit_price = float(room.price_per_night or 0)
        total = pricing["subtotal"]
        vendor = await _get_vendor_for_property(db, room.property_id)
        commission_rate = (
            vendor.commission_rate if vendor else settings.STRIPE_COMMISSION_RATE
        )

        return {
            "unit_price": unit_price,
            "total_price": round(total, 2),
            "commission_rate": commission_rate,
            "commission_amount": round(total * commission_rate / 100, 2),
            "vendor_payout": round(total * (1 - commission_rate / 100), 2),
            "breakdown": {
                k: pricing[k]
                for k in [
                    "nights",
                    "weekday_nights",
                    "weekend_nights",
                    "weekday_price",
                    "weekend_price",
                    "weekday_total",
                    "weekend_total",
                    "base_subtotal",
                    "extra_guests",
                    "extra_guest_price",
                    "extra_guests_total",
                ]
            },
        }

    if item_type == "tour":
        result = await db.execute(select(Tour).where(Tour.id == reference_id))
        tour = result.scalar_one_or_none()
        if not tour:
            raise ValueError(f"Tour not found: {reference_id}")

        price = float(tour.price or 0)
        unit_price = price
        total = price * quantity
        vendor = await _get_vendor_for_tour(db, tour)
        commission_rate = (
            vendor.commission_rate if vendor else settings.STRIPE_COMMISSION_RATE
        )

        return {
            "unit_price": unit_price,
            "total_price": round(total, 2),
            "commission_rate": commission_rate,
            "commission_amount": round(total * commission_rate / 100, 2),
            "vendor_payout": round(total * (1 - commission_rate / 100), 2),
            "breakdown": {"price_per_person": price, "participants": quantity},
        }

    if item_type in ("transport", "car_rental", "boat"):
        return await _fetch_rental_price(
            db, item_type, reference_type, reference_id, quantity
        )

    if item_type == "flight":
        result = await db.execute(select(Flight).where(Flight.id == reference_id))
        flight = result.scalar_one_or_none()
        if not flight:
            raise ValueError(f"Flight not found: {reference_id}")

        price = float(flight.price or 0)
        unit_price = price
        total = price * quantity
        commission_rate = settings.STRIPE_COMMISSION_RATE

        return {
            "unit_price": unit_price,
            "total_price": round(total, 2),
            "commission_rate": commission_rate,
            "commission_amount": round(total * commission_rate / 100, 2),
            "vendor_payout": round(total * (1 - commission_rate / 100), 2),
            "breakdown": {"price_per_passenger": price, "passengers": quantity},
        }

    return {
        "unit_price": 0,
        "total_price": 0,
        "commission_rate": 0,
        "commission_amount": 0,
        "vendor_payout": 0,
        "breakdown": {},
    }


async def _fetch_rental_price(
    db: AsyncSession,
    item_type: str,
    reference_type: str,
    reference_id: UUID,
    quantity: int,
) -> dict:
    model_map = {
        "transport": (Transportation, "price"),
        "car_rental": (Vehicle, "daily_rate"),
        "boat": (BoatEquipment, "daily_rate"),
    }
    model_info = model_map.get(item_type)
    if not model_info:
        return {
            "unit_price": 0,
            "total_price": 0,
            "commission_rate": 0,
            "commission_amount": 0,
            "vendor_payout": 0,
            "breakdown": {},
        }

    Model, price_field = model_info
    result = await db.execute(select(Model).where(Model.id == reference_id))
    entity = result.scalar_one_or_none()
    if not entity:
        raise ValueError(f"{item_type} not found: {reference_id}")

    unit_price = float(getattr(entity, price_field, 0) or 0)
    total = unit_price * quantity
    vendor_id = getattr(entity, "vendor_id", None)
    commission_rate = settings.STRIPE_COMMISSION_RATE
    if vendor_id:
        v_result = await db.execute(select(Vendor).where(Vendor.id == vendor_id))
        vendor = v_result.scalar_one_or_none()
        if vendor:
            commission_rate = vendor.commission_rate

    return {
        "unit_price": unit_price,
        "total_price": round(total, 2),
        "commission_rate": commission_rate,
        "commission_amount": round(total * commission_rate / 100, 2),
        "vendor_payout": round(total * (1 - commission_rate / 100), 2),
        "breakdown": {f"{price_field}": unit_price, "days": quantity},
    }


async def _get_vendor_for_property(db: AsyncSession, property_id: UUID) -> Vendor:
    result = await db.execute(
        select(Vendor)
        .join(Property, Property.vendor_id == Vendor.id)
        .where(Property.id == property_id)
    )
    return result.scalar_one_or_none()


async def _get_vendor_for_tour(db: AsyncSession, tour: Tour) -> Vendor:
    if tour.vendor_id:
        result = await db.execute(select(Vendor).where(Vendor.id == tour.vendor_id))
        return result.scalar_one_or_none()
    return None


def compute_package_discounts(items: list[dict]) -> list[dict]:
    discounts = []

    item_types = [i.get("item_type") for i in items]
    locations = [i.get("location", "").lower() for i in items]

    for rule in PACKAGE_DISCOUNT_RULES:
        if "min_items" in rule:
            matching = [i for i in items if i.get("item_type") in rule["item_types"]]
            if len(matching) < rule["min_items"]:
                continue
            if rule.get("same_destination") and len(set(l for l in locations if l)) > 1:
                continue
            subtotal = sum(i.get("total_price", 0) for i in matching)
            discount_amount = round(subtotal * rule["discount_percent"] / 100, 2)
            discounts.append(
                {
                    "rule": rule["name"],
                    "label": rule["label"],
                    "discount_percent": rule["discount_percent"],
                    "discount_amount": discount_amount,
                    "applied_to": [i.get("label") for i in matching],
                }
            )

        if "min_item_types" in rule:
            present_types = set(item_types)
            if rule["required_types"] and present_types.issuperset(
                rule["required_types"]
            ):
                subtotal = sum(i.get("total_price", 0) for i in items)
                discount_amount = round(subtotal * rule["discount_percent"] / 100, 2)
                discounts.append(
                    {
                        "rule": rule["name"],
                        "label": rule["label"],
                        "discount_percent": rule["discount_percent"],
                        "discount_amount": discount_amount,
                        "applied_to": [i.get("label") for i in items],
                    }
                )

    return discounts


def compute_summary(items: list[dict], discounts: list[dict]) -> dict:
    subtotal = sum(i.get("total_price", 0) for i in items)
    total_discount = sum(d.get("discount_amount", 0) for d in discounts)
    after_discounts = subtotal - total_discount
    total_commission = sum(i.get("commission_amount", 0) for i in items)
    total_vendor_payout = sum(i.get("vendor_payout", 0) for i in items)
    platform_revenue = total_commission

    return {
        "subtotal": round(subtotal, 2),
        "discounts": discounts,
        "total_discount": round(total_discount, 2),
        "after_discounts": round(after_discounts, 2),
        "total_commission": round(total_commission, 2),
        "total_vendor_payout": round(total_vendor_payout, 2),
        "platform_revenue": round(platform_revenue, 2),
        "grand_total": round(after_discounts, 2),
        "items_count": len(items),
        "currency": "USD",
    }
