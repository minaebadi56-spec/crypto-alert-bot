import os
import requests

TELEGRAM_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

COINS = {
    "bitcoin": "Bitcoin (BTC)",
    "ethereum": "Ethereum (ETH)"
}

def send_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    response = requests.post(
        url,
        data={"chat_id": CHAT_ID, "text": text},
        timeout=20
    )
    response.raise_for_status()

def get_prices(coin):
    url = f"https://api.coingecko.com/api/v3/coins/{coin}/market_chart"
    response = requests.get(
        url,
        params={"vs_currency": "usd", "days": "1", "interval": "hourly"},
        timeout=20
    )
    response.raise_for_status()
    return [item[1] for item in response.json()["prices"]]

def analyze(prices):
    if len(prices) < 15:
        return None

    changes = [
        prices[i] - prices[i - 1]
        for i in range(len(prices) - 14, len(prices))
    ]

    gains = [max(change, 0) for change in changes]
    losses = [max(-change, 0) for change in changes]

    avg_gain = sum(gains) / 14
    avg_loss = sum(losses) / 14

    if avg_loss == 0:
        rsi = 100 if avg_gain > 0 else 50
    else:
        rsi = 100 - (100 / (1 + avg_gain / avg_loss))

    return rsi

def main():
    messages = ["📊 گزارش تحلیل بازار ارز دیجیتال"]

    for coin, name in COINS.items():
        try:
            prices = get_prices(coin)
            rsi = analyze(prices)

            if rsi is None:
                continue

            price = prices[-1]

            if rsi < 30:
                signal = "🟢 احتمال اشباع فروش؛ بررسی فرصت خرید"
            elif rsi > 70:
                signal = "🔴 احتمال اشباع خرید؛ بررسی احتمال اصلاح"
            else:
                signal = "⚪ فعلاً سیگنال RSI صادر نشده"

            messages.append(
                f"\n{name}\n"
                f"قیمت: ${price:,.2f}\n"
                f"RSI: {rsi:.1f}\n"
                f"{signal}"
            )

        except Exception as error:
            messages.append(f"\nخطا در بررسی {name}: {error}")

    send_message("\n".join(messages))

if __name__ == "__main__":
    main()
