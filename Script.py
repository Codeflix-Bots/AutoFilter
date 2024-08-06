class script(object):

    START_TXT = """
𝐇𝐞𝐲 {},
😎 <b>{}</b>, 𝐘𝐨𝐮𝐫 𝐌𝐨𝐯𝐢𝐞 𝐁𝐮𝐝𝐝𝐲!
🌟 𝐓𝐞𝐥𝐥 𝐦𝐞 𝐲𝐨𝐮𝐫 𝐦𝐨𝐯𝐢𝐞 𝐰𝐢𝐬𝐡,
😋 𝐋𝐞𝐭'𝐬 𝐦𝐚𝐤𝐞 𝐦𝐨𝐯𝐢𝐞 𝐦𝐚𝐠𝐢𝐜!
🔮 𝐏𝐨𝐰𝐞𝐫𝐞𝐝 𝐛𝐲 <a href=https://t.me/Movieflix_Universe>MovieFlix™</a>."""

    STATUS_TXT ="""
Total Files: <code>{}</code>
Total Users: <code>{}</code>"""

    REQ_TEXT  = """
#NewRequest
Bot - {}
Name - {} (<code>{}</code>)
Request - <b>{}</b>"""


    REQM = """**To request for a movie please pass movie details along with** /request **command.**\n**Example**: <code>/request Avengers 2019</code>"""

    REQ_REPLY = """📍 **Your Request for** {} **has been submitted to the admins.**\n\n🚀 **Your Request Will Be Uploaded soon.**\n\n📌 **Please Note that Admins might be busy. So, this may take more time.**"""

    REMADS_TEXT = """<b>Free</b>\nAds & no direct links.\n\n<b>Premium</b>\nDirect files & no creepy ads, faster response time, no waiting time, web download and web streaming. ({})\n\n<b>Plan Cost - \n₹29/Month, ₹149/6M & ₹279/Year </b>\nPrices may increase in the future."""

    CNFRM_TEXT = """ **UPI** -\n     <code>iPrimeHub@axl</code>\n          (tap2copy) \n\n**To Confirm Payment Process, Please Send Your Transaction Screenshot Or Transaction ID To** <a href=https://t.me/lemx4>L E M O N</a>\n\n**Admin delays may occur, request refund if plan activation fails.**"""

    # Refferal text
    REFFERAL_TEXT = """
**Here is your referral link:\n\n{}\n\nShare this link with your 5 friends and get 1 month premium access for free.**
    """

    # Terms & Conditions
    TERMS = """
**By using our service, you agree to the following terms:

1. Our service is provided "as is". We may change or stop providing our service at any time without prior notice.
2. We strive to provide accurate information. However, we cannot guarantee the accuracy or availability of all content.
3. Advertisements displayed are not under our control. Any actions you take based on these advertisements are your responsibility.
4. We collect user IDs to provide updates and keep track of purchases for premium services.
5. We are not responsible for any copyright infringement that may occur. Users are solely responsible for how they use our services.

By using our service, you confirm that you have read, understood, and agreed to these terms.**"""

    # removing blacklisted words
    BLACKLIST = ['tamilblaster', 'filmyzilla', 'streamershub', 'xyz', 'cine', 'www', 'http', 'https',
                'cloudsmoviesstore', 'moviez2you', 'bkp', 'cinema', 'filmy', 'flix', 'cutemoviez',
                '4u', 'hub', 'movies', 'otthd', 'telegram', 'hoichoihok', '@', ']', '[', 'missqueenbotx',
                'filmy', 'films', 'cinema', 'join', 'club', 'apd', 'F-Press', 'GDTOT', 'mkv', 'NETFLIX_OFFICIAL',
                'backup', 'primeroom', 'theprofffesorr', 'premium', 'vip', '4wap', 'toonworld4all', 'mlwbd',
                'Telegram@alpacinodump', 'bollywood', "AllNewEnglishMovie", "7MovieRulz", "1TamilMV",
                'Bazar', '_Corner20', 'CornersOfficial', 'support', 'iMediaShare', 'Uᴘʟᴏᴀᴅᴇᴅ', 'Bʏ', 'PFM', 'alpacinodump'
                ]

    # Ads placement
    ADS_TEXT = """
<b>📢 Ads Placement</b>\nReach a wide audience at a minimal cost with impression-based ads, That means you only pay for the times your ad is actually seen! <a href=https://graph.org/Ads-Placement-Screenshot-12-25-2>Screenshot</a>\n
<b>📌 Price</b>\n₹0.5/impression, ₹500/1k impressions\n
<b>To place your ads contact </b><a href=https://t.me/lemx4>L E M O N</a>
"""