import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_percentage_error
import pickle

df = pd.read_csv("hour.csv")

# Selezionare le feature rilevanti per la previsione
relevant_features = ["season", "yr", "mnth", "hr", "holiday", "weekday", "workingday", "weathersit", "temp", "atemp", "hum"]

# Applicare la trasformazione StandardScaler alle feature selezionate
scaler = StandardScaler()
X = scaler.fit_transform(df[relevant_features].values)

# Separare la variabile dipendente dalla variabile predittiva
y = df["cnt"].values.reshape(-1, 1)

# Creare l'oggetto regressione lineare e addestrare il modello
regressor = LinearRegression()
regressor.fit(X, y)

# Salvare il modello addestrato con pickle
with open("regressor.pickle", "wb") as f:
    pickle.dump(regressor, f)

# Valutare l'accuratezza del modello con la metrica MAPE
y_pred = regressor.predict(X)
mape = mean_absolute_percentage_error(y, y_pred)
print(f"MAPE: {mape:.2f}")

# Prevedere il numero di biciclette ora per ora per le prossime 24 ore
last_hour = df.iloc[-1]["instant"]
for i in range(24):
    hour = last_hour + i + 1
    data = scaler.transform(df[relevant_features].tail(1).values)
    data[0][3] = hour % 24  # Trasformare l'ora in un valore compreso tra 0 e 23
    prediction = int(regressor.predict(data))
    print(f"Ora {i}: {prediction} biciclette")
