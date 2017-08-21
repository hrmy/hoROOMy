# Сайт для проверки HTTP
HTTP_URL = 'http://example.com/'

# Сайт для проверки HTTPS
HTTPS_URL = 'https://google.com/'

# Timeout ожидания ответа через прокси
PROXY_TIMEOUT = 5

# Количество запросов перед сменой прокси
PROXY_REQUESTS = 10

# Количество запросов перед сменой юзер-агента
USER_AGENT_REQUESTS = 5

# Константы для вычисления рейтинга (см. модель Proxy)
PROXY_INITIAL_STABILITY = 100
PROXY_SPEED_RATIO = 1
PROXY_STABILITY_RATIO = 2