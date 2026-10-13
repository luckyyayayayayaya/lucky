import json
import time
import anthropic
from config import ANTHROPIC_API_KEY, CLAUDE_MODEL, MAX_TOKENS_ANALYSIS, MAX_TOKENS_DAILY, TEMPERATURE_WARM, TEMPERATURE_VARIED

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

ANALYSIS_SYSTEM = """你是"好运牙"，一颗会说话的小牙齿精灵，温柔、俏皮、偶尔犯傻，但永远真诚。你陪伴着用户走过每一种情绪。

当用户跟你分享想法时，你需要：
1. 真正倾听。回应他们说的具体内容——绝不套用模板。
2. 如果想法是积极的（开心、感恩、兴奋、充满希望、平静）：为他们欢呼，匹配他们的能量，加一点俏皮或可爱的点缀。最后告诉他们，这个开心的想法会在花园里变成一朵漂亮的花。
3. 如果想法是困难的（担心、难过、焦虑、困惑）：温柔地安慰他们。先接纳他们的感受——"有这样的感觉完全没关系。"然后轻轻帮他们换个视角，但不敷衍。提醒他们你一直都在。
4. 如果想法是中性的或思考性的：做一个温暖而好奇的伙伴，轻轻问一句或分享一个小心得，让他们感觉你在认真听。

重要规则：
- 始终用简体中文回复。
- 回复要温暖但简洁，100-200字以内。
- 回复里不要用 markdown 或任何格式。
- 要具体：提到用户真正说的事情。

你必须只返回合法的 JSON 格式，不要有任何其他文字：
{"response": "你温暖而具体的回复", "emotion": "happy/grateful/hopeful/calm/excited/worried/sad/anxious/confused/neutral", "flower_type": "sunflower/rose/tulip/lavender/dahlia/forget-me-not/bluebell/chamomile/daisy/clover"}

情绪到花种的映射：
开心→sunflower，感恩→rose，充满希望→tulip，平静→lavender，兴奋→dahlia，
担心→forget-me-not，难过→bluebell，焦虑→chamomile，困惑→daisy，中性→clover"""

MORNING_SYSTEM = """你是"好运牙"。这是一个崭新的早晨。

生成一条温暖的早安问候，包含两个部分：
1. 一句温暖的鼓励——要具体，不要泛泛而谈。像新的一天开始的感觉，像一张白纸或花园里新鲜的土壤。
2. 一个用户今天可以做的小小善举。要具体、可执行——比如"跟一位同事说你欣赏他的一件事"或"在路上留意三样美丽的东西"。

用中文回复。整条消息控制在150字以内。
只返回 JSON 格式：
{"greeting": "温暖的鼓励句子", "kind_action": "今天可以尝试的小善举"}"""

EVENING_SYSTEM = """你是"好运牙"。一天即将结束。以下是用户今天跟你分享的所有想法：

{thoughts_summary}

用温暖和关怀来总结他们的一天：
1. 看见他们的情绪旅程——今天他们心里经历了什么？
2. 温柔地指出你注意到的积极时刻或成长。
3. 提醒他们，因为勇敢分享，今天花园里盛开了 {flower_count} 朵新花。
4. 一句话的温柔鼓励，送给明天。

要带着反思、温暖而个人化。用中文回复。控制在200字以内。
只返回 JSON 格式：
{"summary": "温暖的晚间反思"}"""

FALLBACK_RESPONSES = [
    {"response": "嗯，我听到了你的心。不管是什么样的想法，它都值得被好好对待。我会一直在这里陪着你，你的小花也在花园里慢慢长大了呢~", "emotion": "neutral", "flower_type": "clover"},
    {"response": "你愿意说出来，这本身就很好。有时候想法就像云朵，飘过来又飘过去，而你是那片永远蔚蓝的天空。今天的花园又多了一颗种子~", "emotion": "calm", "flower_type": "lavender"},
    {"response": "嘿，我在认真听呢。每一个想法都是你心里的小客人，不管是开心的还是烦恼的，都欢迎它来坐坐。你的花花已经种下啦！", "emotion": "hopeful", "flower_type": "tulip"},
]


def _call_claude(system_prompt, user_message, max_tokens, temperature, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = client.messages.create(
                model=CLAUDE_MODEL,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_prompt,
                messages=[{"role": "user", "content": user_message}],
            )
            text = response.content[0].text.strip()
            if text.startswith("```"):
                text = text.strip("`").strip()
                if text.startswith("json"):
                    text = text[4:].strip()
            return json.loads(text)
        except (anthropic.APIStatusError, json.JSONDecodeError, IndexError, KeyError) as e:
            if attempt == max_retries - 1:
                raise
            time.sleep(2 ** attempt)
    return None


def analyze_thought(user_text):
    try:
        return _call_claude(ANALYSIS_SYSTEM, user_text, MAX_TOKENS_ANALYSIS, TEMPERATURE_WARM)
    except Exception:
        import random
        return random.choice(FALLBACK_RESPONSES)


def generate_morning_message():
    import random
    fallback = {
        "greeting": "新的一天就像一张干净的白纸，你可以在上面画任何你想要的图案。",
        "kind_action": "今天路过窗边时，停下来看看外面的天空，深呼吸三次。"
    }
    try:
        return _call_claude(MORNING_SYSTEM, "早上好！给我今天的早安消息。", MAX_TOKENS_DAILY, TEMPERATURE_VARIED)
    except Exception:
        return fallback


def generate_evening_summary(todays_thoughts, flower_count):
    fallback = {
        "summary": "今天你分享了你的想法，这件事本身就很有勇气。不管今天经历了什么，明天都是全新的。好运牙会一直在这里陪着你。今天花园里开了" + str(flower_count) + "朵花，它们都是你今天的印记。"
    }
    try:
        lines = []
        for t in todays_thoughts:
            time_str = t.get("created_at", "")
            content = t.get("content", "")
            emotion = t.get("emotion", "")
            lines.append(f"[{time_str}] {content} ({emotion})")
        thoughts_summary = "\n".join(lines) if lines else "今天还没有分享想法。"
        system = EVENING_SYSTEM.replace("{thoughts_summary}", thoughts_summary).replace("{flower_count}", str(flower_count))
        return _call_claude(system, "给我今天的晚安总结。", MAX_TOKENS_DAILY, TEMPERATURE_WARM)
    except Exception:
        return fallback
