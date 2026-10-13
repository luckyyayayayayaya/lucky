import random
import math

FLOWER_MAP = {
    "happy": {"type": "sunflower", "color": "#FFD54F", "variant": ["#FFC107", "#FFB300", "#FFA000"]},
    "grateful": {"type": "rose", "color": "#F48FB1", "variant": ["#EC407A", "#E91E63", "#F06292"]},
    "hopeful": {"type": "tulip", "color": "#CE93D8", "variant": ["#AB47BC", "#BA68C8", "#9C27B0"]},
    "calm": {"type": "lavender", "color": "#B39DDB", "variant": ["#9575CD", "#7E57C2", "#9FA8DA"]},
    "excited": {"type": "dahlia", "color": "#FF8A65", "variant": ["#FF7043", "#F4511E", "#FF5722"]},
    "worried": {"type": "forget-me-not", "color": "#90CAF9", "variant": ["#64B5F6", "#42A5F5", "#5C6BC0"]},
    "sad": {"type": "bluebell", "color": "#81D4FA", "variant": ["#4FC3F7", "#29B6F6", "#7986CB"]},
    "anxious": {"type": "chamomile", "color": "#FFF9C4", "variant": ["#FFF176", "#FFEE58", "#FDD835"]},
    "confused": {"type": "daisy", "color": "#F8F8F8", "variant": ["#F5F5F5", "#EEEEEE", "#FAFAFA"]},
    "neutral": {"type": "clover", "color": "#A5D6A7", "variant": ["#81C784", "#66BB6A", "#4CAF50"]},
}


def place_flower(existing_flowers):
    for _ in range(50):
        x = random.uniform(3, 97)
        y = random.uniform(5, 85)
        collision = False
        for f in existing_flowers:
            fx = float(f.get("position_x", 0))
            fy = float(f.get("position_y", 0))
            dist = math.sqrt((x - fx) ** 2 + (y - fy) ** 2)
            if dist < 6:
                collision = True
                break
        if not collision:
            size = random.uniform(0.7, 1.3)
            color_variant = random.randint(0, 2)
            return x, y, size, color_variant
    x = random.uniform(3, 97)
    y = random.uniform(5, 85)
    size = random.uniform(0.7, 1.3)
    color_variant = random.randint(0, 2)
    return x, y, size, color_variant


def get_flower_config(emotion):
    entry = FLOWER_MAP.get(emotion, FLOWER_MAP["neutral"])
    variant_idx = random.randint(0, 2)
    return {
        "flower_type": entry["type"],
        "color": entry["variant"][variant_idx],
        "variant_idx": variant_idx,
    }
