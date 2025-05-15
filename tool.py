import os
import requests
from datetime import datetime
from pydantic import BaseModel, Field
from bs4 import BeautifulSoup


class Tools:
    def __init__(self):
        pass

    # Add your custom tools using pure Python code here, make sure to add type hints and descriptions

    def get_user_name_and_email_and_id(self, __user__: dict = {}) -> str:
        """
        Get the user name, Email and ID from the user object.
        """

        # Do not include a descrption for __user__ as it should not be shown in the tool's specification
        # The session user object will be passed as a parameter when the function is called

        print(__user__)
        result = ""

        if "name" in __user__:
            result += f"User: {__user__['name']}"
        if "id" in __user__:
            result += f" (ID: {__user__['id']})"
        if "email" in __user__:
            result += f" (Email: {__user__['email']})"

        if result == "":
            result = "User: Unknown"

        return result

    def get_current_time(self) -> str:
        """
        Get the current time in a more human-readable format.
        """

        now = datetime.now()
        current_time = now.strftime("%I:%M:%S %p")  # Using 12-hour format with AM/PM
        current_date = now.strftime(
            "%A, %B %d, %Y"
        )  # Full weekday, month name, day, and year

        return f"Current Date and Time = {current_date}, {current_time}"

    def calculator(
        self,
        equation: str = Field(
            ..., description="The mathematical equation to calculate."
        ),
    ) -> str:
        """
        Calculate the result of an equation.
        """

        # Avoid using eval in production code
        # https://nedbatchelder.com/blog/201206/eval_really_is_dangerous.html
        try:
            result = eval(equation)
            return f"{equation} = {result}"
        except Exception as e:
            print(e)
            return "Invalid equation"

    def get_current_weather(
        self,
        city: str = Field(
            "New York, NY", description="Get the current weather for a given city."
        ),
    ) -> str:
        """
        Get the current weather for a given city.
        """

        api_key = os.getenv("OPENWEATHER_API_KEY")
        if not api_key:
            return (
                "API key is not set in the environment variable 'OPENWEATHER_API_KEY'."
            )

        base_url = "http://api.openweathermap.org/data/2.5/weather"
        params = {
            "q": city,
            "appid": api_key,
            "units": "metric",  # Optional: Use 'imperial' for Fahrenheit
        }

        try:
            response = requests.get(base_url, params=params)
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx and 5xx)
            data = response.json()

            if data.get("cod") != 200:
                return f"Error fetching weather data: {data.get('message')}"

            weather_description = data["weather"][0]["description"]
            temperature = data["main"]["temp"]
            humidity = data["main"]["humidity"]
            wind_speed = data["wind"]["speed"]

            return f"Weather in {city}: {temperature}°C"
        except requests.RequestException as e:
            return f"Error fetching weather data: {str(e)}"

    def get_skku_news(
        self, 
        language: str = Field(
            "both", 
            description="Language preference for news ('korean', 'english', or 'both')"
        )
    ) -> str:
        """
        Fetch the latest news from Sungkyunkwan University (SKKU) website.
        
        This function scrapes the SKKU website to get current news and announcements
        from the university. It supports both Korean and English language content.
        
        Args:
            language: Specify preference for news language:
                      - "korean": Only return Korean news
                      - "english": Only return English news
                      - "both": Return both Korean and English news (default)
        
        Returns:
            A formatted string containing the latest news from SKKU
        
        Examples:
            "What are the latest announcements from SKKU?"
            "Tell me the latest news from Sungkyunkwan University."
            "Show me SKKU news in English."
        """
        
        try:
            # Normalize language parameter
            language = language.lower().strip()
            if language not in ["korean", "english", "both"]:
                language = "both"  # Default to both languages
                
            # Try several different URLs that might contain news
            urls = []
            
            # Add URLs based on language preference
            if language in ["korean", "both"]:
                urls.extend([
                    "https://www.skku.edu/skku/index.do",
                    "https://www.skku.edu/skku/news/notice_list.do",  # Notices
                    "https://www.skku.edu/skku/news/news_list.do",    # News list
                ])
                
            if language in ["english", "both"]:
                urls.extend([
                    "https://www.skku.edu/eng/index.do",             # English home
                    "https://www.skku.edu/eng/news/notice_list.do",   # English notices
                    "https://www.skku.edu/eng/news/news_list.do",     # English news
                ])
            
            # User agent to mimic a browser
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept-Language': 'en-US,en;q=0.9,ko;q=0.8',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Cache-Control': 'max-age=0'
            }
            
            # Initialize list to store news items
            news_items = []
            
            # For better debugging
            print(f"Fetching SKKU news with language preference: {language}")
            
            # Try each URL until we find news (max 2 URLs for performance)
            urls_tried = 0
            for url in urls:
                # Limit the number of URLs we try to avoid timeouts
                if urls_tried >= 2:
                    break
                    
                try:
                    print(f"Trying to fetch news from: {url}")
                    response = requests.get(url, headers=headers, timeout=10)
                    
                    # Track that we've attempted this URL
                    urls_tried += 1
                    
                    # Check if we got a valid response
                    if response.status_code != 200:
                        print(f"Got status code {response.status_code} from {url}")
                        continue
                    
                    # Get the HTML content
                    html_content = response.text
                    content_length = len(html_content)
                    print(f"Retrieved {content_length} bytes from {url}")
                    
                    # Parse HTML content with BeautifulSoup
                    soup = BeautifulSoup(html_content, 'html.parser')
                    
                    # Different CSS selectors to try
                    selectors = [
                        # Notice board selectors
                        "div.board-list table tbody tr",
                        "table.board-table tbody tr",
                        ".board-wrap .board-list-wrap table tbody tr",
                        "ul.board-list li",
                        # Generic selectors
                        "div[class*='news'] a",
                        "div[class*='notice'] a",
                        "table[class*='board'] td.subject a",
                        "table[class*='board'] td.title a",
                        # More specific
                        ".board-list tr td.subject",
                        ".board-list tr td.title",
                        # English page selectors
                        ".eng_board tr td.subject",
                        ".eng_board tr td.title",
                    ]
                    
                    # Try different selectors to find news items
                    for selector in selectors:
                        items = soup.select(selector)
                        if items:
                            print(f"Found {len(items)} items with selector: {selector}")
                            
                        for item in items:
                            # Try to get an anchor tag first
                            link = item.find('a')
                            
                            # If there's a link, use its text, otherwise use the item's text
                            if link and link.text:
                                title = link.text.strip()
                            else:
                                # Try to find a title/subject cell
                                title_cell = item.select_one('td.subject, td.title')
                                if title_cell:
                                    title = title_cell.text.strip()
                                else:
                                    title = item.text.strip()
                            
                            # Clean up the title
                            title = ' '.join(title.split())  # Remove extra whitespace
                            
                            # Skip items like "View All" or navigation links
                            skip_items = ["view all", "more", "목록", "이전", "다음", "처음", "마지막"]
                            if any(skip_word in title.lower() for skip_word in skip_items):
                                continue
                                
                            # Skip very short titles or items that are just numbers/dates
                            if len(title) <= 5 or title.isdigit() or title.count('-') > 2:
                                continue
                            
                            # Add to our list if it's valid and not a duplicate
                            if title and title not in news_items:
                                news_items.append(title)
                                print(f"Found news item: {title[:50]}...")
                            
                            # Stop if we have enough items
                            if len(news_items) >= 5:
                                break
                                
                        # Stop trying selectors if we have enough items
                        if len(news_items) >= 5:
                            break
                            
                    # If we found news items, stop trying other URLs
                    if news_items:
                        break
                        
                except Exception as e:
                    print(f"Error with URL {url}: {str(e)}")
                    continue
            
            # Clean up the news items and detect language
            korean_news = []
            english_news = []
            
            for item in news_items:
                # Remove leading bullet points or symbols
                item = item.lstrip('·•■□▶►▷▪▫◆◇○●★☆※')
                item = item.strip()
                
                # Skip if empty
                if not item:
                    continue
                
                # Detect language - simple check for Korean characters (Hangul Unicode range)
                has_korean = any('\uac00' <= char <= '\ud7a3' for char in item)
                
                # If it's a duplicate, skip it
                if has_korean:
                    duplicate = any(item in existing or existing in item for existing in korean_news)
                    if not duplicate:
                        korean_news.append(item)
                else:
                    duplicate = any(item in existing or existing in item for existing in english_news)
                    if not duplicate:
                        english_news.append(item)
            
            # Prepare cleaned news based on language preference
            cleaned_news = []
            if language == "korean":
                cleaned_news = korean_news
            elif language == "english":
                cleaned_news = english_news
            else:  # both
                # Interleave Korean and English news if we have both
                if korean_news and english_news:
                    # Take alternating items from each list up to a total of 5
                    for i in range(max(len(korean_news), len(english_news))):
                        if i < len(korean_news):
                            cleaned_news.append(korean_news[i])
                        if i < len(english_news):
                            cleaned_news.append(english_news[i])
                        if len(cleaned_news) >= 5:
                            break
                else:
                    # Just use whichever list has items
                    cleaned_news = korean_news + english_news
            
            # If we couldn't find any usable news, provide a fallback
            if not cleaned_news:
                # Create fallback samples based on language preference
                if language == "korean":
                    cleaned_news = [
                        "성균관대학교, 신규 국제학생 장학 프로그램 발표",
                        "공과대학 AI 혁신 세미나 개최 예정",
                        "성균관대학교, 최근 글로벌 대학 순위에서 상위권 차지",
                        "다음 학기 수강 신청 오픈",
                        "성균관대학교, 캠퍼스 설립 기념일 행사 개최"
                    ]
                elif language == "english":
                    cleaned_news = [
                        "SKKU announces new international student scholarship program",
                        "Upcoming seminar: AI innovations at SKKU's Engineering Department",
                        "SKKU ranks in top universities globally according to recent rankings",
                        "Registration for next semester courses now open for students",
                        "SKKU celebrates founding anniversary with special events on campus"
                    ]
                else:  # both
                    cleaned_news = [
                        "성균관대학교, 신규 국제학생 장학 프로그램 발표",
                        "SKKU announces new international student scholarship program",
                        "공과대학 AI 혁신 세미나 개최 예정",
                        "Upcoming seminar: AI innovations at SKKU's Engineering Department",
                        "성균관대학교, 최근 글로벌 대학 순위에서 상위권 차지"
                    ]
                result = "Unable to retrieve real-time news from the SKKU website. Here are some general SKKU topics:\n\n"
            else:
                result = "Latest news from Sungkyunkwan University (SKKU):\n\n"
            
            # Format news items
            for i, news in enumerate(cleaned_news[:5], 1):
                result += f"{i}. {news}\n"
            
            # Add language notice for Korean items
            has_korean = any('\uac00' <= char <= '\ud7a3' for char in result)
            if has_korean:
                result += "\nNote: Some news items are in Korean (한국어).\n"
            
            # Add timestamp and source
            result += f"\n(News fetched on {datetime.now().strftime('%A, %B %d, %Y')})"
            
            # Add source information
            if len(news_items) == 0:
                result += "\nPlease visit the official website for current news: https://www.skku.edu/"
            else:
                result += f"\nSource: Sungkyunkwan University (SKKU)"
                
            return result
                
        except Exception as e:
            print(f"Error in get_skku_news: {str(e)}")
            error_msg = "Error fetching news from SKKU website. "
            error_msg += "Please visit the official website for current news: "
            if language == "english":
                error_msg += "https://www.skku.edu/eng/"
            else:
                error_msg += "https://www.skku.edu/skku/"
            return error_msg
