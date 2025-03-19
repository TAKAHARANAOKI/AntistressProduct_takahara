import json
import os


def load_emotions_data():
    """感情データをJSONファイルから読み込む"""
    try:
        json_path = os.path.join(os.path.dirname(__file__), 'json/emotions.json')
        with open(json_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except Exception as e:
        print(f"JSONファイル読み込みエラー: {e}")
        return {}
    
def save_emotion_coordinates_to_json(emotion_coordinates):
    """感情の2D座標データをJSONファイルに保存"""
    json_path = os.path.join(os.path.dirname(__file__), 'json/emotion_coordinates.json')
    try:
        with open(json_path, 'w', encoding='utf-8') as file:
            json.dump(emotion_coordinates, file, ensure_ascii=False, indent=4)
        print("感情座標データを保存しました。")
    except Exception as e:
        print(f"JSONファイル保存エラー: {e}")

def extract_emotion_scores(emotions_data):
    """JSONデータから各IDごとの感情スコアを抽出"""
    emotion_scores_dict = {}

    for key, value in emotions_data.items():
        if not isinstance(value, dict):
            print(f"警告: {key} のデータ形式が異常です。スキップします: {value}")
            continue

        emotion_scores = {}
        for emotion_dict in value.get("plutchik_emotions", []):
            if isinstance(emotion_dict, dict):
                for emotion, score in emotion_dict.items():
                    emotion_scores[emotion] = score

        emotion_scores_dict[key] = emotion_scores

    return emotion_scores_dict

def get_emotion_coordinates(emotion_scores):
    """感情スコアを2次元座標に変換する"""
    x, y = 0, 0
    total_weight = 0

    for emotion, score in emotion_scores.items():
        if emotion in emotion_mapping:
            ex, ey = emotion_mapping[emotion]
            x += ex * score
            y += ey * score
            total_weight += score

    if total_weight > 0:
        x /= total_weight
        y /= total_weight

    return (x, y)

emotion_mapping = {
    "fear": (-0.7, 0.7),
    "sadness": (-0.7, -0.7),
    "surprise": (0.2, 1),
    "trust": (0.8, -0.5),
    "joy": (1, 0.2),
    "anticipation": (0.5, 0.8),
    "disgust": (-1, 0.2)
}

# 感情データを読み込み、スコアを抽出
emotions_data = load_emotions_data()
emotion_scores = extract_emotion_scores(emotions_data)

# 感情スコアを2次元座標に変換し保存
emotion_coordinates = {key: get_emotion_coordinates(scores) for key, scores in emotion_scores.items()}
save_emotion_coordinates_to_json(emotion_coordinates)
