from authx import TokenPayload
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from src.schemas.video_schema import VideoCreate, VideoUpdate, VideoResponse
from src.schemas.responses.general_response import GeneralResponse
from src.usecases.video_usecase import VideoUseCase, get_video_use_case
from src.usecases.user_usecase import UserUseCase, get_user_use_case
from src.api.http.dependencies import security
from typing import List


router = APIRouter(prefix="/video", tags=["video"])
@router.post("/", dependencies=[Depends(
        security.access_token_required)], 
        response_model=GeneralResponse[VideoResponse])
async def create_video(
    video: VideoCreate,
    use_case: VideoUseCase = Depends(get_video_use_case),
) -> VideoResponse:
    """
    Create a new video.
    """
    try:
        new_video = await use_case.create_video(video)
        if not new_video:
            raise HTTPException(status_code=400, detail="Video creation failed")
        return GeneralResponse[VideoResponse](
            status="success",
            message="Video created successfully",
            data=new_video
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    

@router.get("/{video_id}", dependencies=[Depends(security.access_token_required)], response_model=GeneralResponse[VideoResponse])
async def get_video(
    video_id: int,
    use_case: VideoUseCase = Depends(get_video_use_case),
) -> VideoResponse:
    """
    Retrieve a video by ID.
    """
    try:
        video = await use_case.get_video(video_id)
        if not video:
            raise HTTPException(status_code=404, detail="Video not found")
        return GeneralResponse[VideoResponse](
            status="success",
            message="Video retrieved successfully",
            data=video
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    

@router.put("/{video_id}", dependencies=[Depends(security.access_token_required)], response_model=GeneralResponse[VideoResponse])
async def update_video(
    video_id: int,
    video: VideoUpdate,
    use_case: VideoUseCase = Depends(get_video_use_case),
) -> VideoResponse:
    """
    Update an existing video.
    """
    try:
        updated_video = await use_case.update_video(video_id, video)
        if not updated_video:
            raise HTTPException(status_code=404, detail="Video not found")
        return GeneralResponse[VideoResponse](
            status="success",
            message="Video updated successfully",
            data=updated_video
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    

@router.delete("/{video_id}", dependencies=[Depends(security.access_token_required)], response_model=GeneralResponse[bool])
async def delete_video(
    video_id: int,
    use_case: VideoUseCase = Depends(get_video_use_case),
) -> bool:
    """
    Delete a video by ID.
    """
    try:
        deleted = await use_case.delete_video(video_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Video not found")
        return GeneralResponse[bool](
            status="success",
            message="Video deleted successfully",
            data=deleted
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    

@router.get("/", dependencies=[Depends(security.access_token_required)], response_model=GeneralResponse[List[VideoResponse]])
async def list_videos(
    page: int = 1,
    limit: int = 10,
    use_case: VideoUseCase = Depends(get_video_use_case),
) -> List[VideoResponse]:
    """
    List videos with pagination.
    """
    try:
        videos = await use_case.list_videos(page, limit)
        return GeneralResponse[List[VideoResponse]](
            status="success",
            message="Videos retrieved successfully",
            data=videos
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    

@router.get("/users/{user_id}", dependencies=[Depends(security.access_token_required)], response_model=GeneralResponse[List[VideoResponse]])
async def get_videos_by_user(
    user_id: int,
    use_case: VideoUseCase = Depends(get_video_use_case),
) -> VideoResponse:
    """
    Retrieve videos by user ID.
    """
    try:
        video = await use_case.get_videos_by_fields(user_id=user_id)
        if not video:
            raise HTTPException(status_code=404, detail="Video not found")
        return GeneralResponse[List[VideoResponse]](
            status="success",
            message="Video retrieved successfully",
            data=video
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    

@router.post("/s3/upload", dependencies=[Depends(security.access_token_required)], response_model=GeneralResponse[VideoResponse])
async def upload_video_file(
    file: UploadFile = File(...),
    user: TokenPayload = Depends(security.access_token_required),
    video_use_case: VideoUseCase = Depends(get_video_use_case),
    user_use_case: UserUseCase = Depends(get_user_use_case),
) -> VideoResponse:
    try:
        user_info = await user_use_case.get_user_by_fields(email=user.sub)
        if not user_info:
            raise HTTPException(status_code=404, detail="User not found")
        
        # file_name = f"{user_info.email}/{file.filename}"
        video_url = await video_use_case.upload_video_file(user_info.id, file.file, f"{user_info.email}/{file.filename}")

        video = VideoCreate(
            user_id=user_info.id,
            file_url=video_url,
            file_name=file.filename  # ✅ now passed to DB
        )
        new_video = await video_use_case.create_video(video)

        return GeneralResponse[VideoResponse](
            status="success",
            message="Video uploaded successfully",
            data=new_video
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    