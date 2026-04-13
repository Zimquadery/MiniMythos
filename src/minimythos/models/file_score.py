from pydantic import BaseModel


class FileScore(BaseModel):
    path: str
    score: int
    reason: str


class ScoreBatch(BaseModel):
    batch_id: int
    files: list[str]
    scores: list[FileScore] = []


class VulnerabilityScoreFile(BaseModel):
    target_path: str
    batches: list[ScoreBatch]
