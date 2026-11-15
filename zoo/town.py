"""Observed native receipts, never planner proposals, for retained borg-rs cells."""
from collections import Counter
import json
import re

MESSAGE = re.compile(r'^(\d+) (\d+) (\d+) (.*)$')
BUY = re.compile(r'^You bought (.+) for (\d+) gold\.$')


def collect(directory):
    events = []
    frames = []
    state = directory / 'state.log'
    if state.exists():
        for line in state.read_text(errors='replace').splitlines():
            gold = re.search(r'\bau(-?\d+)\b', line)
            frames.append(int(gold[1]) if gold else None)
    messages = directory / 'messages.log'
    pending_key = None
    shop = None
    live_executor = False
    if messages.exists():
        for line in messages.read_text(errors='replace').splitlines():
            match = MESSAGE.match(line)
            if not match:
                continue
            key, turn, text = int(match[1]), int(match[2]), match[4]
            entered = re.search(r"# Entering a '(\d+)' shop", text)
            preferred = re.search(r"# Currently in preferred store '(\d+)'", text)
            if entered:
                shop = int(entered[1])
            if preferred:
                shop = int(preferred[1]) - 1
            execution = re.match(r'^# Town plan executing action (\d+) at shop (-?\d+) slot (\d+)', text)
            if execution:
                live_executor = True
                action, where = int(execution[1]), int(execution[2])
                if 0 <= where <= 7:
                    shop = where
                if action == 1 and 0 <= where < 7:
                    pending_key = key
            # In the live executor, Buying is a post-receipt confirmation.
            # Anchor the wallet at its earlier execution message instead.
            if not live_executor and text.startswith('# Buying ') and not text.startswith(("# Buying '", '# Buying time ')):
                pending_key = key
            receipt = BUY.match(text)
            if not receipt:
                continue
            item, cost = receipt[1], int(receipt[2])
            count = re.match(r'^(\d+) ', item)
            quantity = int(count[1]) if count else 1
            before = frames[pending_key] if pending_key is not None and pending_key < len(frames) else None
            after = frames[key] if key < len(frames) else None
            events.append({'key_index': key, 'game_turn': turn, 'shop_index': shop,
                           'item': item, 'quantity': quantity, 'gold_spent': cost,
                           'gold_before': before, 'gold_after': after,
                           'wallet_verified': before - after == cost if before is not None and after is not None else None,
                           'native_receipt': text})
            pending_key = None
    (directory / 'town-transactions.jsonl').write_text(''.join(json.dumps(row) + '\n' for row in events))
    # Compact totals survive collection on the results branch; full chronological
    # receipts, Home transfers and policy consultations remain in raw archives.
    totals = {}
    for row in events:
        group = (row['shop_index'], row['item'])
        total = totals.setdefault(group, {'shop_index': row['shop_index'], 'item': row['item'],
                                         'transactions': 0, 'units': 0, 'gold': 0})
        total['transactions'] += 1
        total['units'] += row['quantity']
        total['gold'] += row['gold_spent']
    return {'schema': 'borg-zoo/town-activity@1', 'purchases': len(events),
            'gold_spent': sum(row['gold_spent'] for row in events),
            'wallet_checks': dict(Counter(str(row['wallet_verified']) for row in events)),
            'items': list(totals.values()),
            'qualification': 'Native retail receipts only. Home transfers require inspection of retained messages; no planned action counts as a completed transaction.'}
