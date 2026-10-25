import requests
import time

# تنظیمات تحلیل
COINS = {
    "bitcoin": "BTC",
    "ethereum": "ETH"
}

API_URL = "https://api.coingecko.com/api/v3/coins/{}/market_chart"

def get_prices(coin):
    try:
        url = API_URL.format(coin)
        params = {"vs_currency": "usd", "days": "1", "interval": "hourly"}
        response = requests.get(url, params=params, timeout=20)
        response.raise_for_status()
        data = response.json()
        return [item[1] for item in data["prices"]]
    except Exception as e:
        print(f"خطا در دریافت قیمت {coin}: {e}")
        return None

def analyze(prices):
    if not prices or len(prices) < 15:
        return None

    current = prices[-1]
    rsi_prices = prices[-15:]
    gains = []
    losses = []

    for i in range(1, len(rsi_prices)):
        change = rsi_prices[i] - rsi_prices[i-1]
        gains.append(max(change, 0))
        losses.append(max(-change, 0))

    avg_gain = sum(gains) / len(gains)
    avg_loss = sum(losses) / len(losses)

    if avg_loss == 0:
        rsi = 100 if avg_gain > 0 else 50
    else:
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))

    if rsi < 30:
        signal = "احتمال خرید"
    elif rsi > 70:
        signal = "احتمال فروش"
    else:
        signal = "بدون سیگنال"

    return current, rsi, signal

def main():
    print("ربات تحلیل بازار شروع شد.")

    while True:
        for coin, symbol in COINS.items():
            prices = get_prices(coin)

            if prices:
                result = analyze(prices)

                if result:
                    price, rsi, signal = result
                    print(
                        f"{symbol} | قیمت: ${price:.2f} | "
                        f"RSI: {rsi:.1f} | {signal}"
                    )

        print("بررسی بعدی 15 دقیقه دیگر.")
        time.sleep(900)

if __name__ == "__main__":
    main()
