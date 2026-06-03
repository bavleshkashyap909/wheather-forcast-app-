import sys
import requests
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from datetime import datetime

API_KEY = "9a3d2e5c3e03e8636aeff047cf303bfb"


class WeatherApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Modern Weather App")
        self.setFixedSize(450, 950)

        # Sky blue gradient background
        palette = QPalette()
        gradient = QLinearGradient(0, 0, 0, 650)
        gradient.setColorAt(0.0, QColor("#b5e8ff"))
        gradient.setColorAt(1.0, QColor("#a1d6ff"))
        palette.setBrush(QPalette.Window, gradient)
        self.setPalette(palette)

        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        # TOP EMOJI ICON
        self.top_icon = QLabel("☁️")
        self.top_icon.setAlignment(Qt.AlignCenter)
        self.top_icon.setStyleSheet("font-size: 70px;")
        layout.addWidget(self.top_icon)

        # SEARCH BAR
        search_layout = QHBoxLayout()

        self.city_input = QLineEdit()
        self.city_input.setPlaceholderText("City Name")
        self.city_input.setFixedHeight(45)
        self.city_input.setStyleSheet("""
            QLineEdit {
                border-radius: 20px;
                padding-left: 20px;
                background: white;
                font-size: 17px;
            }
        """)

        search_btn = QPushButton("🔍")
        search_btn.setFixedSize(45, 45)
        search_btn.setStyleSheet("font-size:22px; border:none;")
        search_btn.clicked.connect(self.get_weather)

        search_layout.addWidget(self.city_input)
        search_layout.addWidget(search_btn)
        layout.addLayout(search_layout)

        # MAIN CARD
        card = QFrame()
        card.setFixedSize(380, 300)
        card.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 #c4e0ff, stop:1 #98c9ff);
            border-radius: 25px;
        """)

        card_layout = QVBoxLayout()

        self.icon_label = QLabel("☀️")
        self.icon_label.setAlignment(Qt.AlignCenter)
        self.icon_label.setStyleSheet("font-size: 90px;")

        self.temp_label = QLabel("--°C")
        self.temp_label.setStyleSheet("font-size: 55px; font-weight: bold;")
        self.temp_label.setAlignment(Qt.AlignCenter)

        self.city_label = QLabel("")
        self.city_label.setStyleSheet("font-size: 28px;")
        self.city_label.setAlignment(Qt.AlignCenter)

        card_layout.addWidget(self.icon_label)
        card_layout.addWidget(self.temp_label)
        card_layout.addWidget(self.city_label)

        card.setLayout(card_layout)
        layout.addWidget(card)

        # DETAILS BOX
        self.details_label = QLabel("")
        self.details_label.setFixedSize(380, 180)
        self.details_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.details_label.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 #b7ddff, stop:1 #9ac8ff);
            border-radius: 25px;
            padding: 15px;
            font-size: 18px;
        """)
        layout.addWidget(self.details_label)

        # FORECAST TITLE
        self.forecast_title = QLabel("")
        self.forecast_title.setStyleSheet(
            "font-size: 20px; font-weight: bold; margin-top: 10px;"
        )
        self.forecast_title.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.forecast_title)

        # FORECAST LAYOUT
        self.forecast_layout = QHBoxLayout()
        self.forecast_layout.setSpacing(10)
        layout.addLayout(self.forecast_layout)

        self.setLayout(layout)

    def get_weather(self):
        city = self.city_input.text().strip()

        if not city:
            QMessageBox.warning(self, "Error", "Please enter a city name.")
            return

        try:
            url = (
                f"https://api.openweathermap.org/data/2.5/weather?"
                f"q={city}&appid={API_KEY}&units=metric"
            )

            data = requests.get(url, timeout=6).json()

            if data.get("cod") != 200:
                QMessageBox.warning(self, "Error", "City not found.")
                return

            temp = data["main"]["temp"]
            feels = data["main"].get("feels_like", temp)
            humidity = data["main"].get("humidity", "--")
            wind_spd = data["wind"].get("speed", "--")
            pressure = data["main"].get("pressure", "--")

            desc = data["weather"][0]["description"].title()
            weather_main = data["weather"][0]["main"].lower()

            # WEATHER EMOJIS
            if "cloud" in weather_main:
                weather_emoji = "☁️"
            elif "rain" in weather_main:
                weather_emoji = "🌧️"
            elif "storm" in weather_main or "thunder" in weather_main:
                weather_emoji = "⛈️"
            elif "sun" in weather_main or "clear" in weather_main:
                weather_emoji = "☀️"
            elif "fog" in weather_main or "haze" in weather_main:
                weather_emoji = "🌫️"
            elif "few" in weather_main:
                weather_emoji = "⛅"
            else:
                weather_emoji = "⛅"

            self.icon_label.setText(weather_emoji)

            # UPDATE TEXT
            self.temp_label.setText(f"{int(round(temp))}°C")
            self.city_label.setText(data.get("name", city).title())

            self.details_label.setText(
                f"""
                <b>{desc}</b><br><br>
                Feels Like: {feels}°C<br>
                Humidity: {humidity}%<br>
                Wind: {wind_spd} km/h<br>
                Pressure: {pressure} hPa<br>
                """
            )

            # FORECAST
            self.forecast_title.setText("5-Day Forecast")
            self.get_forecast(city)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Unexpected Error:\n{e}")

    def get_forecast(self, city):
        try:
            # CLEAR OLD FORECAST
            for i in reversed(range(self.forecast_layout.count())):
                widget = self.forecast_layout.itemAt(i).widget()

                if widget:
                    widget.setParent(None)

            url = (
                f"https://api.openweathermap.org/data/2.5/forecast?"
                f"q={city}&appid={API_KEY}&units=metric"
            )

            data = requests.get(url, timeout=6).json()

            if data.get("cod") != "200":
                return

            daily_forecasts = []
            seen_dates = set()

            for item in data['list']:
                date = datetime.fromtimestamp(item['dt']).date()

                if date not in seen_dates and len(daily_forecasts) < 5:
                    daily_forecasts.append(item)
                    seen_dates.add(date)

            for forecast in daily_forecasts:
                self.create_forecast_card(forecast)

        except Exception as e:
            print(f"Forecast error: {e}")

    def create_forecast_card(self, forecast):
        card = QFrame()
        card.setFixedSize(70, 110)

        card.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 #c4e0ff, stop:1 #98c9ff);
            border-radius: 15px;
        """)

        layout = QVBoxLayout()
        layout.setSpacing(2)
        layout.setContentsMargins(5, 5, 5, 5)

        # DATE
        date = datetime.fromtimestamp(
            forecast['dt']
        ).strftime('%a\n%d')

        date_label = QLabel(date)
        date_label.setAlignment(Qt.AlignCenter)
        date_label.setStyleSheet(
            "font-size: 11px; font-weight: bold;"
        )

        # WEATHER EMOJIS
        weather_main = forecast['weather'][0]['main'].lower()

        if "cloud" in weather_main:
            weather_emoji = "☁️"
        elif "rain" in weather_main:
            weather_emoji = "🌧️"
        elif "storm" in weather_main or "thunder" in weather_main:
            weather_emoji = "⛈️"
        elif "sun" in weather_main or "clear" in weather_main:
            weather_emoji = "☀️"
        elif "fog" in weather_main or "haze" in weather_main:
            weather_emoji = "🌫️"
        else:
            weather_emoji = "☁️"

        icon_label = QLabel(weather_emoji)
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet("font-size: 28px;")

        # TEMPERATURE
        temp = int(round(forecast['main']['temp']))

        temp_label = QLabel(f"{temp}°C")
        temp_label.setAlignment(Qt.AlignCenter)
        temp_label.setStyleSheet(
            "font-size: 13px; font-weight: bold;"
        )

        layout.addWidget(date_label)
        layout.addWidget(icon_label)
        layout.addWidget(temp_label)

        card.setLayout(layout)
        self.forecast_layout.addWidget(card)


# RUN APP
app = QApplication(sys.argv)

window = WeatherApp()
window.show()

sys.exit(app.exec_())