from flask import Flask,request,jsonify
from web_segmentation import WebSegmentation

app = Flask(__name__)
WS = WebSegmentation()


@app.route("/")
def home():
    return  "welcome to web segmentation server"

@app.route("/segmentation", methods=['POST'])
def segment():
    if request.method == "POST":
        page = request.form.get('page')
        cp = WS.clean_page(page)
        blocks = WS.segmentation(cp)
        return jsonify(
            blocks = blocks
        )


app.run()