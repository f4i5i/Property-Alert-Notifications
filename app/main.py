from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
import uvicorn

from .models import UserPreferences
from .schemas import UserPreferenceRequest, UserPreferenceResponse
from .database import SessionLocal, engine, Base
from .crud import get_user_preferences, create_or_update_user_preferences
import queue
import threading


Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Initialize a queue for task management
task_queue = queue.Queue()

# Background task to process queued tasks
def process_tasks():
    while True:
        task_data = task_queue.get()
        user_id = task_data.get("user_id")
        email_enabled = task_data.get("email_enabled")
        sms_enabled = task_data.get("sms_enabled")
        # Simulate sending notifications
        messages = []
        if email_enabled:
            messages.append(f"Email would be sent for Property Listing & offers to {user_id}")
        if sms_enabled:
            messages.append(f"SMS would be sent for Property Listing & offers to {user_id}")
        print("Processing task:", messages)
        # Mark task as done
        task_queue.task_done()

# Start background task to process queued tasks
task_thread = threading.Thread(target=process_tasks)
task_thread.daemon = True
task_thread.start()

@app.post("/preferences/{user_id}", response_model=UserPreferenceResponse)
def update_user_preferences(user_id: int, pref_request: UserPreferenceRequest, db: Session = Depends(get_db)):
    return create_or_update_user_preferences(db, user_id=user_id, **pref_request.model_dump())


@app.get("/preferences/{user_id}", response_model= UserPreferenceResponse)
def read_user_preferences(user_id: int, db: Session = Depends(get_db)):
    user_pref = get_user_preferences(db, user_id=user_id)
    if user_pref is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user_pref


@app.post("/notifications/{user_id}")
def schedule_notifications(user_id: int, db: Session = Depends(get_db)):
    user_prefs = get_user_preferences(db, user_id=user_id)
    if user_prefs is None:
        raise HTTPException(status_code=404, detail="User preferences not found")
    
    # Enqueue task to send notifications
    task_data = {"user_id": user_id, "email_enabled": user_prefs.email_enabled, "sms_enabled": user_prefs.sms_enabled}
    task_queue.put(task_data)

    # Determine the notification delivery method
    delivery_method = []
    if user_prefs.email_enabled:
        delivery_method.append("Email")
    if user_prefs.sms_enabled:
        delivery_method.append("SMS")

    # Construct response message
    if delivery_method:
        return {"message": f"Notifications scheduled successfully via {', '.join(delivery_method)}"}
    else:
        return {"message": "No notification method enabled. Notifications not scheduled."}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)