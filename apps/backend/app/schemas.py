from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = "ok"


class SignedUploadRequest(BaseModel):
    bucket: str = Field(default="files")
    path: str = Field(..., description="Storage path, e.g. userId/tasks/taskId/file.pdf")
    content_type: str | None = None


class SignedUploadResponse(BaseModel):
    bucket: str
    path: str
    signed_url: str
    token: str | None = None


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    mode: str = Field(default="learn", description="learn | review")
    task_id: str | None = None


class ChatResponse(BaseModel):
    answer: str

