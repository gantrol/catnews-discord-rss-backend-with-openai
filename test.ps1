$Env:http_proxy="http://127.0.0.1:7890";$Env:https_proxy="http://127.0.0.1:7890"
$env:TESTING=1
$env:PYTHONPATH += ";."
pytest tests/