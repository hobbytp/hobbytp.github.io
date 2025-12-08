# Spec Delta: docs-python3

## ADDED Requirements

### Requirement: Integrate Python 3.14 updates into `content/zh/technologies/python3.md`

The documentation SHALL integrate Python 3.14 changes into existing chapters without creating a standalone "3.14" section.

#### Scenario: Annotations and typing updates (PEP 649/749)

- WHEN reading chapters on annotations/typing (Ch.1 and Ch.4)
- THEN readers see deferred-evaluation semantics and `annotationlib` usage (value/forwardref/string) with a minimal example
- AND forward references no longer require string quotes on 3.14+
- AND the doc provides cross-version guidance

#### Scenario: Concurrency and interpreters (PEP 734, PEP 779)

- WHEN reading the concurrency chapter (Ch.5)
- THEN readers see the new `concurrent.interpreters` APIs and `InterpreterPoolExecutor` with positioning vs multiprocessing/threads
- AND the free-threaded (no-GIL) build official support status is summarized with cautions
- AND Unix default `forkserver` change is noted for `multiprocessing`/`ProcessPoolExecutor`
- AND asyncio introspection/call graph tips are included

#### Scenario: Advanced expressions and built-ins (PEP 750 and tweaks)

- WHEN reading advanced expressions (Ch.6)
- THEN readers see template string literals (t-strings) with 1–2 concise examples and contrast with f-strings
- AND built-in tweaks (e.g., `map(strict=...)`, `memoryview` generic, `NotImplemented` boolean context TypeError) are summarized

#### Scenario: Exceptions and diagnostics (PEP 758, PEP 765, error messages)

- WHEN reading exception handling and diagnostics (Ch.7)
- THEN readers see bracket-less `except`/`except*` (PEP 758) and `finally` flow warnings (PEP 765)
- AND a short note on `sys.remote_exec` and `pdb -p` is added near error-reporting improvements

#### Scenario: Standard library, platforms, and performance (PEP 784 etc.)

- WHEN reading performance/platform sections (Ch.8 and summary)
- THEN readers see zstandard module availability and positioning (PEP 784)
- AND new platform/build notes (JIT binaries, Android releases, Emscripten tier 3) are summarized with stability notes
- AND incremental GC and related runtime behavior changes are noted

#### Scenario: Style and lint

- GIVEN markdown linting and Hugo style conventions
- WHEN integrating content
- THEN no inline HTML is introduced
- AND links resolve to official docs/PEPs
- AND local preview renders correctly
