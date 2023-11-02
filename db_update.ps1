$env:FLASK_APP = "server"
$env:FLASK_DEBUG = "1"
flask db migrate
flask db upgrade