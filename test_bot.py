#!/usr/bin/env python3
"""
Quick test script to demonstrate the bot composition working.
Usage: python test_bot.py
"""

import json
import os
import sys

# Add the app directory to path
sys.path.insert(0, os.path.dirname(__file__))

from app import compose, contexts

def test_compose():
    print("=" * 80)
    print("MAGICPIN AI CHALLENGE - BOT COMPOSITION TEST")
    print("=" * 80)
    
    # Load a test case
    test_cases = [
        {
            "name": "Research Digest for Dentist",
            "category_slug": "dentists",
            "merchant_id": "m_001_drmeera_dentist_delhi",
            "trigger_id": "trg_001_research_digest_dentists",
            "customer_id": None,
        },
        {
            "name": "Performance Spike Alert",
            "category_slug": "salons",
            "merchant_id": "m_003_studio11_salon_hyderabad",
            "trigger_id": "trg_024_perf_spike_zen",
            "customer_id": None,
        },
        {
            "name": "Customer Recall Reminder",
            "category_slug": "dentists",
            "merchant_id": "m_001_drmeera_dentist_delhi",
            "trigger_id": "trg_003_recall_due_priya",
            "customer_id": "c_001_priya_for_m001",
        },
    ]
    
    for test in test_cases:
        print(f"\n{'─' * 80}")
        print(f"Test: {test['name']}")
        print(f"{'─' * 80}")
        
        try:
            category = contexts['category'].get(test['category_slug'])
            merchant = contexts['merchant'].get(test['merchant_id'])
            trigger = contexts['trigger'].get(test['trigger_id'])
            customer = contexts['customer'].get(test['customer_id']) if test['customer_id'] else None
            
            if not all([category, merchant, trigger]):
                print(f"❌ MISSING DATA")
                print(f"   Category: {bool(category)}, Merchant: {bool(merchant)}, Trigger: {bool(trigger)}")
                continue
            
            result = compose(category, merchant, trigger, customer)
            
            print(f"✅ Merchant: {merchant['identity']['name']}")
            print(f"✅ Category: {test['category_slug']}")
            print(f"✅ Trigger: {trigger['kind']}")
            if customer:
                print(f"✅ Customer: {customer['identity']['name']}")
            
            print(f"\n📧 MESSAGE:")
            print(f"   {result['body']}")
            print(f"\n🔧 METADATA:")
            print(f"   CTA: {result['cta']}")
            print(f"   Send as: {result['send_as']}")
            print(f"   Suppression Key: {result['suppression_key']}")
            print(f"   Rationale: {result['rationale']}")
            
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
            import traceback
            traceback.print_exc()
    
    print(f"\n{'=' * 80}")
    print("✅ Bot composition tests complete!")
    print(f"{'=' * 80}")

if __name__ == '__main__':
    test_compose()
