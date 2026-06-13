#!/usr/bin/env python3
"""Quick backend test script"""

import sys

sys.path.insert(0, "/home/marcelo/Documents/costaricatravel.dev/backend")

try:
    print("Testing backend imports...")
    from app.main import app

    print("✅ App imports successfully")

    # List some routes
    routes = [r.path for r in app.routes if hasattr(r, "path")]
    print(f"✅ Found {len(routes)} routes")
    print(f"   Sample routes: {routes[:5]}")

    # Check auth routes specifically
    auth_routes = [r for r in app.routes if hasattr(r, "path") and "/auth" in r.path]
    print(f"✅ Found {len(auth_routes)} auth routes")
    for r in auth_routes[:3]:
        print(f"   - {r.path}")

    print("\n✅ ALL TESTS PASSED")

except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)
