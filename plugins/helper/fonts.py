from pyrogram import Client, filters
from pyrogram.types import CallbackQuery 
from plugins.helper.aks_font_func import Fonts

@Client.on_message(filters.private & filters.command(["font"]))
async def style_buttons(c, m, cb=False):
    try:
        title = m.text.split(" ", 1)[1]
    except:
        await m.reply_text(text="Ente Any Text Eg:- `/font [text]`")    
        return
    await m.reply_text(f"`{Fonts.typewriter(title)}`")
    await m.reply_text(f"`{Fonts.script(title)}`")
    await m.reply_text(f"`{Fonts.outline(title)}`")
    await m.reply_text(f"`{Fonts.serief(title)}`")
    await m.reply_text(f"`{Fonts.bold_cool(title)}`")
    await m.reply_text(f"`{Fonts.cool(title)}`")
    await m.reply_text(f"`{Fonts.smallcap(title)}`")
    await m.reply_text(f"`{Fonts.script(title)}`")
    await m.reply_text(f"`{Fonts.bold_script(title)}`")
    await m.reply_text(f"`{Fonts.tiny(title)}`")
    await m.reply_text(f"`{Fonts.comic(title)}`")
    await m.reply_text(f"`{Fonts.san(title)}`")
    await m.reply_text(f"`{Fonts.slant_san(title)}`")
    await m.reply_text(f"`{Fonts.slant(title)}`")
    await m.reply_text(f"`{Fonts.sim(title)}`")
    await m.reply_text(f"`{Fonts.circles(title)}`")
    await m.reply_text(f"`{Fonts.dark_circle(title)}`")
    await m.reply_text(f"`{Fonts.gothic(title)}`")
    await m.reply_text(f"`{Fonts.bold_gothic(title)}`")
    await m.reply_text(f"`{Fonts.cloud(title)}`")
    await m.reply_text(f"`{Fonts.happy(title)}`")
    await m.reply_text(f"`{Fonts.sad(title)}`")
    await m.reply_text(f"`{Fonts.special(title)}`")
    await m.reply_text(f"`{Fonts.square(title)}`")
    await m.reply_text(f"`{Fonts.dark_square(title)}`")
    await m.reply_text(f"`{Fonts.andalucia(title)}`")
    await m.reply_text(f"`{Fonts.manga(title)}`")
    await m.reply_text(f"`{Fonts.stinky(title)}`")
    await m.reply_text(f"`{Fonts.bubbles(title)}`")
    await m.reply_text(f"`{Fonts.underline(title)}`")
    await m.reply_text(f"`{Fonts.ladybug(title)}`")
    await m.reply_text(f"`{Fonts.rays(title)}`")
    await m.reply_text(f"`{Fonts.birds(title)}`")
    await m.reply_text(f"`{Fonts.slash(title)}`")
    await m.reply_text(f"`{Fonts.stop(title)}`")
    await m.reply_text(f"`{Fonts.skyline(title)}`")
    await m.reply_text(f"`{Fonts.arrows(title)}`")
    await m.reply_text(f"`{Fonts.rvnes(title)}`")
    await m.reply_text(f"`{Fonts.strike(title)}`")
    await m.reply_text(f"`{Fonts.frozen(title)}`")

@Client.on_callback_query(filters.regex('^style'))
async def style(c, m):
    await m.answer()
    cmd, style = m.data.split('+')

    if style == 'typewriter':
        cls = Fonts.typewriter
    if style == 'outline':
        cls = Fonts.outline
    if style == 'serif':
        cls = Fonts.serief
    if style == 'bold_cool':
        cls = Fonts.bold_cool
    if style == 'cool':
        cls = Fonts.cool
    if style == 'small_cap':
        cls = Fonts.smallcap
    if style == 'script':
        cls = Fonts.script
    if style == 'script_bolt':
        cls = Fonts.bold_script
    if style == 'tiny':
        cls = Fonts.tiny
    if style == 'comic':
        cls = Fonts.comic
    if style == 'sans':
        cls = Fonts.san
    if style == 'slant_sans':
        cls = Fonts.slant_san
    if style == 'slant':
        cls = Fonts.slant
    if style == 'sim':
        cls = Fonts.sim
    if style == 'circles':
        cls = Fonts.circles
    if style == 'circle_dark':
        cls = Fonts.dark_circle
    if style == 'gothic':
        cls = Fonts.gothic
    if style == 'gothic_bolt':
        cls = Fonts.bold_gothic
    if style == 'cloud':
        cls = Fonts.cloud
    if style == 'happy':
        cls = Fonts.happy
    if style == 'sad':
        cls = Fonts.sad
    if style == 'special':
        cls = Fonts.special
    if style == 'squares':
        cls = Fonts.square
    if style == 'squares_bold':
        cls = Fonts.dark_square
    if style == 'andalucia':
        cls = Fonts.andalucia
    if style == 'manga':
        cls = Fonts.manga
    if style == 'stinky':
        cls = Fonts.stinky
    if style == 'bubbles':
        cls = Fonts.bubbles
    if style == 'underline':
        cls = Fonts.underline
    if style == 'ladybug':
        cls = Fonts.ladybug
    if style == 'rays':
        cls = Fonts.rays
    if style == 'birds':
        cls = Fonts.birds
    if style == 'slash':
        cls = Fonts.slash
    if style == 'stop':
        cls = Fonts.stop
    if style == 'skyline':
        cls = Fonts.skyline
    if style == 'arrows':
        cls = Fonts.arrows
    if style == 'qvnes':
        cls = Fonts.rvnes
    if style == 'strike':
        cls = Fonts.strike
    if style == 'frozen':
        cls = Fonts.frozen

    r, oldtxt = m.message.reply_to_message.text.split(None, 1) 
    new_text = cls(oldtxt)            
    try:
        await m.message.edit_text(f"`{new_text}`\n\n👆 Click To Copy", reply_markup=m.message.reply_markup)
    except Exception as e:
        print(e)
