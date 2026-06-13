"""
Unit tests for Destination schemas
"""

import pytest
from uuid import uuid4


class TestDestinationSchemas:
    def test_destination_create_valid(self):
        from app.schemas import DestinationCreate

        data = DestinationCreate(
            name="Guanacaste",
            description="Beautiful beaches",
            region="Pacific",
            province="Guanacaste",
        )
        assert data.name == "Guanacaste"
        assert data.region == "Pacific"
        assert data.province == "Guanacaste"

    def test_destination_create_minimal(self):
        from app.schemas import DestinationCreate

        data = DestinationCreate(name="San José", region="Central Valley")
        assert data.name == "San José"
        assert data.description is None
        assert data.province is None

    def test_destination_create_name_too_short(self):
        from app.schemas import DestinationCreate

        with pytest.raises(ValueError):
            DestinationCreate(name="X", region="Test")

    def test_destination_update_partial(self):
        from app.schemas import DestinationUpdate

        data = DestinationUpdate(description="Nice beaches and forests")
        assert data.description == "Nice beaches and forests"
        assert data.name is None

    def test_destination_response(self):
        from app.schemas import DestinationResponse

        data = DestinationResponse(
            id=uuid4(),
            name="Manuel Antonio",
            region="Pacific",
            province="Puntarenas",
            is_featured=True,
            is_active=True,
        )
        assert data.name == "Manuel Antonio"
        assert data.is_featured is True
        assert data.is_active is True


class TestDestinationImports:
    def test_router_import(self):
        from app.api.v1.destinations import router

        assert router

    def test_schemas_import(self):
        from app.schemas import (
            DestinationCreate,
            DestinationUpdate,
            DestinationResponse,
        )

        assert DestinationCreate
        assert DestinationUpdate
        assert DestinationResponse
