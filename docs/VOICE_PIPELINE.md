# Voice Pipeline and Model Evaluation

## Requirement

Push-to-talk input in Punjabi, Hindi, English, and mixed speech. The output is a proposed cart, never an automatic financial transaction.

## Pipeline

1. Capture locally.
2. Validate duration, size, sample rate and channels.
3. Preprocess/resample if required.
4. Run offline ASR adapter.
5. Preserve transcript and available language/segment metadata.
6. Normalize text without discarding original transcript.
7. Parse number words, digits, fractions, quantities, and units.
8. Extract product phrases and command intent.
9. Match aliases/catalog.
10. Show candidates and unresolved choices.
11. Add only operator-approved lines to uncommitted cart.

## Candidate models

- Whisper multilingual Small via a CPU-friendly runtime such as faster-whisper: baseline candidate.
- AI4Bharat Indic-Transcribe family: Indian multilingual/code-mixed candidate.
- IndicConformer Punjabi/Hindi variants: optional language-specific comparison.

The final model is not selected until tested on the target PC. Validate exact version, runtime, supported scripts/languages, model size, RAM, latency, offline behavior, redistribution license, and installer size before adoption.

## Benchmark target machine

Initial deployment hardware: HP EliteDesk 800 G2 Mini, Intel i5-6500TE, 16 GB RAM, Intel HD 530. Benchmark the actual machine. Do not assume GPU acceleration.

Record model revision/checksum, quantization, WER, product-name accuracy, quantity/unit accuracy, real-time factor, peak RAM, CPU, noise conditions, speaker/language breakdown, and license.

## Evaluation corpus

Begin with 10–15 products and at least 100 utterances, then expand across speakers and noise:
- Punjabi, Hindi, English and code-switching.
- Gurmukhi, Devanagari and Roman spellings.
- Number words and digits.
- Fractions: aadha, pauna, sawa.
- kg, g, litre, ml, packet, piece, dozen.
- Similar product names and brands/pack sizes.
- Add/remove/change quantity/show total commands.

Obtain consent before recording shopkeeper speech. Store audio locally and delete after processing by default.

## Parser rules

- Decimal quantities.
- Explicit number/fraction grammar.
- Explicit unit conversions only.
- Multiple products per utterance.
- Missing quantity follows configured product default or requires confirmation.
- Unknown/ambiguous unit or product requires operator review.
- Preserve original transcript.
- Corrections apply only to uncommitted cart.

## Confidence

Keep ASR quality metadata, parser validity, and product match score separate. Exact alias can still be ambiguous across SKUs. Fuzzy thresholds are calibrated on evaluation data. Never silently select an uncertain product.
