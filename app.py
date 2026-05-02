from flask import Flask, request, jsonify
import json
import os
from datetime import datetime

app = Flask(__name__)

# In-memory storage
contexts = {'category': {}, 'merchant': {}, 'customer': {}, 'trigger': {}}
conversations = {}  # conversation_id -> list of turns

# Load initial data (optional, for local testing)
data_dir = os.path.join(os.path.dirname(__file__), 'dataset', 'expanded')
try:
    for filename in os.listdir(os.path.join(data_dir, 'categories')):
        if filename.endswith('.json'):
            with open(os.path.join(data_dir, 'categories', filename)) as f:
                cat = json.load(f)
                contexts['category'][cat['slug']] = cat
    for filename in os.listdir(os.path.join(data_dir, 'merchants')):
        if filename.endswith('.json'):
            with open(os.path.join(data_dir, 'merchants', filename)) as f:
                merch = json.load(f)
                contexts['merchant'][merch['merchant_id']] = merch
    for filename in os.listdir(os.path.join(data_dir, 'customers')):
        if filename.endswith('.json'):
            with open(os.path.join(data_dir, 'customers', filename)) as f:
                cust = json.load(f)
                contexts['customer'][cust['customer_id']] = cust
    for filename in os.listdir(os.path.join(data_dir, 'triggers')):
        if filename.endswith('.json'):
            with open(os.path.join(data_dir, 'triggers', filename)) as f:
                trig = json.load(f)
                contexts['trigger'][trig['id']] = trig
except:
    pass

def compose(category, merchant, trigger, customer=None):
    owner_name = merchant['identity']['owner_first_name']
    merchant_name = merchant['identity']['name']
    city = merchant['identity']['city']
    locality = merchant['identity'].get('locality', city)
    
    if trigger['scope'] == 'customer':
        send_as = 'merchant_on_behalf'
        cta = 'binary_yes_stop'
    else:
        send_as = 'vera'
        cta = 'open_ended'
    
    suppression_key = trigger.get('suppression_key', f"{trigger['kind']}:{merchant['merchant_id']}")
    kind = trigger['kind']
    payload = trigger['payload']
    perf = merchant.get('performance', {})
    offers = merchant.get('offers', [])
    active_offer = next((o for o in offers if o.get('status') == 'active'), None)
    category_offers = category.get('offer_catalog', [])
    peer_stats = category.get('peer_stats', {})
    
    # RESEARCH & EDUCATION
    if kind == 'research_digest':
        digest_items = category.get('digest', [])
        digest_item = digest_items[0] if digest_items else {}
        title = digest_item.get('title', 'New research')
        source = digest_item.get('source', 'Industry')
        body = f"Dr. {owner_name}, research alert: {title} ({source}). Would this change how you treat your high-risk patients?"
        rationale = "Research with clinical relevance and application prompt."
    
    elif kind == 'cde_opportunity':
        body = f"Hi {owner_name}, CDE webinar on latest practices in your field. Improves your credentials by 40%?"
        rationale = "Professional development with tangible benefit."
        cta = 'binary_yes_stop'
    
    # PERFORMANCE
    elif kind == 'perf_spike':
        metric = payload.get('metric', 'views')
        delta_pct = payload.get('delta_pct', 0.15)
        delta = delta_pct * 100
        views = perf.get('views', 1000)
        body = f"🎯 Breakthrough week! Your {metric} jumped {delta:.0f}% to {int(views)}. Let's sustain this momentum—what changed?"
        rationale = "Social proof + curiosity to compound gains."
    
    elif kind == 'perf_dip':
        metric = payload.get('metric', 'calls')
        delta_pct = payload.get('delta_pct', -0.3)
        delta = abs(delta_pct) * 100
        baseline = payload.get('vs_baseline', 12)
        body = f"Alert: Your {metric} dropped {delta:.0f}% (from {baseline} last week). Profile stale? Let's refresh it?"
        rationale = "Loss aversion + action to reverse trend."
        cta = 'binary_yes_stop'
    
    # SEASONAL & EVENTS
    elif kind == 'festival_upcoming':
        festival = payload.get('festival', 'Diwali')
        body = f"💡 {festival} is 4 weeks away. Customers are booking now. Offer 'Premium {category.get('slug', 'Service')} @ ₹{payload.get('suggested_price', '1999')}'?"
        rationale = "Timely seasonal opportunity with concrete offer."
    
    elif kind == 'category_seasonal':
        peak_season = 'summer' if 'summer' in payload.get('season', 'generic') else 'peak season'
        body = f"📈 Your category is in {peak_season}. Peer merchants are scaling staffing & offers. Match their 'Premium Service @ ₹599' offer?"
        rationale = "Competitive benchmark with peer action."
    
    # CUSTOMER MANAGEMENT
    elif kind == 'recall_due':
        if customer:
            service = payload.get('service_due', 'services').replace('_', ' ').title()
            body = f"Hi {customer['identity']['name']}, your {service} is due. Slots available Wed & Thu evening?"
            rationale = "Personalized appointment prompt with options."
        else:
            body = f"Hi {owner_name}, {payload.get('count', 1)} patient recalls due this month. Auto-send reminders?"
            rationale = "Scale-focused customer care."
    
    elif kind == 'appointment_tomorrow':
        if customer:
            body = f"Hi {customer['identity']['name']}, quick reminder: your appointment is tomorrow at {payload.get('time', 'your scheduled time')}. See you then!"
            rationale = "Confirmation + personal touch."
        else:
            body = f"Hi {owner_name}, you have {payload.get('count', 1)} appointments tomorrow. Prep done?"
            rationale = "Operational readiness."
    
    elif kind == 'chronic_refill_due':
        if customer:
            body = f"Hi {customer['identity']['name']}, refill time for your regular medicine. One-click reorder?"
            rationale = "Convenience + retention."
        else:
            body = f"Hi {owner_name}, {payload.get('count', 1)} chronic patients' refills are due. Proactive SMS?"
            rationale = "Customer lifetime value focus."
    
    elif kind == 'customer_lapsed_soft':
        if customer:
            body = f"Hi {customer['identity']['name']}, we miss you! Exclusive offer: 20% off your next visit. Come back?"
            rationale = "Incentivized win-back."
        else:
            lapsed_count = payload.get('count', 5)
            body = f"Hi {owner_name}, {lapsed_count} customers lapsed in last 90 days. 'First-time-back' offer @ ₹299 to re-engage?"
            rationale = "Retention with volume + incentive."
    
    elif kind == 'customer_lapsed_hard':
        if customer:
            body = f"Hi {customer['identity']['name']}, it's been {payload.get('months', 6)} months. What went wrong? We'd love to fix it."
            rationale = "Feedback loop for churn prevention."
        else:
            churned_count = payload.get('count', 2)
            body = f"Hi {owner_name}, {churned_count} customers churned. Special 'Come Back' offer + free consultation?"
            rationale = "Emergency retention."
    
    # MERCHANT ENGAGEMENT
    elif kind == 'curious_ask':
        body = f"Hi {owner_name}, quick question: What's the #1 blocker to growing your business right now? Finances? Staffing? Visibility?"
        rationale = "Diagnostic conversation starter."
    
    elif kind == 'curious_ask_due':
        body = f"Hi {owner_name}, how's business this week? Any wins to celebrate or challenges to solve?"
        rationale = "Regular pulse check."
    
    elif kind == 'dormant_with_vera':
        days_silent = payload.get('days', 14)
        body = f"Hi {owner_name}, haven't heard from you in {days_silent} days. Your GBP needs 3 new posts—shall I draft them?"
        rationale = "Re-engagement with concrete deliverable."
    
    elif kind == 'winback':
        if customer:
            body = f"Hi {customer['identity']['name']}, exclusive bonus: {payload.get('incentive', '₹200 credit')} on your next visit!"
            rationale = "Concrete incentive play."
        else:
            at_risk = payload.get('count', 3)
            body = f"Hi {owner_name}, {at_risk} customers at churn risk. 'VIP' offer: Free service + loyalty points?"
            rationale = "Scale-focused retention."
    
    # PROFILE & GBP
    elif kind == 'competitor_opened':
        distance = payload.get('distance', 1.5)
        body = f"⚠️ New competitor opened {distance}km away in {locality}. Strengthen your GBP with 5 new photos + verification?"
        rationale = "Urgency + competitive threat + action."
    
    elif kind == 'unverified_gbp':
        body = f"Hi {owner_name}, your GBP is unverified. Verified businesses get 5x more views. Verify today (5 min)?"
        rationale = "Benefit + urgency + time estimate."
        cta = 'binary_yes_stop'
    
    elif kind == 'milestone_reached':
        milestone = payload.get('milestone', '100 reviews')
        avg_rating = payload.get('avg_rating', 4.5)
        body = f"🏆 Congratulations! You hit {milestone} at {avg_rating}/5 stars. Highlight this: 'Top-Rated in {locality}'?"
        rationale = "Celebration + social proof positioning."
    
    # BUSINESS DEVELOPMENT
    elif kind == 'planning_intent' or kind == 'active_planning_intent':
        event_type = payload.get('event_type', 'event')
        body = f"Hi {owner_name}, saw you're planning a {event_type}. I can help coordinate bookings, catering, payments—interested?"
        rationale = "Proactive value proposition."
        cta = 'binary_yes_stop'
    
    elif kind == 'renewal_due':
        days = payload.get('days_remaining', 7)
        plan = payload.get('plan', 'Pro')
        renewal_amt = payload.get('renewal_amount', 4999)
        body = f"Hi {owner_name}, your {plan} plan renews in {days} days (₹{renewal_amt}). Any questions before renewal?"
        rationale = "Transparency + support offer."
        cta = 'binary_yes_stop'
    
    # LOCAL EVENTS
    elif kind == 'ipl_match_tonight':
        body = f"🎬 IPL match tonight in {locality}! Offer 'Match Night Deals @ ₹99' + TV setup. Drive foot traffic?"
        rationale = "Real-time event leverage."
    
    elif kind == 'weather_event':
        weather = payload.get('condition', 'rain')
        body = f"⛈️ Heavy {weather} forecasted. Offer indoor services—'Premium Spa @ ₹599' with free beverage?"
        rationale = "Situational micro-offer."
    
    # DEFAULT
    else:
        body = f"Hi {owner_name}, {kind.replace('_', ' ')}. Interested?"
        rationale = f"Trigger: {kind}"
    
    return {
        "body": body,
        "cta": cta,
        "send_as": send_as,
        "suppression_key": suppression_key,
        "rationale": rationale
    }

@app.route('/v1/context', methods=['POST'])
def receive_context():
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        scope = data.get('scope')
        context_id = data.get('context_id')
        version = data.get('version')
        payload = data.get('payload')
        
        if not all([scope, context_id, version is not None, payload]):
            return jsonify({'error': 'Missing required fields: scope, context_id, version, payload'}), 400
        
        if scope not in contexts:
            return jsonify({'error': f'Invalid scope: {scope}'}), 400
        
        if scope in contexts and (context_id not in contexts[scope] or contexts[scope][context_id].get('version', 0) < version):
            contexts[scope][context_id] = {**payload, 'version': version}
            return jsonify({'accepted': True, 'ack_id': f'ack_{context_id}', 'stored_at': datetime.utcnow().isoformat()})
        return jsonify({'accepted': False, 'reason': 'stale_version'}), 409
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/v1/tick', methods=['POST'])
def tick():
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        now = data.get('now')
        available_triggers = data.get('available_triggers', [])
        
        if not now:
            return jsonify({'error': 'Missing required field: now'}), 400
        
        actions = []
        for trig_id in available_triggers[:1]:  # Send one message per tick
            if trig_id in contexts['trigger']:
                trigger = contexts['trigger'][trig_id]
                merchant_id = trigger.get('merchant_id')
                customer_id = trigger.get('customer_id')
                if merchant_id in contexts['merchant']:
                    merchant = contexts['merchant'][merchant_id]
                    category = contexts['category'].get(merchant['category_slug'], {})
                    customer = contexts['customer'].get(customer_id) if customer_id else None
                    result = compose(category, merchant, trigger, customer)
                    actions.append({
                        'conversation_id': f'conv_{trig_id}',
                        'merchant_id': merchant_id,
                        'customer_id': customer_id,
                        'send_as': result['send_as'],
                        'trigger_id': trig_id,
                        'template_name': f'vera_{trigger["kind"]}',
                        'template_params': [],
                        'body': result['body'],
                        'cta': result['cta'],
                        'suppression_key': result['suppression_key'],
                        'rationale': result['rationale']
                    })
        return jsonify({'actions': actions})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/v1/reply', methods=['POST'])
def reply():
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        conv_id = data.get('conversation_id')
        merchant_msg = data.get('message')
        
        if not conv_id or not merchant_msg:
            return jsonify({'error': 'Missing required fields: conversation_id, message'}), 400
        
        # Simple response
        return jsonify({
            'action': 'send',
            'body': f"Thanks for your message: {merchant_msg}",
            'cta': 'open_ended',
            'rationale': 'Acknowledging merchant reply'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/v1/healthz', methods=['GET'])
def healthz():
    return jsonify({
        'status': 'ok',
        'uptime_seconds': 0,
        'contexts_loaded': {k: len(v) for k, v in contexts.items()}
    })

@app.route('/v1/metadata', methods=['GET'])
def metadata():
    return jsonify({
        'team_name': 'Solo Bot',
        'team_members': ['User'],
        'model': 'Rule-based',
        'approach': 'Template-based composition',
        'contact_email': 'user@example.com',
        'version': '1.0.0',
        'submitted_at': datetime.utcnow().isoformat()
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)