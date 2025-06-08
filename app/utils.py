from collections import defaultdict

def price_str_to_number(price_str: str) -> int:
    s = price_str.replace(",", "").strip()
    total = 0
    if "억" in s:
        eok, rest = s.split("억", 1)
        total += int(eok) * 100_000_000
        if rest.isdigit():
            total += int(rest) * 10_000
    elif s.isdigit():
        total += int(s) * 10_000
    return total


def compute_monthly_avg(price_history: dict) -> dict:
    """
    날짜별 시세 이력을 받아 월별 평균 하한가/상한가를 계산.
    예: {"2025-06-01": {"하한가": "4억2000", "상한가": "4억6000"}, ...}
    """
    monthly_data = defaultdict(lambda: {"하한가": [], "상한가": []})

    for date, values in price_history.items():
        month = date[:7]  # 예: '2025-06'

        low = price_str_to_number(values.get("하한가", "0"))
        high = price_str_to_number(values.get("상한가", "0"))

        if low > 0:
            monthly_data[month]["하한가"].append(low)
        if high > 0:
            monthly_data[month]["상한가"].append(high)

    monthly_avg = {}
    for month, prices in monthly_data.items():
        avg_low = round(sum(prices["하한가"]) / len(prices["하한가"])) if prices["하한가"] else 0
        avg_high = round(sum(prices["상한가"]) / len(prices["상한가"])) if prices["상한가"] else 0

        monthly_avg[month] = {
            "평균 하한가": avg_low,
            "평균 상한가": avg_high
        }
    print("📅 월별 평균 매매가:")
    print(monthly_avg)
    return monthly_avg


def convert_complex_info_keys(complex_info: dict) -> dict:
    key_map = {
        "세대수": "household_count",
        "저/최고층": "floor_info",
        "사용승인일": "approved_date",
        "총주차대수": "parking_count",
        "용적률": "floor_area_ratio",
        "건폐율": "building_coverage",
        "건설사": "constructor",
        "난방": "heating_type",
        "관리사무소": "management_office",
        "지번주소": "lot_address",
        "도로명주소": "street_address",
        "면적": "area_options",
    }
    return {key_map.get(k, k): v for k, v in complex_info.items()}


def convert_area_info_keys(area_info: dict) -> dict:
    key_map = {
        "면적": "area",
        "공급면적": "supply_area",
        "전용면적": "exclusive_area",
        "전용률": "exclusive_rate",
        "방 수": "room_count",
        "욕실 수": "bathroom_count",
        "해당면적 세대수": "household_count",
        "현관구조": "entrance_structure",
        "매매": "sale_count",
        "전세": "jeonse_count",
        "월세": "monthly_count",
        "단기": "short_term_count",
        "매매가": "sale_price",
        "전세가": "jeonse_price",
        "전세가율": "jeonse_ratio",
        "공시가격": "official_price",
        "보유세": "holding_tax",
    }

    result = {}
    for k, v in area_info.items():
        if k == "maintenance_cost" and isinstance(v, dict):
            result["maintenance_cost"] = v 
        else:
            result[key_map.get(k, k)] = v 

    return result


def convert_price_history_keys(price_history: dict) -> dict:
    key_map = {
        "기준일": "date",
        "하위평균가": "lower_avg_price",
        "일반평균가": "general_avg_price",
        "상위평균가": "upper_avg_price",
        "매매가 대비 전세가": "jeonse_to_sale_ratio",
        "매매가 대비 전세가": "jeonse_ratio",
        "보증금": "deposit",
        "월세": "monthly_rent",
    }
    converted = {}
    for date, values in price_history.items():
        converted[date] = {key_map.get(k, k): v for k, v in values.items()}
    return converted