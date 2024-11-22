from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random
import sys
import json
from datetime import datetime
import logging

class YouTubeViewBot:
    def __init__(self):
        self.running = True
        self.setup_logging()
        self.stats = {
            'total_views': 0,
            'total_time': 0,
            'successful_views': 0,
            'failed_views': 0,
            'interactions': {
                'likes': 0,
                'fullscreen': 0,
                'speed_changes': 0,
                'scrolls': 0
            },
            'sessions': []
        }
        
        # ตั้งค่า Chrome Options
        chrome_options = Options()
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('--disable-notifications')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        # ปิดการตรวจจับ automation
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    def setup_logging(self):
        logging.basicConfig(
            filename=f'youtube_bot_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
    
    def log_session(self, video_url, watch_time, success=True, error=None):
        session = {
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'video_url': video_url,
            'watch_time': watch_time,
            'success': success,
            'error': str(error) if error else None
        }
        self.stats['sessions'].append(session)
        
        if success:
            self.stats['successful_views'] += 1
            self.stats['total_time'] += watch_time
        else:
            self.stats['failed_views'] += 1
        
        self.save_stats()
        logging.info(f"Session logged: {session}")
    
    def save_stats(self):
        with open(f'youtube_bot_stats_{datetime.now().strftime("%Y%m%d")}.json', 'w') as f:
            json.dump(self.stats, f, indent=4)
    
    def human_like_interaction(self):
        try:
            # สุ่มเลื่อนหน้าจอ
            if random.random() < 0.7:
                scroll_amount = random.randint(100, 500)
                self.driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
                self.stats['interactions']['scrolls'] += 1
                logging.info(f"Scrolled: {scroll_amount}px")
                time.sleep(random.uniform(1, 3))
            
            # สุ่มขยายวิดีโอเต็มจอ
            if random.random() < 0.3:
                try:
                    fullscreen_button = self.driver.find_element(By.CLASS_NAME, "ytp-fullscreen-button")
                    fullscreen_button.click()
                    self.stats['interactions']['fullscreen'] += 1
                    logging.info("Toggled fullscreen")
                    time.sleep(random.uniform(5, 10))
                    fullscreen_button.click()
                except:
                    pass
            
            # สุ่มกดไลค์
            if random.random() < 0.4:
                try:
                    like_button = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "button[aria-label*='like']"))
                    )
                    like_button.click()
                    self.stats['interactions']['likes'] += 1
                    logging.info("Liked video")
                except:
                    pass
                    
        except Exception as e:
            logging.error(f"Interaction error: {str(e)}")
    
    def watch_video(self, video_url, watch_time):
        try:
            if not self.running:
                return
                
            logging.info(f"Starting to watch video: {video_url}")
            self.driver.get(video_url)
            
            # รอให้วิดีโอโหลดและเริ่มเล่น
            video_element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "video.html5-main-video"))
            )
            
            # จำลองพฤติกรรมการดูวิดีโอ
            watched_time = 0
            while watched_time < watch_time and self.running:
                if watched_time % 30 == 0:
                    self.human_like_interaction()
                time.sleep(1)
                watched_time += 1
            
            self.log_session(video_url, watched_time, success=True)
            
        except Exception as e:
            logging.error(f"Error watching video: {str(e)}")
            self.log_session(video_url, 0, success=False, error=e)
    
    def get_stats_summary(self):
        return f"""
Bot Statistics:
Total Views Attempted: {self.stats['successful_views'] + self.stats['failed_views']}
Successful Views: {self.stats['successful_views']}
Failed Views: {self.stats['failed_views']}
Total Watch Time: {self.stats['total_time']} seconds
Interactions:
- Likes: {self.stats['interactions']['likes']}
- Fullscreen Toggles: {self.stats['interactions']['fullscreen']}
- Scrolls: {self.stats['interactions']['scrolls']}
        """
    
    def stop(self):
        self.running = False
        self.close()
    
    def close(self):
        try:
            self.driver.quit()
        except:
            pass

def main():
    bot = None
    try:
        while True:  # วนลูปหลัก
            try:
                print("กำลังเริ่มรอบใหม่...")
                bot = YouTubeViewBot()
                video_url = "https://www.youtube.com/watch?v=a-C1WpTeVTI"
                
                # ดูวิดีโอ
                watch_time = random.randint(120, 300)  # 2-5 นาที
                bot.watch_video(video_url, watch_time)
                print(bot.get_stats_summary())
                
                # ปิด browser และรอก่อนเริ่มรอบใหม่
                bot.close()
                
                wait_time = random.randint(30, 60)  # รอ 30-60 วินาที
                print(f"\nรอ {wait_time} วินาทีก่อนเริ่มรอบใหม่...")
                time.sleep(wait_time)
                
            except KeyboardInterrupt:
                print("\nกำลังหยุดบอท...")
                if bot:
                    bot.stop()
                    bot.save_stats()
                sys.exit(0)
                
            except Exception as e:
                print(f"เกิดข้อผิดพลาด: {str(e)}")
                if bot:
                    bot.close()
                time.sleep(10)
                continue
                
    finally:
        if bot:
            bot.save_stats()
            bot.close()

if __name__ == "__main__":
    main() 