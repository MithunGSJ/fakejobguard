# backend/services/risk_scorer.py


def calculate_final_risk(text_result=None, image_result=None,
                         url_result=None) -> dict:
    """
    Combines text, image, and URL risk scores into one final risk score.
    Weights: text=60%, image=25%, url=15%
    """
    weighted_score = 0
    all_flags = []
    components = {}

    if text_result:
        score = text_result.get('risk_score', 0)
        weighted_score += score * 0.60

        # Heuristic flags (phone, fee, salary, etc.) — human readable
        heuristic_flags = text_result.get('heuristic_flags', [])
        all_flags.extend(heuristic_flags)

        # Gemini red flags (if available)
        gemini = text_result.get('gemini', {})
        if gemini:
            gemini_flags = gemini.get('red_flags', [])
            for gf in gemini_flags:
                if not any(gf[:30] in hf for hf in all_flags):
                    all_flags.append(gf)
            # Add Gemini explanation as summary
            if gemini.get('verdict') in ('SCAM', 'SUSPICIOUS') and gemini.get('explanation'):
                all_flags.append(f"AI Analysis: {gemini['explanation']}")

        # Fallback: use SHAP words if no other flags
        if not all_flags:
            all_flags.extend(
                [f"Suspicious term detected: '{r['word']}'"
                 for r in text_result.get('top_reasons', [])]
            )

        components['text'] = score

    if image_result:
        score = image_result.get('risk_score', 0)
        weighted_score += score * 0.25
        all_flags.extend([f'[Image] {f}' for f in image_result.get('flags', [])])
        components['image'] = score

    if url_result:
        score = url_result.get('risk_score', 0)
        weighted_score += score * 0.15
        all_flags.extend([f'[URL] {f}' for f in url_result.get('flags', [])])
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

    if not all_flags:
        all_flags = ['No suspicious signals detected. This posting appears safe.']

    return {
        'final_score': final_score,
        'label': label,
        'color': color,
        'flags': all_flags,
        'components': components
    }
