"""
Pytest configuration and shared fixtures for the Mergington High School Activities API tests.
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """
    Fixture that provides a TestClient instance for making synchronous requests to the FastAPI app.
    
    The TestClient is a wrapper around the ASGI app that allows us to make HTTP-style
    requests without running a live server.
    """
    return TestClient(app)
