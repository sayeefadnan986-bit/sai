from flask import Flask, request, jsonify, render_template_string
import requests
import os

app = Flask(__name__)

# ==========================================
# 🎨 প্রিমিয়াম এআই ইন্টারফেস
# ==========================================
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="bn">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Nexus AI v2.5 - Sayeef Adnan</title>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600&family=Hind+Siliguri:wght@300;400;600&display=swap" rel="stylesheet">
    <style>
        :root {
            --primary: #00f2fe;
            --secondary: #4facfe;
            --bg-dark: #050505;
            --glass: rgba(255, 255, 255, 0.03);
            --glass-border: rgba(255, 255, 255, 0.1);
            --text-main: #f0f0f0;
        }

        * { box-sizing: border-box; margin: 0; padding: 0; }

        body {
            font-family: 'Plus Jakarta Sans', 'Hind Siliguri', sans-serif;
            background-color: var(--bg-dark);
            background-image: 
                radial-gradient(circle at 10% 20%, rgba(0, 242, 254, 0.08) 0%, transparent 40%),
                radial-gradient(circle at 90% 80%, rgba(79, 172, 254, 0.08) 0%, transparent 40%);
            height: 100vh;
            display: flex;
            flex-direction: column;
            color: var(--text-main);
            overflow: hidden;
        }

        .header {
            padding: 20px;
            text-align: center;
            border-bottom: 1px solid var(--glass-border);
            backdrop-filter: blur(20px);
            z-index: 10;
        }
        .header h1 {
            font-size: 22px;
            letter-spacing: 4px;
            text-transform: uppercase;
            background: linear-gradient(to right, var(--primary), var(--secondary));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 800;
        }

        .chat-container {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
            display: flex;
            flex-direction: column;
            gap: 20px;
        }
        .chat-container::-webkit-scrollbar { width: 4px; }
        .chat-container::-webkit-scrollbar-thumb { background: var(--glass-border); border-radius: 10px; }

        .msg {
            max-width: 85%;
            padding: 18px;
            border-radius: 24px;
            font-size: 15.5px;
            line-height: 1.7;
            animation: appear 0.4s cubic-bezier(0, 0, 0.2, 1);
            position: relative;
        }

        @keyframes appear { from { opacity: 0; transform: translateY(15px); } to { opacity: 1; transform: translateY(0); } }

        .user-msg {
            align-self: flex-end;
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            color: #000;
            font-weight: 600;
            border-bottom-right-radius: 4px;
            box-shadow: 0 4px 15px rgba(0, 242, 254, 0.2);
        }

        .bot-msg {
            align-self: flex-start;
            background: var(--glass);
            border: 1px solid var(--glass-border);
            border-bottom-left-radius: 4px;
            backdrop-filter: blur(10px);
        }

        .bot-header {
            font-size: 11px;
            color: var(--primary);
            margin-bottom: 10px;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            font-weight: bold;
            display: flex;
            align-items: center;
            gap: 6px;
        }

        .input-wrapper {
            padding: 25px;
            background: rgba(0,0,0,0.6);
            backdrop-filter: blur(30px);
            border-top: 1px solid var(--glass-border);
            display: flex;
            gap: 12px;
        }
        input {
            flex: 1;
            padding: 16px 24px;
            border-radius: 35px;
            border: 1px solid var(--glass-border);
            background: rgba(255,255,255,0.05);
            color: white;
            outline: none;
            font-size: 16px;
            transition: 0.3s;
        }
        input:focus { border-color: var(--primary); box-shadow: 0 0 20px rgba(0, 242, 254, 0.1); }
        
        #sendBtn {
            background: var(--primary);
            border: none;
            width: 54px;
            height: 54px;
            border-radius: 50%;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        }
        #sendBtn:hover { transform: scale(1.1) rotate(-10deg); box-shadow: 0 0 25px var(--primary); }

        .typing { display: flex; gap: 5px; padding: 10px; }
        .typing span { width: 7px; height: 7px; background: var(--primary); border-radius: 50%; animation: pulse 0.8s infinite alternate; }
        .typing span:nth-child(2) { animation-delay: 0.2s; }
        .typing span:nth-child(3) { animation-delay: 0.4s; }
        @keyframes pulse { from { opacity: 0.2; transform: scale(0.8); } to { opacity: 1; transform: scale(1.1); } }

        .footer {
            padding: 12px;
            font-size: 10px;
            text-align: center;
            background: #000;
            color: #555;
            letter-spacing: 1px;
        }
    </style>
</head>
<body>

<div class="header">
    <h1>Nexus AI v2.5</h1>
</div>

<div class="chat-container" id="chatBox">
    <div class="msg bot-msg">
        <div class="bot-header">✨ System Active</div>
        আসসালামু আলাইকুম! আমি <strong>Nexus AI</strong>। আমি এখন সক্রিয় আছি। আপনার যেকোনো প্রশ্ন থাকলে করতে পারেন। 😊
    </div>
</div>

<div class="input-wrapper">
    <input type="text" id="userInput" placeholder="এখানে মেসেজ লিখুন..." autocomplete="off" onkeypress="if(event.key==='Enter') sendMessage()">
    <button id="sendBtn" onclick="sendMessage()">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="black" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><line x1="22" y1="2" x2="11" y2="13"></line><polygon points="22 2 15 22 11 13 2 9 22 2"></polygon></svg>
    </button>
</div>

<div class="footer">
    <div>BUILD BY SAYEEF ADNAN | ALL RIGHTS RESERVED © 2026</div>
</div>

<script>
    async function sendMessage() {
        const input = document.getElementById('userInput');
        const query = input.value.trim();
        const chatBox = document.getElementById('chatBox');
        if(!query) return;

        chatBox.innerHTML += `<div class="msg user-msg">${query}</div>`;
        input.value = '';
        chatBox.scrollTop = chatBox.scrollHeight;

        const loadId = 'L' + Date.now();
        chatBox.innerHTML += `<div class="msg bot-msg" id="${loadId}"><div class="typing"><span></span><span></span><span></span></div></div>`;
        chatBox.scrollTop = chatBox.scrollHeight;

        try {
            const response = await fetch('/chat', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({query: query})
            });
            const data = await response.json();
            document.getElementById(loadId).remove();

            let html = `<div class="bot-header">🤖 Nexus Intelligence</div>`;
            html += `<div>${data.answer}</div>`;
            html += `<div style="margin-top:15px; font-size:9px; color:#444; border-top:1px solid rgba(255,255,255,0.03); padding-top:8px; text-align:right;">Nexus Core v2.5</div>`;

            chatBox.innerHTML += `<div class="msg bot-msg">${html}</div>`;
        } catch(e) {
            document.getElementById(loadId).remove();
            chatBox.innerHTML += `<div class="msg bot-msg" style="border-color:red">সিস্টেম লোড নিতে পারছে না। ⚠️</div>`;
        }
        chatBox.scrollTop = chatBox.scrollHeight;
    }
</script>

</body>
</html>
"""

GEMINI_API_KEY = "AIzaSyDufL-sCOsQ3yc-LIO8Bn6P6ctxQZS8h20" 

# নতুন পিং রুট যা সার্ভারকে সজাগ রাখবে
@app.route('/ping')
def ping():
    return "OK", 200

def get_ai_response(user_query):
    if "আদনান" in user_query or "adnan" in user_query.lower():
        return "আদনান একজন খুব ভালো ছেলে 😊 । সে ২০২৬ সালের অর্থাৎ এখন কলারোয়া সরকারি জি. কে. এম. কে. পাইলট মাধ্যমিক বিদ্যালয়ের নবম শ্রেণীতে পড়ে |সে সবার সাথে সুন্দর ব্যবহার করে | সে এখন কলারোয়া, সাতক্ষীরাতে থাকে |তার সম্পর্কে সে বেশি কিছু তথ্য দিতে নিষেধ করেছে এবং আমাকে সেই বানিয়েছে আল্লাহর রহমতে। ❤️"

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {'Content-Type': 'application/json'}
    system_prompt = "আপনার নাম Nexus AI। আপনার নির্মাতা Sayeef Adnan। আপনার কথাবার্তা হবে মার্জিত এবং ইমোজি সমৃদ্ধ।"
    
    payload = {
        "contents": [{"parts": [{"text": f"System Instruction: {system_prompt}\nUser Query: {user_query}"}]}]
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=20)
        if response.status_code == 200:
            result = response.json()
            return result['candidates'][0]['content']['parts'][0]['text']
        else:
            return "দুঃখিত, আমি এই মুহূর্তে উত্তর দিতে পারছি না। ⚠️"
    except Exception as e:
        return "সার্ভার সংযোগ বিচ্ছিন্ন। 🌐"

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    query = data.get('query', '')
    answer = get_ai_response(query)
    return jsonify({'answer': answer})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

