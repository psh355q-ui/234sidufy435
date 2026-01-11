"""
Multi-Strategy Orchestration API Contracts (Draft)
Phase 0, Task T0.5

This file defines the API contract for the Strategy Management System.
It serves as the specification for the implementation of `backend/api/strategy_router.py`.

RESTful Resource Structure:
- /strategies
    - GET /: List strategies
    - POST /: Create strategy
    - GET /{id}: Get strategy details
    - PUT /{id}: Update strategy
    - DELETE /{id}: Delete strategy
    - POST /{id}/activate: Activate
    - POST /{id}/deactivate: Deactivate

- /positions/ownership
    - GET /: List ownerships (filter by ticker, strategy)
    - GET /{ticker}/primary: Get primary owner
    - POST /acquire: Acquire ownership
    - POST /transfer: Transfer ownership
    - DELETE /{id}: Release ownership

- /conflicts
    - POST /check: Check for potential conflict (Dry Run)
    - GET /logs: Get conflict logs (filter by ticker, strategy, date)

Error Responses:
- 400 Bad Request: Validation errors
- 404 Not Found: Resource not found
- 409 Conflict: Ownership conflict or state conflict
- 422 Unprocessable Entity: Business logic violation (e.g. invalid transition)
- 500 Internal Server Error: Unexpected system error

Authentication:
- All endpoints require valid API Key or JWT (Admin role preferred for write ops).
"""

from typing import List, Optional, Union
from typing import Protocol # or abstractmethod
from backend.api.schemas.strategy_schemas import (
    StrategyCreate, StrategyUpdate, StrategyResponse,
    PositionOwnershipCreate, PositionOwnershipResponse, PositionOwnershipWithStrategy,
    ConflictLogResponse, ConflictCheckRequest, ConflictCheckResponse,
    BulkStrategyActivateRequest, BulkOperationResponse
)

# Using Protocol to define the Interface expected from the Service/Router layer
# This is documentation-as-code.

class StrategyAPIContract(Protocol):
    """
    Contract for Strategy Management API
    Base Path: /api/v1/strategies
    """

    async def list_strategies(self, active_only: bool = False) -> List[StrategyResponse]:
        """
        GET /
        Query Params:
            active_only (bool): If true, return only active strategies.
        """
        ...

    async def create_strategy(self, strategy: StrategyCreate) -> StrategyResponse:
        """
        POST /
        Body: StrategyCreate
        Returns: 201 Created
        Error: 409 Conflict (Duplicate Name)
        """
        ...

    async def get_strategy(self, strategy_id: str) -> StrategyResponse:
        """
        GET /{strategy_id}
        Returns: 200 OK
        Error: 404 Not Found
        """
        ...

    async def update_strategy(self, strategy_id: str, strategy: StrategyUpdate) -> StrategyResponse:
        """
        PUT /{strategy_id}
        Body: StrategyUpdate (Partial fields allowed)
        Returns: 200 OK
        Error: 404 Not Found
        Note: JSONB fields are merged or replaced based on implementation (Specify: Replace)
        """
        ...

    async def delete_strategy(self, strategy_id: str) -> None:
        """
        DELETE /{strategy_id}
        Returns: 204 No Content
        Error: 404 Not Found, 409 Conflict (If ownership exists)
        """
        ...

    async def activate_strategy(self, strategy_id: str) -> StrategyResponse:
        """
        POST /{strategy_id}/activate
        Returns: 200 OK
        """
        ...

    async def deactivate_strategy(self, strategy_id: str) -> StrategyResponse:
        """
        POST /{strategy_id}/deactivate
        Returns: 200 OK
        Side Effect: Does NOT release ownerships automatically (unless implemented)
        """
        ...
    
    async def bulk_activate(self, request: BulkStrategyActivateRequest) -> BulkOperationResponse:
        """
        POST /bulk/activate
        Body: { strategy_ids: [...], is_active: bool }
        """
        ...

class OwnershipAPIContract(Protocol):
    """
    Contract for Position Ownership API
    Base Path: /api/v1/positions/ownership
    """

    async def list_ownerships(self, 
                              ticker: Optional[str] = None, 
                              strategy_id: Optional[str] = None) -> List[PositionOwnershipWithStrategy]:
        """
        GET /
        Query Params: ticker, strategy_id
        Returns: List of ownerships with strategy details
        """
        ...

    async def get_primary_owner(self, ticker: str) -> PositionOwnershipResponse:
        """
        GET /{ticker}/primary
        Returns: Primary ownership record
        Error: 404 Not Found (If no primary owner)
        """
        ...

    async def acquire_ownership(self, request: PositionOwnershipCreate) -> PositionOwnershipResponse:
        """
        POST /acquire
        Body: PositionOwnershipCreate
        Returns: 201 Created
        Error: 409 Conflict (If primary already exists)
        """
        ...
        
    # Transfer endpoint might be needed if not handled purely via conflict resolution
    async def transfer_ownership(self, ticker: str, to_strategy_id: str, reasoning: str) -> PositionOwnershipResponse:
        """
        POST /transfer
        Body: { ticker, to_strategy_id, reasoning }
        Returns: 200 OK (New ownership)
        Error: 404 (No current owner), 409 (Lock conflict)
        """
        ...

class ConflictAPIContract(Protocol):
    """
    Contract for Conflict Management API
    Base Path: /api/v1/conflicts
    """

    async def check_conflict(self, request: ConflictCheckRequest) -> ConflictCheckResponse:
        """
        POST /check
        Body: ConflictCheckRequest (ticker, action, strategy_id)
        Returns: Check result (Allowed/Blocked/Override + Reasoning)
        Note: This is a read-only simulation (Dry Run) usually. 
        If used for actual pre-trade check, it should be fast.
        """
        ...

    async def list_conflict_logs(self, 
                                 ticker: Optional[str] = None, 
                                 days: int = 7) -> List[ConflictLogResponse]:
        """
        GET /logs
        Query Params: ticker, days
        Returns: Recent conflict logs
        """
        ...
