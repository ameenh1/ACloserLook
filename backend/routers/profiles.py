"""
FastAPI router for user profile management
Handles profile creation, updates, and retrieval with personalization data
"""

import logging
from datetime import datetime
from fastapi import APIRouter, HTTPException, status
from models.schemas import ProfileCreateRequest, ProfileResponse
from utils.supabase_client import get_supabase_client

logger = logging.getLogger(__name__)

# Create router (will be included in main.py with /api prefix)
router = APIRouter(tags=["Profiles"])


@router.post("/profiles", response_model=ProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_or_update_profile(request: ProfileCreateRequest) -> ProfileResponse:
    """
    Create or update a user profile with health sensitivities
    
    Args:
        request: Profile data including user_id and sensitivities list
        
    Returns:
        ProfileResponse with user profile details
        
    Raises:
        HTTPException 400: Invalid user_id or request data
        HTTPException 500: Database error
    """
    try:
        # Validate request data
        if not request.user_id or not request.user_id.strip():
            logger.warning("Profile creation request with empty user_id")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="user_id cannot be empty"
            )
        
        user_id = request.user_id.strip()
        logger.info(f"Processing profile request for user: {user_id}")
        
        # Get Supabase client
        supabase = get_supabase_client()
        
        # Prepare profile data
        now = datetime.utcnow()
        
        # Check if profile exists
        try:
            existing = supabase.table("profiles").select("*").eq("user_id", user_id).execute()
            profile_exists = len(existing.data) > 0
        except Exception as e:
            logger.error(f"Error checking existing profile: {e}")
            profile_exists = False
        
        # Prepare upsert data
        profile_data = {
            "user_id": user_id,
            "sensitivities": request.sensitivities,
            "updated_at": now.isoformat() + "Z"
        }
        
        # Add created_at only if new profile
        if not profile_exists:
            profile_data["created_at"] = now.isoformat() + "Z"
        
        # Upsert profile to database
        try:
            response = supabase.table("profiles").upsert(profile_data).execute()
            logger.info(f"Profile upserted for user: {user_id}")
        except Exception as e:
            logger.error(f"Error upserting profile to database: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to save profile: {str(e)}"
            )
        
        # Get scan history info
        scan_count = 0
        last_scan = None
        try:
            scans = supabase.table("scans").select("timestamp").eq("user_id", user_id).order("timestamp", desc=True).limit(1).execute()
            if scans.data and len(scans.data) > 0:
                scan_count = len(supabase.table("scans").select("id").eq("user_id", user_id).execute().data)
                last_scan_str = scans.data[0].get("timestamp")
                if last_scan_str:
                    last_scan = datetime.fromisoformat(last_scan_str.replace("Z", "+00:00"))
        except Exception as e:
            logger.debug(f"Could not fetch scan history: {e}")
        
        # Parse response data
        created_at_str = response.data[0].get("created_at") if response.data else now.isoformat() + "Z"
        updated_at_str = response.data[0].get("updated_at") if response.data else now.isoformat() + "Z"
        
        # Ensure proper ISO format
        try:
            created_at = datetime.fromisoformat(created_at_str.replace("Z", "+00:00"))
            updated_at = datetime.fromisoformat(updated_at_str.replace("Z", "+00:00"))
        except:
            created_at = now
            updated_at = now
        
        profile_response = ProfileResponse(
            user_id=user_id,
            sensitivities=request.sensitivities,
            created_at=created_at,
            updated_at=updated_at,
            scan_history_count=scan_count,
            last_scan_date=last_scan
        )
        
        logger.info(f"Profile created/updated successfully for user: {user_id}")
        return profile_response
    
    except HTTPException:
        raise
    
    except Exception as e:
        logger.error(f"Unexpected error in create_or_update_profile: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )


@router.get("/profiles/{user_id}", response_model=ProfileResponse)
async def get_profile(user_id: str) -> ProfileResponse:
    """
    Retrieve user profile with sensitivities and scan history
    
    Args:
        user_id: Unique user identifier
        
    Returns:
        ProfileResponse with user profile and statistics
        
    Raises:
        HTTPException 404: User profile not found
        HTTPException 500: Database error
    """
    try:
        # Validate user_id
        if not user_id or not user_id.strip():
            logger.warning("Get profile request with empty user_id")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="user_id cannot be empty"
            )
        
        user_id = user_id.strip()
        logger.info(f"Fetching profile for user: {user_id}")
        
        # Get Supabase client
        supabase = get_supabase_client()
        
        # Fetch profile from database
        try:
            response = supabase.table("profiles").select("*").eq("user_id", user_id).execute()
        except Exception as e:
            logger.error(f"Error querying profiles table: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error: {str(e)}"
            )
        
        # Check if profile exists
        if not response.data or len(response.data) == 0:
            logger.warning(f"Profile not found for user: {user_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Profile not found for user_id: {user_id}"
            )
        
        profile_data = response.data[0]
        logger.debug(f"Profile data retrieved: {profile_data}")
        
        # Get scan history statistics
        scan_count = 0
        last_scan = None
        try:
            scans_response = supabase.table("scans").select("timestamp").eq("user_id", user_id).execute()
            if scans_response.data:
                scan_count = len(scans_response.data)
                # Get most recent scan
                scans_ordered = supabase.table("scans").select("timestamp").eq("user_id", user_id).order("timestamp", desc=True).limit(1).execute()
                if scans_ordered.data and len(scans_ordered.data) > 0:
                    last_scan_str = scans_ordered.data[0].get("timestamp")
                    if last_scan_str:
                        last_scan = datetime.fromisoformat(last_scan_str.replace("Z", "+00:00"))
        except Exception as e:
            logger.debug(f"Could not fetch scan history for user {user_id}: {e}")
        
        # Parse timestamps
        created_at_str = profile_data.get("created_at", datetime.utcnow().isoformat() + "Z")
        updated_at_str = profile_data.get("updated_at", datetime.utcnow().isoformat() + "Z")
        
        try:
            created_at = datetime.fromisoformat(created_at_str.replace("Z", "+00:00"))
            updated_at = datetime.fromisoformat(updated_at_str.replace("Z", "+00:00"))
        except:
            now = datetime.utcnow()
            created_at = now
            updated_at = now
        
        profile_response = ProfileResponse(
            user_id=user_id,
            sensitivities=profile_data.get("sensitivities", []),
            created_at=created_at,
            updated_at=updated_at,
            scan_history_count=scan_count,
            last_scan_date=last_scan
        )
        
        logger.info(f"Profile retrieved successfully for user: {user_id}")
        return profile_response
    
    except HTTPException:
        raise
    
    except Exception as e:
        logger.error(f"Unexpected error in get_profile: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )
