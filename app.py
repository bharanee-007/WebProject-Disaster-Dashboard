from flask import Flask, render_template, request
import requests
from sklearn.tree import DecisionTreeClassifier

app = Flask(__name__)

# Your OpenWeather API key
API_KEY = "2d684f8945172e0029170f169b6bfd31"


# ---------------- AI RISK MODEL ----------------

# Training data:
# [temperature, humidity, wind speed]
X = [
    [20, 80, 2],
    [25, 70, 5],
    [28, 65, 8],
    [30, 60, 10],
    [32, 50, 15],
    [35, 40, 20],
    [38, 35, 25],
    [40, 30, 30]
]

# Risk labels
y = [
    "LOW RISK",
    "LOW RISK",
    "LOW RISK",
    "MEDIUM RISK",
    "MEDIUM RISK",
    "HIGH RISK",
    "HIGH RISK",
    "HIGH RISK"
]

# Create and train AI model
model = DecisionTreeClassifier(random_state=42)
model.fit(X, y)


# ---------------- MAIN PAGE ----------------

@app.route("/", methods=["GET", "POST"])
def home():

    weather = None
    error = None

    if request.method == "POST":

        city = request.form.get("city")

        # OpenWeather API
        url = "https://api.openweathermap.org/data/2.5/weather"

        params = {
            "q": city,
            "appid": API_KEY,
            "units": "metric"
        }

        try:

            response = requests.get(url, params=params, timeout=10)

            if response.status_code == 200:

                data = response.json()

                # Get live environmental values
                temperature = data["main"]["temp"]
                humidity = data["main"]["humidity"]
                pressure = data["main"]["pressure"]
                wind = data["wind"]["speed"]

                description = data["weather"][0]["description"]

                # AI prediction
                risk = model.predict([
                    [temperature, humidity, wind]
                ])[0]

                # Data sent to dashboard
                weather = {
                    "city": data["name"],
                    "temperature": temperature,
                    "humidity": humidity,
                    "pressure": pressure,
                    "wind": wind,
                    "description": description,
                    "risk": risk
                }

            else:

                error = "City not found or API request failed."

        except requests.exceptions.RequestException:

            error = "Unable to connect to the weather service."


    return render_template(
        "index.html",
        weather=weather,
        error=error
    )


# ---------------- START SERVER ----------------

if __name__ == "__main__":
    app.run(debug=True)