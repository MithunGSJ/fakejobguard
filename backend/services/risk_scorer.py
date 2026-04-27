# backend/services/risk_scorer.py


def calculate_final_risk(text_result=None, image_result=None,
                         url_result=None) -> dict:
    """
    Combines text, image, and URL risk scores into one final risk score.
    Weights: text=60%, image=25%, url=15%

    Returns:
    - final_score: int (0-100)
    - label: str (LIKELY SAFE / SUSPICIOUS / LIKELY SCAM)
    - color: str (green / orange / red)
    - flags: list of all flags from all modules
    - components: dict of individual module scores
    """
    weighted_score = 0
    all_flags = []
    components = {}

    if text_result:
        score = text_result.get('risk_score', 0)
        weighted_score += score * 0.60
        all_flags.extend(
            [f"[TEXT] {r['word']} (impact: {r['impact']})"
             for r in text_result.get('top_reasons', [])]
        )
        components['text'] = score

    if image_result:
        score = image_result.get('risk_score', 0)
        weighted_score += score * 0.25
        all_flags.extend(
            [f'[IMAGE] {f}' for f in image_result.get('flags', [])]
        )
        components['image'] = score

    if url_result:
        score = url_result.get('risk_score', 0)
        weighted_score += score * 0.15
        all_flags.extend(
            [f'[URL] {f}' for f in url_result.get('flags', [])]
        )
        components['url'] = score

    final_score = min(int(weighted_score), 100)

    if final_score >= 70:
        label = 'LIKELY SCAM'
        color = 'red'
    elif final_score >= 40:
        label = 'SUSPICIOUS'
        color = 'orange'
    else:
        label = 'LIKELY SAFE'
        color = 'green'

    return {
        'final_score': final_score,
        'label': label,
        'color': color,
        'flags': all_flags,
        'components': components
    }
