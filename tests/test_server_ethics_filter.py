
import pytest
from eff import server
import eff.retrieval


############
# FIXTURES #
############

@pytest.fixture
def rag_mode(monkeypatch):
    monkeypatch.setenv("SUPABASE_URL", "http://dummy")
    def fake_score_story(content, dimensions_path, model):
        return {
            "results": {
                "fairness": {"result": "fail", "reason": "not fair enough"},
                "privacy": {"result": "pass", "reason": "ok"},
            },
            "sources": ["should be ignored"],
        }
    monkeypatch.setattr(server, "score_story", fake_score_story)
    class DummyChunk:
        def __init__(self, text, source, score):
            self.text = text
            self.source = source
            self.score = score
    class DummyRetriever:
        def retrieve(self, query):
            if "fairness" in query:
                return [DummyChunk("chunk1", "src1", 0.9), DummyChunk("chunk2", "src2", 0.8)]
            return []
    monkeypatch.setattr(eff.retrieval, "get_retriever", lambda: DummyRetriever())


@pytest.fixture
def citation_mode(monkeypatch):
    monkeypatch.delenv("SUPABASE_URL", raising=False)
    def fake_score_story(content, dimensions_path, model):
        return {
            "results": {
                "privacy": {"result": "Needs Improvement", "reason": "not private enough"},
                "utility": {"result": "pass", "reason": "ok"},
            }
        }
    monkeypatch.setattr(server, "score_story", fake_score_story)
    async def fake_generate_and_verify_citations(dim, fail_or_ni, story, model):
        return [{"author": "A", "doi": "1"}, {"author": "B", "doi": "2"}]
    monkeypatch.setattr(server, "generate_and_verify_citations", fake_generate_and_verify_citations)

#########
# TESTS #
#########

@pytest.mark.asyncio
async def test_rag_sources_per_dimension(rag_mode):
    result = await server._run_ethics_filter("story", None)
    assert "sources" in result
    assert all(chunk["dimension"] == "fairness" for chunk in result["sources"])
    assert {chunk["snippet"] for chunk in result["sources"]} == {"chunk1", "chunk2"}


@pytest.mark.asyncio
async def test_citation_mode_sources(citation_mode):
    result = await server._run_ethics_filter("story", None)
    assert "sources" in result
    assert all(chunk["dimension"] == "privacy" for chunk in result["sources"])
    assert {chunk["author"] for chunk in result["sources"]} == {"A", "B"}
