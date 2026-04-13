import json
import pytest
from minimythos.models.file_score import FileScore, ScoreBatch, VulnerabilityScoreFile


def test_file_score_creation():
    fs = FileScore(path="src/main.py", score=8, reason="Handles user input unsafely")
    assert fs.path == "src/main.py"
    assert fs.score == 8
    assert fs.reason == "Handles user input unsafely"


def test_score_batch_with_scores():
    scores = [
        FileScore(path="a.py", score=7, reason="high"),
        FileScore(path="b.py", score=3, reason="low"),
    ]
    sb = ScoreBatch(batch_id=1, files=["a.py", "b.py"], scores=scores)
    assert len(sb.scores) == 2
    assert sb.scores[0].score == 7


def test_vulnerability_score_file_round_trip():
    scores = [FileScore(path="a.py", score=10, reason="critical")]
    batches = [ScoreBatch(batch_id=0, files=["a.py"], scores=scores)]
    vsf = VulnerabilityScoreFile(target_path="/project", batches=batches)
    json_str = vsf.model_dump_json()
    restored = VulnerabilityScoreFile.model_validate_json(json_str)
    assert restored.batches[0].scores[0].score == 10
