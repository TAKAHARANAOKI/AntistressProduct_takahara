from flask import Flask, render_template, request, redirect, url_for
import json
import os
import random
from model import analyze_emotions
from emotion_mapping import extract_emotion_scores, get_emotion_coordinates, save_emotion_coordinates_to_json
from recommend import recommend_stress_relief

app = Flask(__name__)


responses = {}


def load_diagnosis_data():
    try:
        json_path = os.path.join(os.path.dirname(__file__), 'json/diagnosis.json')
        with open(json_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except Exception as e:
        print(f"JSONファイル読み込みエラー: {e}")
        return {}


diagnosis_data = load_diagnosis_data()


def save_emotions_to_json(emotions):
    json_path = os.path.join(os.path.dirname(__file__), 'json/emotions.json')
    try:
        with open(json_path, 'w', encoding='utf-8') as file:
            json.dump(emotions, file, ensure_ascii=False, indent=4)
        print("感情データを保存しました。")
    except Exception as e:
        print(f"JSONファイル保存エラー: {e}")


def load_emotions_from_json():
    json_path = os.path.join(os.path.dirname(__file__), 'json/emotions.json')
    if os.path.exists(json_path):
        try:
            with open(json_path, 'r', encoding='utf-8') as file:
                data=json.load(file)
                data.pop("vader_scores", None)  # 不要なキーを削除
                return data
        except Exception as e:
            print(f"感情データ読み込みエラー: {e}")
    return {}


def get_random_answer(question, num_answer=4):
    all_answers = question['answer']
    return all_answers if len(all_answers) <= num_answer else random.sample(all_answers, num_answer)

def transform_coordinates_dict(coordinates_dict):
    transformed_data = {}
    for quadrant, emotions in coordinates_dict.items():
        for emotion, coords in emotions.items():
            transformed_data[emotion] = (coords["x"], coords["y"])  # タプル形式に変換

    return transformed_data

@app.route('/')
def index():
    global responses
    responses = {}
    return render_template('index.html', diagnosis_data=diagnosis_data)


@app.route('/diagnosis', methods=['GET', 'POST'])
def diagnosis():
    global responses
   
    if request.method == 'GET':
        question_id = request.args.get('id', 1, type=int)
        for question in diagnosis_data.get('diagnosis', []):
            if question['id'] == question_id:
                question_copy = question.copy()
                question_copy['answer'] = get_random_answer(question)
                return render_template('diagnosis.html', question=question_copy)
        return "質問が見つかりません", 404


    elif request.method == 'POST':
        question_id = str(request.form.get('question_id'))
        selected_answer = request.form.get('selected_answer')
       
        responses[question_id] = selected_answer
        emotions = analyze_emotions(selected_answer)
       
        all_emotions = load_emotions_from_json()
        all_emotions[question_id] = emotions
       
        save_emotions_to_json(all_emotions)
       
        next_id = int(question_id) + 1
       
        if any(q['id'] == next_id for q in diagnosis_data['diagnosis']):
            return redirect(url_for('diagnosis', id=next_id))
        return redirect(url_for('predict'))


@app.route('/predict', methods=['GET', 'POST'])
def predict():
    emotions = load_emotions_from_json()
    emotion_scores = extract_emotion_scores(emotions)
    emotion_coordinates = {key: get_emotion_coordinates(scores) for key, scores in emotion_scores.items()}
   
    emotions_date = load_emotions_from_json()
    emotions_dict={}


    for key in emotions_date:
        if key.isdigit():
            number=emotions_date[key]
            plutchik_emotions_list=number.get("plutchik_emotions",[])
            emotions_dict[key]={}
            for p in plutchik_emotions_list:
                for emotions_name,emotions_score, in p.items():
                    try:
                        emotions_dict[key][emotions_name]=emotions_score
                    except ValueError:
                        print(f"エラー: '{emotions_score}' は数値に変換できません。スキップします。")
   
    emotion_mapping = {
        "fear": (-0.7, 0.7),
        "sadness": (-0.7, -0.7),
        "surprise": (0.2, 1),
        "trust": (0.8, -0.5),
        "joy": (1, 0.2),
        "anticipation": (0.5, 0.8),
        "disgust": (-1, 0.2)
    }


    coordinates_dict={}


    print("感情データ (emotions_dict):", emotions_dict)


    for key,coordinates in emotions_dict.items():
        x,y = 0,0
        coordinates_dict[key]={}
        for name,score in coordinates.items():
            print(f"処理中の感情: {name}, スコア: {score}")  # ここで出力して確認
            if name in emotion_mapping:
               
                X,Y=emotion_mapping[name]


                x += X * score
                y += Y * score
                coordinates_dict[key][name]={'x':x, 'y':y}
        print("修正後のemotion_dict",emotions_dict)
        print("計算後の座標データ:", coordinates_dict)


    save_emotion_coordinates_to_json(coordinates_dict)
   
    print("最終座標データ:",coordinates_dict)

    transformed_data = transform_coordinates_dict(coordinates_dict)

    recommended_method=recommend_stress_relief(transformed_data)

    # デバッグ用: 推奨されるストレス解消法を確認
    print("推奨されるストレス解消法:", recommended_method)

    return render_template('predict.html', recommended_method=recommended_method)



#if __name__ == '__main__':
#    app.run(debug=True)
