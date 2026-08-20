from app.agent import nodes


def test_rag_node_keeps_relevant_policy_documents(monkeypatch):
    monkeypatch.setattr(
        nodes,
        "search_policy",
        lambda query: [
            {
                "text": "Returns are accepted within the stated period.",
                "source": "returns.md",
                "distance": 1.1,
            }
        ],
    )

    result = nodes.rag_node({"message": "What is your return policy?"})

    assert len(result["retrieved_context"]) == 1
    assert result["sources"] == ["returns.md"]
    assert result["action"] == "KNOWLEDGE_LOOKUP"
