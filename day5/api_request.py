import requests
import sys
GEOCODING_BASE_URL="https://geocoding-api.open-meteo.com/v1/search"
FORECAST_BASE_URL="https://api.open-meteo.com/v1/forecast"
TIMEOUT_SECONDS=10
class APIRequest:
    @staticmethod
    def get(url,params=None,headers=None,timeout=TIMEOUT_SECONDS):
        try:
            response=requests.get(
                url,
                params=params,
                headers=headers,
                timeout=timeout
            )
            response.raise_for_status()
            try:
                return response.json()
            except ValueError:
                print("错误：接口返回的数据格式异常，无法解析为 JSON。")
                return None
        except requests.exceptions.Timeout:
            print(f"错误：请求超时({timeout}秒)，请检查网络或稍后重试。")
        except requests.exceptions.ConnectionError:
            print("错误：网络连接失败，请检查网络设置。")
        except requests.exceptions.HTTPError as e:
            print(f"错误：服务器返回错误状态码。")
        except Exception as e:
            print(f"未知网络错误：{e}")
        return None
def search_city(city_name):
    params={
        "name":city_name,
        "count":1,
        "language":"zh",
        "format":"json"
    }
    data=APIRequest.get(GEOCODING_BASE_URL,params=params)
    if data is None:
        return None
    results=data.get("results")
    if not results:
        print(f"未找到城市“{city_name}”，请检查名称并重试。")
        return None
    city=results[0]
    lat=city.get("latitude")
    lon=city.get("longitude")
    display_name=city.get("name") or city_name
    country=city.get("country","")
    return lat,lon,f"{display_name}({country})"
def get_current_weather(lat,lon):
    params={
        "latitude":lat,
        "longitude":lon,
        "current_weather":True
    }
    data=APIRequest.get(FORECAST_BASE_URL,params=params)
    if data is None:
        return None
    current=data.get("current_weather")
    if not current:
        print("错误：天气数据缺失，请稍后重试。")
        return None
    return current
def get_weather_description(code):
    weather_map={
        0: "晴天",
        1: "大部晴朗",
        2: "多云",
        3: "阴天",
        45: "雾",
        48: "沉积雾凇",
        51: "小毛毛雨",
        53: "中毛毛雨",
        55: "大毛毛雨",
        61: "小雨",
        63: "中雨",
        65: "大雨",
        71: "小雪",
        73: "中雪",
        75: "大雪",
        77: "雪粒",
        80: "阵雨",
        81: "中阵雨",
        82: "大阵雨",
        85: "小阵雪",
        86: "大阵雪",
        95: "雷暴",
        96: "小冰雹雷暴",
        99: "大冰雹雷暴"
    }
    return weather_map.get(code,f"未知(代码{code})")
def print_weather(city_full_name,weather):
    temperature=weather.get("temperature")
    wind_speed=weather.get("windspeed")
    weather_code=weather.get("weathercode")
    desc=get_weather_description(weather_code)
    print(f"\n城市：{city_full_name}")
    print(f"温度：{temperature}°C")
    print(f"风速：{wind_speed} km/h")
    print(f"天气：{desc}\n")
def main():
    print("="*30)
    print("天气查询工具(数据源：Open-Meteo)")
    print("="*30)
    while True:
        city=input("\n请输入城市名(输入0退出)：").strip()
        if city =='0':
            print("感谢使用，再见！")
            break
        if not city:
            print("城市名不能为空，请重新输入。")
            continue
        coords=search_city(city)
        if coords is None:
            continue
        lat,lon,city_full_name=coords
        weather=get_current_weather(lat, lon)
        if weather is None:
            continue
        print_weather(city_full_name,weather)
if __name__ =="__main__":
    main()