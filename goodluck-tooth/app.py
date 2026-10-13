import json
from datetime import date, datetime
from pathlib import Path

from flask import Flask, render_template, request, jsonify, g

from config import MORNING_START, MORNING_END, EVENING_START, EVENING_END
from models import init_db, save_thought, get_todays_thoughts, get_thoughts_page, get_thought_by_id
from models import get_or_create_daily_message, add_flower, get_all_flowers, get_stats, garden_level
from ai_client import analyze_thought, generate_morning_message, generate_evening_summary
from garden import place_flower, get_flower_config

BASE_DIR = Path(__file__).resolve().parent
app = Flask(
    __name__,
    template_folder=str(BASE_DIR / "templates"),
    static_folder=str(BASE_DIR / "static"),
)


@app.before_request
def before_request():
    g.request_start = datetime.now()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/thoughts", methods=["POST"])
def api_create_thought():
    data = request.get_json(silent=True)
    if not data or not data.get("content"):
        return jsonify({"error": "请输入内容"}), 400
    content = data["content"].strip()
    if len(content) > 500:
        return jsonify({"error": "内容太长啦，控制在500字以内吧"}), 400

    today = date.today().isoformat()
    stats = get_stats()
    if stats["today_count"] >= 50:
        return jsonify({"error": "今天的想法已经够多啦，休息一下，明天再来找好运牙聊天吧~"}), 429

    result = analyze_thought(content)
    emotion = result.get("emotion", "neutral")
    ai_response = result.get("response", "")
    flower_config = get_flower_config(emotion)

    thought_id = save_thought(content, emotion, ai_response, flower_config["flower_type"])

    existing = get_all_flowers()
    x, y, size, color_variant = place_flower(existing)
    flower_id = add_flower(thought_id, flower_config["flower_type"], x, y, size, color_variant)

    return jsonify({
        "thought": {
            "id": thought_id,
            "content": content,
            "emotion": emotion,
            "ai_response": ai_response,
            "flower_type": flower_config["flower_type"],
            "created_at": datetime.now().isoformat(),
        },
        "flower": {
            "id": flower_id,
            "thought_id": thought_id,
            "flower_type": flower_config["flower_type"],
            "position_x": x,
            "position_y": y,
            "size": size,
            "color_variant": color_variant,
        },
    })


@app.route("/api/thoughts", methods=["GET"])
def api_get_thoughts():
    page = request.args.get("page", 1, type=int)
    limit = request.args.get("limit", 20, type=int)
    thoughts, total = get_thoughts_page(page, limit)
    return jsonify({"thoughts": thoughts, "total": total, "page": page, "limit": limit})


@app.route("/api/thoughts/<int:thought_id>", methods=["GET"])
def api_get_thought(thought_id):
    thought = get_thought_by_id(thought_id)
    if not thought:
        return jsonify({"error": "没找到这条想法"}), 404
    return jsonify(thought)


@app.route("/api/garden", methods=["GET"])
def api_garden():
    flowers = get_all_flowers()
    return jsonify({"flowers": flowers})


@app.route("/api/garden/stats", methods=["GET"])
def api_garden_stats():
    stats = get_stats()
    stats["garden_level"] = garden_level(stats["total_flowers"])
    return jsonify(stats)


@app.route("/api/daily/message", methods=["GET"])
def api_daily_message():
    msg_type = request.args.get("type", "morning")
    current_hour = datetime.now().hour

    if msg_type == "morning":
        if not (MORNING_START <= current_hour < MORNING_END):
            return jsonify({"type": "morning", "available": False, "message": "早上5点到12点才能收到早安消息哦"})
    elif msg_type == "evening":
        if not (EVENING_START <= current_hour < EVENING_END):
            return jsonify({"type": "evening", "available": False, "message": "下午5点到晚上11点才能收到晚安总结哦"})
    else:
        return jsonify({"error": "type 必须是 morning 或 evening"}), 400

    existing = get_or_create_daily_message(msg_type)
    if existing:
        try:
            content = json.loads(existing["content"])
        except (json.JSONDecodeError, TypeError):
            content = {"message": existing["content"]}
        return jsonify({"type": msg_type, "available": True, "data": content})

    if msg_type == "morning":
        result = generate_morning_message()
        content_str = json.dumps(result, ensure_ascii=False)
    else:
        todays = get_todays_thoughts()
        stats = get_stats()
        result = generate_evening_summary(todays, stats.get("today_flowers", 0))
        content_str = json.dumps(result, ensure_ascii=False)

    saved = get_or_create_daily_message(msg_type, content_str)
    return jsonify({"type": msg_type, "available": True, "data": result})


@app.route("/api/stats", methods=["GET"])
def api_stats():
    stats = get_stats()
    stats["garden_level"] = garden_level(stats["total_flowers"])
    return jsonify(stats)


@app.errorhandler(400)
def bad_request(e):
    return jsonify({"error": str(e.description) if e.description else "请求有误"}), 400


@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "没找到"}), 404


@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "服务器出了点小问题，请稍后再试"}), 500


if __name__ == "__main__":
    init_db()
    app.run(debug=True, host="0.0.0.0", port=5000, threaded=True)
