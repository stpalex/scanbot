
#НЕОБХОДИМЫЕ БИБИЛИОТЕКИ
#!pip install PyPDF2
#!pip install pytesseract
#!apt install tesseract-ocr
#!apt install tesseract-ocr-rus
#!pip install  pdf2image
#!apt-get install poppler-utils
#!pip install  telebot
!pip install PyPDF2
!pip install pytesseract
!apt install tesseract-ocr
!apt install tesseract-ocr-rus
!pip install  pdf2image
!apt-get install poppler-utils
!pip install  telebot
import os
import re
import pytesseract
from PyPDF2 import PdfReader, PdfWriter
from pdf2image import convert_from_path
from PIL import Image
from IPython.display import display
import telebot



folder_path = 'output'

# Проверяем, существует ли папка, если нет, то создаем её
if not os.path.exists(folder_path):
    os.makedirs(folder_path)
    #print("Папка 'output' успешно создана!")
else:
    print("Папка 'output' уже существует.")

bot = telebot.TeleBot("622034566:AAHE5mrR9Rpu1p4daxp1-4desy7iaf9W_k8")
#@bot.message_handler(commands=['start'])
#def start_message(message):
#    bot.send_message(message.chat.id, 'Привет, я бот!')

@bot.message_handler(content_types=['document'])
def handle_document(message):
    # Проверяем, что сообщение содержит документ типа PDF
    if message.document.mime_type == 'application/pdf':
        # Скачиваем PDF-файл
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        # Сохраняем PDF-файл на сервере
        with open("downloaded_pdf.pdf", 'wb') as new_file:
            new_file.write(downloaded_file)
        # Отправляем сообщение о успешном сохранении
        bot.send_message(message.chat.id, "PDF-файл успешно получен.")
        clear_directory(directory_to_clear)
        main("/content/downloaded_pdf.pdf")
        files = os.listdir('/content/output')
         # Отправляем каждый файл пользователю
        for file in files:
           file_path = os.path.join('/content/output', file)
            # Проверяем, что это файл, а не директория
           if os.path.isfile(file_path):
              with open(file_path, 'rb') as f:
                bot.send_document(message.chat.id, f)
    else:
        # Отправляем сообщение об ошибке, если полученный документ не является PDF
        bot.send_message(message.chat.id, "Пожалуйста, отправьте PDF-файл.")


def clear_directory(directory):
    # Получаем список файлов в каталоге
    files = os.listdir(directory)
    # Удаляем каждый файл из каталога
    for file in files:
        file_path = os.path.join(directory, file)
        # Проверяем, что это файл, а не директория, и удаляем его
        if os.path.isfile(file_path):
            os.remove(file_path)

# Указываем путь к каталогу, который нужно очистить
directory_to_clear = '/content/output'

# Вызываем функцию для очистки каталога

def extract_identifier(image,image2):
    # Используйте OCR для извлечения текста из изображения

    text = pytesseract.image_to_string(image, lang='rus')
    text2 = pytesseract.image_to_string(image2, lang='rus')
    #print(text)
    #print(text2)
    # Найдите последовательность из 10 цифр в тексте
    # Поиск слова "Акт" и последовательности из 10 цифр в тексте
    match = re.search(r'Акт.*?приема', text)
    if match:
        print (text)
        match = re.search(r'\d+',text)
        return match.group()  # Возвращаем найденную последовательность из 10 цифр
    else:
        match = re.search(r'Акт.*?тправле.', text)
        if match:
            match = re.search(r'\d+',text)
            print (text)
            return match.group()
        else:
             match = re.search(r'ниверсал.*?фактур.', text2)
             if match:
                 match = re.search(r'\d+',text2)
                 print ('УПД_'+ match.group())
                 return ('УПД_'+ match.group())

        #print (text)

        return None

def main(pdf_path):
    # Создайте папку для сохранения страниц с одинаковыми идентификаторами
    os.makedirs("output", exist_ok=True)
    current_identifier = None
    current_output_pdf = None

    # Чтение PDF-файла
    pdf_reader = PdfReader(open(pdf_path, "rb"))
    identifier_pdf_writer_dict = {}
    current_pdf_writers = []
    current_pdf_writer = None
    current_identifier = None

    for page_num in range(len(pdf_reader.pages)):
        # Конвертирование страницы PDF в изображение
        images = convert_from_path(pdf_path, first_page=page_num+1, last_page=page_num+1)
        image = images[0]

        # Обрезка верхних 10% изображения
        width, height = image.size
        cropped_height = int(height * 0.1)
        cropped_image = image.crop((0, int(height * 0.04),  int(width * 0.8), cropped_height))
        cropped_image2 = image.crop((int(width * 0.85), 0,  width,int(height * 0.4)))
        ##cropped_image.save("cropped_image.jpg")

        #Для отладки:
        display(cropped_image)
        #display(cropped_image2)
        # Извлечение идентификатора
        identifier = extract_identifier(cropped_image,cropped_image2)

        if identifier:
            # Если идентификатор найден, создаем новый PdfFileWriter объект и добавляем текущую страницу
            if current_pdf_writer:
                output_pdf_path = f"output/{current_identifier}.pdf"
                with open(output_pdf_path, "wb") as output_pdf:
                    current_pdf_writer.write(output_pdf)

            current_pdf_writer = PdfWriter()
            current_pdf_writer.add_page(pdf_reader.pages[page_num])
            current_identifier = identifier
        else:
            # Если идентификатор не найден, добавляем текущую страницу к текущему PdfFileWriter объекту
            if current_pdf_writer:
                current_pdf_writer.add_page(pdf_reader.pages[page_num])

    # Сохранение последнего PdfFileWriter объекта
    if current_pdf_writer:
        output_pdf_path = f"output/{current_identifier}.pdf"
        with open(output_pdf_path, "wb") as output_pdf:
            current_pdf_writer.write(output_pdf)

bot.polling(none_stop=True, interval=0)






