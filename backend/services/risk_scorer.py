# backend/services/risk_scorer.py


def calculate_final_risk(text_result=None, image_result=None,
                         url_result=None) -> dict:
    """
    Combines text, image, and URL risk scores into one final risk score.

    Weights adapt based on which inputs are provided:
    - Text only:       text = 100%
    - URL only:        url  = 100%
    - Image only:      image = 100%
    - Text + URL:      text = 70%, url = 30%
    - Text + Image:    text = 70%, image = 30%
    - All three:       text = 60%, image = 25%, url = 15%
    """
    all_flags = []
    components = {}
    scores = {}

    # Collect individual scores and flags
    if text_result:
        score = text_result.get('risk_score', 0)
        scores['text'] = score
        components['text'] = score

        # Heuristic flags (phone, fee, salary, etc.)
        heuristic_flags = text_result.get('heuristic_flags', [])
        all_flags.extend(heuristic_flags)

        # Gemini AI flags
        gemini = text_result.get('gemini', {})
        if gemini:
            gemini_flags = gemini.get('red_flags', [])
            for gf in gemini_flags:
                # Avoid duplicating flags already caught by heuristics
                if not any(gf[:35] in hf for hf in all_flags):
                    all_flags.append(gf)
            if gemini.get('verdict') in ('SCAM', 'SUSPICIOUS') and gemini.get('explanation'):
                all_flags.append(f"AI Analysis: {gemini['explanation']}")

        # Fallback: use SHAP words if no other flags
        if not all_flags:
            all_flags.extend(
                [f"Suspicious term detected: '{r['word']}'"
                 for r in text_result.get('top_reasons', [])]
            )

    if image_result:
        score = image_result.get('risk_score', 0)
        scores['image'] = score
        components['image'] = score
        all_flags.extend([f'[Image] {f}' for f in image_result.get('flags', [])])

    if url_result:
        score = url_result.get('risk_score', 0)
        scores['url'] = score
        components['url'] = score
        all_flags.extend([f'[URL] {f}' for f in url_result.get('flags', [])])

    # ── Adaptive weighting ──────────────────────────────────────────────────
    active = list(scores.keys())
    n = len(active)

    if n == 0:
        final_score = 0
    elif n == 1:
        # Single input — use full score, no dilution
        final_score = list(scores.values())[0]
    elif n == 2:
        # Two inputs
        if 'text' in scores and 'url' in scores:
            final_score = int(scores['text'] * 0.70 + scores['url'] * 0.30)
        elif 'text' in scores and 'image' in scores:
            final_score = int(scores['text'] * 0.70 + scores['image'] * 0.30)
        else:
            final_score = int(sum(scores.values()) / 2)
    else:
        # All three inputs
        final_score = int(
            scores.get('text', 0)  * 0.60 +
            scores.get('image', 0) * 0.25 +
            scores.get('url', 0)   * 0.15
        )

    final_score = min(max(final_score, 0), 100)

    # ── Label ───────────────────────────────────────────────────────────────
    if final_score >= 70:
        label = 'LIKELY SCAM'
        color = 'red'
    elif final_score >= 40:
        label = 'SUSPICIOUS'
        color = 'orange'
    else:
        label = 'LIKELY SAFE'
        color = 'green'

    if not all_flags:
        all_flags = ['No suspicious signals detected. This posting appears safe.']

    return {
        'final_score': final_score,
        'label': label,
        'color': color,
        'flags': all_flags,
        'components': components
    }
