"""Offline educational arithmetic only; no network, broker, portfolio or order access."""

import argparse
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation, ROUND_FLOOR
import json


def _number(value):
    try:
        result = Decimal(str(value))
    except InvalidOperation as exc:
        raise ValueError('a finite numeric value is required') from exc
    if not result.is_finite():
        raise ValueError('a finite numeric value is required')
    return result


def size_long(entry, stop, risk_budget, cash, fixed_cost, per_share_cost, lot_size=1):
    """Simple unlevered LONG under a supplied fixed-plus-linear cost estimate."""
    entry, stop, budget, cash, fixed, variable = map(
        _number, (entry, stop, risk_budget, cash, fixed_cost, per_share_cost))
    if not 0 < stop < entry:
        raise ValueError('supported example requires 0 < stop < entry')
    if min(budget, cash, fixed, variable) < 0:
        raise ValueError('budgets, cash and cost estimates must be nonnegative')
    if type(lot_size) is not int or lot_size <= 0:
        raise ValueError('lot_size must be a positive integer')
    risk_qty = int(((budget - fixed) / (entry - stop + variable)).to_integral_value(rounding=ROUND_FLOOR))
    cash_qty = int(((cash - fixed) / (entry + variable)).to_integral_value(rounding=ROUND_FLOOR))
    qty = max(0, min(risk_qty, cash_qty)) // lot_size * lot_size
    costs = fixed + qty * variable if qty else Decimal(0)
    planned_loss = qty * (entry - stop) + costs
    required_cash = qty * entry + costs
    assert planned_loss <= budget and required_cash <= cash
    return {'qty': qty, 'estimated_round_trip_cost': str(costs),
            'planned_loss_at_stop': str(planned_loss), 'estimated_cash_required': str(required_cash),
            'educational_only': True,
            'limit': 'Linear cost estimate only; gaps can exceed planned loss. Not trade permission.'}


def available_at_decision(available_at, decision_at):
    times = []
    for value in (available_at, decision_at):
        parsed = datetime.fromisoformat(value)
        if parsed.tzinfo is None or parsed.utcoffset() is None:
            raise ValueError('availability and decision times require explicit UTC offsets')
        times.append(parsed.astimezone(timezone.utc))
    return times[0] <= times[1]


def self_check():
    base = (500, 490, 500, '33333.33', 20, 2)
    checks = [
        ('cost-aware integer size', lambda: size_long(*base)['qty'] == 40),
        ('planned loss', lambda: Decimal(size_long(*base)['planned_loss_at_stop']) == 500),
        ('cash cap', lambda: size_long(500, 490, 500, 1000, 20, 2)['qty'] == 1),
        ('lot rounding', lambda: size_long(*base, lot_size=25)['qty'] == 25),
        ('too small budget means no position', lambda: size_long(500, 490, 10, 1000, 20, 2)['qty'] == 0),
        ('zero budget means no position', lambda: size_long(500, 490, 0, 1000, 0, 2)['qty'] == 0),
        ('gap can exceed budget', lambda: 40 * (500 - 480) + 100 > 500),
        ('high win rate can lose', lambda: Decimal('.6') - Decimal('.4') * 2 == Decimal('-.2')),
        ('later release excluded', lambda: not available_at_decision('2026-11-06T18:00:00+05:30', '2026-11-06T15:30:00+05:30')),
        ('same instant across offsets', lambda: available_at_decision('2026-11-06T18:00:00+05:30', '2026-11-06T12:30:00+00:00')),
        ('earlier release usable chronologically', lambda: available_at_decision('2026-11-06T18:00:00+05:30', '2026-11-07T09:15:00+05:30')),
    ]
    rejects = [
        ('equal entry and stop', lambda: size_long(500, 500, 500, 1000, 20, 2)),
        ('negative cost', lambda: size_long(500, 490, 500, 1000, -1, 2)),
        ('non-finite input', lambda: size_long('NaN', 490, 500, 1000, 20, 2)),
        ('infinite input', lambda: size_long(500, 490, 'Infinity', 1000, 20, 2)),
        ('invalid lot', lambda: size_long(*base, lot_size=0)),
        ('naive news time', lambda: available_at_decision('2026-11-06T18:00:00', '2026-11-06T12:30:00+00:00')),
    ]
    for name, check in checks:
        assert check(), name
    for name, operation in rejects:
        try:
            operation()
        except ValueError:
            continue
        raise AssertionError(f'expected rejection: {name}')
    return {'status': 'PASS', 'synthetic_checks': len(checks) + len(rejects),
            'scope': 'Arithmetic and timestamp checks, not market-performance validation.'}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('self-check')
    risk = sub.add_parser('risk')
    for name in ('entry', 'stop', 'risk-budget', 'cash', 'fixed-cost', 'per-share-cost'):
        risk.add_argument('--' + name, required=True)
    risk.add_argument('--lot-size', type=int, default=1)
    news = sub.add_parser('available')
    news.add_argument('--available-at', required=True)
    news.add_argument('--decision-at', required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == 'self-check':
            result = self_check()
        elif args.command == 'risk':
            result = size_long(args.entry, args.stop, args.risk_budget, args.cash,
                               args.fixed_cost, args.per_share_cost, args.lot_size)
        else:
            result = {'chronologically_available': available_at_decision(args.available_at, args.decision_at),
                      'limit': 'Timestamp ordering only; source truth and execution latency not validated.'}
    except ValueError as exc:
        parser.error(str(exc))
    print(json.dumps(result, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
