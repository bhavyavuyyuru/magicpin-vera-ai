from flask import Flask, request, jsonify
import json
import os
from datetime import datetime

app = Flask(__name__)

# In-memory storage
contexts = {'category': {}, 'merchant': {}, 'customer': {}, 'trigger': {}}

# 🔥 Conversation memory (for STOP + loop control)
conversation_state = {}

# 🔥 Trigger priority
PRIORITY = {
    "appointment_tomorrow": 10,
    "chronic_refill_due": 9,
    "customer_lapsed_hard": 9,
    "perf_dip": 9,
    "customer_lapsed_soft": 8,
    "competitor_opened": 8,
    "recall_due": 8,
    "festival_upcoming": 7,
    "category_seasonal": 7,
    "perf_spike": 6,
    "milestone_reached": 5,
    "curious_ask": 3
}

def pick_best_trigger(triggers):
    return max(triggers, key=lambda t: PRIORITY.get(t.get("kind"), 1))


# 🔥 VERA-style message generator
def generate_message(trigger, merchant, customer=None):
    kind = trigger.get("kind")
    payload = trigger.get("payload", {})

    owner = merchant.get("identity", {}).get("owner_first_name", "there")
    locality = merchant.get("identity", {}).get("locality", "your area")
    name = customer.get("identity", {}).get("name") if customer else None

    if kind == "appointment_tomorrow" and name:
        return f"Hi {name}, reminder: your appointment is tomorrow. Need to reschedule?"

    if kind == "perf_dip":
        return f"Hi {owner}, your calls dropped this week. Updating your profile + adding a ₹299 offer can recover traffic. Want me to fix it?"

    if kind == "perf_spike":
        return f"🎯 Great week! Your views are up. Perfect time to launch an offer—want me to set it up?"

    if kind == "competitor_opened":
        return f"⚠️ A new competitor opened in {locality}. Add fresh photos + verify your profile to stay ahead. Want me to do it?"

    if kind == "customer_lapsed_soft" and name:
        return f"Hi {name}, we miss you! A 20% comeback offer can bring you back. Want me to book your visit?"

    if kind == "customer_lapsed_hard" and name:
        return f"Hi {name}, it’s been a while. Anything we can improve? We’d love to have you back."

    if kind == "chronic_refill_due" and name:
        return f"Hi {name}, your regular medicine is due. Reordering now avoids hassle—want me to place it?"

    if kind == "recall_due" and name:
        return f"Hi {name}, your service is due. Slots available this week—shall I book one?"

    if kind == "festival_upcoming":
        fest = payload.get("festival", "Festival")
        return f"💡 {fest} bookings are rising. Launch a ₹999 festive package—want me to set it up?"

    if kind == "category_seasonal":
        return f"📈 Your category is entering peak season. Top merchants are pushing premium offers. Want to match them?"

    if kind == "milestone_reached":
        return f"🏆 You hit a milestone! Promote this as 'Top-rated in {locality}' to boost conversions—want me to highlight it?"

    if kind == "curious_ask":
        return f"Hi {owner}, what's limiting growth right now—visibility, demand, or staffing?"

    return f"Hi {owner}, I spotted a growth opportunity for your business. Want help improving it?"


# Load dataset (safe)
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


# ✅ ROOT
@app.route('/')
def home():
    return jsonify({
        "service": "Magicpin VERA AI",
        "status": "running",
        "message": "API is live 🚀"
    })


# ✅ HEALTH
@app.route('/v1/healthz', methods=['GET'])
def healthz():
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.utcnow().isoformat()
    })


# ✅ METADATA
@app.route('/v1/metadata', methods=['GET'])
def metadata():
    return jsonify({
        'team_name': 'Solo Bot',
        'team_members': ['Bhavya Vuyyuru'],
        'model': 'Rule-based decision engine',
        'approach': 'Trigger prioritization + contextual message generation',
        'contact_email': 'your_email@gmail.com',
        'version': '2.0.0',
        'submitted_at': datetime.utcnow().isoformat()
    })


# ✅ CONTEXT
@app.route('/v1/context', methods=['POST'])
def receive_context():
    data = request.get_json(silent=True) or {}

    scope = data.get('scope')
    context_id = data.get('context_id')
    payload = data.get('payload')

    if not all([scope, context_id, payload]):
        return jsonify({'error': 'Missing fields'}), 400

    contexts[scope][context_id] = payload

    return jsonify({'accepted': True})


# ✅ TICK (SMART DECISION ENGINE)
@app.route('/v1/tick', methods=['POST'])
def tick():
    data = request.get_json(silent=True) or {}

    trigger_ids = data.get('available_triggers', [])
    triggers = [contexts['trigger'].get(t) for t in trigger_ids if t in contexts['trigger']]

    if not triggers:
        return jsonify({
            "actions": [{
                "conversation_id": "default",
                "body": "Hi! Want help improving your business performance?",
                "cta": "open_ended"
            }]
        })

    best = pick_best_trigger(triggers)

    merchant = contexts['merchant'].get(best.get('merchant_id'), {})
    customer = contexts['customer'].get(best.get('customer_id'))

    message = generate_message(best, merchant, customer)

    return jsonify({
        "actions": [{
            "conversation_id": f"conv_{best.get('id')}",
            "send_as": "merchant_on_behalf" if customer else "vera",
            "body": message,
            "cta": "binary_yes_stop"
        }]
    })


# ✅ REPLY (INTELLIGENT)
@app.route('/v1/reply', methods=['POST'])
def reply():
    data = request.get_json(silent=True) or {}

    msg = data.get("message", "").lower()
    conv = data.get("conversation_id", "default")

    # STOP
    if "stop" in msg or "unsubscribe" in msg:
        conversation_state[conv] = "ended"
        return jsonify({"action": "end"})

    if conversation_state.get(conv) == "ended":
        return jsonify({"action": "end"})

    if any(x in msg for x in ["book", "appointment"]):
        return jsonify({
            "action": "send",
            "body": "Got it 👍 Checking availability and confirming shortly."
        })

    if any(x in msg for x in ["yes", "ok", "sure"]):
        return jsonify({
            "action": "send",
            "body": "Perfect 👍 I’ll take care of this and update you shortly."
        })

    if any(x in msg for x in ["no", "not now"]):
        conversation_state[conv] = "ended"
        return jsonify({
            "action": "end",
            "body": "No worries 🙂 Reach out anytime!"
        })

    return jsonify({
        "action": "send",
        "body": "Got it 👍 Let me help you with that."
    })


# RUN
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)