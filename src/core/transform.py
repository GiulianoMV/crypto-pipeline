import polars as pl
from typing import Optional

from src.logger import get_logger


logger = get_logger(__name__)


# ======================
# MÉDIAS MÓVEIS
# ======================

def add_sma(df:pl.DataFrame, period:int=20) -> pl.DataFrame:
    '''
        Adiciona coluna de SMA (média móvel simples).
    '''
    return df.with_columns(
        pl.col("close").rolling_mean(window_size=period).alias(f"sma_{period}")
    )



def add_ema(df:pl.DataFrame, period:int=12) -> pl.DataFrame:
    '''
        Adiciona coluna de EMA (média móvel exponencial).
    '''
    return df.with_columns(
        pl.col("close").ewm_mean(span=period).alias(f"ema_{period}")
    )


# ======================
# RSI (Relative Strength Index)
# ======================

def add_rsi(df:pl.DataFrame, period:int=14) -> pl.DataFrame:
    '''
        Adiciona coluna de RSI (Índice de Força Relativa).
    '''
    delta = pl.col("close").diff()
    gain = pl.when(delta > 0).then(delta).otherwise(0)
    loss = pl.when(delta < 0).then(-delta).otherwise(0)
    
    avg_gain = gain.rolling_mean(window_size=period)
    avg_loss = loss.rolling_mean(window_size=period)
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    return df.with_columns(rsi.alias(f"rsi_{period}"))


# ======================
# MACD (Moving Average Convergence Divergence)
# ======================

def add_macd(df:pl.DataFrame,
             short_period:int=12,
             long_period:int=26,
             signal_period:int= 9) -> pl.DataFrame:
    '''
        Adiciona colunas de MACD, sinal e histograma.
    '''
    # Calcular as EMAs
    df = df.with_columns([
        pl.col("close").ewm_mean(span=short_period).alias(f"ema_{short_period}"),
        pl.col("close").ewm_mean(span=long_period).alias(f"ema_{long_period}")
    ])
    
    # Calcular MACD
    macd_col = f"macd_{short_period}_{long_period}"
    df = df.with_columns(
        (pl.col(f"ema_{short_period}") - pl.col(f"ema_{long_period}")).alias(macd_col)
    )
    
    # Calcular linha de sinal (EMA do MACD)
    signal_col = f"macd_signal_{signal_period}"
    df = df.with_columns(
        pl.col(macd_col).ewm_mean(span=signal_period).alias(signal_col)
    )
    
    # Calcular histograma
    return df.with_columns(
        (pl.col(macd_col) - pl.col(signal_col)).alias("macd_histogram")
    )


# ======================
# Bollinger Bands
# ======================

def add_bollinger_bands(df:pl.DataFrame, period:int=20, std_dev:float=2.0) -> pl.DataFrame:
    '''
        Adiciona colunas de Bollinger Bands.
    '''
    rolling_mean = pl.col("close").rolling_mean(window_size=period)
    rolling_std = pl.col("close").rolling_std(window_size=period)
    
    return df.with_columns([
        rolling_mean.alias(f"bb_middle_{period}"),
        (rolling_mean + (rolling_std * std_dev)).alias(f"bb_upper_{period}"),
        (rolling_mean - (rolling_std * std_dev)).alias(f"bb_lower_{period}"),
        rolling_std.alias(f"bb_std_{period}")
    ])


# ======================
# ATR (Average True Range)
# ======================

def add_atr(df:pl.DataFrame, period:int=14) -> pl.DataFrame:
    '''
        Adiciona coluna de ATR (faixa média verdadeira).
    '''
    high = pl.col("high")
    low = pl.col("low")
    close = pl.col("close")
    
    tr1 = high - low
    tr2 = (high - close.shift(1)).abs()
    tr3 = (low - close.shift(1)).abs()
    
    true_range = pl.max_horizontal(tr1, tr2, tr3)
    
    return df.with_columns(
        true_range.rolling_mean(window_size=period).alias(f"atr_{period}")
    )


# ======================
# VWAP (Volume Weighted Average Price)
# ======================

def add_vwap(df:pl.DataFrame) -> pl.DataFrame:
    '''
        Adiciona coluna de VWAP (preço médio ponderado pelo volume).
    '''
    typical_price = (pl.col("high") + pl.col("low") + pl.col("close")) / 3
    cumulative_vp = (typical_price * pl.col("volume")).cum_sum()
    cumulative_vol = pl.col("volume").cum_sum()
    
    return df.with_columns(
        (cumulative_vp / cumulative_vol).alias("vwap")
    )


# ======================
# FUNÇÃO PRINCIPAL
# ======================

def add_all_indicators(df:pl.DataFrame, 
                      sma_periods:list=[20, 50],
                      ema_periods:list=[12, 26],
                      rsi_period:int=14,
                      macd_short:int=12,
                      macd_long:int=26,
                      macd_signal:int=9,
                      bb_period:int=20,
                      bb_std:float=2.0,
                      atr_period:int=14) -> pl.DataFrame:
    '''
        Adiciona todos os indicadores técnicos ao DataFrame.
        
        Parameters
        ----------
        df: pl.DataFrame
            DataFrame com colunas: date, symbol, open, high, low, close, volume
            
        sma_periods: list
            Lista de períodos para SMA
            
        ema_periods: list
            Lista de períodos para EMA
            
        rsi_period: int
            Período para RSI
            
        macd_short: int
            Período curto para MACD
            
        macd_long: int
            Período longo para MACD
            
        macd_signal: int
            Período para linha de sinal do MACD
            
        bb_period: int
            Período para Bollinger Bands
            
        bb_std: float
            Desvio padrão para Bollinger Bands
            
        atr_period: int
            Período para ATR
    '''
    
    result_df = df.clone()
    
    # Adicionar SMAs
    for period in sma_periods:
        result_df = add_sma(result_df, period)
    
    # Adicionar EMAs
    for period in ema_periods:
        result_df = add_ema(result_df, period)
    
    # Adicionar RSI
    result_df = add_rsi(result_df, rsi_period)
    
    # Adicionar MACD
    result_df = add_macd(result_df, macd_short, macd_long, macd_signal)
    
    # Adicionar Bollinger Bands
    result_df = add_bollinger_bands(result_df, bb_period, bb_std)
    
    # Adicionar ATR
    result_df = add_atr(result_df, atr_period)
    
    # Adicionar VWAP
    result_df = add_vwap(result_df)
    
    return result_df