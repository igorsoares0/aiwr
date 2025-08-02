#!/usr/bin/env python3
"""
Production runner for Writify
"""

from app import create_app
from security import SecurityHeaders

app = create_app()
SecurityHeaders.init_app(app)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)