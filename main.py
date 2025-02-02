from app.core.factory import AppFactory


app = AppFactory()
app.configure()


if __name__ == '__main__':
    app.run()
