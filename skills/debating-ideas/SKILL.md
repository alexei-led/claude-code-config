---
name: debating-ideas
description: Dialectic thinking — spawn thesis and antithesis agents to stress-test ideas, then synthesize and verify against code. Use when user says "debate", "argue both sides", "devil's advocate", "stress test this idea", "pros and cons of approach", or wants rigorous evaluation of a design decision.
user-invocable: true
context: fork
model: sonnet
argument-hint: "<question or topic>"
allowed-tools:
  - Task
  - TaskOutput
  - TodoWrite
  - Read
  - Grep
  - Glob
---

# Dialectic Debate

Stress-test ideas by spawning competing perspectives, then synthesize and ground-truth against code.

**`$ARGUMENTS` is the question or topic to debate.**

If no argument provided, ask the user what they want to evaluate.

**Use TodoWrite** to track these 4 phases:

1. Frame the debate
2. Spawn thesis + antithesis agents
3. Synthesize positions
4. Verify claims against code

---

## Phase 1: Frame the Debate

Parse the topic from `$ARGUMENTS`. Identify:

- **The core tension** — what are the two opposing positions?
- **Stakes** — what depends on getting this right?
- **Scope** — bound the debate to avoid sprawl

Frame as a clear binary or spectrum question. Examples:

- "Should we use microservices or a monolith for X?"
- "Is caching worth the complexity here?"
- "Should this be a library or an inline implementation?"

---

## Phase 2: Spawn Thesis + Antithesis (Parallel)

Spawn two Explore agents in a single message:

```
Task(
  subagent_type="Explore",
  run_in_background=true,
  description="Thesis: argue FOR",
  prompt="You are arguing FOR: {position A}.
  Topic: {framed question}

  Build the strongest possible case:
  1. Search the codebase for evidence supporting this position
  2. Identify concrete benefits with file:line references
  3. Anticipate and preempt counterarguments
  4. Rate your confidence (high/medium/low) with reasoning

  Be specific — cite code, patterns, and constraints you find.
  DO NOT hedge or present both sides. Argue your position fully."
)

Task(
  subagent_type="Explore",
  run_in_background=true,
  description="Antithesis: argue AGAINST",
  prompt="You are arguing AGAINST: {position A} (i.e., FOR {position B}).
  Topic: {framed question}

  Build the strongest possible case:
  1. Search the codebase for evidence supporting this position
  2. Identify concrete risks/costs of the opposing view with file:line references
  3. Anticipate and preempt counterarguments
  4. Rate your confidence (high/medium/low) with reasoning

  Be specific — cite code, patterns, and constraints you find.
  DO NOT hedge or present both sides. Argue your position fully."
)
```

---

## Phase 3: Synthesize

Collect both results:

```
TaskOutput(task_id=<thesis_id>, block=true)
TaskOutput(task_id=<antithesis_id>, block=true)
```

Synthesize into a structured verdict:

1. **Where they agree** — shared facts, common ground
2. **Where they conflict** — genuine disagreements with evidence
3. **Weak arguments** — flag claims that lack code evidence or rely on generalities
4. **Verdict** — which position has stronger grounding, and why
5. **Conditions** — when would the other position win instead?

---

## Phase 4: Verify Claims

For any factual claims made by either side (file references, pattern assertions, dependency claims):

- Read the cited files to confirm accuracy
- Flag any misrepresentations or hallucinated evidence
- Adjust verdict if verification changes the balance

---

## Output

```
DEBATE: {topic}
==============

Thesis: {position A}
  Confidence: {high/medium/low}
  Key evidence: {1-2 strongest points with file refs}

Antithesis: {position B}
  Confidence: {high/medium/low}
  Key evidence: {1-2 strongest points with file refs}

Verdict: {position} wins because {reason}
Caveat: {position} would win if {conditions}

Verified claims: {N}/{M} checked, {K} corrected
```

---

## Examples

```
/debating-ideas Should we split the API into microservices?
/debating-ideas Is it worth adding Redis caching to the auth flow?
/debating-ideas Monorepo vs polyrepo for our frontend packages
```

---

**Frame the debate now.**
