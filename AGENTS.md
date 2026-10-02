# AGENTS.md — AI Astrologer

## Mission

Build a production-quality Vedic astrology application with deterministic calculations and an AI interpretation layer.

## Non-negotiable rule

The LLM is NOT the astrology calculator.

Never use an LLM to calculate:

- planetary longitude
- ascendant
- houses
- nakshatra
- dasha dates
- transit dates
- divisional chart positions

Use deterministic code and a verified ephemeris/calculation library.

## Methodology

Initial configuration:

- tradition: Vedic/Jyotish
- zodiac: sidereal
- ayanamsa: Lahiri
- dasha: Vimshottari

Never silently change these settings.

## Architecture rules

1. Astrology calculations must be deterministic.
2. Rules must be explicit and testable.
3. LLM code must consume an evidence package.
4. LLM providers must be replaceable.
5. Domain logic must not depend on one AI provider.
6. Store methodology/rule/prompt versions with generated answers.
7. Add tests with every important calculation or rule.
8. Do not mix unrelated refactoring into feature work.

## AI rules

The AI must:

- answer the user's question directly
- use only supplied evidence
- explain relevant astrological factors
- distinguish strong/moderate/weak indications
- explain conflicting evidence
- use timing only when timing evidence is available
- avoid generic filler
- avoid presenting astrology as scientific certainty

The AI must never:

- invent planetary positions
- invent dasha periods
- invent dates
- invent rules
- fabricate citations
- claim to have consulted a source that was not supplied

## High-stakes topics

For health, legal, financial, investment, or similar high-stakes questions, do not turn an astrological interpretation into a guaranteed diagnosis, legal result, investment return, or financial certainty.

## Engineering

Python:

- type hints
- Pydantic
- pytest
- Ruff
- clear modules
- dependency injection where useful

TypeScript:

- strict mode
- typed API contracts
- avoid `any`

## Security

Never commit:

- API keys
- passwords
- database credentials
- private user data

Birth data is personal data and should be handled carefully.

## Definition of done

A feature is complete only when:

- implementation exists
- tests exist
- tests pass
- error handling exists
- documentation is updated when needed
- no secrets are committed
