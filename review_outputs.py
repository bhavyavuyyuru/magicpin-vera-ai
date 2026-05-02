#!/usr/bin/env python3
"""
Comprehensive Bot Output Review Script
Shows all 30 test pair outputs before deployment
"""

import json
import os
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(__file__))
from app import compose, contexts

def load_test_pairs():
    """Load the 30 test pairs"""
    with open('dataset/expanded/test_pairs.json') as f:
        return json.load(f)['pairs']

def review_outputs():
    print("\n" + "=" * 100)
    print(" " * 30 + "MAGICPIN AI CHALLENGE - OUTPUT REVIEW")
    print("=" * 100)
    
    test_pairs = load_test_pairs()
    submission_data = []
    stats = defaultdict(int)
    
    print(f"\nReviewing {len(test_pairs)} test cases...\n")
    
    for i, pair in enumerate(test_pairs, 1):
        test_id = pair['test_id']
        trigger_id = pair['trigger_id']
        merchant_id = pair['merchant_id']
        customer_id = pair['customer_id']
        
        # Load contexts
        trigger = contexts['trigger'].get(trigger_id)
        merchant = contexts['merchant'].get(merchant_id)
        customer = contexts['customer'].get(customer_id) if customer_id else None
        
        if not (trigger and merchant):
            print(f"❌ {test_id}: Missing data - skipping")
            continue
        
        category = contexts['category'].get(merchant['category_slug'])
        trigger_kind = trigger.get('kind', 'unknown')
        
        try:
            result = compose(category, merchant, trigger, customer)
            stats[trigger_kind] += 1
            stats['total'] += 1
            
            # Display
            print(f"TEST {test_id}: {trigger_kind.upper()}")
            print(f"  Merchant: {merchant['identity']['name']}")
            print(f"  City: {merchant['identity']['city']}")
            if customer:
                print(f"  Customer: {customer['identity']['name']}")
            print(f"  CTA: {result['cta']}")
            print(f"  Send as: {result['send_as']}")
            print(f"  Message: {result['body']}")
            print(f"  Rationale: {result['rationale']}")
            print()
            
            submission_data.append({
                'test_id': test_id,
                'body': result['body'],
                'cta': result['cta'],
                'send_as': result['send_as'],
                'suppression_key': result['suppression_key'],
                'rationale': result['rationale']
            })
            
        except Exception as e:
            print(f"ERROR {test_id}: {str(e)}")
            stats['errors'] += 1
            print()
    
    # Statistics
    print("\n" + "=" * 100)
    print("STATISTICS")
    print("=" * 100)
    print(f"\nTotal Generated: {stats['total']}")
    print(f"Errors: {stats['errors']}")
    print(f"\nBreakdown by trigger type:")
    for trigger_type in sorted(stats.keys()):
        if trigger_type not in ['total', 'errors']:
            count = stats[trigger_type]
            print(f"  • {trigger_type}: {count}")
    
    # Save for review
    with open('review_outputs.json', 'w') as f:
        json.dump(submission_data, f, indent=2)
    
    print(f"Review saved to: review_outputs.json")
    
    # Show sample message variations
    print("\nSAMPLE MESSAGE VARIATIONS:")
    print("=" * 100)
    
    seen_types = set()
    for item in submission_data:
        print(f"\nMESSAGE:")
        print(f"   {item['body']}")
        print(f"   CTA: {item['cta']}")

if __name__ == '__main__':
    review_outputs()
