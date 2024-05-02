from flask import Flask, render_template, request, jsonify
from models import Model

app = Flask(__name__)


@app.route("/")
def index():
    print("hello world")
    # return empty page
    return render_template("hi.html")
    # return render_template("index.html")


@app.route("/calculate", methods=["POST"])
def calculate():
    if request.method == "POST":
        tickers = request.form["ticker"]
        params = request.form.to_dict()

        model = Model()
        tickers = tickers.split(",")
        valuations_df, invalid = model.get_valuations(tickers, params)
        result_html = valuations_df.to_html(classes="table table-bordered", index=False)
        return jsonify({"result_html": result_html, "invalid_tickers": list(invalid)})


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
