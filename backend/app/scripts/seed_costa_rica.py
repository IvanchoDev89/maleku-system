"""
Seed script to populate Costa Rica Travel database with realistic sample data.
Run with: python -m app.scripts.seed_costa_rica
"""

import asyncio
import os
import secrets
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import select, func

from app.core.config import settings
from app.core.security import get_password_hash
from app.models.base import VendorStatus, UserRole
from app.models.property import PropertyType, PropertyCategory
from app.models import (
    Destination,
    Property,
    Tour,
    BlogPost,
    Vendor,
    User,
    TourCategory,
    TourDifficulty,
    BlogPostStatus,
)

engine = create_async_engine(settings.DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


def _get_default_password() -> str:
    """Read SEED_DEFAULT_PASSWORD env var, or generate a random one and print it.

    Never use a hardcoded password. Operators in non-dev environments MUST
    set SEED_DEFAULT_PASSWORD explicitly. In dev/CI, a random password is
    generated and printed so it doesn't leak into git history.
    """
    pwd = os.environ.get("SEED_DEFAULT_PASSWORD")
    if pwd:
        return pwd
    if not settings.DEBUG:
        raise RuntimeError(
            "SEED_DEFAULT_PASSWORD env var is required when DEBUG=False. "
            "Refusing to seed with a random password in production."
        )
    generated = secrets.token_urlsafe(16)
    print(
        f"[seed] SEED_DEFAULT_PASSWORD not set; generated random dev password: {generated}"
    )
    return generated


def slugify(text: str) -> str:
    """Convert text to URL-friendly slug."""
    import re

    text = text.lower()
    text = re.sub(r"[áàä]", "a", text)
    text = re.sub(r"[éèë]", "e", text)
    text = re.sub(r"[íìï]", "i", text)
    text = re.sub(r"[óòö]", "o", text)
    text = re.sub(r"[úùü]", "u", text)
    text = re.sub(r"ñ", "n", text)
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = re.sub(r"^-|-$", "", text)
    return text


async def seed_destinations(db: AsyncSession):
    """Seed destinations table with Costa Rica regions."""
    destinations_data = [
        {
            "name": "Guanacaste",
            "slug": "guanacaste",
            "description": "Guanacaste es la provincia más famosa de Costa Rica por sus playas espectaculares, sunsets increíbles y clima seco. Tamarindo, Flamingo, Conchal y Papagayo son destinos de clase mundial para surf, diving y relaxation.",
            "region": "Pacífico Norte",
            "province": "Guanacaste",
            "highlights": [
                "Playas vírgenes",
                "Surf de clase mundial",
                "Sunsets espectaculares",
                "Resorts de lujo",
            ],
            "things_to_do": [
                "Surf en Tamarindo",
                "Snorkel en Isla Murciélago",
                "Tour de canopy en Diamante",
                "Pesca deportiva en Flamingo",
            ],
            "best_time": "Diciembre a Abril (temporada seca)",
            "image": "https://images.unsplash.com/photo-1538108149393-fbbd81895907?w=1200&q=80",
            "gallery": [
                "https://images.unsplash.com/photo-1510414842594-a61c69b5ae57?w=800&q=80",
                "https://images.unsplash.com/photo-1544551763-46a013bb70d5?w=800&q=80",
            ],
            "order": 1,
            "is_featured": True,
            "is_active": True,
        },
        {
            "name": "La Fortuna",
            "slug": "la-fortuna",
            "description": "La Fortuna es el corazón de la aventura en Costa Rica. Domina el paisaje el Volcán Arenal, majestuoso con sus 1,633 metros. La región ofrece aguas termales naturales, cascadas impresionantes, puentes colgantes en la selva y experiencias de vida silvestre únicas.",
            "region": "Norte",
            "province": "Alajuela",
            "highlights": [
                "Volcán Arenal",
                "Aguas termales naturales",
                "Cascada La Fortuna",
                "Puentes colgantes en la selva",
            ],
            "things_to_do": [
                "Caminata al Volcán Arenal",
                "Baño en aguas termales",
                "Rafting en ríos salvajes",
                "Avistamiento de fauna",
            ],
            "best_time": "Diciembre a Marzo (mejor visibilidad del volcán)",
            "image": "https://images.unsplash.com/photo-1598971639058-fab3c3109a00?w=1200&q=80",
            "gallery": [
                "https://images.unsplash.com/photo-1551882547-ff40c63fe5fa?w=800&q=80",
                "https://images.unsplash.com/photo-1506929562872-bb421503ef21?w=800&q=80",
            ],
            "order": 2,
            "is_featured": True,
            "is_active": True,
        },
        {
            "name": "Monteverde",
            "slug": "monteverde",
            "description": "Monteverde es un bosque nuboso que alberga el 5% de la biodiversidad mundial. Los senderos serpentean entre árboles cubiertos de musgo, y el coro de aves exóticas acompaña cada paso. Ideal para observación de quetzales, puentes colgantes y experiencias de ecoturismo de clase mundial.",
            "region": "Norte",
            "province": "Puntarenas",
            "highlights": [
                "Bosque nuboso único",
                "Observación de quetzales",
                "Puentes colgantes naturales",
                "Vida silvestre exótica",
            ],
            "things_to_do": [
                "Puentes colgantes Sky Walk",
                "Avistamiento de quetzales",
                "Tour nocturno en la selva",
                "Conservatorio de colibríes",
            ],
            "best_time": "Enero a Marzo (mejor para avistamiento de quetzales)",
            "image": "https://images.unsplash.com/photo-1518623380242-4a8806cef5b8?w=1200&q=80",
            "gallery": [
                "https://images.unsplash.com/photo-1551632811-561732d1e306?w=800&q=80",
                "https://images.unsplash.com/photo-1547036967-23d11aacaee0?w=800&q=80",
            ],
            "order": 3,
            "is_featured": True,
            "is_active": True,
        },
        {
            "name": "Manuel Antonio",
            "slug": "manuel-antonio",
            "description": "Manuel Antonio combina selva tropical y playas de postal en solo 7 km². El Parque Nacional ofrece avistamiento de monos, perezosos y más. Sus playas de aguas cristalinas son perfectas para snorkel y relaxation.",
            "region": "Pacífico Central",
            "province": "Puntarenas",
            "highlights": [
                "Playas de aguas cristalinas",
                "Selva tropical accesible",
                "Fauna diversa",
                "Atardeceres únicos",
            ],
            "things_to_do": [
                "Snorkel en Playa Manuel Antonio",
                "Avistamiento de perezosos",
                "Sunset cruise",
                "Kayak en manglares",
            ],
            "best_time": "Diciembre a Abril (temporada seca)",
            "image": "https://images.unsplash.com/photo-1589802829985-817e51171b92?w=1200&q=80",
            "gallery": [
                "https://images.unsplash.com/photo-1596577932257-3c7ab64b3f8f?w=800&q=80",
                "https://images.unsplash.com/photo-1590534247854-e97d5e3feef6?w=800&q=80",
            ],
            "order": 4,
            "is_featured": True,
            "is_active": True,
        },
        {
            "name": "San José",
            "slug": "san-jose",
            "description": "San José es la capital vibrante de Costa Rica, mezcla de historia colonial y modernidad. Museos de oro precolombino, teatros históricos y el bullicio del mercado central ofrecen una inmersión cultural única.",
            "region": "Valle Central",
            "province": "San José",
            "highlights": [
                "Museo del Oro Precolombino",
                "Teatro Nacional",
                "Mercado Central",
                "Cultura Tica auténtica",
            ],
            "things_to_do": [
                "Tour por el centro histórico",
                "Museo Nacional",
                "Mercado de artesanías",
                "Tour de café",
            ],
            "best_time": "Todo el año (clima templado)",
            "image": "https://images.unsplash.com/photo-1611121976909-8c4de5273880?w=1200&q=80",
            "gallery": [
                "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800&q=80",
                "https://images.unsplash.com/photo-1591123120675-6f7f1aae0e5b?w=800&q=80",
            ],
            "order": 5,
            "is_featured": False,
            "is_active": True,
        },
        {
            "name": "Tortuguero",
            "slug": "tortuguero",
            "description": "Conocido como la 'Pequeña Amazonía' de Costa Rica, Tortuguero es un laberinto de canales rodeados de selva tropical exuberante. Cada año, miles de tortugas marinas anidan en sus playas.",
            "region": "Caribe",
            "province": "Limón",
            "highlights": [
                "Canales tortuguero",
                "Anidación de tortugas marinas",
                "Biodiversidad única",
                "Selva tropical prístina",
            ],
            "things_to_do": [
                "Tour de canales en lancha",
                "Avistamiento de tortugas",
                "Caminatas en selva",
                "Observación de aves",
            ],
            "best_time": "Julio a Septiembre (temporada de tortugas)",
            "image": "https://images.unsplash.com/photo-1504208434309-cb69f4fe52f0?w=1200&q=80",
            "gallery": [
                "https://images.unsplash.com/photo-1544979590-37e9b7c5c72e?w=800&q=80",
                "https://images.unsplash.com/photo-1564429238979-f6d3de5643e1?w=800&q=80",
            ],
            "order": 6,
            "is_featured": False,
            "is_active": True,
        },
        {
            "name": "Cahuita y Puerto Viejo",
            "slug": "cahuita-puerto-viejo",
            "description": "La costa caribeña de Costa Rica vibra con cultura afrocaribeña y un ambiente relajado único. Cahuita ofrece arrecifes de coral perfectos para snorkel, mientras Puerto Viejo es célebre por su ambiente bohemio, surf de clase y gastronomía créolle.",
            "region": "Caribe",
            "province": "Limón",
            "highlights": [
                "Cultura afrocaribeña",
                "Snorkel en arrecifes",
                "Surf de clase mundial",
                "Ambiente bohemio único",
            ],
            "things_to_do": [
                "Snorkel en Parque Nacional Cahuita",
                "Surf en Playa Cocles",
                "Yoga y wellness",
                "Tour de cacao",
            ],
            "best_time": "Febrero a Abril, Septiembre a Octubre",
            "image": "https://images.unsplash.com/photo-1518623489668-2799b5809c43?w=1200&q=80",
            "gallery": [
                "https://images.unsplash.com/photo-1596838132731-1fa1e57b8b26?w=800&q=80",
                "https://images.unsplash.com/photo-1601933513796-5de9b6a7c9e8?w=800&q=80",
            ],
            "order": 7,
            "is_featured": False,
            "is_active": True,
        },
        {
            "name": "Corcovado y Osa",
            "slug": "corcovado-osa",
            "description": "National Geographic lo llama 'el lugar biológicamente más intenso de la Tierra'. Corcovado alberga jaguares, tapires, guacamayas y cuatro especies de monos. Un paraíso para excursionistas y fotógrafos de naturaleza.",
            "region": "Pacífico Sur",
            "province": "Puntarenas",
            "highlights": [
                "Biodiversidad máxima",
                "Jaguar y fauna exótica",
                "Playas vírgenes",
                "Selva tropical prístina",
            ],
            "things_to_do": [
                "Senderismo en Corcovado",
                "Avistamiento de jaguares",
                "Snorkel en Isla del Caño",
                "Tour de vida silvestre",
            ],
            "best_time": "Diciembre a Abril (temporada seca)",
            "image": "https://images.unsplash.com/photo-1597074866923-dc0589151855?w=1200&q=80",
            "gallery": [
                "https://images.unsplash.com/photo-1547471080-7ac2f5514419?w=800&q=80",
                "https://images.unsplash.com/photo-1587974869209-9b86d5c0a8c6?w=800&q=80",
            ],
            "order": 8,
            "is_featured": False,
            "is_active": True,
        },
    ]

    print("Seeding destinations...")
    for data in destinations_data:
        result = await db.execute(
            select(Destination).where(Destination.slug == data["slug"])
        )
        existing = result.scalar_one_or_none()
        if not existing:
            dest = Destination(**data)
            db.add(dest)
            print(f"  Created: {data['name']}")
        else:
            print(f"  Already exists: {data['name']}")

    await db.commit()
    result = await db.execute(select(func.count(Destination.id)))
    print(f"  Total destinations: {result.scalar()}")


async def seed_vendor(db: AsyncSession) -> Vendor:
    """Create or get a vendor for the properties and tours."""
    vendor_email = "vendor@costaricatravel.dev"
    default_password = _get_default_password()

    result = await db.execute(select(User).where(User.email == vendor_email))
    existing_user = result.scalar_one_or_none()
    if not existing_user:
        user = User(
            email=vendor_email,
            full_name="Costa Rica Travel Vendor",
            password_hash=get_password_hash(default_password),
            role=UserRole.VENDOR,
            is_verified=True,
            is_active=True,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        print(f"  Created user: {vendor_email} (password: {default_password})")
    else:
        user = existing_user

    result = await db.execute(select(Vendor).where(Vendor.email == vendor_email))
    existing_vendor = result.scalar_one_or_none()
    if not existing_vendor:
        vendor = Vendor(
            user_id=user.id,
            business_name="Costa Rica Travel",
            business_slug="costa-rica-travel",
            business_type="tour_operator",
            phone="+506 2222-0000",
            email=vendor_email,
            status=VendorStatus.ACTIVE,
            is_verified=True,
        )
        db.add(vendor)
        await db.commit()
        await db.refresh(vendor)
        print("  Created vendor")
    else:
        vendor = existing_vendor

    return vendor


async def seed_properties(db: AsyncSession, vendor: Vendor):
    """Seed properties/hotels table."""
    properties_data = [
        {
            "vendor_id": vendor.id,
            "name": "Tabacon Thermal Resort & Spa",
            "slug": "tabacon-thermal-resort-spa",
            "short_description": "Resort de lujo con aguas termales naturales y vistas al Volcán Arenal.",
            "description": "Tabacon Thermal Resort es un oasis de relax enclavado en la falda del Volcán Arenal. Sus aguas termales naturales ofrecen una experiencia de spa única.",
            "property_type": "RESORT",
            "category": "JUNGLE",
            "province": "Alajuela",
            "region": "La Fortuna",
            "city": "La Fortuna",
            "latitude": 10.4738,
            "longitude": -84.2315,
            "cover_image": "https://images.unsplash.com/photo-1566073771259-6a8506099945?w=800&q=80",
            "images": [
                "https://images.unsplash.com/photo-1582719508461-905c673771fd?w=800&q=80",
                "https://images.unsplash.com/photo-1571896349842-33c89424de2d?w=800&q=80",
                "https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?w=800&q=80",
            ],
            "amenities": [
                "Aguas termales",
                "Spa",
                "Restaurante",
                "Bar",
                "Wifi gratis",
                "Piscina",
                "Estacionamiento",
                "Room service",
            ],
            "features": ["Vista al Volcán", "Baño termal privado", "Balcón privado"],
            "check_in_time": "15:00",
            "check_out_time": "11:00",
            "cancellation_policy": "Cancelación gratuita hasta 7 días antes de la llegada.",
            "min_guests": 1,
            "max_guests": 4,
            "beds": 1,
            "baths": 1,
            "base_price": 220.00,
            "currency": "USD",
            "weekend_price": 280.00,
            "rating": 4.8,
            "total_reviews": 847,
            "seo_keywords": [
                "hot springs",
                "arenal",
                "thermal resort",
                "luxury",
                "spa",
            ],
            "is_featured": True,
            "is_active": True,
            "is_verified": True,
        },
        {
            "vendor_id": vendor.id,
            "name": "Flamingo Beach Resort & Spa",
            "slug": "flamingo-beach-resort",
            "short_description": "Resort frente al mar en Guanacaste con paquetes todo incluido.",
            "description": "Flamingo Beach Resort ofrece una experiencia de lujo frente a las aguas cristalinas del Pacífico.",
            "property_type": "RESORT",
            "category": "BEACH",
            "province": "Guanacaste",
            "region": "Guanacaste",
            "city": "Flamingo",
            "latitude": 10.4217,
            "longitude": -85.7706,
            "cover_image": "https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?w=800&q=80",
            "images": [
                "https://images.unsplash.com/photo-1564501049412-61c2a3083791?w=800&q=80",
                "https://images.unsplash.com/photo-1571003123894-1f0594d2b5d9?w=800&q=80",
                "https://images.unsplash.com/photo-1584132967334-10e028bd69f7?w=800&q=80",
            ],
            "amenities": [
                "Todo incluido",
                "Piscina",
                "Spa",
                "Restaurante",
                "Bar",
                "Wifi gratis",
                "Gimnasio",
                "Centro de buceo",
            ],
            "features": ["Frente a la playa", "All inclusive", "Diving", "Pesca"],
            "check_in_time": "15:00",
            "check_out_time": "11:00",
            "cancellation_policy": "Cancelación gratuita hasta 14 días antes.",
            "min_guests": 1,
            "max_guests": 6,
            "beds": 2,
            "baths": 2,
            "base_price": 150.00,
            "currency": "USD",
            "weekend_price": 195.00,
            "rating": 4.6,
            "total_reviews": 623,
            "seo_keywords": [
                "flamingo beach",
                "all inclusive",
                "guanacaste resort",
                "diving",
            ],
            "is_featured": True,
            "is_active": True,
            "is_verified": True,
        },
        {
            "vendor_id": vendor.id,
            "name": "Nayara Springs",
            "slug": "nayara-springs",
            "short_description": "Resort exclusivo para adultos con plunge pools privados y spa.",
            "description": "Nayara Springs es un refugio de lujo exclusivo para adultos, enclavado en las montañas con vistas panorámicas al Volcán Arenal.",
            "property_type": "RESORT",
            "category": "MOUNTAIN",
            "province": "Alajuela",
            "region": "La Fortuna",
            "city": "El Castillo",
            "latitude": 10.4523,
            "longitude": -84.2654,
            "cover_image": "https://images.unsplash.com/photo-1582719508461-905c673771fd?w=800&q=80",
            "images": [
                "https://images.unsplash.com/photo-1566073771259-6a8506099945?w=800&q=80",
                "https://images.unsplash.com/photo-1571896349842-33c89424de2d?w=800&q=80",
                "https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?w=800&q=80",
            ],
            "amenities": [
                "Plunge pool privado",
                "Spa",
                "Restaurante gourmet",
                "Bar",
                "Wifi gratis",
                "Concierge 24/7",
                "Yoga",
            ],
            "features": [
                "Adults only",
                "Private plunge pool",
                "Volcano view",
                "Romantic",
            ],
            "check_in_time": "14:00",
            "check_out_time": "12:00",
            "cancellation_policy": "Cancelación gratuita hasta 30 días antes.",
            "min_guests": 2,
            "max_guests": 2,
            "beds": 1,
            "baths": 1,
            "base_price": 280.00,
            "currency": "USD",
            "weekend_price": 350.00,
            "rating": 4.9,
            "total_reviews": 412,
            "seo_keywords": [
                "nayara springs",
                "adults only",
                "luxury resort",
                "honeymoon",
            ],
            "is_featured": True,
            "is_active": True,
            "is_verified": True,
        },
        {
            "vendor_id": vendor.id,
            "name": "Hotel Balmoral",
            "slug": "hotel-balmoral-san-jose",
            "short_description": "Mejor hotel en el centro de San José, ubicado en la Avenida Central.",
            "description": "El Hotel Balmoral es un icono de San José, ubicado en la famosa Avenida Central.",
            "property_type": "HOTEL",
            "category": PropertyCategory.CITY,
            "province": "San José",
            "region": "Valle Central",
            "city": "San José",
            "latitude": 9.9323,
            "longitude": -84.0745,
            "cover_image": "https://images.unsplash.com/photo-1551882547-ff40c63fe5fa?w=800&q=80",
            "images": [
                "https://images.unsplash.com/photo-1611892440504-42a792e24d32?w=800&q=80",
                "https://images.unsplash.com/photo-1564501049412-61c2a3083791?w=800&q=80",
                "https://images.unsplash.com/photo-1571003123894-1f0594d2b5d9?w=800&q=80",
            ],
            "amenities": [
                "Restaurante",
                "Bar",
                "Wifi gratis",
                "Business center",
                "Gimnasio",
                "Estacionamiento",
                "Room service",
            ],
            "features": [
                "Centro ciudad",
                "Walking distance attractions",
                "Business friendly",
            ],
            "check_in_time": "14:00",
            "check_out_time": "12:00",
            "cancellation_policy": "Cancelación gratuita hasta 48 horas antes.",
            "min_guests": 1,
            "max_guests": 2,
            "beds": 1,
            "baths": 1,
            "base_price": 89.00,
            "currency": "USD",
            "weekend_price": 109.00,
            "rating": 4.3,
            "total_reviews": 1523,
            "seo_keywords": [
                "san jose hotel",
                "central avenue",
                "downtown",
                "business hotel",
            ],
            "is_featured": True,
            "is_active": True,
            "is_verified": True,
        },
        {
            "vendor_id": vendor.id,
            "name": "Monteverde Lodge & Gardens",
            "slug": "monteverde-lodge-gardens",
            "short_description": "Hotel en el bosque nuboso con jardines exuberantes y observación de aves.",
            "description": "Monteverde Lodge & Gardens ofrece una experiencia auténtica en el corazón del bosque nuboso.",
            "property_type": PropertyType.ECO_LODGE,
            "category": "MOUNTAIN",
            "province": "Puntarenas",
            "region": "Monteverde",
            "city": "Monteverde",
            "latitude": 10.3031,
            "longitude": -84.8175,
            "cover_image": "https://images.unsplash.com/photo-1590490360182-c33d57733427?w=800&q=80",
            "images": [
                "https://images.unsplash.com/photo-1566073771259-6a8506099945?w=800&q=80",
                "https://images.unsplash.com/photo-1584132967334-10e028bd69f7?w=800&q=80",
                "https://images.unsplash.com/photo-1571896349842-33c89424de2d?w=800&q=80",
            ],
            "amenities": [
                "Restaurante",
                "Bar",
                "Wifi gratis",
                "Senderos naturales",
                "Observación de aves",
                "Calefacción",
            ],
            "features": [
                "Cloud forest",
                "Birdwatching",
                "Nature trails",
                "Organic gardens",
            ],
            "check_in_time": "15:00",
            "check_out_time": "10:00",
            "cancellation_policy": "Cancelación gratuita hasta 7 días antes.",
            "min_guests": 1,
            "max_guests": 4,
            "beds": 1,
            "baths": 1,
            "base_price": 120.00,
            "currency": "USD",
            "weekend_price": 145.00,
            "rating": 4.7,
            "total_reviews": 534,
            "seo_keywords": [
                "monteverde lodge",
                "cloud forest",
                "birdwatching",
                "eco lodge",
            ],
            "is_featured": True,
            "is_active": True,
            "is_verified": True,
        },
        {
            "vendor_id": vendor.id,
            "name": "Parador Resort & Spa",
            "slug": "parador-resort-manuel-antonio",
            "short_description": "Resort en acantilado con vistas al Pacífico y acceso cercano al Parque Nacional.",
            "description": "Parador Resort & Spa se encuentra en un acantilado spectacular con vistas panorámicas al Océano Pacífico.",
            "property_type": "RESORT",
            "category": "JUNGLE",
            "province": "Puntarenas",
            "region": "Manuel Antonio",
            "city": "Quepos",
            "latitude": 9.3815,
            "longitude": -84.1432,
            "cover_image": "https://images.unsplash.com/photo-1582719508461-905c673771fd?w=800&q=80",
            "images": [
                "https://images.unsplash.com/photo-1564501049412-61c2a3083791?w=800&q=80",
                "https://images.unsplash.com/photo-1571896349842-33c89424de2d?w=800&q=80",
                "https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?w=800&q=80",
            ],
            "amenities": [
                "Spa",
                "Piscina",
                "Restaurante",
                "Bar",
                "Wifi gratis",
                "Gimnasio",
                "Transporte al parque",
            ],
            "features": [
                "Cliff location",
                "Pacific views",
                "Near Manuel Antonio Park",
                "Spa",
            ],
            "check_in_time": "15:00",
            "check_out_time": "11:00",
            "cancellation_policy": "Cancelación gratuita hasta 10 días antes.",
            "min_guests": 1,
            "max_guests": 4,
            "beds": 1,
            "baths": 1,
            "base_price": 180.00,
            "currency": "USD",
            "weekend_price": 220.00,
            "rating": 4.5,
            "total_reviews": 789,
            "seo_keywords": [
                "parador resort",
                "manuel antonio",
                "cliffs",
                "pacific views",
            ],
            "is_featured": False,
            "is_active": True,
            "is_verified": True,
        },
        {
            "vendor_id": vendor.id,
            "name": "The Springs Resort & Spa",
            "slug": "the-springs-resort-arenal",
            "short_description": "Resort de aventura con parque acuático y aguas termales.",
            "description": "The Springs Resort & Spa es el destino definitivo para familias en La Fortuna.",
            "property_type": "RESORT",
            "category": "JUNGLE",
            "province": "Alajuela",
            "region": "La Fortuna",
            "city": "La Fortuna",
            "latitude": 10.4892,
            "longitude": -84.2456,
            "cover_image": "https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?w=800&q=80",
            "images": [
                "https://images.unsplash.com/photo-1566073771259-6a8506099945?w=800&q=80",
                "https://images.unsplash.com/photo-1582719508461-905c673771fd?w=800&q=80",
                "https://images.unsplash.com/photo-1571896349842-33c89424de2d?w=800&q=80",
            ],
            "amenities": [
                "Parque acuático",
                "Aguas termales",
                "Spa",
                "Restaurante",
                "Bar",
                "Wifi gratis",
                "Kids club",
            ],
            "features": [
                "Water park",
                "Hot springs",
                "Family friendly",
                "Volcano views",
            ],
            "check_in_time": "15:00",
            "check_out_time": "11:00",
            "cancellation_policy": "Cancelación gratuita hasta 7 días antes.",
            "min_guests": 1,
            "max_guests": 6,
            "beds": 2,
            "baths": 2,
            "base_price": 200.00,
            "currency": "USD",
            "weekend_price": 260.00,
            "rating": 4.6,
            "total_reviews": 956,
            "seo_keywords": [
                "the springs",
                "water park",
                "family resort",
                "hot springs",
            ],
            "is_featured": False,
            "is_active": True,
            "is_verified": True,
        },
        {
            "vendor_id": vendor.id,
            "name": "Hotel Tamarindo",
            "slug": "hotel-tamarindo",
            "short_description": "Hotel en el corazón de Tamarindo, perfecto base para surf y aventuras.",
            "description": "Hotel Tamarindo ofrece comodidad y ubicación inmejorable en el centro del pueblo más vibrante de Guanacaste.",
            "property_type": "HOTEL",
            "category": "BEACH",
            "province": "Guanacaste",
            "region": "Guanacaste",
            "city": "Tamarindo",
            "latitude": 10.3231,
            "longitude": -85.8407,
            "cover_image": "https://images.unsplash.com/photo-1590490360182-c33d57733427?w=800&q=80",
            "images": [
                "https://images.unsplash.com/photo-1564501049412-61c2a3083791?w=800&q=80",
                "https://images.unsplash.com/photo-1611892440504-42a792e24d32?w=800&q=80",
                "https://images.unsplash.com/photo-1571003123894-1f0594d2b5d9?w=800&q=80",
            ],
            "amenities": [
                "Piscina",
                "Restaurante",
                "Bar",
                "Wifi gratis",
                "Surf rentals",
                "Tour desk",
            ],
            "features": [
                "Surf town",
                "Beach walking distance",
                "Central location",
                "Surf rentals",
            ],
            "check_in_time": "14:00",
            "check_out_time": "11:00",
            "cancellation_policy": "Cancelación gratuita hasta 5 días antes.",
            "min_guests": 1,
            "max_guests": 4,
            "beds": 1,
            "baths": 1,
            "base_price": 95.00,
            "currency": "USD",
            "weekend_price": 125.00,
            "rating": 4.2,
            "total_reviews": 412,
            "seo_keywords": ["tamarindo hotel", "surf", "beach hotel", "guanacaste"],
            "is_featured": False,
            "is_active": True,
            "is_verified": True,
        },
        {
            "vendor_id": vendor.id,
            "name": "Le Caméléon Boutique Hotel",
            "slug": "le-cameleon-puerto-viejo",
            "short_description": "Hotel boutique en Puerto Viejo con beach club y ambiente relajado.",
            "description": "Le Caméléon es un hotel boutique único en el corazón de Puerto Viejo.",
            "property_type": "BOUTIQUE",
            "category": "BEACH",
            "province": "Limón",
            "region": "Caribe",
            "city": "Puerto Viejo",
            "latitude": 9.6569,
            "longitude": -82.7569,
            "cover_image": "https://images.unsplash.com/photo-1582719508461-905c673771fd?w=800&q=80",
            "images": [
                "https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?w=800&q=80",
                "https://images.unsplash.com/photo-1566073771259-6a8506099945?w=800&q=80",
                "https://images.unsplash.com/photo-1571896349842-33c89424de2d?w=800&q=80",
            ],
            "amenities": [
                "Beach club",
                "Restaurante",
                "Bar",
                "Wifi gratis",
                "Yoga",
                "Bicicletas",
            ],
            "features": ["Boutique hotel", "Beach club", "Yoga", "Caribbean vibe"],
            "check_in_time": "15:00",
            "check_out_time": "11:00",
            "cancellation_policy": "Cancelación gratuita hasta 7 días antes.",
            "min_guests": 1,
            "max_guests": 2,
            "beds": 1,
            "baths": 1,
            "base_price": 130.00,
            "currency": "USD",
            "weekend_price": 160.00,
            "rating": 4.4,
            "total_reviews": 287,
            "seo_keywords": [
                "le cameleon",
                "puerto viejo",
                "boutique hotel",
                "caribbean",
            ],
            "is_featured": False,
            "is_active": True,
            "is_verified": True,
        },
        {
            "vendor_id": vendor.id,
            "name": "Pacuare Lodge",
            "slug": "pacuare-lodge",
            "short_description": "Eco lodge de lujo en la selva tropical, accesible solo por balsa.",
            "description": "Pacuare Lodge es un escondite de lujo en medio de la selva tropical de Turrialba.",
            "property_type": PropertyType.ECO_LODGE,
            "category": "JUNGLE",
            "province": "Cartago",
            "region": "Turrialba",
            "city": "Turrialba",
            "latitude": 9.8234,
            "longitude": -83.6845,
            "cover_image": "https://images.unsplash.com/photo-1590490360182-c33d57733427?w=800&q=80",
            "images": [
                "https://images.unsplash.com/photo-1582719508461-905c673771fd?w=800&q=80",
                "https://images.unsplash.com/photo-1566073771259-6a8506099945?w=800&q=80",
                "https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?w=800&q=80",
            ],
            "amenities": [
                "Restaurante",
                "Bar",
                "Spa",
                "Guías naturalistas",
                "Paquetes aventura",
            ],
            "features": [
                "Remote location",
                "River crossing",
                "Eco luxury",
                "Adventure packages",
            ],
            "check_in_time": "14:00",
            "check_out_time": "10:00",
            "cancellation_policy": "Cancelación gratuita hasta 30 días antes.",
            "min_guests": 1,
            "max_guests": 4,
            "beds": 1,
            "baths": 1,
            "base_price": 250.00,
            "currency": "USD",
            "weekend_price": 300.00,
            "rating": 4.9,
            "total_reviews": 198,
            "seo_keywords": ["pacuare lodge", "eco lodge", "luxury", "rainforest"],
            "is_featured": False,
            "is_active": True,
            "is_verified": True,
        },
    ]

    print("\nSeeding properties...")
    for data in properties_data:
        result = await db.execute(select(Property).where(Property.slug == data["slug"]))
        existing = result.scalar_one_or_none()
        if not existing:
            prop = Property(**data)
            db.add(prop)
            print(f"  Created: {data['name']}")
        else:
            print(f"  Already exists: {data['name']}")

    await db.commit()
    result = await db.execute(select(func.count(Property.id)))
    print(f"  Total properties: {result.scalar()}")


async def seed_tours(db: AsyncSession, vendor: Vendor):
    """Seed tours table."""
    tours_data = [
        {
            "vendor_id": vendor.id,
            "name": "Canopy Arenal Adventure",
            "slug": "canopy-arenal-adventure",
            "description": "Experimenta la adrenalina de volar por el dosel del bosque tropical con vistas espectaculares del Volcán Arenal.",
            "category": "ADVENTURE",
            "difficulty": TourDifficulty.EASY,
            "duration_hours": 2.0,
            "duration_text": "2 horas",
            "location": "La Fortuna",
            "meeting_point": "Centro de Aventura Arenal, La Fortuna",
            "included": [
                "Equipo de seguridad",
                "Guía certificado",
                "Transfer desde hotel",
                "Frutas y agua",
            ],
            "not_included": ["Transporte adicional", "Propinas"],
            "itinerary": [
                {"step": 1, "activity": "Briefing de seguridad", "duration": "15 min"},
                {
                    "step": 2,
                    "activity": "Inicio del canopy - 15 cables",
                    "duration": "90 min",
                },
                {"step": 3, "activity": "Refrigerio y fotos", "duration": "15 min"},
            ],
            "max_group_size": 15,
            "min_age": 5,
            "price": 65.00,
            "currency": "USD",
            "images": [
                "https://images.unsplash.com/photo-1601584115197-04ecc0da31d7?w=800&q=80",
                "https://images.unsplash.com/photo-1530866495561-507c9faab2ed?w=800&q=80",
            ],
            "cover_image": "https://images.unsplash.com/photo-1601584115197-04ecc0da31d7?w=800&q=80",
            "schedule_days": [
                "monday",
                "tuesday",
                "wednesday",
                "thursday",
                "friday",
                "saturday",
                "sunday",
            ],
            "rating": 4.7,
            "total_reviews": 1234,
            "total_bookings": 5678,
            "is_featured": True,
            "is_active": True,
        },
        {
            "vendor_id": vendor.id,
            "name": "White Water Rafting Río Pacuare",
            "slug": "white-water-rafting-pacuare",
            "description": "El Río Pacuare es considerado uno de los mejores ríos para rafting en el mundo. Rápidos de clase III-IV rodeados de selva tropical prístina.",
            "category": "ADVENTURE",
            "difficulty": TourDifficulty.CHALLENGING,
            "duration_hours": 5.0,
            "duration_text": "5 horas",
            "location": "La Fortuna / Turrialba",
            "meeting_point": "Hotel pickup en La Fortuna o Turrialba",
            "included": [
                "Equipo de rafting",
                "Guía certificado",
                "Almuerzo",
                "Transfer desde hotel",
                "Seguro",
            ],
            "not_included": ["Ropa de agua personal", "Zapatos mojados"],
            "itinerary": [
                {
                    "step": 1,
                    "activity": "Pickup y transporte al río",
                    "duration": "45 min",
                },
                {
                    "step": 2,
                    "activity": "Briefing y equipamiento",
                    "duration": "20 min",
                },
                {
                    "step": 3,
                    "activity": "Rafting - 20kms de río",
                    "duration": "3.5 horas",
                },
                {"step": 4, "activity": "Almuerzo en la rivera", "duration": "30 min"},
                {"step": 5, "activity": "Regreso al hotel", "duration": "45 min"},
            ],
            "max_group_size": 12,
            "min_age": 12,
            "price": 95.00,
            "currency": "USD",
            "images": [
                "https://images.unsplash.com/photo-1530866495561-507c9faab2ed?w=800&q=80",
                "https://images.unsplash.com/photo-1601584115197-04ecc0da31d7?w=800&q=80",
            ],
            "cover_image": "https://images.unsplash.com/photo-1530866495561-507c9faab2ed?w=800&q=80",
            "schedule_days": ["monday", "wednesday", "friday", "saturday", "sunday"],
            "rating": 4.9,
            "total_reviews": 876,
            "total_bookings": 3456,
            "is_featured": True,
            "is_active": True,
        },
        {
            "vendor_id": vendor.id,
            "name": "Tour Parque Nacional Manuel Antonio",
            "slug": "tour-parque-nacional-manuel-antonio",
            "description": "Explora uno de los parques nacionales más diversos del mundo con un guía naturalista certificado. Monos, perezosos, iguanas y más.",
            "category": TourCategory.NATURE,
            "difficulty": TourDifficulty.EASY,
            "duration_hours": 2.5,
            "duration_text": "2-3 horas",
            "location": "Manuel Antonio",
            "meeting_point": "Entrada del Parque Nacional Manuel Antonio",
            "included": [
                "Guía naturalista certificado",
                "Equipo de snorkel",
                "Agua y frutas",
                "Entrada al parque",
            ],
            "not_included": ["Transporte", "Almuerzo"],
            "itinerary": [
                {"step": 1, "activity": "Encuentro con guía", "duration": "10 min"},
                {
                    "step": 2,
                    "activity": "Senderismo con avistamiento de fauna",
                    "duration": "90 min",
                },
                {"step": 3, "activity": "Playa y snorkel", "duration": "45 min"},
                {"step": 4, "activity": "Tiempo libre", "duration": "15 min"},
            ],
            "max_group_size": 20,
            "min_age": 0,
            "price": 49.00,
            "currency": "USD",
            "images": [
                "https://images.unsplash.com/photo-1589802829985-817e51171b92?w=800&q=80",
                "https://images.unsplash.com/photo-1596577932257-3c7ab64b3f8f?w=800&q=80",
            ],
            "cover_image": "https://images.unsplash.com/photo-1589802829985-817e51171b92?w=800&q=80",
            "schedule_days": [
                "monday",
                "tuesday",
                "wednesday",
                "thursday",
                "friday",
                "saturday",
                "sunday",
            ],
            "rating": 4.8,
            "total_reviews": 2345,
            "total_bookings": 8765,
            "is_featured": True,
            "is_active": True,
        },
        {
            "vendor_id": vendor.id,
            "name": "Safari Float Penas Blancas",
            "slug": "safari-float-penas-blancas",
            "description": "Una experiencia relajante en balsa por el río Penas Blancas. Observa caimanes, monos, perezosos y tucanes.",
            "category": TourCategory.NATURE,
            "difficulty": TourDifficulty.EASY,
            "duration_hours": 4.0,
            "duration_text": "4 horas",
            "location": "La Fortuna",
            "meeting_point": "Hotel pickup en La Fortuna",
            "included": [
                "Balsa y remos",
                "Guía naturalista",
                "Frutas y agua",
                "Transfer desde hotel",
            ],
            "not_included": ["Propinas"],
            "itinerary": [
                {"step": 1, "activity": "Pickup y transporte", "duration": "20 min"},
                {"step": 2, "activity": "Navegación por el río", "duration": "3 horas"},
                {"step": 3, "activity": "Snack y regreso", "duration": "40 min"},
            ],
            "max_group_size": 16,
            "min_age": 0,
            "price": 50.00,
            "currency": "USD",
            "images": [
                "https://images.unsplash.com/photo-1504208434309-cb69f4fe52f0?w=800&q=80",
                "https://images.unsplash.com/photo-1598971639058-fab3c3109a00?w=800&q=80",
            ],
            "cover_image": "https://images.unsplash.com/photo-1504208434309-cb69f4fe52f0?w=800&q=80",
            "schedule_days": [
                "monday",
                "tuesday",
                "wednesday",
                "thursday",
                "friday",
                "saturday",
                "sunday",
            ],
            "rating": 4.6,
            "total_reviews": 654,
            "total_bookings": 2345,
            "is_featured": False,
            "is_active": True,
        },
        {
            "vendor_id": vendor.id,
            "name": "Mistico Park Hanging Bridges",
            "slug": "mistico-park-hanging-bridges",
            "description": "Camina por 15 puentes colgantes que te llevan a través del dosel del bosque tropical con vistas a cascadas.",
            "category": TourCategory.NATURE,
            "difficulty": TourDifficulty.EASY,
            "duration_hours": 3.0,
            "duration_text": "2-3 horas",
            "location": "La Fortuna",
            "meeting_point": "Mistico Park, La Fortuna",
            "included": ["Entrada al parque", "Guía local", "Agua"],
            "not_included": ["Transporte"],
            "itinerary": [
                {"step": 1, "activity": "Registro y briefing", "duration": "15 min"},
                {
                    "step": 2,
                    "activity": "Caminata en puentes colgantes",
                    "duration": "2 horas",
                },
                {
                    "step": 3,
                    "activity": "Observación de flora y fauna",
                    "duration": "45 min",
                },
            ],
            "max_group_size": 25,
            "min_age": 0,
            "price": 54.00,
            "currency": "USD",
            "images": [
                "https://images.unsplash.com/photo-1551632811-561732d1e306?w=800&q=80",
                "https://images.unsplash.com/photo-1547036967-23d11aacaee0?w=800&q=80",
            ],
            "cover_image": "https://images.unsplash.com/photo-1551632811-561732d1e306?w=800&q=80",
            "schedule_days": [
                "monday",
                "tuesday",
                "wednesday",
                "thursday",
                "friday",
                "saturday",
                "sunday",
            ],
            "rating": 4.7,
            "total_reviews": 1178,
            "total_bookings": 4567,
            "is_featured": False,
            "is_active": True,
        },
        {
            "vendor_id": vendor.id,
            "name": "Catamarán Sunset Cruise Tamarindo",
            "slug": "catamaran-sunset-cruise-tamarindo",
            "description": "Navega por las aguas cristalinas de Tamarindo a bordo de un catamarán de lujo. Snorkel, delfines y cocktails tropicales.",
            "category": TourCategory.WATER,
            "difficulty": TourDifficulty.EASY,
            "duration_hours": 5.0,
            "duration_text": "5 horas",
            "location": "Tamarindo, Guanacaste",
            "meeting_point": "Muelle de Tamarindo",
            "included": [
                "Barco catamarán",
                "Open bar",
                "Snorkel equipment",
                "Almuerzo",
                "Frutas",
            ],
            "not_included": ["Transporte al muelle"],
            "itinerary": [
                {"step": 1, "activity": "Embarque y briefing", "duration": "15 min"},
                {
                    "step": 2,
                    "activity": "Navegación y snorkel",
                    "duration": "2.5 horas",
                },
                {"step": 3, "activity": "Open bar y almuerzo", "duration": "1.5 horas"},
                {"step": 4, "activity": "Sunset cruise", "duration": "1 hora"},
            ],
            "max_group_size": 40,
            "min_age": 0,
            "price": 108.00,
            "currency": "USD",
            "images": [
                "https://images.unsplash.com/photo-1544551763-46a013bb70d5?w=800&q=80",
                "https://images.unsplash.com/photo-1538108149393-fbbd81895907?w=800&q=80",
            ],
            "cover_image": "https://images.unsplash.com/photo-1544551763-46a013bb70d5?w=800&q=80",
            "schedule_days": ["monday", "wednesday", "friday", "saturday"],
            "rating": 4.8,
            "total_reviews": 543,
            "total_bookings": 1987,
            "is_featured": False,
            "is_active": True,
        },
        {
            "vendor_id": vendor.id,
            "name": "Tour Tortuguero - La Pequeña Amazonía",
            "slug": "tour-tortuguero",
            "description": "Explora los famosos canales de Tortuguero. Navegación, caminata en la selva y visita al pueblo. Caimans, monos, perezosos y más de 300 especies de aves.",
            "category": TourCategory.NATURE,
            "difficulty": TourDifficulty.EASY,
            "duration_hours": 8.0,
            "duration_text": "Día completo",
            "location": "Tortuguero",
            "meeting_point": "Pickup en Lodge o Transfers available from Moín",
            "included": [
                "Navegación en lancha",
                "Guía certificado",
                "Almuerzo buffet",
                "Entrada al Parque Nacional",
            ],
            "not_included": ["Transporte terrestre opcional", "Propinas"],
            "itinerary": [
                {
                    "step": 1,
                    "activity": "Navegación matutina por canales",
                    "duration": "2 horas",
                },
                {"step": 2, "activity": "Caminata en selva", "duration": "1.5 horas"},
                {"step": 3, "activity": "Almuerzo buffet", "duration": "45 min"},
                {
                    "step": 4,
                    "activity": "Tour por el pueblo de Tortuguero",
                    "duration": "1 hora",
                },
                {
                    "step": 5,
                    "activity": "Navegación vespertina",
                    "duration": "1.5 horas",
                },
            ],
            "max_group_size": 20,
            "min_age": 0,
            "price": 85.00,
            "currency": "USD",
            "images": [
                "https://images.unsplash.com/photo-1504208434309-cb69f4fe52f0?w=800&q=80",
                "https://images.unsplash.com/photo-1544979590-37e9b7c5c72e?w=800&q=80",
            ],
            "cover_image": "https://images.unsplash.com/photo-1504208434309-cb69f4fe52f0?w=800&q=80",
            "schedule_days": ["monday", "wednesday", "friday", "saturday"],
            "rating": 4.7,
            "total_reviews": 432,
            "total_bookings": 1567,
            "is_featured": False,
            "is_active": True,
        },
        {
            "vendor_id": vendor.id,
            "name": "Canyoning y Rappel en La Fortuna",
            "slug": "canyoning-rappel-la-fortuna",
            "description": "Desciende por cascadas naturales y rappel en la selva tropical. Aventura extrema con guías certificados y equipo profesional.",
            "category": "ADVENTURE",
            "difficulty": TourDifficulty.CHALLENGING,
            "duration_hours": 4.0,
            "duration_text": "4 horas",
            "location": "La Fortuna",
            "meeting_point": "Hotel pickup en La Fortuna",
            "included": [
                "Equipo de rappelen",
                "Guía certificado",
                "Snack",
                "Transfer desde hotel",
                "Seguro",
            ],
            "not_included": ["Zapatos de agua personal"],
            "itinerary": [
                {
                    "step": 1,
                    "activity": "Transporte y equipamiento",
                    "duration": "30 min",
                },
                {"step": 2, "activity": "Briefing de seguridad", "duration": "20 min"},
                {
                    "step": 3,
                    "activity": "Canyoning - 4 rappeles",
                    "duration": "2.5 horas",
                },
                {"step": 4, "activity": "Snack y fotos", "duration": "30 min"},
            ],
            "max_group_size": 8,
            "min_age": 12,
            "price": 125.00,
            "currency": "USD",
            "images": [
                "https://images.unsplash.com/photo-1598971639058-fab3c3109a00?w=800&q=80",
                "https://images.unsplash.com/photo-1601584115197-04ecc0da31d7?w=800&q=80",
            ],
            "cover_image": "https://images.unsplash.com/photo-1598971639058-fab3c3109a00?w=800&q=80",
            "schedule_days": ["tuesday", "thursday", "saturday"],
            "rating": 4.9,
            "total_reviews": 321,
            "total_bookings": 987,
            "is_featured": False,
            "is_active": True,
        },
        {
            "vendor_id": vendor.id,
            "name": "Cloud Forest Night Walk Monteverde",
            "slug": "cloud-forest-night-walk-monteverde",
            "description": "Descubre el lado nocturno del bosque nuboso de Monteverde. Ranas venenosas, serpientes, búhos y más criaturas nocturnas.",
            "category": TourCategory.NATURE,
            "difficulty": TourDifficulty.EASY,
            "duration_hours": 2.5,
            "duration_text": "2.5 horas",
            "location": "Monteverde",
            "meeting_point": "Centro de Visitantes Monteverde",
            "included": ["Guía certificado", "Linterna", "Botella de agua"],
            "not_included": ["Transporte"],
            "itinerary": [
                {"step": 1, "activity": "Registro y briefing", "duration": "15 min"},
                {"step": 2, "activity": "Caminata nocturna", "duration": "2 horas"},
            ],
            "max_group_size": 12,
            "min_age": 8,
            "price": 55.00,
            "currency": "USD",
            "images": [
                "https://images.unsplash.com/photo-1518623380242-4a8806cef5b8?w=800&q=80",
                "https://images.unsplash.com/photo-1551632811-561732d1e306?w=800&q=80",
            ],
            "cover_image": "https://images.unsplash.com/photo-1518623380242-4a8806cef5b8?w=800&q=80",
            "schedule_days": ["monday", "wednesday", "friday", "saturday"],
            "rating": 4.8,
            "total_reviews": 567,
            "total_bookings": 2134,
            "is_featured": False,
            "is_active": True,
        },
        {
            "vendor_id": vendor.id,
            "name": "Coffee Tour Experience Alajuela",
            "slug": "coffee-tour-alajuela",
            "description": "Visita una plantación de café en las montañas de Alajuela. Desde la cosecha hasta la taza, con degustación.",
            "category": TourCategory.CULTURAL,
            "difficulty": TourDifficulty.EASY,
            "duration_hours": 3.0,
            "duration_text": "3 horas",
            "location": "Alajuela",
            "meeting_point": "Pickup en hoteles de San José",
            "included": [
                "Transporte ida y vuelta",
                "Guía certificado",
                "Degustación de café",
                "Chocolate samples",
            ],
            "not_included": ["Almuerzo opcional"],
            "itinerary": [
                {
                    "step": 1,
                    "activity": "Transporte desde San José",
                    "duration": "45 min",
                },
                {
                    "step": 2,
                    "activity": "Tour por la plantación",
                    "duration": "1.5 horas",
                },
                {"step": 3, "activity": "Degustación y compras", "duration": "45 min"},
            ],
            "max_group_size": 15,
            "min_age": 0,
            "price": 45.00,
            "currency": "USD",
            "images": [
                "https://images.unsplash.com/photo-1447933601403-0c6688de566e?w=800&q=80",
                "https://images.unsplash.com/photo-1514432324607-a09d9b4aefdd?w=800&q=80",
            ],
            "cover_image": "https://images.unsplash.com/photo-1447933601403-0c6688de566e?w=800&q=80",
            "schedule_days": [
                "monday",
                "tuesday",
                "wednesday",
                "thursday",
                "friday",
                "saturday",
            ],
            "rating": 4.5,
            "total_reviews": 234,
            "total_bookings": 1234,
            "is_featured": False,
            "is_active": True,
        },
    ]

    print("\nSeeding tours...")
    for data in tours_data:
        result = await db.execute(select(Tour).where(Tour.slug == data["slug"]))
        existing = result.scalar_one_or_none()
        if not existing:
            tour = Tour(**data)
            db.add(tour)
            print(f"  Created: {data['name']}")
        else:
            print(f"  Already exists: {data['name']}")

    await db.commit()
    result = await db.execute(select(func.count(Tour.id)))
    print(f"  Total tours: {result.scalar()}")


async def seed_blog_posts(db: AsyncSession):
    """Seed blog posts/articles."""
    blog_posts_data = [
        {
            "title": "Guía Completa para Visitar el Volcán Arenal 2025",
            "slug": "guia-completa-visitar-volcan-arenal-2025",
            "excerpt": "Todo lo que necesitas saber para planificar tu visita al Volcán Arenal: mejores hoteles, tours, aguas termales y cuando ir.",
            "content": """<h2>El Volcán Arenal: Un Destino Imperdible</h2><p>El Volcán Arenal es, sin duda, uno de los destinos más emblemáticos de Costa Rica. Durante más de 40 años, este coloso de 1,633 metros fue el volcano más activo del país.</p><h2>Mejor Época para Visitar</h2><p>La mejor época para visitar el Volcán Arenal es de <strong>diciembre a marzo</strong>, cuando las lluvias son menos frecuentes y la visibilidad del volcano es óptima.</p><h2>Qué Hacer en La Fortuna</h2><h3>1. Caminata al Volcán Arenal</h3><p>El sendero de 3.7 km te lleva a través de antiguas lenguas de lava y ofrece vistas espectaculares del crater.</p><h3>2. Aguas Termales</h3><p>No puedes ir a La Fortuna sin bañarte en sus famosas aguas termales. Tabacon, Baldi, and Eco Termales ofrecen experiencias desde lujo hasta económico.</p><h3>3. Cascada La Fortuna</h3><p>A solo 5 km del centro de town, esta cascada de 70 metros es perfecta para una excursión de medio día.</p><h3>4. Puentes colgantes y Canopy</h3><p>Para los amantes de la adrenalina, las 15+ platforms y 2 km de cables de Sky Trek ofrecen una experiencia de canopy inolvidable.</p><h2>Dónde Hospedarse</h2><p>La Fortuna ofrece opciones para todos los presupuestos: Lujo (Nayara Springs, The Springs, Tabacon), Medio (Arenal Kioro, Hotel Lagos), Económico (Arenal Backpackers).</p>""",
            "featured_image": "https://images.unsplash.com/photo-1598971639058-fab3c3109a00?w=1200&q=80",
            "category": "Destinos",
            "tags": ["arenal", "la fortuna", "volcano", "hot springs", "adventure"],
            "status": BlogPostStatus.PUBLISHED,
            "published_at": datetime.now(timezone.utc),
            "views_count": 4523,
            "is_featured": True,
        },
        {
            "title": "Las 10 Mejores Playas de Costa Rica para Surf",
            "slug": "mejores-playas-costa-rica-surf",
            "excerpt": "Descubre las mejores playas para surf en Costa Rica: Tamarindo, Jacó, Manuel Antonio y más. Ondas para todos los niveles.",
            "content": """<h2>Costa Rica: Paraíso del Surf</h2><p>Costa Rica es un destino de clase mundial para el surf, con olas para todos los niveles y una cultura de surf vibrante.</p><h2>Las 10 Mejores Playas para Surf</h2><h3>1. Tamarindo - Guanacaste</h3><p>El hotspot de surf más famoso de Costa Rica. Olas consistentes para todos los niveles.</p><h3>2. Jacó - Pacífico Central</h3><p>La playa más accessible desde San José. Olas consistentes y una escena de surf floreciente.</p><h3>3. Playa Hermosa - Guanacaste</h3><p>Conocida por sus olas potentes, perfecta para surfers intermedios y avanzados.</p><h3>4. Boca Barranca - Pacífico Central</h3><p>Considerada la mejor playa para principiantes en Costa Rica.</p><h3>5. Santa Teresa - Península de Nicoya</h3><p>Un destino remoto con olas consistentes y un ambiente bohemio único.</p><h3>6. Puerto Viejo - Caribe</h3><p>El Caribe tiene su propia energía de surf. Olas diferentes, más suitable para intermedios.</p><h2>Mejor Época para Surfear</h2><ul><li><strong>Pacífico:</strong> Mayo - Noviembre (mejor swells de diciembre a marzo)</li><li><strong>Caribe:</strong> Diciembre - Marzo, pero las mejores olas de julio a octubre</li></ul>""",
            "featured_image": "https://images.unsplash.com/photo-1538108149393-fbbd81895907?w=1200&q=80",
            "category": "Actividades",
            "tags": ["surf", "playas", "tamarindo", "jaco", "puerto viejo"],
            "status": BlogPostStatus.PUBLISHED,
            "published_at": datetime.now(timezone.utc),
            "views_count": 3876,
            "is_featured": True,
        },
        {
            "title": "Qué Hacer en Monteverde: Guía del Bosque Nuboso",
            "slug": "que-hacer-monteverde-guia-bosque-nuboso",
            "excerpt": "Descubre las mejores actividades en Monteverde: puentes colgantes, avistamiento de quetzales, tour nocturno y más.",
            "content": """<h2>Monteverde: El Paraíso del Bosque Nuboso</h2><p>Monteverde es mucho más que un destino turístico; es un ecosistema único donde la naturaleza reigns supreme.</p><h2>Cómo Llegar a Monteverde</h2><p>Monteverde se encuentra en las montañas de Puntarenas, a unas 3-4 horas de San José.</p><h2>Las Mejores Actividades</h2><h3>1. Puentes Colgantes Sky Walk</h3><p>Los puentes colgantes de Monteverde te llevan a través del dosel del bosque, ofreciendo vistas espectaculares.</p><h3>2. Avistamiento de Quetzales</h3><p>El quetzal es el santo grial para birdwatchers. La mejor época es de enero a marzo.</p><h3>3. Tour Nocturno</h3><p>El bosque se transforma después del atardecer. Ranas venenosas, serpientes, búhos y otros creatures nocturnos.</p><h3>4. Conservatorio de Colibríes Selvatura</h3><p>Este jardín es home to 14 species de colibríes. Un paraíso para fotógrafos.</p><h2>Dónde Hospedarse</h2><p>Monteverde Lodge & Gardens, Hotel Belmar, Senda Monteverde son opciones recomendadas.</p>""",
            "featured_image": "https://images.unsplash.com/photo-1518623380242-4a8806cef5b8?w=1200&q=80",
            "category": "Destinos",
            "tags": ["monteverde", "cloud forest", "quetzal", "ziplines", "nature"],
            "status": BlogPostStatus.PUBLISHED,
            "published_at": datetime.now(timezone.utc),
            "views_count": 2987,
            "is_featured": True,
        },
        {
            "title": "Costa Rica en Familia: Los Mejores Destinos para Niños",
            "slug": "costa-rica-en-familia-mejores-destinos-ninos",
            "excerpt": "Planifica tu viaje familiar a Costa Rica. Los mejores destinos, hoteles y actividades para viajar con niños.",
            "content": """<h2>Viajar a Costa Rica con Niños</h2><p>Costa Rica es uno de los mejores destinos familiares del mundo. La combinación de naturaleza accessible, aventura adaptée para todas las edades y la calidez del pueblo tico hacen de este país un paradise para familias.</p><h2>Mejores Destinos Familiares</h2><h3>1. La Fortuna</h3><p>Perfecto para familias con niños de todas las edades. Las aguas termales son ideales para pequenos.</p><h3>2. Manuel Antonio</h3><p>Las playas de Manuel Antonio son perfectas para niños. El agua es tranquila y poco profunda.</p><h3>3. Monteverde</h3><p>Los niños aman los puentes colgantes y la posibilidad de ver colibríes de cerca.</p><h3>4. Guanacaste (Tamarindo area)</h3><p>Las playas de Guanacaste tienen algo para todos. Los niños pueden aprender a surfear en olas suaves.</p><h2>Hoteles Familiares Recomendados</h2><p>The Springs Resort & Spa (Water park), Parador Resort (Kids club), Hotel Tamarindo (Family-friendly).</p>""",
            "featured_image": "https://images.unsplash.com/photo-1589802829985-817e51171b92?w=1200&q=80",
            "category": "Familia",
            "tags": ["family", "kids", "children", "activities", "planning"],
            "status": BlogPostStatus.PUBLISHED,
            "published_at": datetime.now(timezone.utc),
            "views_count": 1856,
            "is_featured": False,
        },
        {
            "title": "Temporada de Tortugas Marinas en Tortuguero: Guía 2025",
            "slug": "temporada-tortugas-marinas-tortuguero-guia-2025",
            "excerpt": "Todo sobre la temporada de anidación de tortugas marinas en Tortuguero. Cuándo ir, tours y cómo contribuir a la conservación.",
            "content": """<h2>Tortuguero: Santuario de Tortugas Marinas</h2><p>Tortuguero, ubicado en la costa caribeña de Costa Rica, es uno de los santuarios de anidación de tortugas marinas más importantes del mundo.</p><h2>Temporada de Anidación</h2><h3>Tortuga Verde</h3><p>La principal temporada de anidación va de <strong>julio a octubre</strong>, con peak en agosto y septiembre.</p><h3>Tortuga Carey</h3><p>La tortuga carey anida de <strong>mayo a noviembre</strong>, con peak en septiembre-octubre.</p><h3>Tortuga Lora</h3><p>La más pequeña también tiene su momento, de <strong>julio a septiembre</strong>.</p><h2>Cómo Visitar</h2><p>Para ver la anidación, necesitas contratar un guía local certificado. Solo así podrás acceder a las playas durante la noche.</p><h2>Conservación</h2><p>Tortuguero es un modelo de conservación exitoso. Los programas locales han protegido las playas por décadas.</p>""",
            "featured_image": "https://images.unsplash.com/photo-1544551763-46a013bb70d5?w=1200&q=80",
            "category": "Vida Silvestre",
            "tags": ["tortuguero", "turtles", "sea turtles", "nesting", "conservation"],
            "status": BlogPostStatus.PUBLISHED,
            "published_at": datetime.now(timezone.utc),
            "views_count": 1234,
            "is_featured": False,
        },
    ]

    print("\nSeeding blog posts...")
    for data in blog_posts_data:
        result = await db.execute(select(BlogPost).where(BlogPost.slug == data["slug"]))
        existing = result.scalar_one_or_none()
        if not existing:
            post = BlogPost(**data)
            db.add(post)
            print(f"  Created: {data['title']}")
        else:
            print(f"  Already exists: {data['title']}")

    await db.commit()
    result = await db.execute(select(func.count(BlogPost.id)))
    print(f"  Total blog posts: {result.scalar()}")


async def seed_admin_users(db: AsyncSession, default_password: str) -> None:
    """Create superadmin and admin accounts for the superadmin dashboard.

    Idempotent: skips creation if the email already exists.
    """
    for email, role, full_name in [
        ("superadmin@costaricatravel.dev", UserRole.SUPER_ADMIN, "Super Admin"),
        ("admin@costaricatravel.dev", UserRole.ADMIN, "Admin User"),
    ]:
        result = await db.execute(select(User).where(User.email == email))
        if result.scalar_one_or_none():
            print(f"  Already exists: {email}")
            continue
        user = User(
            email=email,
            full_name=full_name,
            password_hash=get_password_hash(default_password),
            role=role,
            is_verified=True,
            is_active=True,
        )
        db.add(user)
        print(f"  Created: {email} (role={role.value})")
    await db.commit()


async def main():
    """Main function to seed all data."""
    print("=" * 60)
    print("COSTA RICA TRAVEL - SEED DATA")
    print("=" * 60)

    default_password = _get_default_password()
    print(f"[seed] default password for all seeded accounts: {default_password}")

    async with AsyncSessionLocal() as db:
        try:
            print("\nStarting seed process...")

            await seed_destinations(db)
            await seed_admin_users(db, default_password)
            vendor = await seed_vendor(db)
            await seed_properties(db, vendor)
            await seed_tours(db, vendor)
            await seed_blog_posts(db)

            print("\n" + "=" * 60)
            print("SEED COMPLETE!")
            print("=" * 60)
            print("\nSummary:")
            for model, name in [
                (Destination, "Destinations"),
                (Property, "Properties"),
                (Tour, "Tours"),
                (BlogPost, "Blog Posts"),
            ]:
                result = await db.execute(select(func.count(model.id)))
                print(f"  {name}: {result.scalar()}")
            print("\nAll data is now editable from the backend!")

        except Exception as e:
            print(f"\nError seeding data: {e}")
            await db.rollback()
            raise


if __name__ == "__main__":
    asyncio.run(main())
