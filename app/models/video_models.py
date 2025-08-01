from typing import Optional
from pydantic import BaseModel

class VideoDownloadRequest(BaseModel):
    url: str
    filename: Optional[str] = None
    validate: bool = True
    cookies: Optional[str] = None
    cookies_from_browser: Optional[str] = None

class VideoCutRequest(BaseModel):
    video_id: str
    start_time: str
    end_time: str
    output_filename: Optional[str] = None

class DownloadAndCutRequest(BaseModel):
    url: str
    start_time: str
    end_time: str
    filename: Optional[str] = None
    output_filename: Optional[str] = None
    cookies: Optional[str] = None
    cookies_from_browser: Optional[str] = None

class HealthResponse(BaseModel):
    status: str
    message: str
    timestamp: str