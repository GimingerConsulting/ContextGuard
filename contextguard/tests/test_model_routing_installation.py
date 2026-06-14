from pathlib import Path

from contextguard.documentation import write_model_routing_agent


def test_model_routing_agent_pins_mini_model_and_medium_reasoning(tmp_path: Path):
    changed = write_model_routing_agent(tmp_path)
    agent = tmp_path / ".codex" / "agents" / "contextguard-worker.toml"

    assert changed is True
    content = agent.read_text(encoding="utf-8")
    assert 'name = "contextguard-worker"' in content
    assert 'model = "gpt-5.4-mini"' in content
    assert 'model_reasoning_effort = "medium"' in content
    assert "lower-cost gpt-5.4-mini execution worker" in content
    assert "Do not spawn subagents" in content
    assert "focused tests" in content


def test_model_routing_installation_preserves_other_agents(tmp_path: Path):
    agents = tmp_path / ".codex" / "agents"
    agents.mkdir(parents=True)
    custom = agents / "user-reviewer.toml"
    custom.write_text('name = "user-reviewer"\n', encoding="utf-8")

    write_model_routing_agent(tmp_path)

    assert custom.read_text(encoding="utf-8") == 'name = "user-reviewer"\n'
