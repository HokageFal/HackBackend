from pydantic import BaseModel

class AddSubscriptionRequest(BaseModel):
    plan_id: int
