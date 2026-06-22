import uuid
from typing import Optional
from fastapi import APIRouter, Depends, Request
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.rate_limiter import limiter
from app.models.planner import PlannerLead
from app.models.base import UserRole
from app.core.security import require_role
from pydantic import BaseModel

router = APIRouter(tags=["Planner"])


class ActivitySchema(BaseModel):
    time: str
    desc: str
    detail: Optional[str] = None
    cost: int = 0


class DayCostSchema(BaseModel):
    housing: int = 0
    food: int = 0
    activities: int = 0
    transport: int = 0


class DaySchema(BaseModel):
    title: str
    region: str
    icon: Optional[str] = None
    activities: list[ActivitySchema] = []
    tip: Optional[str] = None
    dayCost: int = 0
    costs: DayCostSchema = DayCostSchema()


class PlannerLeadCreate(BaseModel):
    duration: str
    budget: int
    style: str
    destinations: list[str]
    travelers: int = 2
    season: str = "any"
    transport: str = "shuttle"
    accommodation: str = "mid"
    notes: Optional[str] = None
    estimated_cost: Optional[float] = None
    total_days: Optional[int] = None
    itinerary: Optional[list[DaySchema]] = None


class PlannerLeadResponse(BaseModel):
    id: str
    duration: str
    budget: int
    style: str
    destinations: list[str]
    travelers: int
    season: str
    transport: str
    accommodation: str
    notes: Optional[str] = None
    estimated_cost: Optional[float] = None
    total_days: Optional[int] = None
    status: str
    created_at: str
    updated_at: str


@router.post("/leads", status_code=201)
@limiter.limit("5/minute")
async def create_planner_lead(
    data: PlannerLeadCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    lead = PlannerLead(
        duration=data.duration,
        budget=data.budget,
        style=data.style,
        destinations=data.destinations,
        travelers=data.travelers,
        season=data.season,
        transport=data.transport,
        accommodation=data.accommodation,
        notes=data.notes,
        estimated_cost=data.estimated_cost,
        total_days=data.total_days,
        itinerary=[d.model_dump() for d in (data.itinerary or [])],
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent", "")[:500],
    )
    db.add(lead)
    await db.commit()
    await db.refresh(lead)

    return {"id": str(lead.id), "status": "created"}


@router.get("/leads", response_model=list[PlannerLeadResponse])
async def list_planner_leads(
    db: AsyncSession = Depends(get_db),
    _=Depends(require_role(UserRole.SUPER_ADMIN)),
):
    result = await db.execute(
        select(PlannerLead).order_by(desc(PlannerLead.created_at))
    )
    leads = result.scalars().all()
    return [
        {
            "id": str(l.id),
            "duration": l.duration,
            "budget": l.budget,
            "style": l.style,
            "destinations": l.destinations,
            "travelers": l.travelers,
            "season": l.season,
            "transport": l.transport,
            "accommodation": l.accommodation,
            "notes": l.notes,
            "estimated_cost": l.estimated_cost,
            "total_days": l.total_days,
            "status": l.status,
            "created_at": l.created_at.isoformat() if l.created_at else "",
            "updated_at": l.updated_at.isoformat() if l.updated_at else "",
        }
        for l in leads
    ]


@router.get("/leads/{lead_id}", response_model=PlannerLeadResponse)
async def get_planner_lead(
    lead_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_role(UserRole.SUPER_ADMIN)),
):
    result = await db.execute(select(PlannerLead).where(PlannerLead.id == lead_id))
    lead = result.scalar_one_or_none()
    if not lead:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Lead not found")

    return {
        "id": str(lead.id),
        "duration": lead.duration,
        "budget": lead.budget,
        "style": lead.style,
        "destinations": lead.destinations,
        "travelers": lead.travelers,
        "season": lead.season,
        "transport": lead.transport,
        "accommodation": lead.accommodation,
        "notes": lead.notes,
        "estimated_cost": lead.estimated_cost,
        "total_days": lead.total_days,
        "status": lead.status,
        "created_at": lead.created_at.isoformat() if lead.created_at else "",
        "updated_at": lead.updated_at.isoformat() if lead.updated_at else "",
    }
