"""Integration tests for style templates API endpoints.

Tests template management including CRUD, filtering, and usage tracking.
"""

import pytest


# =============================================================================
# Test Fixtures
# =============================================================================


@pytest.fixture
def template_factory(test_db, test_user):
    """Factory for creating test style templates."""
    from app.models.style_template import StyleTemplate

    def create_template(
        name: str = "Test Template",
        genre: str = "Pop",
        is_public: bool = True,
        **kwargs,
    ) -> StyleTemplate:
        template = StyleTemplate(
            name=name,
            description=kwargs.get("description", "A test template"),
            style_prompt=kwargs.get("style_prompt", "Pop song, upbeat, catchy"),
            genre=genre,
            sub_genre=kwargs.get("sub_genre"),
            mood=kwargs.get("mood", "happy"),
            energy=kwargs.get("energy", "high"),
            tags=kwargs.get("tags", "pop,upbeat,test"),
            is_public=is_public,
            is_featured=kwargs.get("is_featured", False),
            usage_count=kwargs.get("usage_count", 0),
            created_by_id=kwargs.get("created_by_id", test_user.id),
        )
        test_db.add(template)
        test_db.commit()
        test_db.refresh(template)
        return template

    return create_template


# =============================================================================
# List Templates Tests
# =============================================================================


@pytest.mark.integration
@pytest.mark.api
class TestListTemplates:
    """Test template listing functionality."""

    def test_list_templates_empty(self, client, auth_headers):
        """Test listing templates when database is empty."""
        response = client.get("/api/v1/templates", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0

    def test_list_templates_with_data(self, client, auth_headers, template_factory):
        """Test listing templates with existing data."""
        template_factory(name="Template 1", genre="Pop")
        template_factory(name="Template 2", genre="Rock")
        template_factory(name="Template 3", genre="Pop")

        response = client.get("/api/v1/templates", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 3
        assert data["total"] == 3

    def test_list_templates_filter_by_genre(self, client, auth_headers, template_factory):
        """Test filtering templates by genre."""
        template_factory(name="Pop Template 1", genre="Pop")
        template_factory(name="Rock Template", genre="Rock")
        template_factory(name="Pop Template 2", genre="Pop")

        response = client.get(
            "/api/v1/templates",
            params={"genre": "Pop"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2
        assert all(item["genre"] == "Pop" for item in data["items"])

    def test_list_templates_filter_by_mood(self, client, auth_headers, template_factory):
        """Test filtering templates by mood."""
        template_factory(name="Happy Template", mood="happy")
        template_factory(name="Sad Template", mood="sad")
        template_factory(name="Another Happy", mood="happy")

        response = client.get(
            "/api/v1/templates",
            params={"mood": "happy"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2

    def test_list_templates_filter_by_energy(self, client, auth_headers, template_factory):
        """Test filtering templates by energy level."""
        template_factory(name="High Energy", energy="high")
        template_factory(name="Low Energy", energy="low")
        template_factory(name="Medium Energy", energy="medium")

        response = client.get(
            "/api/v1/templates",
            params={"energy": "high"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1

    def test_list_templates_search(self, client, auth_headers, template_factory):
        """Test searching templates."""
        template_factory(name="Summer Vibes", description="A summer song template")
        template_factory(name="Winter Blues", description="A melancholy winter template")
        template_factory(name="Party Mix", description="Upbeat party music")

        response = client.get(
            "/api/v1/templates",
            params={"search": "summer"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert "Summer" in data["items"][0]["name"]

    def test_list_templates_featured_only(self, client, auth_headers, template_factory):
        """Test filtering for featured templates only."""
        template_factory(name="Featured Template", is_featured=True)
        template_factory(name="Regular Template", is_featured=False)
        template_factory(name="Another Featured", is_featured=True)

        response = client.get(
            "/api/v1/templates",
            params={"featured_only": True},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2
        assert all(item["is_featured"] is True for item in data["items"])

    def test_list_templates_my_templates(self, client, auth_headers, template_factory, test_admin):
        """Test filtering for user's own templates."""
        template_factory(name="My Template 1")
        template_factory(name="My Template 2")
        template_factory(name="Admin Template", created_by_id=test_admin.id)

        response = client.get(
            "/api/v1/templates",
            params={"my_templates": True},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2

    def test_list_templates_pagination(self, client, auth_headers, template_factory):
        """Test pagination of template listing."""
        for i in range(10):
            template_factory(name=f"Template {i}")

        response = client.get(
            "/api/v1/templates",
            params={"page": 1, "per_page": 3},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 3
        assert data["total"] == 10
        assert data["page"] == 1
        assert data["per_page"] == 3
        assert data["pages"] == 4

    def test_list_templates_public_visibility(
        self, client, auth_headers, template_factory, test_admin
    ):
        """Test that users see public templates and their own private ones."""
        template_factory(name="Public Template", is_public=True)
        template_factory(name="My Private", is_public=False)
        template_factory(name="Other Private", is_public=False, created_by_id=test_admin.id)

        response = client.get("/api/v1/templates", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        # Should see public + own private, not other's private
        assert len(data["items"]) == 2

    def test_list_templates_unauthorized(self, client):
        """Test listing templates without authentication."""
        response = client.get("/api/v1/templates")
        assert response.status_code == 403


# =============================================================================
# Get Template Tests
# =============================================================================


@pytest.mark.integration
@pytest.mark.api
class TestGetTemplate:
    """Test getting individual template details."""

    def test_get_template_success(self, client, auth_headers, template_factory):
        """Test successful template retrieval."""
        template = template_factory(
            name="Test Template",
            genre="Pop",
            style_prompt="Pop song, upbeat, catchy hooks",
        )

        response = client.get(f"/api/v1/templates/{template.id}", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == template.id
        assert data["name"] == "Test Template"
        assert data["genre"] == "Pop"
        assert data["style_prompt"] == "Pop song, upbeat, catchy hooks"

    def test_get_template_not_found(self, client, auth_headers):
        """Test getting non-existent template."""
        response = client.get("/api/v1/templates/nonexistent-id", headers=auth_headers)
        assert response.status_code == 404

    def test_get_template_private_not_owner(
        self, client, auth_headers, template_factory, test_admin
    ):
        """Test accessing private template by non-owner."""
        template = template_factory(
            name="Private Template",
            is_public=False,
            created_by_id=test_admin.id,
        )

        response = client.get(f"/api/v1/templates/{template.id}", headers=auth_headers)
        assert response.status_code == 403

    def test_get_template_private_owner(self, client, auth_headers, template_factory):
        """Test owner can access their private template."""
        template = template_factory(name="My Private", is_public=False)

        response = client.get(f"/api/v1/templates/{template.id}", headers=auth_headers)
        assert response.status_code == 200


# =============================================================================
# Create Template Tests
# =============================================================================


@pytest.mark.integration
@pytest.mark.api
class TestCreateTemplate:
    """Test template creation."""

    def test_create_template_success(self, client, auth_headers):
        """Test successful template creation."""
        template_data = {
            "name": "New Template",
            "genre": "Rock",
            "style_prompt": "Rock song with heavy guitars and powerful drums",
            "description": "A rock template for epic songs",
            "mood": "energetic",
            "energy": "high",
            "tags": ["rock", "heavy", "epic"],
        }

        response = client.post(
            "/api/v1/templates",
            json=template_data,
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "New Template"
        assert data["genre"] == "Rock"
        assert data["is_public"] is True
        assert data["usage_count"] == 0

    def test_create_template_minimal_data(self, client, auth_headers):
        """Test creating template with minimal required data."""
        template_data = {
            "name": "Minimal Template",
            "genre": "Pop",
            "style_prompt": "Pop song",
        }

        response = client.post(
            "/api/v1/templates",
            json=template_data,
            headers=auth_headers,
        )

        assert response.status_code == 201

    def test_create_template_private(self, client, auth_headers):
        """Test creating private template."""
        template_data = {
            "name": "Private Template",
            "genre": "Jazz",
            "style_prompt": "Jazz song",
            "is_public": False,
        }

        response = client.post(
            "/api/v1/templates",
            json=template_data,
            headers=auth_headers,
        )

        assert response.status_code == 201
        assert response.json()["is_public"] is False

    def test_create_template_invalid_energy(self, client, auth_headers):
        """Test creating template with invalid energy level."""
        template_data = {
            "name": "Test",
            "genre": "Pop",
            "style_prompt": "Test",
            "energy": "extreme",  # Invalid - should be low/medium/high
        }

        response = client.post(
            "/api/v1/templates",
            json=template_data,
            headers=auth_headers,
        )

        assert response.status_code == 422

    def test_create_template_unauthorized(self, client):
        """Test creating template without authentication."""
        response = client.post(
            "/api/v1/templates",
            json={"name": "Test", "genre": "Pop", "style_prompt": "Test"},
        )
        assert response.status_code == 403


# =============================================================================
# Update Template Tests
# =============================================================================


@pytest.mark.integration
@pytest.mark.api
class TestUpdateTemplate:
    """Test template update functionality."""

    def test_update_template_success(self, client, auth_headers, template_factory):
        """Test successful template update."""
        template = template_factory(name="Original Name")

        response = client.put(
            f"/api/v1/templates/{template.id}",
            json={"name": "Updated Name"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        assert response.json()["name"] == "Updated Name"

    def test_update_template_multiple_fields(self, client, auth_headers, template_factory):
        """Test updating multiple template fields."""
        template = template_factory(name="Original", genre="Pop", mood="happy")

        response = client.put(
            f"/api/v1/templates/{template.id}",
            json={
                "name": "Updated",
                "genre": "Rock",
                "mood": "energetic",
                "tags": ["rock", "updated"],
            },
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated"
        assert data["genre"] == "Rock"
        assert data["mood"] == "energetic"

    def test_update_template_not_owner(
        self, client, auth_headers, template_factory, test_admin
    ):
        """Test updating template by non-owner."""
        template = template_factory(name="Admin Template", created_by_id=test_admin.id)

        response = client.put(
            f"/api/v1/templates/{template.id}",
            json={"name": "Hacked Name"},
            headers=auth_headers,
        )

        assert response.status_code == 403

    def test_update_template_admin_can_update(
        self, client, admin_auth_headers, template_factory, test_user
    ):
        """Test admin can update any template."""
        template = template_factory(name="User Template", created_by_id=test_user.id)

        response = client.put(
            f"/api/v1/templates/{template.id}",
            json={"name": "Admin Updated"},
            headers=admin_auth_headers,
        )

        assert response.status_code == 200

    def test_update_template_not_found(self, client, auth_headers):
        """Test updating non-existent template."""
        response = client.put(
            "/api/v1/templates/nonexistent-id",
            json={"name": "New Name"},
            headers=auth_headers,
        )
        assert response.status_code == 404


# =============================================================================
# Delete Template Tests
# =============================================================================


@pytest.mark.integration
@pytest.mark.api
class TestDeleteTemplate:
    """Test template deletion."""

    def test_delete_template_success(self, client, auth_headers, template_factory):
        """Test successful template deletion."""
        template = template_factory(name="To Delete")

        response = client.delete(
            f"/api/v1/templates/{template.id}",
            headers=auth_headers,
        )

        assert response.status_code == 204

        # Verify deleted
        get_response = client.get(
            f"/api/v1/templates/{template.id}",
            headers=auth_headers,
        )
        assert get_response.status_code == 404

    def test_delete_template_not_owner(
        self, client, auth_headers, template_factory, test_admin
    ):
        """Test deleting template by non-owner."""
        template = template_factory(name="Admin Template", created_by_id=test_admin.id)

        response = client.delete(
            f"/api/v1/templates/{template.id}",
            headers=auth_headers,
        )

        assert response.status_code == 403

    def test_delete_template_admin_can_delete(
        self, client, admin_auth_headers, template_factory, test_user
    ):
        """Test admin can delete any template."""
        template = template_factory(name="User Template", created_by_id=test_user.id)

        response = client.delete(
            f"/api/v1/templates/{template.id}",
            headers=admin_auth_headers,
        )

        assert response.status_code == 204

    def test_delete_template_not_found(self, client, auth_headers):
        """Test deleting non-existent template."""
        response = client.delete("/api/v1/templates/nonexistent-id", headers=auth_headers)
        assert response.status_code == 404


# =============================================================================
# Use Template Tests
# =============================================================================


@pytest.mark.integration
@pytest.mark.api
class TestUseTemplate:
    """Test template usage tracking."""

    def test_use_template_success(self, client, auth_headers, template_factory):
        """Test incrementing template usage count."""
        template = template_factory(name="Popular Template", usage_count=5)

        response = client.post(
            f"/api/v1/templates/{template.id}/use",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["usage_count"] == 6

    def test_use_template_multiple_times(self, client, auth_headers, template_factory):
        """Test using template multiple times."""
        template = template_factory(name="Template", usage_count=0)

        for i in range(3):
            response = client.post(
                f"/api/v1/templates/{template.id}/use",
                headers=auth_headers,
            )
            assert response.status_code == 200
            assert response.json()["usage_count"] == i + 1

    def test_use_template_private_not_owner(
        self, client, auth_headers, template_factory, test_admin
    ):
        """Test using private template by non-owner."""
        template = template_factory(
            name="Private Template",
            is_public=False,
            created_by_id=test_admin.id,
        )

        response = client.post(
            f"/api/v1/templates/{template.id}/use",
            headers=auth_headers,
        )

        assert response.status_code == 403

    def test_use_template_not_found(self, client, auth_headers):
        """Test using non-existent template."""
        response = client.post(
            "/api/v1/templates/nonexistent-id/use",
            headers=auth_headers,
        )
        assert response.status_code == 404


# =============================================================================
# Toggle Featured Tests
# =============================================================================


@pytest.mark.integration
@pytest.mark.api
class TestToggleFeatured:
    """Test template featured status toggling."""

    def test_toggle_featured_admin(
        self, client, admin_auth_headers, template_factory
    ):
        """Test admin can toggle featured status."""
        template = template_factory(name="Template", is_featured=False)

        response = client.post(
            f"/api/v1/templates/{template.id}/feature",
            headers=admin_auth_headers,
        )

        assert response.status_code == 200
        assert response.json()["is_featured"] is True

        # Toggle again
        response = client.post(
            f"/api/v1/templates/{template.id}/feature",
            headers=admin_auth_headers,
        )

        assert response.status_code == 200
        assert response.json()["is_featured"] is False

    def test_toggle_featured_non_admin(self, client, auth_headers, template_factory):
        """Test non-admin cannot toggle featured status."""
        template = template_factory(name="Template")

        response = client.post(
            f"/api/v1/templates/{template.id}/feature",
            headers=auth_headers,
        )

        assert response.status_code == 403
        assert "admin" in response.json()["detail"].lower()

    def test_toggle_featured_not_found(self, client, admin_auth_headers):
        """Test toggling featured for non-existent template."""
        response = client.post(
            "/api/v1/templates/nonexistent-id/feature",
            headers=admin_auth_headers,
        )
        assert response.status_code == 404


# =============================================================================
# List Genres Tests
# =============================================================================


@pytest.mark.integration
@pytest.mark.api
class TestListGenres:
    """Test genre listing endpoint."""

    def test_list_genres_empty(self, client, auth_headers):
        """Test listing genres when no public templates exist."""
        response = client.get("/api/v1/templates/genres", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["genres"] == []

    def test_list_genres_with_templates(self, client, auth_headers, template_factory):
        """Test listing genres with existing templates."""
        template_factory(name="Pop 1", genre="Pop")
        template_factory(name="Pop 2", genre="Pop")
        template_factory(name="Rock 1", genre="Rock")
        template_factory(name="Jazz 1", genre="Jazz")

        response = client.get("/api/v1/templates/genres", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert len(data["genres"]) == 3

        # Pop should have highest count
        genres = {g["genre"]: g["count"] for g in data["genres"]}
        assert genres["Pop"] == 2
        assert genres["Rock"] == 1
        assert genres["Jazz"] == 1

    def test_list_genres_only_public(
        self, client, auth_headers, template_factory, test_admin
    ):
        """Test that only public templates count in genre list."""
        template_factory(name="Public Pop", genre="Pop", is_public=True)
        template_factory(name="Private Rock", genre="Rock", is_public=False, created_by_id=test_admin.id)

        response = client.get("/api/v1/templates/genres", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        genres = [g["genre"] for g in data["genres"]]
        assert "Pop" in genres
        assert "Rock" not in genres
