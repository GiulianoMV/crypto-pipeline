import polars as pl

from src.logger import get_logger


logger = get_logger(__name__)


# ======================
# MÉDIAS MÓVEIS
# ======================

def add_sma(df:pl.DataFrame, period:int=20) -> pl.DataFrame:
    '''
        Adiciona coluna de SMA (média móvel simples).

        Parameters
        ----------
        df: pl.DataFrame
            DataFrame usado na adição da média móvel simples.

        period: int
            Período usado no cálculo da média móvel; Padrão de 20u.
    '''
    return df.with_columns(
        pl.col("close").rolling_mean(window_size=period).alias(f"sma_{period}")
    )


def add_ema(df:pl.DataFrame, period:int=12) -> pl.DataFrame:
    '''
        Adiciona coluna de EMA (média móvel exponencial).
    
        Parameters
        ----------
        df: pl.DataFrame
            DataFrame usado na adição da média móvel exponencial.

        period: int
            Período usado no cálculo da média móvel; Padrão de 12u.
    '''
    alpha = 2 / (period + 1)
    ema_col = f"ema_{period}"

    df = df.with_columns(pl.lit(None).alias(ema_col))

    # Cálculo iterativo
    closes = df["close"].to_list()
    ema_vals = [closes[0]]
    for price in closes[1:]:
        ema_vals.append((price * alpha) + (ema_vals[-1] * (1 - alpha)))

    return df.with_columns(pl.Series(ema_col, ema_vals))


# ======================
# RSI (Relative Strength Index)
# ======================

def add_rsi(df: pl.DataFrame, period: int = 14) -> pl.DataFrame:
    '''
        Adiciona coluna de RSI (Índice de Força Relativa).
    
        Parameters
        ----------
        df: pl.DataFrame
            DataFrame usado na adição do índice de força relativa.

        period: int
            Período usado no cálculo do rsi; Padrão de 14u.
    '''
    delta = df["close"].diff()
    gain = [max(x, 0) if x is not None else None for x in delta]
    loss = [abs(min(x, 0)) if x is not None else None for x in delta]

    gain_s = pl.Series("gain", gain)
    loss_s = pl.Series("loss", loss)

    avg_gain = gain_s.rolling_mean(window_size=period)
    avg_loss = loss_s.rolling_mean(window_size=period)

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    return df.with_columns(rsi.alias(f"rsi_{period}"))


# ======================
# MACD (Moving Average Convergence Divergence)
# ======================

def add_macd(df: pl.DataFrame,
             short_period: int = 12,
             long_period: int = 26,
             signal_period: int = 9) -> pl.DataFrame:
    '''
        Adiciona colunas de MACD, sinal e histograma.

        Parameters
        ----------
        df: pl.DataFrame
            DataFrame usado na adição do MACD.

        short_period: int
            Menor período usado na adição do MACD; Padrão de 12u.
        
        long_peiod: int
            Maior período usado na adição do MACD; Padrão de 26u.
        
        signal_period: int
            Período usado para adição de sinais; Padrão de 9u.
    '''
    df = add_ema(df, short_period)
    df = add_ema(df, long_period)

    macd_col = f"macd_{short_period}_{long_period}"
    df = df.with_columns(
        (pl.col(f"ema_{short_period}") - pl.col(f"ema_{long_period}")).alias(macd_col)
    )

    # Linha de sinal (EMA do MACD)
    macd_vals = df[macd_col].to_list()
    alpha = 2 / (signal_period + 1)
    signal_vals = [macd_vals[0]]
    for val in macd_vals[1:]:
        signal_vals.append((val * alpha) + (signal_vals[-1] * (1 - alpha)))

    df = df.with_columns([
        pl.Series(f"macd_signal_{signal_period}", signal_vals),
        (pl.col(macd_col) - pl.col(f"macd_signal_{signal_period}")).alias("macd_hist")
    ])
    return df


# ======================
# Bollinger Bands
# ======================

def add_bollinger_bands(df: pl.DataFrame, period: int = 20, std_dev: float = 2.0) -> pl.DataFrame:
    '''
        Adiciona colunas de Bollinger Bands (superior, média e inferior).

        Parameters
        ----------
        df: pl.DataFrame
            DataFrame usado na adição das bandas de Bollinger.
        
        period: int
            Período usado no cálculo; Padrão de 20u.
        
        std_dev: float
            Fator de desvio padrão para cálculo de largura do parâmetro; Padrão de 2.
    '''
    ma = df["close"].rolling_mean(window_size=period)
    std = df["close"].rolling_std(window_size=period)

    upper = ma + std_dev * std
    lower = ma - std_dev * std

    return df.with_columns([
        pl.Series(f"bb_mid_{period}", ma),
        pl.Series(f"bb_upper_{period}", upper),
        pl.Series(f"bb_lower_{period}", lower)
    ])


# ======================
# ATR (Average True Range)
# ======================

def add_atr(df: pl.DataFrame, period: int = 14) -> pl.DataFrame:
    '''
        Adiciona coluna de ATR (faixa média verdadeira).

        Parameters
        ----------
        df: pl.DataFrame
            Dataframe usado na adição da ATR.

        period: int
            Periodo usado no cálculo; Padrão de 14u.
    '''
    high = df["high"]
    low = df["low"]
    close = df["close"]

    prev_close = close.shift(1)
    tr = pl.max_horizontal(
        (high - low).abs(),
        (high - prev_close).abs(),
        (low - prev_close).abs()
    )

    atr = tr.rolling_mean(window_size=period)
    return df.with_columns(atr.alias(f"atr_{period}"))


# ======================
# VWAP (Volume Weighted Average Price)
# ======================

def add_vwap(df: pl.DataFrame) -> pl.DataFrame:
    '''
        Adiciona coluna de VWAP (preço médio ponderado pelo volume).

        Parameters
        ----------
        df: pl.DataFrame
            Dataframe usado na adição do VWAP.
    '''
    typical_price = (df["high"] + df["low"] + df["close"]) / 3
    cumulative_vp = (typical_price * df["volume"]).cumsum()
    cumulative_vol = df["volume"].cumsum()
    vwap = cumulative_vp / cumulative_vol

    return df.with_columns(vwap.alias("vwap"))