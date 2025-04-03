from fastapi import APIRouter
from app.api.routes.auth import router as auth_router
from app.api.routes.test_papers import router as test_papers_router
from app.api.routes.questions import router as questions_router
from app.api.routes.results import router as results_router

# Create main API router
router = APIRouter(prefix="/api")

# Include all sub-routers
router.include_router(auth_router)
router.include_router(test_papers_router)
router.include_router(questions_router)
router.include_router(results_router)

# Add more routers here as they are created 