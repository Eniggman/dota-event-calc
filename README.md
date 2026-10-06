v1.0 [20.09.26]

# Калькулятор эффективности ивента Dota 2 Dark Carnival (Clownfall)

> 💡 **Примечание для ИИ-разработчиков и пользователей:** Этот репозиторий оформлен как готовый навык (skill). Вы можете загрузить его содержимое или просто скопировать этот файл и передать любому ИИ-агенту (AI Agent), чтобы он мгновенно научился рассчитывать оптимальный игровой режим для вас или ваших пользователей.

Рассчитывает, в каком игровом режиме выгоднее фармить билеты ивента — в Рейтинге (All Pick) или в Турбо — на основе вашей личной игровой статистики.

Программа использует реальные данные игрока из **OpenDota API** и **STRATZ API** для расчёта средней продолжительности матчей и винрейта в обоих режимах, помогая максимизировать получение билетов в минуту реального времени.

## Правила начисления билетов (Dark Carnival / Clownfall)

| Игровой режим | Билеты за победу | Билеты за поражение |
| :--- | :--- | :--- |
| **Рейтинг (All Pick)** | +3 билета | +1 билет |
| **Турбо** | +2 билета | 0 билетов |

## Возможности

- **Интеграция с OpenDota**: Получение данных о рейтинговых матчах за последний год (не требует авторизации).
- **Интеграция с STRATZ GraphQL API**: Получение детальной статистики по Турбо и Рейтингу. Настоятельно рекомендуется использовать STRATZ API токен для получения точных данных по Турбо-матчам.
- **Расчет и Вердикт**: Показывает точное количество билетов в минуту и в час для каждого режима, а также выносит математически обоснованный вердикт.
- **Порог окупаемости Турбо**: Рассчитывает точный винрейт, который вам необходим в Турбо, чтобы этот режим стал выгоднее Рейтинга.

## Требования

- Python 3.x
- Подключение к интернету (для запросов к API OpenDota и STRATZ)
- (Желательно) API-токен STRATZ. Его можно бесплатно получить на сайте [stratz.com](https://stratz.com).

## Использование

Клонируйте репозиторий и запустите скрипт, указав ваш Steam Account ID (числовой):

```bash
python3 dota_event_calc.py <steam_account_id> [--stratz-token ВАШ_ТОКЕН_STRATZ]
```

### Пример запуска

```bash
python3 dota_event_calc.py 123456789 --stratz-token eyJhbGciOi...
```

### Пример вывода программы

```text
📊 ГДЕ ВЫГОДНЕЕ ФАРМИТЬ БИЛЕТЫ?
🏆 Ивент Dark Carnival (Clownfall) — Рейтинг vs Турбо

━━━━━━━━━━━━━━━━━━━━━━

🔴 РЕЙТИНГ (All Pick)
──────── STRATZ ──────────
Побед: 55 | Поражений: 45
Винрейт: 55.0% | Средняя длина: 40.5 мин

💰 +3 билета за победу / +1 за поражение
✅ 0.052 билета/мин — 3.1 билетов/час

━━━━━━━━━━━━━━━━━━━━━━

🟢 ТУРБО
──────── STRATZ ──────────
Побед: 60 | Поражений: 40
Винрейт: 60.0% | Средняя длина: 22.1 мин

💰 +2 билета за победу / +0 за поражение
✅ 0.054 билета/мин — 3.2 билетов/час

━━━━━━━━━━━━━━━━━━━━━━

📈 СРАВНЕНИЕ

Рейтинг: 0.052 билета/мин
Турбо:   0.054 билета/мин

📌 Турбо выгоднее на 4%

━━━━━━━━━━━━━━━━━━━━━━

🧮 РАСЧЁТ
Рейтинг: (0.550×3 + 0.450×1) ÷ 40.5 мин = 0.052
Турбо:   (0.600×2 + 0.400×0) ÷ 22.1 мин = 0.054

━━━━━━━━━━━━━━━━━━━━━━

⚠️ ПОРОГ ОКУПАЕМОСТИ ТУРБО:
Турбо станет выгоднее только при WR > 57%
Сейчас 60.0%

🔥 ВЕРДИКТ: Играй в ТУРБО — на 4% больше билетов!
```

---

## English summary

A Python command-line calculator for the Dota 2 Dark Carnival (Clownfall) event that tells you whether Ranked All Pick or Turbo earns more event tickets per minute of real time. It pulls your own match statistics from the OpenDota API and the STRATZ GraphQL API (a free STRATZ token is recommended), compares win rate and average match length, and prints tickets per minute and per hour, a verdict and the break-even Turbo win rate. Run it with your numeric Steam account ID: `python3 dota_event_calc.py <steam_account_id> [--stratz-token TOKEN]`; you can also hand the repo to an AI agent and let it run the calculation for you. The repo ships an AI agent skill (SKILL.md): copy the repo into your agent's skills directory or give it SKILL.md, then ask where to farm event tickets faster and provide your numeric Steam account ID (with your STRATZ token in an environment variable such as STRATZ_TOKEN).
