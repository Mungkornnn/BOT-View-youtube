from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def test_driver():
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service)
        print("Chrome WebDriver ติดตั้งสำเร็จ!")
        driver.get("https://www.youtube.com")
        driver.quit()
    except Exception as e:
        print(f"เกิดข้อผิดพลาด: {str(e)}")

if __name__ == "__main__":
    test_driver() 