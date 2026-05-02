import json
import os

# Load all contexts
data_dir = os.path.join(os.path.dirname(__file__), 'dataset', 'expanded')

categories = {}
merchants = {}
customers = {}
triggers = {}

for filename in os.listdir(os.path.join(data_dir, 'categories')):
    if filename.endswith('.json'):
        with open(os.path.join(data_dir, 'categories', filename)) as f:
            cat = json.load(f)
            categories[cat['slug']] = cat

for filename in os.listdir(os.path.join(data_dir, 'merchants')):
    if filename.endswith('.json'):
        with open(os.path.join(data_dir, 'merchants', filename)) as f:
            merch = json.load(f)
            merchants[merch['merchant_id']] = merch

for filename in os.listdir(os.path.join(data_dir, 'customers')):
    if filename.endswith('.json'):
        with open(os.path.join(data_dir, 'customers', filename)) as f:
            cust = json.load(f)
            customers[cust['customer_id']] = cust

for filename in os.listdir(os.path.join(data_dir, 'triggers')):
    if filename.endswith('.json'):
        with open(os.path.join(data_dir, 'triggers', filename)) as f:
            trig = json.load(f)
            triggers[trig['id']] = trig

def compose(category, merchant, trigger, customer=None):
    """
    Inputs are the dicts loaded from the dataset JSON.
    Return a dict with keys: body, cta, send_as, suppression_key, rationale.
    """
    # Get merchant name
    owner_name = merchant['identity']['owner_first_name']
    merchant_name = merchant['identity']['name']
    
    # Determine send_as and cta based on scope
    if trigger['scope'] == 'customer':
        send_as = 'merchant_on_behalf'
        cta = 'binary_yes_stop'  # for customer messages, usually yes/stop
    else:
        send_as = 'vera'
        cta = 'open_ended'  # default for merchant
    
    suppression_key = trigger.get('suppression_key', f"{trigger['kind']}:{merchant['merchant_id']}")
    
    # Generate body based on trigger kind
    kind = trigger['kind']
    payload = trigger['payload']
    
    if kind == 'research_digest':
        digest_id = payload['top_item_id']
        digest_item = next((d for d in category['digest'] if d['id'] == digest_id), None)
        if digest_item:
            body = f"Dr. {owner_name}, {digest_item['title']} — {digest_item['source']}. This could impact your high-risk adult patients."
            rationale = f"Sharing relevant research digest with clinical anchor for {category['slug']} category."
        else:
            body = f"Hi {owner_name}, new research available in {category['slug']} field."
            rationale = "Generic research notification."
    
    elif kind == 'regulation_change':
        body = f"Dr. {owner_name}, important update: {payload['top_item_id']} deadline approaching. Check DCI guidelines."
        rationale = "Compliance reminder with urgency."
        cta = 'binary_yes_stop'
    
    elif kind == 'recall_due':
        if customer:
            service = payload.get('service_due', 'checkup').replace('_', ' ')
            due_date = payload.get('due_date', 'soon')[:10]
            body = f"Hi {customer['identity']['name']}, your {service} is due on {due_date}. Book now?"
            rationale = "Customer recall reminder with specific service and date."
        else:
            body = f"Hi {owner_name}, a customer's recall is due."
            rationale = "Merchant notification for customer recall."
    
    elif kind == 'perf_spike':
        metric = payload.get('metric', 'performance')
        delta = payload.get('delta_pct', 0.1) * 100
        body = f"Great news {owner_name}! Your {metric} increased {delta:.0f}% this week. What's driving this?"
        rationale = "Positive performance feedback to encourage sharing success."
    
    elif kind == 'perf_dip':
        metric = payload.get('metric', 'performance')
        delta = payload.get('delta_pct', -0.1) * 100
        body = f"Hi {owner_name}, your {metric} dropped {abs(delta):.0f}% vs last week. Any issues?"
        rationale = "Performance dip alert to identify problems."
        cta = 'binary_yes_stop'
    
    elif kind == 'festival_upcoming':
        festival = payload.get('festival', 'upcoming festival')
        days = payload.get('days_until', 30)
        body = f"Hi {owner_name}, {festival} is in {days} days. Consider festive offers?"
        rationale = "Festival timing prompt for seasonal marketing."
    
    elif kind == 'competitor_opened':
        body = f"Hi {owner_name}, new competitor opened nearby. Update your GBP to stand out?"
        rationale = "Competitor alert to prompt profile optimization."
    
    elif kind == 'curious_ask':
        body = f"Hi {owner_name}, what's one thing I can help with to grow your business?"
        rationale = "Curious question to engage dormant merchants."
    
    elif kind == 'milestone_reached':
        body = f"Congratulations {owner_name}! You crossed 100 reviews. Share your story?"
        rationale = "Milestone celebration to build rapport."
    
    elif kind == 'dormant_with_vera':
        body = f"Hi {owner_name}, it's been a while. Ready to optimize your profile?"
        rationale = "Re-engagement for dormant merchants."
    
    elif kind == 'customer_lapsed_soft':
        if customer:
            body = f"Hi {customer['identity']['name']}, we miss you! Come back for a special offer?"
            rationale = "Winback message to lapsed customer."
        else:
            body = f"Hi {owner_name}, a customer hasn't visited in 6 months. Reach out?"
            rationale = "Merchant alert for lapsed customer."
    
    elif kind == 'appointment_tomorrow':
        if customer:
            time = payload.get('time', 'your scheduled time')
            body = f"Hi {customer['identity']['name']}, reminder: your appointment tomorrow at {time}."
            rationale = "Appointment reminder to customer."
        else:
            body = f"Hi {owner_name}, you have an appointment tomorrow."
            rationale = "Merchant reminder for tomorrow's booking."
    
    elif kind == 'renewal_due':
        days = payload['days_remaining']
        body = f"Hi {owner_name}, your subscription renews in {days} days. Renew now?"
        rationale = "Renewal reminder with urgency."
        cta = 'binary_yes_stop'
    
    else:
        body = f"Hi {owner_name}, update from Vera: {kind.replace('_', ' ')}."
        rationale = "Generic message for unhandled trigger kind."
    
    return {
        "body": body,
        "cta": cta,
        "send_as": send_as,
        "suppression_key": suppression_key,
        "rationale": rationale
    }