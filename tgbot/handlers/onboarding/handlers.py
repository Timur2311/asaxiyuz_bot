import datetime

from django.utils import timezone
from telegram import ParseMode, Update, ForceReply
from telegram.ext import CallbackContext

from tgbot.handlers.onboarding import static_text
from tgbot.handlers.utils.info import extract_user_data_from_update
from tgbot.models import User
from tgbot.handlers.onboarding.keyboards import make_keyboard_for_start_command

import requests
from telegram import ParseMode
from bs4 import BeautifulSoup

def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    update.message.reply_text(
        'Salom. Ma\'lumot qidirish uchun quyida qidirayotgan narsangizni yozing!',
        
    )


def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')


def echo(update: Update, context: CallbackContext) -> None:
    URL = "https://asaxiy.uz/product?key="
    URL+=str(update.message.text)
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, 'html.parser')
    item_divs= soup.find_all('div', class_="product__item d-flex flex-column justify-content-between")[:10]
    images = []
    titles =[]
    prices = []
    linkes = []
    
    for item_div in item_divs:
        image = item_div.find("div", class_="product__item-img").img.get('data-src')
        
        if image is not None:
            if ".webp" in image:
                images.append(image[:(len(image)-5)])
            else:
                images.append(image)
                
        else:
            images.append("https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRd-y-IJN8glQlf1qoU01dEgGPUa0d1-sjfWg&usqp=CAU")
        
            
            
        
        product_info =item_div.find("div", class_="product__item-info")
        
        title = product_info.a.h5.text
        titles.append(title)
        if product_info.a['href'] is not None:
            link = product_info.a['href']
            linkes.append("asaxiy.uz"+link)            
        else:
            link = None  
        price = product_info.find("div", class_="product__item-info--prices").find('span',class_="product__item-price").text
        if price is not None:
            prices.append(price)
        else:
            prices.append("Narxi belgilanmagan")
            
            
    print(f"titles======{len(titles)}\n\nprices====={len(prices)}\n\nimages======{len(images)}\n\nlinkes======{len(linkes)}")
    for i in range(10):
        update.message.reply_photo(photo=f"{images[i]}", caption=f"<a href='{linkes[i]}'> {titles[i]} </a> \n\n Price: {prices[i]}", parse_mode=ParseMode.HTML)



def command_start(update: Update, context: CallbackContext) -> None:
    u, created = User.get_user_and_created(update, context)

    if created:
        text = static_text.start_created.format(first_name=u.first_name)
    else:
        text = static_text.start_not_created.format(first_name=u.first_name)

    update.message.reply_text(text=text,
                              reply_markup=make_keyboard_for_start_command())


def secret_level(update: Update, context: CallbackContext) -> None:
    # callback_data: SECRET_LEVEL_BUTTON variable from manage_data.py
    """ Pressed 'secret_level_button_text' after /start command"""
    user_id = extract_user_data_from_update(update)['user_id']
    text = static_text.unlock_secret_room.format(
        user_count=User.objects.count(),
        active_24=User.objects.filter(updated_at__gte=timezone.now() - datetime.timedelta(hours=24)).count()
    )

    context.bot.edit_message_text(
        text=text,
        chat_id=user_id,
        message_id=update.callback_query.message.message_id,
        parse_mode=ParseMode.HTML
    )