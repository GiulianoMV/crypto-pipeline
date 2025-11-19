import polars as pl
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Optional, List, Dict

from src.logger import get_logger


logger = get_logger(__name__)


class FinancialChart:
    def __init__(self, df: pl.DataFrame, config: Dict = None):
        '''
        Inicializa o gerador de gráficos financeiros

        Parameters
        ----------
        df: Dataframe com dados e indicadores
        config: Configurações de visualização
        '''
        self.df = df
        self.config = config or {}
        self.symbol = df['symbol'][0] if 'symbol' in df.columns else 'UNKNOWN'
        self.theme = self.config.get('theme', 'light')
        self.validate_data()
        self._setup_theme_colors()
        
    def set_theme(self, theme: str):
        '''
        Altera o tema dinamicamente
        '''
        self.theme = theme
        self._setup_theme_colors()

    def validate_data(self):
        '''
        Valida colunas necessárias
        '''
        required = ['date', 'open', 'high', 'low', 'close', 'volume']
        missing = [col for col in required if col not in self.df.columns]

        if missing:
            raise ValueError(f'Colunas obrigatórias faltando: {missing}')

    def _setup_theme_colors(self):
        '''
        Configura esquema de cores baseado no tema
        '''
        if self.theme == 'dark':
            self.colors = {
                'background': '#1e1e1e',
                'text': '#ffffff',
                'grid': '#2d2d2d',
                'candle_increase': '#26a69a',
                'candle_decrease': '#ef5350',
                'sma_20': '#ff6b00',
                'sma_50': '#e63946',
                'ema_12': '#2979ff',
                'ema_26': '#7b2cbf',
                'bollinger': '#90a4ae',
                'bollinger_fill': 'rgba(144, 164, 174, 0.2)',
                'vwap': '#00e5ff',
                'rsi': '#ba68c8',
                'rsi_overbought': '#ff5252',
                'rsi_oversold': '#69f0ae',
                'rsi_fill': 'rgba(255, 82, 82, 0.1)',
                'macd_line': '#2962ff',
                'macd_signal': '#ff6d00',
                'macd_positive': '#00c853',
                'macd_negative': '#ff1744',
                'volume_increase': '#26a69a',
                'volume_decrease': '#ef5350',
            }
        else:
            self.colors = {
                'background': '#ffffff',
                'text': '#000000',
                'grid': '#e0e0e0',
                'candle_increase': '#2e7d32',
                'candle_decrease': '#c62828',
                'sma_20': '#ff9800',
                'sma_50': '#d32f2f',
                'ema_12': '#1976d2',
                'ema_26': '#7b1fa2',
                'bollinger': '#546e7a',
                'bollinger_fill': 'rgba(84, 110, 122, 0.1)',
                'vwap': '#0097a7',
                'rsi': '#8e24aa',
                'rsi_overbought': '#d32f2f',
                'rsi_oversold': '#388e3c',
                'rsi_fill': 'rgba(211, 47, 47, 0.1)',
                'macd_line': '#1565c0',
                'macd_signal': '#ef6c00',
                'macd_positive': '#2e7d32',
                'macd_negative': '#c62828',
                'volume_increase': '#2e7d32',
                'volume_decrease': '#c62828',
            }

    def create_comprehensive_chart(self, height: int = 1200) -> go.Figure:
        '''
        Geração gráfica com todos os indicadores.
        '''
        fig = make_subplots(
            rows=4, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.05,
            subplot_titles=(
                f'Price & Indicators - {self.symbol}',
                'RSI',
                'MACD',
                'Volume'
            ),
            row_heights=[0.5, 0.15, 0.15, 0.2],
            specs=[
                [{'secondary_y': False}],
                [{'secondary_y': False}],
                [{'secondary_y': False}],
                [{'secondary_y': False}]
            ]
        )

        self._add_price_indicators(fig, row=1)
        self._add_rsi(fig, row=2)
        self._add_macd(fig, row=3)
        self._add_volume(fig, row=4)
        
        # Aplicar layout do tema
        fig.update_layout(
            height=height,
            title_text=f'Análise Técnica Completa - {self.symbol}',
            showlegend=True,
            xaxis_rangeslider_visible=False,
            plot_bgcolor=self.colors['background'],
            paper_bgcolor=self.colors['background'],
            font_color=self.colors['text'],
            legend=dict(
                bgcolor=self.colors['background'],
                font=dict(color=self.colors['text'])
            )
        )

        # Aplicar tema aos eixos
        fig.update_xaxes(
            gridcolor=self.colors['grid'],
            linecolor=self.colors['grid'],
            tickfont=dict(color=self.colors['text'])
        )
        fig.update_yaxes(
            gridcolor=self.colors['grid'],
            linecolor=self.colors['grid'],
            tickfont=dict(color=self.colors['text'])
        )

        return fig

    def _add_price_indicators(self, figure: go.Figure, row: int):
        '''
        Adiciona preço e indicadores de tendência.
        '''
        dates = self.df['date'].to_list()
        opens = self.df['open'].to_list()
        highs = self.df['high'].to_list()
        lows = self.df['low'].to_list()
        closes = self.df['close'].to_list()

        # Candlestick com cores temáticas
        figure.add_trace(
            go.Candlestick(
                x=dates,
                open=opens,
                high=highs,
                low=lows,
                close=closes,
                name='Price',
                showlegend=False,
                increasing_line_color=self.colors['candle_increase'],
                decreasing_line_color=self.colors['candle_decrease']
            ),
            row=row, col=1
        )

        if 'sma_20' in self.df.columns:
            figure.add_trace(
                go.Scatter(
                    x=dates,
                    y=self.df['sma_20'].to_list(),
                    line=dict(color=self.colors['sma_20'], width=1.5),
                    name='SMA 20'
                ),
                row=row, col=1
            )

        if 'sma_50' in self.df.columns:
            figure.add_trace(
                go.Scatter(
                    x=dates,
                    y=self.df['sma_50'].to_list(),
                    line=dict(color=self.colors['sma_50'], width=1.5),
                    name='SMA 50'
                ),
                row=row, col=1
            )

        if 'ema_12' in self.df.columns:
            figure.add_trace(
                go.Scatter(
                    x=dates,
                    y=self.df['ema_12'].to_list(),
                    line=dict(color=self.colors['ema_12'], width=1.5),
                    name='EMA 12'
                ),
                row=row, col=1
            )
        
        if 'ema_26' in self.df.columns:
            figure.add_trace(
                go.Scatter(
                    x=dates,
                    y=self.df['ema_26'].to_list(),
                    line=dict(color=self.colors['ema_26'], width=1.5),
                    name='EMA 26'
                ),
                row=row, col=1
            )

        if all(col in self.df.columns for col in ['bb_upper_20', 'bb_middle_20', 'bb_lower_20']):
            bb_upper = self.df['bb_upper_20'].to_list()
            bb_middle = self.df['bb_middle_20'].to_list()
            bb_lower = self.df['bb_lower_20'].to_list()

            figure.add_trace(
                go.Scatter(
                    x=dates,
                    y=bb_upper,
                    line=dict(color=self.colors['bollinger'], width=1, dash='dash'),
                    name='BB Upper',
                    showlegend=False
                ),
                row=row, col=1
            )

            figure.add_trace(
                go.Scatter(
                    x=dates,
                    y=bb_middle,
                    line=dict(color=self.colors['bollinger'], width=1),
                    name='BB Middle',
                    showlegend=False
                ),
                row=row, col=1
            )

            figure.add_trace(
                go.Scatter(
                    x=dates,
                    y=bb_lower,
                    line=dict(color=self.colors['bollinger'], width=1, dash='dash'),
                    name='BB Lower',
                    showlegend=True,
                    legendgroup='bollinger'
                ),
                row=row, col=1
            )

            figure.add_trace(
                go.Scatter(
                    x=dates + dates[::-1],
                    y=bb_upper + bb_lower[::-1],
                    fill='toself',
                    fillcolor=self.colors['bollinger_fill'],
                    line=dict(color='rgba(255,255,255,0)'),
                    name='Bollinger Bands',
                    showlegend=True
                ),
                row=row, col=1
            )

        if 'vwap' in self.df.columns:
            figure.add_trace(
                go.Scatter(
                    x=dates,
                    y=self.df['vwap'].to_list(),
                    line=dict(color=self.colors['vwap'], width=2),
                    name='VWAP'
                ),
                row=row, col=1
            )

    def _add_rsi(self, figure: go.Figure, row: int):
        '''
        Adiciona indicador RSI
        '''
        if 'rsi_14' in self.df.columns:
            dates = self.df['date'].to_list()
            rsi_values = self.df['rsi_14'].to_list()

            figure.add_trace(
                go.Scatter(
                    x=dates,
                    y=rsi_values,
                    line=dict(color=self.colors['rsi'], width=1.5),
                    name='RSI 14'
                ),
                row=row, col=1
            )

            figure.add_hline(
                y=70,
                line_dash='dash',
                line_color=self.colors['rsi_overbought'],
                row=row,
                col=1
            )
            figure.add_hline(
                y=30,
                line_dash='dash',
                line_color=self.colors['rsi_oversold'],
                row=row,
                col=1
            )

            figure.add_trace(
                go.Scatter(
                    x=dates,
                    y=[70] * len(dates),
                    fill=None,
                    line=dict(color='rgba(255,255,255,0)'),
                    showlegend=False
                ),
                row=row, col=1
            )

            figure.add_trace(
                go.Scatter(
                    x=dates,
                    y=[30] * len(dates),
                    fill='tonexty',
                    fillcolor=self.colors['rsi_fill'],
                    line=dict(color='rgba(255,255,255,0)'),
                    name='Zona de Sobrecompra',
                    showlegend=True
                ),
                row=row, col=1
            )

    def _add_macd(self, figure: go.Figure, row: int):
        '''
        Adiciona indicador MACD
        '''
        if all(col in self.df.columns for col in ['macd_12_26', 'macd_signal_9']):
            dates = self.df['date'].to_list()
            macd_line = self.df['macd_12_26'].to_list()
            macd_signal = self.df['macd_signal_9'].to_list()

            figure.add_trace(
                go.Scatter(
                    x=dates,
                    y=macd_line,
                    line=dict(color=self.colors['macd_line'], width=1.5),
                    name='MACD'
                ),
                row=row, col=1
            )

            figure.add_trace(
                go.Scatter(
                    x=dates,
                    y=macd_signal,
                    line=dict(color=self.colors['macd_signal'], width=1.5),
                    name='MACD Signal'
                ),
                row=row, col=1
            )

            if 'macd_histogram' in self.df.columns:
                macd_histogram = self.df['macd_histogram'].to_list()
                colors = [
                    self.colors['macd_positive'] if x >= 0 
                    else self.colors['macd_negative'] 
                    for x in macd_histogram
                ]

                figure.add_trace(
                    go.Bar(
                        x=dates,
                        y=macd_histogram,
                        marker_color=colors,
                        name='MACD Hist',
                        opacity=0.6
                    ),
                    row=row, col=1
                )
            
            figure.add_hline(
                y=0,
                line_color=self.colors['text'],
                line_width=1,
                row=row,
                col=1
            )
    
    def _add_volume(self, figure: go.Figure, row: int):
        '''
        Adiciona volume
        '''
        if 'volume' in self.df.columns:
            dates = self.df['date'].to_list()
            volumes = self.df['volume'].to_list()
            opens = self.df['open'].to_list()
            closes = self.df['close'].to_list()

            colors = [
                self.colors['volume_decrease'] if close < open 
                else self.colors['volume_increase'] 
                for open, close in zip(opens, closes)
            ]

            figure.add_trace(
                go.Bar(
                    x=dates,
                    y=volumes,
                    marker_color=colors,
                    name='Volume',
                    opacity=0.7
                ),
                row=row, col=1
            )

    def create_simple_price_chart(self) -> go.Figure:
        '''
        Cria gráfico simplificado apenas com elementos simples (OHLCV)
        '''
        dates = self.df['date'].to_list()
        opens = self.df['open'].to_list()
        highs = self.df['high'].to_list()
        lows = self.df['low'].to_list()
        closes = self.df['close'].to_list()
        volumes = self.df['volume'].to_list()

        figure = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.03,
            row_heights=[0.7, 0.3]
        )

        figure.add_trace(
            go.Candlestick(
                x=dates,
                open=opens,
                high=highs,
                low=lows,
                close=closes,
                name='Price',
                increasing_line_color=self.colors['candle_increase'],
                decreasing_line_color=self.colors['candle_decrease']
            ),
            row=1, col=1
        )

        volume_colors = [
            self.colors['volume_decrease'] if close < open 
            else self.colors['volume_increase'] 
            for open, close in zip(opens, closes)
        ]

        figure.add_trace(
            go.Bar(
                x=dates,
                y=volumes,
                marker_color=volume_colors,
                name='Volume'
            ),
            row=2, col=1
        )

        figure.update_layout(
            title_text=f'Price & Volume - {self.symbol}',
            xaxis_rangeslider_visible=False,
            plot_bgcolor=self.colors['background'],
            paper_bgcolor=self.colors['background'],
            font_color=self.colors['text']
        )

        figure.update_xaxes(
            gridcolor=self.colors['grid'],
            linecolor=self.colors['grid'],
            tickfont=dict(color=self.colors['text'])
        )
        figure.update_yaxes(
            gridcolor=self.colors['grid'],
            linecolor=self.colors['grid'],
            tickfont=dict(color=self.colors['text'])
        )

        return figure