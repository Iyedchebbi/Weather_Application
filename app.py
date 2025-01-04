import requests
import tkinter as tk
from tkinter import messagebox
import mysql.connector


API_KEY = "43bc8097abed4d9684c175137240512 "  
BASE_URL = "http://api.weatherapi.com/v1/current.json"

# Configuration de la base de données MySQL
def connect_db():
    """Se connecter à la base de données MySQL"""
    try:
        conn = mysql.connector.connect(
            host="localhost",  # Adresse de l'hôte
            user="root",  # Nom d'utilisateur
            password="IYED1920@CHEBBI#",  # Mot de passe pour 'root'
            database="testdb"  # Nom de la base de données
        )
        return conn
    except mysql.connector.Error as err:
        messagebox.showerror("Erreur", f"Erreur de connexion à la base de données: {err}")
        return None

def insert_weather_data(city_name, temp, description, humidity, wind_speed):
    """Insérer les données météo dans la base de données"""
    conn = connect_db()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO weather (city_name, temperature, description, humidity, wind_speed)
                VALUES (%s, %s, %s, %s, %s)
            """, (city_name, temp, description, humidity, wind_speed))
            conn.commit()
            cursor.close()
            conn.close()
        except mysql.connector.Error as err:
            messagebox.showerror("Erreur", f"Erreur d'insertion dans la base de données: {err}")

def get_weather(city):
    """Récupérer les prévisions météo pour une ville donnée"""
    try:
        params = {
            "key": API_KEY,
            "q": city,
            "lang": "fr"
        }
        
        response = requests.get(BASE_URL, params=params)
        
        if response.status_code == 200:
            return response.json()
        else:
            messagebox.showerror("Erreur", f"Erreur : {response.status_code}")
            return None
    except Exception as e:
        messagebox.showerror("Erreur", f"Une erreur s'est produite : {e}")
        return None


def get_forecast(city):
    """Récupérer les prévisions météo pour les prochains jours d'une ville donnée"""
    try:
        params = {
            "key": API_KEY,
            "q": city,
            "days": 7,  # Demander les prévisions pour les 7 prochains jours
            "lang": "fr"
        }
        
        forecast_url = "http://api.weatherapi.com/v1/forecast.json"
        response = requests.get(forecast_url, params=params)
        
        if response.status_code == 200:
            return response.json()
        else:
            messagebox.showerror("Erreur", f"Erreur : {response.status_code}")
            return None
    except Exception as e:
        messagebox.showerror("Erreur", f"Une erreur s'est produite : {e}")
        return None

def display_weather():
    """Afficher les données météo dans la fenêtre Tkinter et insérer dans MySQL"""
    city = city_entry.get()
    if not city:
        messagebox.showwarning("Attention", "Veuillez entrer le nom d'une ville.")
        return
    
    data = get_weather(city)
    print(data)

    if data:
        city_name = data ['location']['name']
        temp = data['current']['temp_c']
        weather = data['current']['condition']['text']
        humidity = data['current']['humidity']
        wind_speed = data['current']['wind_kph']
        
        # Insérer les données dans MySQL
        insert_weather_data(city_name, temp, weather, humidity, wind_speed)
        
        # Afficher les résultats dans Tkinter
        result_label.config(text=f"Météo à {city_name}:\n"
                                 f"Température : {temp}°C\n"
                                 f"Description : {weather}\n"
                                 f"Humidité : {humidity}%\n"
                                 f"Vitesse du vent : {wind_speed} m/s")
    else:
        result_label.config(text="Impossible de récupérer les données météo.")


def display_forecast():
    """Afficher les prévisions météorologiques sur plusieurs jours"""
    city = city_entry.get()
    if not city:
        messagebox.showwarning("Attention", "Veuillez entrer le nom d'une ville.")
        return
    
    forecast_data = get_forecast(city)
    if forecast_data:
        city_name = forecast_data['location']['name']
        forecast_text = f"Prévisions pour {city_name}\n"
        
        for day in forecast_data['forecast']['forecastday']:
            date = day['date']
            temp_max = day['day']['maxtemp_c']
            temp_min = day['day']['mintemp_c']
            condition = day['day']['condition']['text']
            forecast_text += f"{date} : Max: {temp_max}°C, Min: {temp_min}°C, Condition: {condition}\n"
        
        # Afficher les prévisions dans Tkinter
        result_label.config(text=forecast_text)
    else:
        result_label.config(text="Impossible de récupérer les prévisions météo.")

# Création de la fenêtre principale Tkinter
root = tk.Tk()
root.title("Application Météo avec MySQL")
root.geometry("600x480")

# Widgets
city_label = tk.Label(root, text="Entrez le nom d'une ville :", font=("Arial", 12))
city_label.pack(pady=10)

city_entry = tk.Entry(root, font=("Arial", 14), width=20)
city_entry.pack(pady=5)

search_button = tk.Button(root, text="Rechercher", font=("Arial", 12), command=display_weather)
search_button.pack(pady=5)

forecast_button = tk.Button(root, text="Voir les prévisions", font=("Arial", 12), command=display_forecast)
forecast_button.pack(pady=2)


result_label = tk.Label(root, text="", font=("Arial", 12), justify="left", wraplength=350)
result_label.pack(pady=2)

# Lancer la boucle Tkinter
root.mainloop()
