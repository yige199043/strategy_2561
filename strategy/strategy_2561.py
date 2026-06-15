import pandas as pd
import numpy as np


class BaseStrategy:
    def __init__(self, name, params):
        self.name = name
        self.params = params

    def _validate_stock_name(self, stock_name):
        return True


class Strategy2560Selection(BaseStrategy):
    """
    2560战法：
    1. 收盘价上穿25日均线
    2. 5日均量线上穿60日均量线
    """

    def __init__(self, params=None):
        default_params = {
            "ma_period": 25,
            "vol_ma_short": 5,
            "vol_ma_long": 60,
            "min_price_change": 0.03,
            "min_volume_ratio": 1.2,
            "strategy_weight": 70,
        }
        if params:
            default_params.update(params)

        super().__init__("2560战法", default_params)

    def calculate_indicators(self, df):
        df = df.copy()

        df["ma25"] = df["close"].rolling(25).mean()
        df["ma10"] = df["close"].rolling(10).mean()

        df["vol_ma5"] = df["volume"].rolling(5).mean()
        df["vol_ma60"] = df["volume"].rolling(60).mean()

        return df

    def select_stocks(self, df, stock_name=""):
        if len(df) < 60:
            return []

        df = self.calculate_indicators(df)

        latest = df.iloc[-1]
        prev = df.iloc[-2]

        # 1. 价格突破MA25
        price_break = latest["close"] > latest["ma25"] and prev["close"] <= prev["ma25"]

        # 2. 量能金叉
        vol_cross = latest["vol_ma5"] > latest["vol_ma60"] and prev["vol_ma5"] <= prev["vol_ma60"]

        # 3. MA10过滤
        ma_filter = latest["close"] > latest["ma10"]

        # 4. 涨幅
        price_change = (latest["close"] - prev["close"]) / prev["close"]

        # 5. 放量
        volume_ratio = latest["volume"] / latest["vol_ma5"] if latest["vol_ma5"] > 0 else 0

        if not (price_break and vol_cross and ma_filter):
            return []

        if price_change < self.params["min_price_change"]:
            return []

        if volume_ratio < self.params["min_volume_ratio"]:
            return []

        return [{
            "stock": stock_name,
            "close": round(latest["close"], 2),
            "price_change": round(price_change * 100, 2),
            "volume_ratio": round(volume_ratio, 2),
        }]


# ====== 关键：这个必须要有（否则GitHub只会“运行成功但没输出”）======

if __name__ == "__main__":
    print("2560战法启动")

    # ⚠️ 这里必须替换成你的真实数据加载
    df = pd.DataFrame({
        "close": np.random.rand(100) * 10 + 10,
        "volume": np.random.rand(100) * 1000 + 500
    })

    strat = Strategy2560Selection()

    result = strat.select_stocks(df, "测试股票")

    print("====选股结果====")
    print(result)
