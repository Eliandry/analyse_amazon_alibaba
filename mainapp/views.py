import os
import shlex
import subprocess
import csv

from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
from django.http import HttpResponseRedirect
from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import TfidfVectorizer
import nltk
from nltk.corpus import stopwords
import re
import string
import random
import base64
from io import BytesIO
from .forms import ScraperForm, UploadFileForm
import os
from django.conf import settings


def run_spider(request):
    if request.method == 'POST':
        form = ScraperForm(request.POST)
        if form.is_valid():
            my_base_url = form.cleaned_data['my_base_url']
            # Запуск скрипта Scrapy с параметром
            command = f'scrapy runspider amazon_reviews_scraping/spiders/amazon_review.py -a my_base_url="{my_base_url}"'
            subprocess.run(shlex.split(command))
    else:
        form = ScraperForm()
    return render(request, 'run_spider.html', {'form': form})


def run_parser(request):
    if request.method == 'POST':
        form = ScraperForm(request.POST)
        if form.is_valid():
            url = form.cleaned_data['my_base_url']

            driver = webdriver.Chrome()  # Укажите путь к драйверу Chrome
            driver.get(url)

            # Функция для извлечения оценок
            def get_reviews(driver):
                reviews = driver.find_elements(By.CLASS_NAME, 'review-item')
                review_data = []
                for review in reviews:
                    try:
                        review_info = review.find_element(By.CLASS_NAME, 'review-info').text
                        rating_elements = review.find_elements(By.CLASS_NAME, 'detail-next-rating-icon')
                        rating = len(rating_elements)
                        review_data.append({"star": rating, "comment": review_info})
                    except NoSuchElementException:
                        print("Элемент не найден")
                return review_data

            # Проверка наличия и клик по кнопке "Следующая"
            def click_next_page():
                try:
                    next_button = driver.find_element(By.CLASS_NAME, 'detail-next-next')
                    if next_button.is_enabled():
                        next_button.click()
                        time.sleep(5)  # Ожидание для полной загрузки страницы
                        return True
                except :
                    return False

            # Сбор данных
            all_reviews = []
            while True:
                all_reviews.extend(get_reviews(driver))
                if not click_next_page():
                    break

            driver.quit()

            # Сохранение данных в CSV
            with open('ali_data.csv', mode='w', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=["star", "comment"])
                writer.writeheader()
                for review in all_reviews:
                    writer.writerow(review)
    else:
        form = ScraperForm()
    return render(request, 'run_parser.html', {'form': form})


def file_list(request):
    # Получаем список всех файлов в папке 'res'
    files = os.listdir('media')
    csv_files = [file for file in files if file.endswith('.csv')]
    return render(request, 'file_list.html', {'files': csv_files})


def main(request):
    return render(request, "main.html")


def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            handle_uploaded_file(request.FILES['file'])
            return HttpResponseRedirect('files/')
    else:
        form = UploadFileForm()
    return render(request, 'upload.html', {'form': form})


def handle_uploaded_file(f):
    file_path = os.path.join(settings.MEDIA_ROOT, f.name)
    with open(file_path, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)


def preprocess_text(text):
    # Приведение текста к нижнему регистру
    text = text.lower()
    # Удаление знаков пунктуации
    text = re.sub(f"[{string.punctuation}]", " ", text)
    # Удаление стоп-слов
    stop_words = set(stopwords.words('english'))
    text = ' '.join([word for word in text.split() if word not in stop_words])
    return text


def plot_view(request, filename):
    nltk.download('stopwords')

    # Загрузка данных
    df = pd.read_csv(f'media/{filename}')

    # Фильтрация комментариев с 5 звездами
    df = df[df['star'] != 5]

    # Предобработка данных
    df['comment'] = df['comment'].apply(preprocess_text)

    # Извлечение ключевых словосочетаний с использованием TF-IDF
    # Настройка для биграмм или триграмм
    vectorizer = TfidfVectorizer(max_features=100, max_df=0.85, min_df=2, ngram_range=(2,3))
    tfidf_matrix = vectorizer.fit_transform(df['comment'])
    feature_names = vectorizer.get_feature_names_out()
    scores = tfidf_matrix.sum(axis=0).tolist()[0]
    sorted_words = sorted(zip(feature_names, scores), key=lambda x: x[1], reverse=True)
    keywords, values = zip(*sorted_words)

    # Создание гистограммы для топ-15 словосочетаний
    plt.figure(figsize=(10, 6))
    plt.bar(keywords[:15], values[:15], edgecolor='black')
    plt.title('Топ-15 словосочетаний ')
    plt.xlabel('Словосочетания')
    plt.ylabel('Счет')
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Сохранение и отображение гистограммы
    buf = BytesIO()
    plt.savefig(buf, format='png')
    image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8').replace('\n', '')
    plt.close()

    # Возврат ответа с изображением
    return render(request, 'plot.html', {'image_base64': image_base64})