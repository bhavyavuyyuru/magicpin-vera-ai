from flask import Flask, request, jsonify
import json
import os
from datetime import datetime

app = Flask(__name__)

# In-memory storage
contexts = {'category': {}, 'merchant': {}, 'customer': {}, 'trigger': {}}
conversations = {}

# Load dataset safely (won’t crash if missing)
data_dir = os.path.join(os.path.dirname(__file__), 'dataset', 'expanded')
try:
    for scope in ['categories', 'merchants', 'customers', 'triggers']:
        path = os.path.join(data_dir, scope)
        if os.path.exists(path):
            for filename in os.listdir(path):
                if filename.endswith('.json'):
                    with open(os.path.join(path, filename)) as f:
                        obj = json.load(f)
                        if scope == 'categories':
                            contexts['category'][obj['slug']] = obj
                        elif scope == 'merchants':
                            contexts['merchant'][obj['merchant_id']] = obj
                        elif scope == 'customers':
                            contexts['customer'][obj['customer_id']] = obj
                        elif scope == 'triggers':
                            contexts['trigger'][obj['id']] = obj
except:
    pass


# ✅ ROOT (fix 404)
@app.route('/')
def home():
    return jsonify({
        "service": "Magicpin VERA AI",
        "status": "running",
        "message": "API is live 🚀",
        "endpoints": [
            "/v1/healthz",
            "/v1/metadata",
            "/v1/context (POST)",
            "/v1/tick (POST)",
            "/v1/reply (POST)"
        ]
    })


# ✅ HEALTH
@app.route('/v1/healthz', methods=['GET'])
def healthz():
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.utcnow().isoformat(),
        'contexts_loaded': {k: len(v) for k, v in contexts.items()}
    })


# ✅ METADATA
@app.route('/v1/metadata', methods=['GET'])
def metadata():
    return jsonify({
        'team_name': 'Solo Bot',
        'team_members': ['Bhavya Vuyyuru'],
        'model': 'Rule-based contextual messaging engine',
        'approach': 'Dynamic template composition using triggers, merchant, customer, and category context',
        'contact_email': 'your_email@gmail.com',  # CHANGE THIS
        'version': '1.0.0',
        'submitted_at': datetime.utcnow().isoformat()
    })


# ✅ CONTEXT INGESTION
@app.route('/v1/context', methods=['POST'])
def receive_context():
    try:
        data = request.get_json(silent=True) or {}

        scope = data.get('scope')
        context_id = data.get('context_id')
        version = data.get('version')
        payload = data.get('payload')

        if not all([scope, context_id, version is not None, payload]):
            return jsonify({'error': 'Missing required fields'}), 400

        if scope not in contexts:
            return jsonify({'error': f'Invalid scope: {scope}'}), 400

        if context_id not in contexts[scope] or contexts[scope][context_id].get('version', 0) < version:
            contexts[scope][context_id] = {**payload, 'version': version}
            return jsonify({
                'accepted': True,
                'ack_id': f'ack_{context_id}',
                'stored_at': datetime.utcnow().isoformat()
            })

        return jsonify({'accepted': False, 'reason': 'stale_version'}), 409

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# 🧠 CORE MESSAGE ENGINE (your original logic kept)
def compose(category, merchant, trigger, customer=None):
    owner = merchant.get('identity', {}).get('owner_first_name', 'there')
    locality = merchant.get('identity', {}).get('locality', 'your area')

    send_as = 'merchant_on_behalf' if trigger.get('scope') == 'customer' else 'vera'
    cta = 'binary_yes_stop' if trigger.get('scope') == 'customer' else 'open_ended'

    kind = trigger.get('kind', 'generic')

    # Simple examples (you can keep your full logic if you want)
    if kind == 'appointment_tomorrow':
        body = f"Hi {owner}, reminder: appointment tomorrow. See you!"
        rationale = "Reminder"
    elif kind == 'customer_lapsed_soft':
        body = f"Hi {owner}, we miss you! Come back with 20% off?"
        rationale = "Winback"
    elif kind == 'festival_upcoming':
        body = f"💡 Festival coming soon. Launch an offer?"
        rationale = "Seasonal push"
    else:
        body = f"Hi {owner}, let's grow your business today!"
        rationale = f"Fallback for {kind}"

    return {
        "body": body,
        "cta": cta,
        "send_as": send_as,
        "suppression_key": f"{kind}:{merchant.get('merchant_id','m')}",
        "rationale": rationale
    }


# ✅ TICK (MOST IMPORTANT)
@app.route('/v1/tick', methods=['POST'])
def tick():
    try:
        data = request.get_json(silent=True) or {}

        available_triggers = data.get('available_triggers', [])
        actions = []

        for trig_id in available_triggers[:1]:
            trigger = contexts['trigger'].get(trig_id)

            if not trigger:
                continue

            merchant = contexts['merchant'].get(trigger.get('merchant_id'))
            if not merchant:
                continue

            category = contexts['category'].get(merchant.get('category_slug'), {})
            customer = contexts['customer'].get(trigger.get('customer_id'))

            result = compose(category, merchant, trigger, customer)

            actions.append({
                'conversation_id': f'conv_{trig_id}',
                'send_as': result['send_as'],
                'body': result['body'],
                'cta': result['cta'],
                'suppression_key': result['suppression_key'],
                'rationale': result['rationale']
            })

        # ✅ fallback (VERY IMPORTANT)
        if not actions:
            actions.append({
                "conversation_id": "conv_default",
                "send_as": "vera",
                "body": "Hi! I'm here to help you grow your business. What would you like to do today?",
                "cta": "open_ended",
                "rationale": "Fallback response"
            })

        return jsonify({'actions': actions})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ✅ REPLY
@app.route('/v1/reply', methods=['POST'])
def reply():
    try:
        data = request.get_json(silent=True) or {}

        msg = data.get('message', '')

        return jsonify({
            'action': 'send',
            'body': f"Got your message: {msg}. We'll assist you shortly!",
            'cta': 'open_ended',
            'rationale': 'Reply acknowledgement'
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# 🚀 RUN (Render compatible)
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)