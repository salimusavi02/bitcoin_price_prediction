import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter
import mplfinance as mpf
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error

# فانکشن برای دریافت داده از اینترنت
def fetch_data(ticker='BTC-USD', start_date='2010-01-01', end_date='2025-03-06'):
    print(f"Fetching {ticker} data from {start_date} to {end_date}...")
    data = yf.download(ticker, start=start_date, end=end_date)
    data.index.name = 'Date'
    save_data_to_csv(data)
    return data

# فانکشن برای خوندن داده از فایل CSV
def load_data_from_csv(file_path='bitcoin_data.csv'):
    try:
        data = pd.read_csv(file_path, header=0, skiprows=[1, 2], index_col=0, parse_dates=True)
        data.index.name = 'Date'
        print("Data loaded from CSV successfully.")
        return data
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return None

# فانکشن برای ذخیره داده در CSV
def save_data_to_csv(data, file_path='bitcoin_data.csv'):
    data.to_csv(file_path)
    print(f"Data saved to {file_path}.")

# فانکشن برای رسم قیمت بسته شدن
def plot_close_price(data):
    plt.figure(figsize=(14, 7))
    plt.plot(data['Close'], label='Bitcoin Close Price')
    plt.title('Bitcoin Close Price (USD)')
    plt.xlabel('Date')
    plt.ylabel('Price (USD)')
    plt.legend()
    plt.gca().yaxis.set_major_formatter(ScalarFormatter(useOffset=False))
    plt.ticklabel_format(style='plain', axis='y')
    plt.show()

# فانکشن برای رسم حجم معاملات
def plot_volume(data):
    plt.figure(figsize=(14, 7))
    plt.plot(data['Volume'], label='Bitcoin Volume')
    plt.title('Bitcoin Volume Traded')
    plt.xlabel('Date')
    plt.ylabel('Volume')
    plt.legend()
    plt.show()

# فانکشن برای رسم میانگین متحرک
def plot_moving_averages(data):
    data['SMA_50'] = data['Close'].rolling(window=50).mean()
    data['SMA_200'] = data['Close'].rolling(window=200).mean()
    plt.figure(figsize=(14, 7))
    plt.plot(data['Close'], label='Bitcoin Close Price')
    plt.plot(data['SMA_50'], label='50-Day SMA')
    plt.plot(data['SMA_200'], label='200-Day SMA')
    plt.title('Bitcoin Price with Moving Averages')
    plt.xlabel('Date')
    plt.ylabel('Price (USD)')
    plt.legend()
    plt.show()

# فانکشن برای رسم نمودار شمعی
def plot_candlestick(data):
    required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
    if not all(col in data.columns for col in required_columns):
        raise ValueError(f"Data must contain: {required_columns}")
    mpf.plot(data, type='candle', style='charles', title='Bitcoin Candlestick Chart', 
             ylabel='Price (USD)', volume=True)

# فانکشن برای رسم هیستوگرام بازده روزانه
def plot_daily_returns(data):
    data['Daily Return'] = data['Close'].pct_change()
    plt.figure(figsize=(14, 7))
    data['Daily Return'].hist(bins=50)
    plt.title('Histogram of Daily Returns')
    plt.xlabel('Daily Return')
    plt.ylabel('Frequency')
    plt.show()


# فانکشن جدید برای آماده‌سازی داده و پیش‌بینی
def prepare_and_predict(data, lag_days=5):
    # آماده‌سازی داده
    data['Target'] = data['Close'].shift(-1)  # قیمت روز بعد به‌عنوان هدف
    for i in range(1, lag_days + 1):
        data[f'Close_Lag_{i}'] = data['Close'].shift(i)  # قیمت‌های قبلی به‌عنوان ویژگی
    
    # حذف ردیف‌های خالی
    data = data.dropna()
    
    # ویژگی‌ها و هدف
    X = data[[f'Close_Lag_{i}' for i in range(1, lag_days + 1)]]
    y = data['Target']
    
    # تقسیم داده به آموزشی و آزمایشی
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)
    
    # ساخت و آموزش مدل
    model = LinearRegression()
    model.fit(X_train, y_train)
    
    # پیش‌بینی
    predictions = model.predict(X_test)
    
    # ارزیابی
    mse = mean_squared_error(y_test, predictions)
    print(f"Mean Squared Error: {mse}")
    
    # رسم پیش‌بینی‌ها در مقابل داده واقعی
    plt.figure(figsize=(14, 7))
    plt.plot(y_test.index, y_test, label='Actual Price')
    plt.plot(y_test.index, predictions, label='Predicted Price')
    plt.title('Bitcoin Price Prediction')
    plt.xlabel('Date')
    plt.ylabel('Price (USD)')
    plt.legend()
    plt.show()


# اجرای اصلی
def main():
    # می‌تونی داده رو از اینترنت بگیری یا از فایل بخونی
    # data = fetch_data()  # برای دریافت از اینترنت
    data = load_data_from_csv()  # برای خوندن از فایل

    if data is None:
        return  # اگه داده بارگذاری نشد، برنامه رو متوقف کن

    # نمایش ۵ ردیف اول
    print(data.head())

    # رسم نمودارها
    plot_close_price(data)
    plot_volume(data)
    plot_moving_averages(data)
    # plot_candlestick(data)
    plot_daily_returns(data)

    # پیش‌بینی قیمت
    prepare_and_predict(data)

    # ذخیره داده (اختیاری)
    # save_data_to_csv(data)

if __name__ == "__main__":
    main()