import joblib
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler

# CSV einlesen
df = pd.read_csv('context_data.csv', header=None,
                 names=['timestamp', 'city', 'sunrise', 'sunset', 'azimuth', 'elevation', 'cloudiness', 'window', 'lux'])

# Zeit extrahieren
df['timestamp'] = pd.to_datetime(df['timestamp'])
df['hour'] = df['timestamp'].dt.hour
df['minute'] = df['timestamp'].dt.minute

# Features auswählen (ohne timestamp, city und lux als Ziel)
features = ['sunrise', 'sunset', 'azimuth', 'elevation', 'cloudiness', 'window', 'hour', 'minute']
X = df[features].values
y = df['lux'].values

#Nicht Zahlen prüfen und ersetzten
y = np.nan_to_num(y, nan=0.0) 

# Skalieren
scaler_X = MinMaxScaler()
X_scaled = scaler_X.fit_transform(X)

scaler_y = MinMaxScaler()
y_scaled = scaler_y.fit_transform(y.reshape(-1,1))

# Sequenzen erzeugen
def create_sequences(X, y, seq_length):
    X_seq, y_seq = [], []
    for i in range(len(X) - seq_length):
        X_seq.append(X[i:i+seq_length])
        y_seq.append(y[i+seq_length])
    return np.array(X_seq), np.array(y_seq)

X_seq, y_seq = create_sequences(X_scaled, y_scaled, seq_length=30)

np.save('X_seq.npy', X_seq)
np.save('y_seq.npy', y_seq)

joblib.dump(scaler_X, 'scaler_X.save')
joblib.dump(scaler_y, 'scaler_y.save')

######### Zum Debuggen###############################
print(f"Original data length: {len(X)}")
print(f"Number of sequences created: {len(X_seq)}")
print(f"Shape of X_seq: {X_seq.shape}")
print(f"Shape of y_seq: {y_seq.shape}")
###################################################