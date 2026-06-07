from app import create_app

app = create_app()

if __name__ == '__main__':
    from app.config import Config
    app.run(debug=Config.FLASK_DEBUG, host='0.0.0.0', port=5000)
