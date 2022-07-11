def generateTemplate(username, code):
    styles = """
        *{
            box-sizing: border-box;
        }
        main{
            width: 80%;
            max-width: 800px;
            margin: 0 auto;
            padding: 10px 25px;
            background-color: #16181b;
            color: #fff;
        }
        p, figcaption{
            text-align: center;
        }
        figure img{
            display: block;
            width: 150px;
            margin: 0 auto;
        }
        figure figcaption{
          margin-top: 15px;
          font-size: 1.3rem;
         }
        .code{
            padding: 10px 20px;
            background-color: #2D2F31;
            border-radius: 15px;
            font-size: 1.2rem;
        }

    """
    return f"""
    <!DOCTYPE html>
    <html lang="en" xmlns="http://www.w3.org/1999/xhtml" xmlns:o="urn:schemas-microsoft-com:office:office">
    <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width,initial-scale=1">
    <style>
        {styles}
    </style>
    </head>
    <body>
        <main>
            <figure>
                <img src="https://user-images.githubusercontent.com/42102027/177230396-91ded39b-e5fd-4018-bfd0-daae89793655.png" alt="Quoting logo"/>
                <figcaption>Quoting</figcaption>
            </figure>
            <section>
                <p>Hello @{username}! Thank you for joining in. To finish your registration, simple inform the code down 
                below in your app. The code will expire in 10 minutes, but you can get another one if necessary by simple logging in with 
                your username and password.</p>
                <p class="code">{code}</p>
            </section>
        </main>
    </body>
    </html>
    """