import redis
import os
import json

def get_farmer_profile(r, farmer_id):
    profile = r.get(f"farmer:{farmer_id}:profile")
    if profile:
        return json.loads(profile)
    return {}

def update_farmer_profile(r, farmer_id, updates):
    profile = get_farmer_profile(r, farmer_id)
    profile.update(updates)
    r.set(f"farmer:{farmer_id}:profile", json.dumps(profile))

def personalize_advisory(farmer_id, intent):
    r = redis.Redis(host=os.getenv("REDIS_HOST", "localhost"), port=6379, db=0)
    profile = get_farmer_profile(r, farmer_id)
    # Example: personalize based on crop, region, last yield, etc.
    crop = profile.get("crop", "unknown crop")
    region = profile.get("region", "unknown region")
    last_yield = profile.get("last_yield", "N/A")
    personalization = (
        f"Advisory for {crop} in {region}. Last yield: {last_yield}. "
        f"Intent: {intent}."
    )
    return personalization