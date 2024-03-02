from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# URL-адрес веб-страницы с картой
url = "http://your_website.com"

# Создаем драйвер Selenium
driver = webdriver.Firefox()  # или используйте другой драйвер, например, Chrome

# Загружаем страницу
driver.get(url)

# Находим все метки камер (замените на правильный селектор)
camera_markers = driver.find_elements_by_css_selector(".camera-marker")

# Список для хранения URL-адресов потоков
stream_urls = []

# "Кликаем" на каждую метку и извлекаем URL-адрес потока
for marker in camera_markers:
    marker.click()

    # Ждем, пока плеер загрузится (замените на правильный селектор)
    player = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".player"))
    )

    # Извлекаем URL-адрес потока (замените на правильный атрибут)
    stream_url = player.get_attribute("data-stream-url")

    # Добавляем URL-адрес потока в список
    stream_urls.append(stream_url)

# Закрываем драйвер
driver.quit()

# Выводим URL-адреса потоков
for url in stream_urls:
    print(url)