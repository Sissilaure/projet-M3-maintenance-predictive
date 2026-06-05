#!/usr/bin/env python
"""Debug script to identify startup issues."""
import sys
print("Step 1: Python started", file=sys.stderr, flush=True)

try:
    print("Step 2: Importing FastAPI...", file=sys.stderr, flush=True)
    from fastapi import FastAPI
    print("Step 2: OK - FastAPI imported", file=sys.stderr, flush=True)
except Exception as e:
    print(f"Step 2: FAILED - {e}", file=sys.stderr, flush=True)
    sys.exit(1)

try:
    print("Step 3: Importing training_service...", file=sys.stderr, flush=True)
    from backend.app.services.training_service import train_all
    print("Step 3: OK - training_service imported", file=sys.stderr, flush=True)
except Exception as e:
    print(f"Step 3: FAILED - {e}", file=sys.stderr, flush=True)
    sys.exit(1)

try:
    print("Step 4: Creating train router...", file=sys.stderr, flush=True)
    from fastapi import APIRouter, BackgroundTasks, HTTPException
    from datetime import datetime
    
    print("Step 4a: Creating APIRouter...", file=sys.stderr, flush=True)
    router = APIRouter(tags=["training"])
    print("Step 4b: Defining functions...", file=sys.stderr, flush=True)
    
    def _test_func():
        pass
    
    print("Step 4: OK - train module code works", file=sys.stderr, flush=True)
except Exception as e:
    print(f"Step 4: FAILED - {e}", file=sys.stderr, flush=True)
    sys.exit(1)

try:
    print("Step 5: Importing train route...", file=sys.stderr, flush=True)
    from backend.app.routes import train
    print("Step 5: OK - train route imported", file=sys.stderr, flush=True)
except Exception as e:
    print(f"Step 5: FAILED - {e}", file=sys.stderr, flush=True)
    import traceback
    traceback.print_exc(file=sys.stderr)
    sys.exit(1)

print("All steps completed successfully!", file=sys.stderr, flush=True)

