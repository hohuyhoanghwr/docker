import time
import redis
from flask import Flask, render_template
import os   # <- new
from dotenv import load_dotenv   # <- new
import pandas as pd
import matplotlib.pyplot as plt

load_dotenv()  # <- new 

cache = redis.Redis(host=os.getenv('REDIS_HOST'), port=6379,  password=os.getenv('REDIS_PASSWORD')) # <- changed
app = Flask(__name__)

def get_hit_count():
    retries = 5
    while True:
        try:
            return cache.incr('hits')
        except redis.exceptions.ConnectionError as exc:
            if retries == 0:
                raise exc
            retries -= 1
            time.sleep(0.5)

@app.route('/')
def hello():
    count = get_hit_count()
    return render_template('hello.html', name= "BIPM", count = count)

@app.route("/titanic")
def titanic():
    csv_path = os.path.join(os.path.dirname(__file__), "titanic.csv")
    df = pd.read_csv(csv_path)

    # Group by Sex and Survived
    grouped = df.groupby(['sex', 'survived']).size().unstack(fill_value=0)

    # Plot
    plt.figure(figsize=(6, 4))
    grouped.plot(kind='bar', color=["tomato", "mediumseagreen"])
    plt.title("Titanic Survival by Gender")
    plt.xlabel("Gender")
    plt.ylabel("Number of Passengers")
    plt.legend(["Did Not Survive", "Survived"], title="Survival Status")
    plt.xticks(rotation=0)
    plt.tight_layout()

    chart_path = os.path.join(os.path.dirname(__file__), "static/survivors_chart.png")
    plt.savefig(chart_path)
    plt.close()

    preview_html = df.head().to_html(classes="data", index=False)
    return render_template("titanic.html", table=preview_html)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80, debug=True)