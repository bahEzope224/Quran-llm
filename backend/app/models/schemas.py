from pydantic import BaseModel, Field


class SourceItem(BaseModel):
    type: str = Field(..., examples=["quran", "tafsir", "hadith", "fatwa"])
    ref: str
    text: str
    source: str | None = None
    url: str | None = None
    role: str | None = None
    arabic: str | None = None
    original_text: str | None = None
    translation_source: str | None = None
    tags: list[str] = Field(default_factory=list)


class UserProfile(BaseModel):
    legal_school: str
    language: str
    mode: str
    notifications_enabled: bool = True
    accepted_privacy: bool = False
    accepted_cgu: bool = False


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
    accepted_privacy: bool
    accepted_cgu: bool


class FeedbackRequest(BaseModel):
    question: str
    answer: str
    feedback: str = Field(..., pattern="^(up|down)$")
    comment: str | None = None
    profile: UserProfile | None = None
    sources: list[SourceItem] = Field(default_factory=list)


class PolicyDocument(BaseModel):
    privacy_text: str
    terms_text: str
    updated_at: str | None = None


class PolicyUpdateRequest(BaseModel):
    privacy_text: str | None = None
    terms_text: str | None = None
