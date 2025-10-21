import os
import requests
from concurrent.futures import ThreadPoolExecutor

def download_image(url, folder, filename):
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            with open(os.path.join(folder, filename), 'wb') as f:
                f.write(response.content)
            print(f"{filename}")
        else:
            print(f"Ошибка загрузки {filename}")
    except Exception as e:
        print(f"Пропущен {filename}: {e}")

if __name__ == "__main__":
    folder = "media/properties"
    os.makedirs(folder, exist_ok=True)

    base_url = "https://picsum.photos/800/600.jpg?random="

    urls = [f"{base_url}{i}" for i in range(1, 101)]
    filenames = [f"property_{i}.jpg" for i in range(1, 101)]

    with ThreadPoolExecutor(max_workers=10) as executor:
        for url, filename in zip(urls, filenames):
            executor.submit(download_image, url, folder, filename)

    print("Все изображения загружены!")