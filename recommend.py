import json
import numpy as np

 # ストレス解消法のマッピング
recommend_mapping = {
    "好きなスポーツをする": (-1, 1),
    "ジョギングをする": (-0.2, 0.8),
    "好きなアーティストのライブに行く": (-0.5, 0.5),
    "カラオケに行く": (-1, 0.2),
    "買い物に行く": (-0.2, 0.2),
    "サウナに行って汗を流す": (-0.2, -0.6),
    "仲のいい友達に愚痴る": (-0.7, -0.2),
    "ゲームをする": (-0.7, -0.5),
    "部屋を綺麗にしてすっきりしよう！": (0.4, 1),
    "散歩する": (0.8, 0.4),
    "満足するまで食べる": (0.2, 0.5),
    "仲のいい友達と遊ぶ": (0.4, 0.2),
    "旅行に行く": (1, 1),
    "大自然に触れる": (1, -0.2),
    "湯船に浸かる": (0.5, -0.5),
    "音楽を聴く": (0.8, -0.6),
    "気の許すまで寝てみよう": (0.2, -1),
    "読書をする": (0.8, -0.8),
    "映画・動画を見る": (0.5, -0.8),
    "瞑想する": (1, -1),
}

def load_emotion_coordinates(filepath):
    """ emotion_coordinates.json を読み込む """
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

def determine_quadrant(x, y):
    """ 座標 (x, y) の象限を判定する """
    if x >= 0 and y >= 0:
        return 1
    elif x < 0 and y >= 0:
        return 2
    elif x < 0 and y < 0:
        return 3
    elif x >= 0 and y < 0:
        return 4

def group_and_average_emotions(emotion_data):
    """ 同じ象限の感情をグループ化し、平均座標を求める """
    quadrant_groups = {1: [], 2: [], 3: [], 4: []}
    
    for emotion, (x, y) in emotion_data.items():
        quadrant = determine_quadrant(x, y)
        quadrant_groups[quadrant].append((x, y))
    
    averaged_coordinates = {}
    for quadrant, points in quadrant_groups.items():
        if points:
            avg_x = np.mean([p[0] for p in points])
            avg_y = np.mean([p[1] for p in points])
            averaged_coordinates[quadrant] = (avg_x, avg_y)
    
    return averaged_coordinates

def invert_coordinates(averaged_coordinates):
    """ 平均化した座標を反転する """
    return {q: (-x, -y) for q, (x, y) in averaged_coordinates.items()}

def find_nearest_recommendation(inverted_coords, recommend_mapping):
    """ 反転後の座標とストレス解消法の座標を比較し、一番近いものを選ぶ """
    def euclidean_distance(p1, p2):
        return np.linalg.norm(np.array(p1) - np.array(p2))
    
    recommendations = {}
    for quadrant, coord in inverted_coords.items():
        nearest_method = min(list(recommend_mapping), key=lambda k: euclidean_distance(coord, recommend_mapping[k]))
        recommendations[quadrant] = nearest_method
    
    return recommendations

"""感情データを元にストレス解消法を推薦する"""  
def recommend_stress_relief(emotion_data):
    """ 感情データを元にストレス解消法を推薦する """
    print("Received emotion data:", emotion_data)  # 受け取ったデータを表示

    averaged_coords = group_and_average_emotions(emotion_data)
    print("Averaged coordinates:", averaged_coords)  # 平均化後の座標を表示

    inverted_coords = invert_coordinates(averaged_coords)
    print("Inverted coordinates:", inverted_coords)  # 反転後の座標を表示

    recommendations = find_nearest_recommendation(inverted_coords, recommend_mapping)
    print("Final Recommendations:", recommendations)  # 最終的な推奨結果を表示

    return recommendations
    


