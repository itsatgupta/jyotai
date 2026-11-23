"""App-wide FastAPI dependencies shared by every router."""

from typing import Annotated

from fastapi import Depends, Request

from astrologer.astrology.dasha import VimshottariDashaEngine


def get_dasha_engine(request: Request) -> VimshottariDashaEngine:
    """Return the one Vimshottari engine owned by the application.

    ``create_app`` installs the engine on ``app.state``; every router (context, Ask/analyze,
    consultation, insights, timing) receives this same instance so Dasha periods are never
    cut by a second, default-constructed engine.
    """
    engine = getattr(request.app.state, "dasha_engine", None)
    if engine is None:
        engine = VimshottariDashaEngine()
        request.app.state.dasha_engine = engine
    return engine


DashaEngineDependency = Annotated[VimshottariDashaEngine, Depends(get_dasha_engine)]
