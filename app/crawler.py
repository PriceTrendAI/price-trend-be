#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import argparse
import datetime
import logging
import time
import random
from dataclasses import dataclass
from collections import defaultdict
from typing import List, Dict

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import datetime
from sqlalchemy.orm import Session
from app.models import ApartmentData 
from app.utils import compute_monthly_avg, run_forecast_from_avg


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class AreaInfo:
    area: str
    supply_area: str
    exclusive_area: str
    exclusive_rate: str
    room_count: str
    bathroom_count: str
    household_count: str
    entrance_structure: str
    price_count: Dict[str, str]
    price_info: Dict[str, str]
    maintenance_cost: Dict[str, str]
    official_price: str
    holding_tax: Dict[str, str]


class SearchPage:
    URL = "https://new.land.naver.com/search"
    INPUT = (By.ID, "land_search")
    ITEM_INNER = (By.CLASS_NAME, "item_inner")

    def __init__(self, driver: WebDriver, wait: WebDriverWait):
        self.driver = driver
        self.wait = wait

    def open(self) -> None:
        self.driver.get(self.URL)
        logger.info("검색 페이지 열기")

    def search(self, keyword: str) -> List[webdriver.remote.webelement.WebElement]:
        elem = self.wait.until(EC.presence_of_element_located(self.INPUT))
        elem.clear()
        elem.send_keys(keyword + "\n")
        logger.info("검색어 입력: %s", keyword)
        time.sleep(random.uniform(1.0, 1.5))
        return self.wait.until(EC.presence_of_all_elements_located(self.ITEM_INNER))


class DetailPage:
    COMPLEX_BUTTON = (By.XPATH, '//button[@class="complex_link" and text()="단지정보"]')
    INFO_TABLE = (By.CSS_SELECTOR, "table.info_table_wrap")
    AREA_TABS = (By.CSS_SELECTOR, ".detail_sorting_tablist a.detail_sorting_tab")
    SISE_TAB = (By.XPATH, '//a[@class="tab_item" and .//span[text()="시세/실거래가"]]')
    PRICE_AREA_TABS = (By.CSS_SELECTOR, "a.detail_sorting_tab")
    DEAL_TABS = (By.CSS_SELECTOR, ".detail_sorting_tabs--underbar .detail_sorting_tab")

    def __init__(self, driver: WebDriver, wait: WebDriverWait):
        self.driver = driver
        self.wait = wait

    def click_complex_info(self) -> None:
        btn = self.wait.until(EC.element_to_be_clickable(self.COMPLEX_BUTTON))
        btn.click()
        logger.info("단지정보 버튼 클릭")

    def get_complex_info(self) -> Dict[str, str]:
        table = self.wait.until(EC.presence_of_element_located(self.INFO_TABLE))
        rows = table.find_elements(By.TAG_NAME, "tr")
        info: Dict[str, str] = {}
        for row in rows:
            ths = row.find_elements(By.TAG_NAME, "th")
            tds = row.find_elements(By.TAG_NAME, "td")
            for th, td in zip(ths, tds):
                key = th.text.strip()
                if key == "주소":
                    ps = td.find_elements(By.TAG_NAME, "p")
                    info["지번주소"] = ps[0].text.strip() if ps else ""
                    if len(ps) > 1:
                        icon = ps[1].find_element(By.TAG_NAME, "i").text
                        info["도로명주소"] = ps[1].text.replace(icon, "").strip()
                else:
                    info[key] = td.text.replace("\n", " ").strip()
        logger.info("단지 정보 수집 완료")
        return info

    def select_area_tab(self, target_area: str) -> None:
        try:
            more_button = self.driver.find_element(By.CSS_SELECTOR, "button.btn_moretab")
            if more_button.is_displayed():
                more_button.click()
                time.sleep(random.uniform(0.2, 0.6))
                logger.info("면적 더보기 버튼 클릭 완료")
        except Exception:
            logger.info("더보기 버튼 없음 또는 이미 펼쳐져 있음")

        try:
            tabs = self.wait.until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".detail_sorting_tab .text"))
            )
            for tab_text in tabs:
                if tab_text.text.strip().startswith(target_area):
                    tab_text.click()
                    logger.info("%s㎡ 탭 클릭 완료", target_area)
                    return
            logger.warning("%s㎡ 탭을 찾지 못함", target_area)
        except Exception as e:
            logger.error("면적 탭 선택 중 오류 발생: %s", e)

    def click_sise_tab(self) -> None:
        tab = self.wait.until(EC.element_to_be_clickable(self.SISE_TAB))
        tab.click()
        logger.info("시세/실거래가 탭 클릭")

    def select_price_area(self, target_area: str) -> None:
        area_buttons = self.wait.until(EC.presence_of_all_elements_located(self.PRICE_AREA_TABS))
        for btn in area_buttons:
            if target_area in btn.text:
                btn.click()
                logger.info("시세 면적 '%s' 선택", target_area)
                time.sleep(random.uniform(1.0, 1.5))
                return
        logger.warning("%s㎡ 시세 면적을 찾지 못함", target_area)

    def select_deal_type(self, deal_type: str) -> None:
        deal_tabs = self.wait.until(EC.presence_of_all_elements_located(self.DEAL_TABS))
        for tab in deal_tabs:
            if tab.text.strip() == deal_type:
                tab.click()
                logger.info("거래 유형 '%s' 선택", deal_type)
                time.sleep(random.uniform(1.0, 1.5))
                return
        logger.warning("%s 거래 유형을 찾지 못함", deal_type)

    def get_area_info(self) -> Dict[str, str]:
        data = {}
        driver = self.driver
        wait = self.wait
        container = driver.find_element(By.CSS_SELECTOR, "#tabpanel")

        def get_text(selector):
            try:
                return container.find_element(By.CSS_SELECTOR, selector).text.strip()
            except:
                return ""

        def get_all_texts(selector):
            try:
                return [el.text.strip() for el in container.find_elements(By.CSS_SELECTOR, selector)]
            except:
                return []

        selected_tab = driver.find_element(By.CSS_SELECTOR, ".detail_sorting_tab[aria-selected='true']")
        area_text = selected_tab.text.strip()
        data["area"] = area_text

        try:
            supply_exclusive = container.find_element(By.XPATH, ".//th[contains(text(), '공급')]/following-sibling::td").text
            supply, exclusive_with_rate = supply_exclusive.split("/")
            exclusive, rate = exclusive_with_rate.strip(")").split("(")
            data["supply_area"] = supply.strip()
            data["exclusive_area"] = exclusive.strip()
            data["exclusive_rate"] = rate.strip()
        except:
            data["supply_area"] = ""
            data["exclusive_area"] = ""
            data["exclusive_rate"] = ""

        try:
            room_bath = container.find_element(By.XPATH, ".//th[contains(text(), '방수')]/following-sibling::td").text
            room, bath = room_bath.split("/")
            data["room_count"] = room.replace("개", "").strip()
            data["bathroom_count"] = bath.replace("개", "").strip()
        except:
            data["room_count"] = ""
            data["bathroom_count"] = ""

        data["household_count"] = get_text("th:contains('해당면적 세대수') + td")
        data["entrance_structure"] = get_text("th:contains('현관구조') + td")

        price_counts = {}
        for label in ["매매", "전세", "월세", "단기"]:
            try:
                el = container.find_element(By.XPATH, f".//a[contains(text(), '{label}')]")
                count = el.find_element(By.CLASS_NAME, "point2").text
                price_counts[label] = count
            except:
                price_counts[label] = "0"
        data["price_count"] = price_counts

        price_info_items = get_all_texts(".info_list_item")
        price_info = {}
        for item in price_info_items:
            if "매매" in item:
                price_info["매매"] = item.replace("매매 ", "")
            elif "전세가율" in item:
                price_info["전세가율"] = item.replace("전세가율 ", "")
            elif "전세" in item:
                price_info["전세"] = item.replace("전세 ", "")
        data["price_info"] = price_info

        maintenance_cost = {}
        maintenance_cost["현재월"] = get_text(".point3.cost")
        try:
            details = container.find_elements(By.CSS_SELECTOR, "ul.info_list_wrap li.info_list_item")
            for item in details:
                text = item.text
                if "월평균 관리비" in text:
                    maintenance_cost["월평균"] = text.split(" ")[-1]
                elif "하절기평균" in text:
                    maintenance_cost["하절기평균"] = text.split(" ")[-1]
                elif "동절기평균" in text:
                    maintenance_cost["동절기평균"] = text.split(" ")[-1]
        except:
            pass
        data["maintenance_cost"] = maintenance_cost

        try:
            data["official_price"] = container.find_element(By.XPATH, ".//th[contains(text(), '공시가격')]/following-sibling::td").text.replace("해당면적 최고가 ", "").strip()
        except:
            data["official_price"] = ""

        holding_tax = {}
        try:
            holding_tax["합계"] = get_text("th:contains('보유세') + td strong")
            li_texts = get_all_texts("tr:has(th:contains('보유세')) + tr li")
            for li in li_texts:
                if "재산세" in li:
                    holding_tax["재산세"] = li.replace("재산세", "").strip()
                elif "종합부동산세" in li:
                    holding_tax["종합부동산세"] = li.replace("종합부동산세", "").strip()
        except:
            pass
        data["holding_tax"] = holding_tax

        return data


class PricePage:
    MORE_BUTTON_XPATH = (
        "//div[contains(@class,'detail_price_data')"
        " and .//table[contains(@class,'detail_data_table') and contains(@class,'type_price')]]"
        "//button[contains(@class,'detail_data_more')]"
    )
    PRICE_TABLE = (By.CSS_SELECTOR, "table.detail_data_table.type_price")

    def __init__(self, driver: WebDriver, wait: WebDriverWait):
        self.driver = driver
        self.wait = wait

    def load_more(self, limit: int = 100) -> None:
        logger.info("매매 시세 더보기 클릭중", limit)
        for i in range(limit):
            try:
                short_wait = WebDriverWait(self.driver, 2)
                btn = short_wait.until(
                    EC.element_to_be_clickable((By.XPATH, self.MORE_BUTTON_XPATH))
                )
                self.driver.execute_script("arguments[0].click();", btn)
                time.sleep(random.uniform(0.2, 0.3))
            except TimeoutException:
                logger.info("더 이상 '매매 시세 더보기' 버튼이 없습니다.")
                break

    def get_price_history(self) -> Dict[str, Dict[str, str]]:
        table = self.wait.until(EC.presence_of_element_located(self.PRICE_TABLE))
        headers = [h.text.strip() for h in table.find_elements(By.CSS_SELECTOR, "thead th")]
        history: Dict[str, Dict[str, str]] = {}
        for row in table.find_elements(By.CSS_SELECTOR, "tbody tr"):
            cols = [c.text.strip() for c in row.find_elements(By.CSS_SELECTOR, "th,td")]
            if len(cols) != len(headers):
                continue
            raw_date = cols[0].replace(".", "-").strip("-")
            try:
                date_key = datetime.datetime.strptime(raw_date, "%Y-%m-%d").strftime("%Y-%m-%d")
            except ValueError:
                continue
            history[date_key] = {headers[i]: cols[i] for i in range(1, len(headers))}
        logger.info("시세 이력 수집 완료: 총 %d건", len(history))
        return history


class NaverLandCrawler:
    def __init__(self, headless: bool = False):
        service = Service("/usr/bin/chromedriver")
        options = webdriver.ChromeOptions()
        if headless:
            options.add_argument("--headless")
        options.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2})
        self.driver = webdriver.Chrome(service=service, options=options)
        self.wait = WebDriverWait(self.driver, 10)
        self.search_page = SearchPage(self.driver, self.wait)
        self.detail_page = DetailPage(self.driver, self.wait)
        self.price_page = PricePage(self.driver, self.wait)

    def close(self):
        self.driver.quit()
        logger.info("브라우저 종료")

    def parse_summary_info(self) -> dict:
        driver = self.driver
        wait = self.wait
        wait.until(EC.presence_of_element_located((By.ID, "summaryInfo")))
        summary = driver.find_element(By.ID, "summaryInfo")

        title = summary.find_element(By.ID, "complexTitle").text.strip()
        dl = summary.find_element(By.CLASS_NAME, "complex_feature")
        dt_elements = dl.find_elements(By.TAG_NAME, "dt")
        dd_elements = dl.find_elements(By.TAG_NAME, "dd")
        feature = {dt.text.strip(): dd.text.strip() for dt, dd in zip(dt_elements, dd_elements)}

        return {
            "title": title,
            "feature": feature
        }


    def fetch_property_info(self, keyword: str):
        driver = self.driver
        try:
            driver.get("https://new.land.naver.com/search")
            wait = WebDriverWait(driver, 10)

            search_input = wait.until(EC.presence_of_element_located((By.ID, "land_search")))
            search_input.clear()
            search_input.send_keys(keyword)
            search_input.send_keys(u'\ue007')

            time.sleep(random.uniform(1.0, 1.5))
            page_html = driver.page_source
            is_direct_detail = "검색결과" not in page_html

            if is_direct_detail:
                try:
                    info = self.parse_summary_info()
                    title = info["title"]
                    feature = info["feature"]
                    COMPLEX_BUTTON = (By.XPATH, '//button[@class="complex_link" and text()="단지정보"]')
                    btn = self.wait.until(EC.element_to_be_clickable(COMPLEX_BUTTON))
                    btn.click()
                    time.sleep(random.uniform(0.5, 1.0))
                    logger.info("단지정보 버튼 클릭")
                    address_elem = driver.find_elements(By.CSS_SELECTOR, "p.address")
                    address = address_elem[0].text if address_elem else None
                    logger.info(f"address : {address}")
                    
                    return {
                        "results": [{
                            "index": 1,
                            "title": title,
                            "address": address,
                            "type": feature.get("유형"),
                            "households": feature.get("세대수"),
                            "buildings": feature.get("동수"),
                            "approval_date": feature.get("사용승인일"),
                            "area": feature.get("면적")
                        }],
                    }

                except Exception as e:
                    return {"error": f"단지 정보 파싱 실패: {str(e)}", "type": 0}

            else:
                try:
                    wait.until(EC.presence_of_element_located((By.CLASS_NAME, "item_inner")))
                    items = driver.find_elements(By.CLASS_NAME, "item_inner")
                    if not items:
                        return {"error": "검색 결과가 없습니다."}

                    results = []
                    for idx, item in enumerate(items, start=1):
                        title = address = item_type = ""
                        spec_list = []
                        try:
                            title_elem = item.find_elements(By.CLASS_NAME, "title")
                            if title_elem:
                                title = title_elem[0].text.strip()

                            address_elem = item.find_elements(By.CLASS_NAME, "address")
                            if address_elem:
                                address = address_elem[0].text.strip()

                            info_area = item.find_elements(By.CLASS_NAME, "info_area")
                            if info_area:
                                type_elem = info_area[0].find_elements(By.CLASS_NAME, "type")
                                if type_elem:
                                    item_type = type_elem[0].text.strip()
                                spec_elems = info_area[0].find_elements(By.CLASS_NAME, "spec")
                                spec_list = [s.text.strip() for s in spec_elems if s.text.strip()]
                        except Exception:
                            continue

                        specs_map = {}
                        if len(spec_list) >= 4:
                            specs_map = {
                                "households": spec_list[0],
                                "buildings": spec_list[1],
                                "approval_date": spec_list[2], 
                                "area": spec_list[3],
                            }

                        results.append({
                            "index": idx,
                            "title": title,
                            "address": address,
                            "type": item_type,
                            **specs_map
                        })

                    return {"results": results}

                except Exception as e:
                    return {"error": f"검색 리스트 파싱 실패: {str(e)}"}

        finally:
            self.close()

    def get_complex_info(self, keyword: str) -> dict:
        complex_info = {}
        try:
            self.search_page.open()
            self.search_page.search(keyword)
            try:
                self.detail_page.click_complex_info()
                complex_info = self.detail_page.get_complex_info()
                #logger.info(f"단지 정보: {complex_info}")
            except Exception as e:
                logger.warning("단지 정보 수집 실패: %s", e)

        finally:
            self.close()

        return {
            "complex_info": complex_info
        }

    def run(self, keyword: str, area: str, deal_type: str) -> dict:
        complex_info = {}
        area_detail = {}
        price_history = {}
        summary_data = {}
        price_monthly_avg = {}
        forecast_json = {}

        try:
            self.search_page.open()
            self.search_page.search(keyword)

            try:
                summary_data = self.parse_summary_info()
                #logger.info(f"요약 정보: {summary_data}")
            except Exception as e:
                logger.warning("요약 정보 파싱 실패: %s", e)

            self.detail_page.click_complex_info()
            complex_info = self.detail_page.get_complex_info()

            try:
                self.detail_page.select_area_tab(area)
            except Exception as e:
                logger.warning("면적 탭 선택 실패: %s", e)

            try:
                area_detail = self.detail_page.get_area_info()
                #logger.info(f"단지내 면적별 정보: {area_detail}")
            except Exception as e:
                logger.warning("단지내 면적별 정보 수집 실패: %s", e)

            try:
                self.detail_page.click_sise_tab()
                time.sleep(random.uniform(0.5, 1.0))
            except Exception as e:
                logger.warning("시세 탭 클릭 실패: %s", e)

            try:
                self.detail_page.select_price_area(area)
            except Exception as e:
                logger.warning("시세 면적 선택 실패: %s", e)

            try:
                self.detail_page.select_deal_type(deal_type)
            except Exception as e:
                logger.warning("거래 유형 선택 실패: %s", e)

            try:
                self.price_page.load_more()
                price_history = self.price_page.get_price_history()
                #logger.info(f"시세 이력: {price_history}")   
            except Exception as e:
                logger.warning("시세 이력 수집 실패: %s", e)

            try:    
                price_monthly_avg = compute_monthly_avg(price_history)
                #logger.info(f"월별 평균 매매가: {price_monthly_avg}")
                forecast_json  = run_forecast_from_avg(price_monthly_avg)
                #logger.info(f"12개월 가격 예측: {forecast_json}")
            except Exception as e:
                logger.warning("부동산 가격 예측 실패: %s", e)

        finally:
            self.close()

        return {
            "summary_data": summary_data,
            "complex_info": complex_info,
            "area_detail": area_detail,
            "price_history": price_history,
            "price_monthly_avg": price_monthly_avg,
            "forecast_json": forecast_json,
        }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="네이버 부동산 시세 크롤러")
    parser.add_argument("keyword", help="검색 키워드")
    parser.add_argument("index", type=int, help="검색 결과 중 선택 번호 (1부터)")
    parser.add_argument("area", help="면적 (예: 89)")
    parser.add_argument("deal_type", help="거래 유형 (예: 매매)")
    parser.add_argument("--headless", action="store_true", help="헤드리스 모드 실행")
    return parser.parse_args()


def main():
    args = parse_args()
    crawler = NaverLandCrawler(headless=args.headless)
    try:
        crawler.run(args.keyword, args.index - 1, args.area, args.deal_type)
    finally:
        crawler.close()


if __name__ == "__main__":
    main()
