import requests
import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

# SQLite adatbázis létrehozása
engine = create_engine('sqlite:///bitcoin_prices.db')
Base = declarative_base()

class BitcoinPrice(Base):
    __tablename__ = 'bitcoin_prices'
    id = Column(Integer, primary_key=True)
    date = Column(String)
    price = Column(Float)

Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

def clear_database(session):
    """Törli az adatokat az adatbázisból."""
    session.query(BitcoinPrice).delete()
    session.commit()

# Adatbázis törlése futtatás előtt
clear_database(session)

def fetch_bitcoin_prices():
    #Bitcoin napi árfolyamainak lekérése a CoinGecko API-ból.
    url = 'https://api.coingecko.com/api/v3/coins/bitcoin/market_chart'
    params = {
        'vs_currency': 'usd',
        'days': '30',  # Lekérjük az utolsó 30 nap árfolyamadatait
        'interval': 'daily'
    }
    response = requests.get(url, params=params)
    data = response.json()

    prices = data['prices']
    df = pd.DataFrame(prices, columns=['timestamp', 'price'])
    df['date'] = pd.to_datetime(df['timestamp'], unit='ms')
    df['price'] = df['price'].astype(float)
    df.drop(columns=['timestamp'], inplace=True)
    return df

# Bitcoin árfolyamok lekérése és tárolása
df = fetch_bitcoin_prices()

for index, row in df.iterrows():
    price_entry = BitcoinPrice(date=row['date'].strftime('%Y-%m-%d'), price=row['price'])
    session.add(price_entry)

session.commit()

# Lekérdezés az adatbázisból
prices = session.query(BitcoinPrice).all()

# Lekérdezés eredményének átalakítása Pandas DataFrame-re
df = pd.DataFrame([(p.date, p.price) for p in prices], columns=['Date', 'Price'])

# Dátumok datetime formátumba konvertálása
df['Date'] = pd.to_datetime(df['Date'])

# Dátumok rendezése
df = df.sort_values('Date')

# Vizualizálás
plt.figure(figsize=(12, 6))
plt.plot(df['Date'], df['Price'], marker='o', linestyle='-', color='b')
plt.title('Bitcoin Napi Árfolyam')
plt.xlabel('Dátum')
plt.ylabel('Árfolyam (USD)')
plt.grid(True)
plt.show()
