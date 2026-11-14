# Данные о мостах Запорожья для дашборда

Этот репозиторий только собирает сообщения о мостах и гребле ДніпроГЕС из публичных
Telegram-каналов (@patrolpolicezp, @zoda_gov_ua) в файл `bridges.json`. Дашборд хранится отдельно.

## Настройка (один раз)
1. Создайте на GitHub **публичный** репозиторий, например `zp-bridges`.
2. Загрузите все файлы, сохранив папки (папка `.github` скрытая — перетащите распакованную папку целиком):
   `bridges.json`, `scripts/fetch_bridges.py`, `.github/workflows/bridges.yml`.
3. Settings → Actions → General → Workflow permissions → **Read and write permissions** → Save.
4. Actions → «Мости — оновлення» → **Run workflow**. Через минуту в `bridges.json` появятся сообщения.

Адрес данных для дашборда:
`https://raw.githubusercontent.com/ЛОГИН/zp-bridges/main/bridges.json`
