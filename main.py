import psutil
import pandas as pd
import re
import numpy as np
import requests
from bs4 import BeautifulSoup
import io
from PIL import Image
import os

project_title = 'Arya Полотенца'

sizes = {'100x150': {'RUS': 'Полотенце банное', 'UKR': 'Рушник банний', 'weight': 400, 'gab': '25x20x5'},
         '70x140': {'RUS': 'Полотенце банное', 'UKR': 'Рушник банний', 'weight': 300, 'gab': '22х16х5'},
         '30x50': {'RUS': 'Полотенце для рук', 'UKR': 'Рушник для рук', 'weight': 200, 'gab': '22х16х5'},
         '50x90': {'RUS': 'Полотенце для лица', 'UKR': 'Рушник для обличчя', 'weight': 250, 'gab': '25х15х3'}
         }

compositions = {'100% хлопок': '100% бавовна'}
colors = {'Персиковый': 'Персиковый',
          'Коралловый': 'Коралловый',
          'Сухая Роза': 'Сухая Роза',
          'Сірий': 'Серый',
          'Кремовий': 'Кремовый',
          'Хаки': 'Хаки',
          'Светло-Розовый': 'Светло-Розовый',
          'Аква': 'Аква',
          'Червоний': 'Красный',
          'Світло-Блакитний': 'Светло-Голубой',
          'Чорний': 'Черный',
          'Кирпичный': 'Кирпичный',
          'Рожевий': 'Розовый',
          'Білий': 'Белый',
          'Голубой': 'Голубой',
          'жовтий': 'Желтый',
          'Блакитний': 'Голубой',
          'Екрю': 'Экрю',
          'Экрю': 'Экрю',
          'Бежевый': 'Бежевый',
          'Коричневый': 'Коричневый',
          'Фуксія': 'Фуксия',
          'Желтый': 'Желтый',
          'Мятный': 'Мятный',
          'Темно-Коричневый': 'Темно-Коричневый',
          'Пурпуровий': 'Пурпуровый',
          'Темно-Блакитний': 'Темно-Голубой',
          'Пурпурный': 'Пурпуровый',
          'Пiсочний': 'Песочный',
          'Ліловий': 'Лиловый',
          'Розовый': 'Розовый',
          'Жовтий': 'Желтый',
          'Персiковий': 'Персиковый',
          'Синий': 'Синий',
          'Белый': 'Белый',
          'Синій': 'Синий',
          'Пудра': 'Пудра',
          'Темно-Синій': 'Темно-Cиний',
          'Коричневий': 'Коричневый',
          'Темно-Бирюзовый': 'Темно-Бирюзовый',
          'Серый': 'Серый',
          'Кремовый': 'Кремовый',
          'Персиковий': 'Персиковый',
          'Песочный': 'Песочный',
          'Лиловый': 'Лиловый',
          'Бежевий': 'Бежевый',
          'Фуксия': 'Фуксия',
          'Цегляний': 'Кирпичный'}

transform_colors = {'Бежевый': 'Бежевый', 'Персиковый': 'Персиковый', 'Коралловый': 'Коралловый',
                    'Темно-Cиний': 'Темно-Cиний', 'Хаки': 'Хаки', 'Белый': 'Белый', 'Пудра': 'Пудровый',
                    'Экрю': 'Айвори', 'Лиловый': 'Лиловый', 'Кремовый': 'Бежевый', 'Желтый': 'Желтый',
                    'Фуксия': 'Фуксия', 'Пурпуровый': 'Пурпуровый', 'Мятный': 'Мятный', 'Кирпичный': 'Коричневый',
                    'Черный': 'Черный', 'Песочный': 'Песочный', 'Голубой': 'Голубой',
                    'Светло-Розовый': 'Светло-Розовый', 'Темно-Голубой': 'Темно-Голубой', 'Синий': 'Синий',
                    'Аква': 'Светло-Голубой', 'Красный': 'Красный', 'Розовый': 'Розовый',
                    'Светло-Голубой': 'Светло-Голубой', 'Серый': 'Серый', 'Коричневый': 'Коричневый',
                    'Сухая Роза': 'Пудровый', 'Темно-Коричневый': 'Темно-Коричневый',
                    'Темно-Бирюзовый': 'Темно-бирюзовый'}


def create_folder_by_name(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


def get_valid_product_range(df, start_barode, end_barcode):
    start_range = int(df[df['Артикул'] == start_barode].iloc[0].name)
    end_range = int(df[df['Артикул'] == end_barcode].iloc[-1].name) + 1
    return range(start_range, end_range)


def detect_color(img_response):
    print(img_response.url)
    image = Image.open(io.BytesIO(img_response.content))
    image.show()
    color = input('Введите цвет')
    return color


def download_pictures(code, link, barcodes_colors):
    print(code)
    composition = ''
    density = ''
    for _ in range(5):
        try:
            create_folder_by_name(f'{project_title}/{code}')
            response = requests.get(link)
            soup = BeautifulSoup(response.text, 'lxml')
            try:
                composition = soup.find('td', text='Состав:').find_next('td').text
            except:
                pass
            try:
                density = re.search('[0-9]*', soup.find('td', text='Плотность ткани:').find_next('td').text).group()
            except:
                pass
            all_pictures = soup.find('div', class_='swiper-wrapper').find_all('img')
            folder_photos = {}
            for picture in all_pictures:
                response = requests.get(picture.parent['href'])
                try:
                    picture_color = re.search('Цвет полотенца: (.*)', picture['title']).group(1)
                    if picture_color not in barcodes_colors.keys():
                        # print(f'Найден цвет на сайте {picture_color}, но товара такого цвета нету в экселе, есть только {barcodes_colors.keys()}')
                        raise Exception

                    folder_name = f'/{barcodes_colors[picture_color]}_{transform_colors[picture_color]}'
                except:
                    folder_name = ''
                folder_photos.setdefault(folder_name, 0)
                folder_photos[folder_name] += 1
                create_folder_by_name(f'{project_title}/{code}{folder_name}')
                image_path = f'{project_title}/{code}{folder_name}/{folder_photos[folder_name]}.jpg'
                with Image.open(io.BytesIO(response.content)) as img:
                    img.resize((1035, 1440))
                    img.save(image_path)
            return {'Артикул': code, 'processed': True, 'composition': composition, 'density': density}
        except Exception as e:
            print(code, e, _)
    return {'Артикул': code, 'processed': False, 'composition': composition, 'density': density}


def process_range_df(df):
    size_regex = '[0-9]{1,}[x,X,х,Х][0-9]{1,}'
    x_regex = '[x,х]'
    df['Размер'] = df['Номенклатура'].apply(
        lambda nomen: re.sub(x_regex, 'x', re.search(size_regex, nomen).group().lower()))
    df['Номенклатура'] = df.apply(lambda row: re.sub(size_regex, row['Размер'], row['Номенклатура']), axis=1)
    df['Модель'] = df.apply(lambda row: row['Номенклатура'].split(row['Размер'])[1].strip(), axis=1)
    processed_result = df.groupby(by=['Артикул'])[['Штрихкод', 'Цвет', 'Артикул', 'Ссылка']].apply(
        lambda g: download_pictures(g['Артикул'].to_list()[0], g['Ссылка'].to_list()[0],
                                    dict(zip(g['Цвет'], g['Штрихкод'])))).to_dict()
    processed_result = pd.DataFrame(list(processed_result.values()))
    processed_df = df.merge(pd.DataFrame(processed_result), on='Артикул').drop(columns=['processed_x']).rename(
        columns={'processed_y': 'processed'})
    processed_df = processed_df[processed_df['processed'] == True]
    return processed_df


def prepare_dataframe(df):
    valid_range = get_valid_product_range(df, 'TR1002181', 'TR1002479')
    valid_range_df = df[valid_range.start:valid_range.stop]
    merged_df = valid_range_df[valid_range_df['Штрихкод'].notna()].merge(
        valid_range_df[valid_range_df['Штрихкод'].isna()], on='Артикул', how='left')
    merged_df = merged_df[["Артикул", "Номенклатура_x", "Ссылка_y", "Штрихкод_x", "Номенклатура_y"]].rename(
        columns={"Номенклатура_x": 'Цвет', 'Ссылка_y': 'Ссылка', "Номенклатура_y": 'Номенклатура',
                 'Штрихкод_x': 'Штрихкод'})
    merged_df['processed'] = False
    merged_df['Цвет'] = merged_df['Цвет'].apply(lambda color: colors[color])
    merged_df.dropna(subset=['Ссылка'], inplace=True)
    return merged_df


def get_description(nomen, density, lang='RUS'):
    if "Жаккард" in nomen:
        if lang == 'RUS':
            text = f'Жаккардовое плотное полотенце плотностью {density} гр м2'
        else:
            text = f'Жакардовий щільний рушник. Щільність {density} гр м2'
    elif 'Коттон' in nomen:
        if lang == 'RUS':
            text = f'Натуральное хлопковое полотенце плотностью {density} гр м2'
        else:
            text = f'Натуральний бавовняний рушник щільністю {density} гр м2'
    else:
        if lang == 'RUS':
            text = f'Полотенце для ежедневного ипользования. Быстро сохнет, так как имеет среднюю плотность - {density} гр м2'
        else:
            text = f'Рушник для щоденного використання. Швидко сохне. Щільність {density} гр м2'
    return text


def final_df_process(df):
    df['Артикул'] = df['Штрихкод']
    df['Принадлежность*'] = 'дом:полотенце'
    df['Аудитория*:9'] = 'Унисекс'
    df['Возвратность*:12'] = 'Невозвратный'
    df['Группа*:13*'] = 'Текстиль'
    df['Группы совместимости*:17'] = '5. Прочее с объемом более 0,2 л'
    df['Подгруппа*:14'] = 'Полотенца'
    df['Принадлежность*:6'] = 'Дом'
    df['Страна производства*:1'] = 'Турция'
    df['Сток*'] = 1
    df['Узор:18'] = 'Однотонный'
    df['composition'] = df['composition'].apply(str.lower)
    df['composition'] = df['composition'].str.replace(' % ', '% ')

    df.rename(columns={'Номенклатура': 'Название', 'composition': 'Состав (рус)'}, inplace=True)
    df['Бренд'] = 'Arya'
    df['Цвет'] = df['Цвет'].apply(lambda color: transform_colors[color])
    df['Вес с упаковкой*:19'] = df['Размер'].apply(lambda size: sizes[size]['weight'])
    df['Габариты (ВхШхГ), см(строка):201'] = df['Размер'].apply(lambda size: sizes[size]['gab'])
    df['Название (рус)*'] = df['Модель'] + ' ' + df['Размер'].apply(lambda size: sizes[size]['RUS']) + ', ' + df[
        'Размер'] + 'см'
    df['Назва (укр)'] = df['Модель'] + ' ' + df['Размер'].apply(lambda size: sizes[size]['UKR']) + ', ' + df[
        'Размер'] + 'см'
    df['Склад (укр)'] = df['Состав (рус)'].apply(lambda composition: compositions[composition])
    df['Описание (рус)*'] = df.apply(lambda row: get_description(row["Название"], row['density']), axis=1)
    df['Опис (укр)'] = df.apply(lambda row: get_description(row["Название"], row['density'], lang='UKR'), axis=1)
    # df['']
    df['Габариты в упаковке (ВхШхГ), см(строка):202'] = df['Габариты (ВхШхГ), см(строка):201']
    df['Вес в упаковке, кг(число):200'] = df['Вес с упаковкой*:19']
    df['Вес, кг(число):199'] = df['Вес с упаковкой*:19']
    df.drop(columns=['density', 'processed', 'Ссылка'], inplace=True)
    return df



create_folder_by_name(project_title)

arya_price_path = 'арья прайс 24.12.20.xlsx'
arya_price_df = pd.read_excel(arya_price_path)
arya_price_df = prepare_dataframe(arya_price_df)
arya_price_df.to_excel('after_process.xlsx', index=False)

after_process = process_range_df(arya_price_df)
after_process.to_excel('after_process.xlsx', index=False)
after_process = final_df_process(after_process)
after_process.to_excel('arya_result.xlsx')
print('b')
