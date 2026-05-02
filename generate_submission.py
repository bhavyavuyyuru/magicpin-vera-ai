import json
import os
from bot import compose, categories, merchants, customers, triggers

# Load test pairs
with open(os.path.join(os.path.dirname(__file__), 'dataset', 'expanded', 'test_pairs.json')) as f:
    test_pairs = json.load(f)['pairs']

# Generate submission
submission = []
for pair in test_pairs:
    trigger = triggers[pair['trigger_id']]
    merchant = merchants[pair['merchant_id']]
    category = categories[merchant['category_slug']]
    customer = customers.get(pair['customer_id']) if pair['customer_id'] else None

    result = compose(category, merchant, trigger, customer)
    result['test_id'] = pair['test_id']
    submission.append(result)

# Write to submission.jsonl
with open('submission.jsonl', 'w') as f:
    for item in submission:
        f.write(json.dumps(item) + '\n')

print("Submission generated: submission.jsonl")