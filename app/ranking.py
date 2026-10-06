from datetime import date


def rank_quotes(quotes, today=None):
    """Rank quotes for ONE product. Higher score = better. Score is 0-100."""
    today = today or date.today()

    # 1. Ignore expired quotes
    valid = [q for q in quotes if q.valid_until is None or q.valid_until >= today]

    # 2. Keep only the newest quote from each supplier
    latest = {}
    for q in valid:
        if q.supplier_id not in latest or q.id > latest[q.supplier_id].id:
            latest[q.supplier_id] = q
    candidates = list(latest.values())
    if not candidates:
        return []

    best_price = min(q.unit_price for q in candidates)
    best_lead = min(q.lead_time_days for q in candidates)

    results = []
    for q in candidates:
        price_score = best_price / q.unit_price                  # 1.0 = cheapest
        lead_score = (best_lead + 1) / (q.lead_time_days + 1)    # 1.0 = fastest
        rating_score = q.supplier.rating / 5                     # 1.0 = rating 5
        score = 100 * (0.6 * price_score + 0.25 * lead_score + 0.15 * rating_score)
        results.append({
            "supplier_id": q.supplier_id,
            "supplier_name": q.supplier.name,
            "unit_price": q.unit_price,
            "lead_time_days": q.lead_time_days,
            "rating": q.supplier.rating,
            "score": round(score, 1),
        })

    results.sort(key=lambda r: r["score"], reverse=True)
    for position, r in enumerate(results, start=1):
        r["rank"] = position
    return results