from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.errors import FloodWait
from helper.database import codeflixbots
from config import Txt

# Define the inline keyboard options
ON = [
    [InlineKeyboardButton('• ᴍᴇᴛᴀᴅᴀᴛᴀ ᴏɴ •', callback_data='metadata_1')],
    [InlineKeyboardButton('• sᴇᴛ ᴄᴜsᴛᴏᴍ ᴍᴇᴛᴀᴅᴀᴛᴀ •', callback_data='custom_metadata')]
]

OFF = [
    [InlineKeyboardButton('• ᴍᴇᴛᴀᴅᴀᴛᴀ ᴏғғ •', callback_data='metadata_0')],
    [InlineKeyboardButton('• sᴇᴛ ᴄᴜsᴛᴏᴍ ᴍᴇᴛᴀᴅᴀᴛᴀ •', callback_data='custom_metadata')]
]

@Client.on_message(filters.private & filters.command('metadata'))
async def handle_metadata(client: Client, message: Message):
    try:
        ms = await message.reply_text("**Please Wait...**", reply_to_message_id=message.id)
        bool_metadata = await codeflixbots.get_metadata(message.from_user.id)
        user_metadata = await codeflixbots.get_metadata_code(message.from_user.id)
        await ms.delete()
        
        reply_markup = InlineKeyboardMarkup(ON if bool_metadata else OFF)
        await message.reply_text(
            f"**Your Current Metadata :-**\n\n➜ `{user_metadata}` ",
            quote=True,
            reply_markup=reply_markup
        )
    except Exception as e:
        await message.reply_text(f"An error occurred: {str(e)}")

@Client.on_callback_query(filters.regex('.*?(custom_metadata|metadata).*?'))
async def query_metadata(client: Client, query: CallbackQuery):
    try:
        data = query.data

        if data.startswith('metadata_'):
            bool_meta = data.split('_')[1] == "1"
            user_metadata = await codeflixbots.get_metadata_code(query.from_user.id)
            
            await codeflixbots.set_metadata(query.from_user.id, bool_meta=not bool_meta)
            reply_markup = InlineKeyboardMarkup(ON if not bool_meta else OFF)
            await query.message.edit(
                f"**Your Current Metadata :-**\n\n➜ `{user_metadata}` ",
                reply_markup=reply_markup
            )

        elif data == 'custom_metadata':
            await query.message.edit("**Please send me the new metadata code within 30 seconds.**")
            
            # Function to handle the response
            def check_response(msg):
                return msg.from_user.id == query.from_user.id

            try:
                response = await client.listen(query.message.chat.id, filters=filters.text & filters.create(check_response), timeout=30)
                metadata_code = response.text
                await codeflixbots.set_metadata_code(query.from_user.id, metadata_code=metadata_code)
                await response.reply_text("**Your Metadata Code Set Successfully ✅**", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('• ᴄʟᴏsᴇ •', callback_data='close')]]))
            except FloodWait as e:
                await query.message.reply_text(
                    f"⚠️ Error !!\n\n**You are being rate limited.**\n\nPlease try again later.",
                    reply_to_message_id=query.message.id
                )
            except Exception as e:
                await query.message.reply_text(
                    f"⚠️ Error !!\n\n**An unexpected error occurred.**\n\n{str(e)}",
                    reply_to_message_id=query.message.id
                )
    except Exception as e:
        await query.message.reply_text(f"An error occurred: {str(e)}")
            