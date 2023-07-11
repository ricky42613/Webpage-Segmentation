from flask import Flask,request,jsonify
from web_segmentation import WebSegmentation
import json
app = Flask(__name__)
WS = WebSegmentation()


@app.route("/")
def home():
    return  "welcome to web segmentation server"

@app.route("/segmentation", methods=['POST'])
def segment():
    if request.method == "POST":
        data = json.loads(request.data.decode())
        page = data['page']
        cp = WS.clean_page(page)
        blocks = WS.segmentation(cp)
        return jsonify(
            blocks = blocks
        )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)