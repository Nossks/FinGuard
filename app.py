from flask import Flask, render_template, request, jsonify
import sys
import os
import traceback

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from src.pipeline.prediction import Prediction
except ImportError:
    try:
        from src.pipeline.prediction import Prediction
    except ImportError:
        print("CRITICAL ERROR: Could not find 'src/pipeline/prediction.py'")
        sys.exit(1)

app = Flask(__name__)
pipeline = None

def initialize_pipeline():
    global pipeline
    if pipeline is None:
        print("⚡ FLASK: Initializing Pipeline...")
        try:
            pipeline = Prediction()
            print("FLASK: Pipeline Ready.")
        except:
            traceback.print_exc()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/get_response", methods=["POST"])
def get_response():
    if pipeline is None:
        initialize_pipeline()
        
    try:
        user_input = request.form["msg"]
        
        bot_reply_object, metrics = pipeline.predict(user_input)
        
        if hasattr(bot_reply_object, 'content'):
            bot_text = bot_reply_object.content
        else:
            bot_text = str(bot_reply_object)

        if metrics.get('cyborg', 0) > 0:
            mode_used = "search"
        else:
            mode_used = "chat"

        return jsonify({
            "response": bot_text, 
            "metrics": metrics,
            "mode_used": mode_used
        })
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({"response": "Error processing request.", "metrics": {}, "mode_used": "error"})

if __name__ == "__main__":
    initialize_pipeline()
    print("Open in Browser: http://127.0.0.1:5000")
    app.run(host="0.0.0.0", port=5000, debug=True)