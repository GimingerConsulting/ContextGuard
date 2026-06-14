from benchmarks.real_codex_model_routing_ab import estimate_api_cost


def test_api_cost_estimate_uses_cached_input_price():
    result = {"input_tokens": 1_000_000, "cached_input_tokens": 800_000, "output_tokens": 100_000}

    assert estimate_api_cost(result, "gpt-5.5") == 4.4
    assert estimate_api_cost(result, "gpt-5.4-mini") == 0.66
