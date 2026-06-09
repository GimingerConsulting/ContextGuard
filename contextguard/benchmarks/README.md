# ContextGuard Benchmark Harness

Run the local benchmark harness:

```bash
PYTHONPATH=. python3 benchmarks/run_benchmarks.py
```

It creates temporary fixture projects for:

- small web project
- medium Node project
- Python data project
- verbose test output
- large JSON
- repeated log errors
- existing undocumented repository

For each fixture, it runs the raw command and then:

```bash
contextguard capture -- <command>
contextguard report
```

Record raw bytes, compact bytes, ContextGuard overhead, execution time, information retained and error detection accuracy. Treat token numbers as estimates only. The main future metric is successfully completed coding tasks per Codex usage window.
