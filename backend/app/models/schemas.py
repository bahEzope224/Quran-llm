from pydantic import BaseModel, Field


class SourceItem(BaseModel):
    type: str = Field(..., examples=["quran", "tafsir", "hadith"])
    ref: str
    text: str
    source: str | None = None
    role: str | None = None
    arabic: str | None = None


class UserProfile(BaseModel):
    legal_school: str
    language: str
    mode: str
    notifications_enabled: bool = True


class ChatRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=3,
        examples=["Quelles sont les vertus de la patience ?"],
    )
    mode: str = Field(default="response", examples=["response", "proofs"])
    profile: UserProfile


class ChatResponse(BaseModel):
    answer: str
    sources: list[SourceItem]


class UserProfileResponse(BaseModel):
    name: str
    avatar_initials: str
    legal_school: str
    language: str
    mode: str
    notifications_enabled: bool
