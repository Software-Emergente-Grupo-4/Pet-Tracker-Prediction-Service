import pandas as pd
from datetime import datetime
from prophet import Prophet
from repository import health_measures_repository

def __from_list_to_df(results: list, column: str) -> pd.DataFrame:
    df = pd.DataFrame(results)
    selected_columns = ['fecha', column]
    df = df[selected_columns].rename(columns={'fecha': 'ds', column: 'y'})
    return df

def __caculate_days_to_predict(df: pd.DataFrame) -> tuple:
    current_date = datetime.today()
    last_day = df['ds'].max()

    first_day_from_next_month = (last_day + pd.DateOffset(months=1)).replace(day=1)
    remaining_days = (first_day_from_next_month - current_date).days + 1
    next_month_days = (first_day_from_next_month + pd.DateOffset(months=1) - pd.Timedelta(days=1)).day
    
    days_to_predict = remaining_days + next_month_days

    return days_to_predict, first_day_from_next_month

def make_future_health_measures(n_months: int, device_record_id: str) -> list:
    results = health_measures_repository.get_daily_averages_for_last_n_months(n_months, device_record_id)
    if len(results) < 30: return []
    df_bpm = __from_list_to_df(results, 'avg_bpm')
    df_spo2 = __from_list_to_df(results, 'avg_spo2')

    # Create a model for each health measure
    model_bpm = Prophet(daily_seasonality=True)
    model_bpm.fit(df_bpm)

    model_spo2 = Prophet(daily_seasonality=True)
    model_spo2.fit(df_spo2)
    
    # Calculate days to predict
    days_to_predict, first_day_from_next_month = __caculate_days_to_predict(df_bpm)

    # Generar fechas futuras
    future_bpm = model_bpm.make_future_dataframe(periods=days_to_predict, freq='D')
    forecast_bpm = model_bpm.predict(future_bpm)

    future_spo2 = model_spo2.make_future_dataframe(periods=days_to_predict, freq='D')
    forecast_spo2 = model_spo2.predict(future_spo2)

    # Filtrar solo las fechas del mes siguiente
    forecast_bpm_next_month = forecast_bpm[forecast_bpm['ds'].dt.month == first_day_from_next_month.month]
    forecast_spo2_next_month = forecast_spo2[forecast_spo2['ds'].dt.month == first_day_from_next_month.month]

    forecast_summary_next_month = pd.DataFrame({
        'date': forecast_bpm_next_month['ds'].dt.strftime('%Y-%m-%d'),
        'avgBpm': forecast_bpm_next_month['yhat'].round(2),
        'avgSpo2': forecast_spo2_next_month['yhat'].round(2),
    })

    forecast_summary_next_month_json_array = forecast_summary_next_month.to_dict(orient='records')

    return forecast_summary_next_month_json_array

if __name__ == "__main__":
    pass
    
