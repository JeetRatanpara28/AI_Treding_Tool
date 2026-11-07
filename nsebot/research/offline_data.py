"""Strict local daily CSV pilot import. No network, credentials or execution."""
import hashlib
import csv
import io
import json
from pathlib import Path
import re

import pandas as pd

from ..backtest import validate_history


def load_dataset(manifest_path, warmup=200, min_evaluation_sessions=252):
    """Return validated frames and provenance; reviewer declarations are not proof
    of source rights/calendar authority or corporate-action accuracy.
    All pilot symbols must cover the supplied calendar exactly. No filling,
    sorting, deduplication or adjustment is silently performed.
    """
    path = Path(manifest_path).resolve(strict=True)
    meta = json.loads(path.read_text(encoding='utf-8'))
    if type(meta.get('format_version')) is not int or meta['format_version'] != 1:
        raise ValueError('OFFLINE DATA: unsupported manifest version')
    for field in ('source', 'source_permission', 'calendar_source'):
        if not isinstance(meta.get(field), str) or not meta[field].strip():
            raise ValueError(f'OFFLINE DATA: missing {field} declaration')
    if meta.get('data_kind') not in ('market', 'synthetic'):
        raise ValueError('OFFLINE DATA: data_kind must be market or synthetic')
    if meta.get('price_basis') != 'split_adjusted_price':
        raise ValueError('OFFLINE DATA: require consistent split_adjusted_price basis; dividends excluded')
    if meta.get('corporate_actions_reviewed') is not True:
        raise ValueError('OFFLINE DATA: corporate-action review declaration is required')
    execution_model = meta.get('execution_model', 'static_research')
    if execution_model not in ('static_research', 'dated_nse_cash_v1'):
        raise ValueError('OFFLINE DATA: unsupported execution_model')
    if execution_model == 'dated_nse_cash_v1' and meta.get('raw_price_scale_verified') is not True:
        raise ValueError('OFFLINE DATA: dated ticks require reviewed raw price/share units')
    symbols = meta.get('stocks')
    if not isinstance(symbols, dict) or not symbols or not all(isinstance(s, str) and s for s in symbols):
        raise ValueError('OFFLINE DATA: stocks must map nonempty symbols to CSV filenames')
    hashes = {path.name: hashlib.sha256(path.read_bytes()).hexdigest()}
    used = set()
    evidence = meta.get('evidence_sha256', {})
    if not isinstance(evidence, dict):
        raise ValueError('OFFLINE DATA: evidence_sha256 must map local files to hashes')
    for relative, expected in evidence.items():
        if (not isinstance(relative, str) or not relative
                or not isinstance(expected, str) or not re.fullmatch('[a-f0-9]{64}', expected)):
            raise ValueError('OFFLINE DATA: invalid evidence file/hash')
        candidate = (path.parent / relative).resolve(strict=True)
        if not candidate.is_relative_to(path.parent) or candidate in used:
            raise ValueError('OFFLINE DATA: evidence files must be distinct and inside the manifest folder')
        actual = hashlib.sha256(candidate.read_bytes()).hexdigest()
        if actual != expected:
            raise ValueError('OFFLINE DATA: reviewed evidence checksum mismatch')
        used.add(candidate)
        hashes[relative] = actual

    def read(relative):
        if not isinstance(relative, str) or not relative:
            raise ValueError('OFFLINE DATA: CSV path is required')
        candidate = (path.parent / relative).resolve(strict=True)
        if (not candidate.is_relative_to(path.parent) or candidate.suffix.lower() != '.csv'
                or candidate in used):
            raise ValueError('OFFLINE DATA: CSV files must be distinct and inside the manifest folder')
        used.add(candidate)
        raw = candidate.read_bytes()
        hashes[str(candidate.relative_to(path.parent))] = hashlib.sha256(raw).hexdigest()
        header = next(csv.reader(io.StringIO(raw.decode('utf-8-sig'))), [])
        if not header or len(header) != len(set(header)):
            raise ValueError('OFFLINE DATA: missing or duplicate CSV column names')
        frame = pd.read_csv(candidate)
        if not frame.columns.is_unique or 'datetime' not in frame:
            raise ValueError('OFFLINE DATA: unique columns including datetime required')
        frame['datetime'] = pd.to_datetime(frame['datetime'], errors='raise')
        for field in ('open', 'high', 'low', 'close', 'volume'):
            if field in frame:
                frame[field] = pd.to_numeric(frame[field], errors='raise')
        return frame

    sessions = read(meta.get('sessions'))
    dates = pd.DatetimeIndex(sessions['datetime'])
    if (dates.empty or dates.tz is not None or dates.isna().any() or not dates.is_unique
            or not dates.is_monotonic_increasing or not dates.equals(dates.normalize())):
        raise ValueError('OFFLINE DATA: calendar must contain ordered unique naive session dates')
    index = read(meta.get('index'))
    universe = {symbol: read(filename) for symbol, filename in symbols.items()}
    validate_history(universe, index, warmup)
    for label, frame in [('index', index), *universe.items()]:
        if not pd.DatetimeIndex(frame['datetime']).equals(dates):
            raise ValueError(f'OFFLINE DATA: {label}: missing or extra sessions versus supplied calendar')
    if (isinstance(min_evaluation_sessions, bool) or not isinstance(min_evaluation_sessions, int)
            or min_evaluation_sessions < 20):
        raise ValueError('OFFLINE DATA: minimum evaluation sessions must be an integer >= 20')
    if len(dates) - warmup < min_evaluation_sessions:
        raise ValueError(f'OFFLINE DATA: need {min_evaluation_sessions} evaluated sessions after warm-up; '
                         f'got {len(dates) - warmup}')
    receipt = dict(data_kind=meta['data_kind'], source=meta['source'],
                   source_permission=meta['source_permission'],
                   calendar_source=meta['calendar_source'], price_basis=meta['price_basis'],
                   execution_model=execution_model,
                   raw_price_scale_verified=meta.get('raw_price_scale_verified', False),
                   source_sha256=hashes, input_sessions=len(dates), warmup_sessions=warmup,
                   evaluation_sessions=len(dates) - warmup, symbols=list(universe),
                   reviewer_declarations_not_independently_verified=True)
    return universe, index, receipt
