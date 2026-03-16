"""Allow running as: python -m mcp.server"""
import asyncio
from .server import main

asyncio.run(main())
