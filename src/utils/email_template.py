def generateTemplate(username, code):
    return f"""
    <!DOCTYPE html>
    <html lang="en" xmlns="http://www.w3.org/1999/xhtml" xmlns:o="urn:schemas-microsoft-com:office:office">
    <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width,initial-scale=1">
    </head>
    <body style="background-color: #f3f2ef; padding: 25px;">
        <div style="max-width: 500px; margin: 0 auto; padding: 30px 25px; background-color: #16181b; color: #fff; border-radius: 15px;">
            <div>
                <img style="display: block; width: 150px; margin: 0 auto;" src="https://user-images.githubusercontent.com/42102027/177230396-91ded39b-e5fd-4018-bfd0-daae89793655.png" alt="Quoting logo"/>
                <p style="margin-top: 15px; font-size: 1.3rem; text-align: center;">Quoting</p>
            </div>
            <div>
                <p style="text-align: center;">Hello @{username}! Thank you for joining in. To finish your registration, simple inform the code down 
                below in your app. The code will expire in 10 minutes, but you can get another one if necessary by simple logging in with 
                your username and password.</p>
                <p style="text-align: center; padding: 10px 25px; background-color: #2D2F31; border-radius: 15px; font-size: 1.2rem;">{code}</p>
            </div>
        </div>
    </body>
    </html>
    """