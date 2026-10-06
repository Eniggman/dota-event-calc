---
name: dota-event-calc
description: "Calculate whether Ranked All Pick or Turbo earns more Dota 2 Dark Carnival (Clownfall) event tickets per real-time minute for a specific player, using their own match history from OpenDota (ranked) and STRATZ GraphQL (ranked + Turbo, needs a free API token). Outputs winrate, average match length, tickets per minute/hour, Turbo breakeven winrate and a verdict. Use when a Dota 2 player asks where to farm event tickets faster. Triggers: «где выгоднее фармить билеты», «рейтинг или турбо», «билеты ивента Dota 2», «Dark Carnival», «Clownfall», «калькулятор ивента дота», «turbo vs ranked tickets»."
---

# Калькулятор ивента Dota 2 Dark Carnival (Clownfall): Рейтинг или Турбо

Инструкция для ИИ-агента. Для людей: [README](https://github.com/Eniggman/dota-event-calc#readme). Весь код — один файл `dota_event_calc.py` (только стандартная библиотека Python).

## Правила начисления (зашиты в скрипт)

| Режим | Победа | Поражение |
|---|---|---|
| Рейтинг (All Pick, `game_mode=22`, `lobby_type=7`) | +3 | +1 |
| Турбо (`game_mode=23`) | +2 | 0 |

Формула: `билеты/мин = (WR×за_победу + (1−WR)×за_поражение) / средняя_длина_матча_мин`.
Порог Турбо: `WR_турбо > билеты_мин_рейтинг × длина_турбо / 2`.
Если правила ивента изменились, скажи человеку, что цифры в скрипте захардкожены (функция `fmt_post`), и не подменяй их молча.

## Шаг 0. Окружение

```bash
python3 --version     # 3.x, внешних пакетов не нужно
git clone https://github.com/Eniggman/dota-event-calc && cd dota-event-calc
```
Нужен интернет: `api.opendota.com` и `api.stratz.com`.

## Шаг 1. Получить данные от человека

1. **Steam Account ID, числовой 32-битный** (Friend ID, как в ссылке OpenDota/Dotabuff: `opendota.com/players/<ID>`). Если человек дал SteamID64 (`7656119…`), вычисли `ID = SteamID64 − 76561197960265728`.
2. **Токен STRATZ** (бесплатно на https://stratz.com). **Без токена Турбо не считается вообще** (см. ниже), поэтому для честного сравнения он нужен.
   - Токен — секрет. Попроси человека положить его в переменную окружения, например `STRATZ_TOKEN`, а не писать в чат. Не печатай токен в ответах и логах.
3. История матчей должна быть публичной (в настройках клиента Dota 2 опция Expose Public Match Data), иначе API вернут пустые данные.

## Шаг 2. Запуск

```bash
python3 dota_event_calc.py <steam_account_id> --stratz-token "$STRATZ_TOKEN"
# Windows PowerShell:
python dota_event_calc.py <steam_account_id> --stratz-token $env:STRATZ_TOKEN
```
- В stderr пишутся `Fetching data...` и ошибки API. Отчёт печатается в stdout.
- Период — последние 365 дней. OpenDota берёт до 1000 рейтинговых матчей, STRATZ листается страницами по 100.

## Шаг 3. Как читать и пересказывать результат

Блоки отчёта: РЕЙТИНГ (OpenDota и/или STRATZ), ТУРБО (только STRATZ), СРАВНЕНИЕ, РАСЧЁТ, ПОРОГ ОКУПАЕМОСТИ ТУРБО, ВЕРДИКТ.
- Для рейтинга скрипт берёт данные STRATZ, если они есть, иначе OpenDota.
- Перескажи человеку: билеты/час в обоих режимах, разницу в процентах, порог WR для Турбо и его текущий WR в Турбо.
- Добавь оговорку: расчёт по прошлой статистике, в нём не учитываются поиск игры, пики и время между матчами.

**Обязательная проверка перед вердиктом:** если в блоке ТУРБО стоит `Побед: 0 | Поражений: 0`, а длина `0.0 мин` (нет токена, ошибка STRATZ или человек не играл в Турбо), то строки «Рейтинг выгоднее на 0%», «Турбо станет выгоднее только при WR > 0%» и «ВЕРДИКТ» **бессмысленны**: так скрипт ведёт себя при пустых данных, это проверено. Не пересказывай этот вердикт. Скажи, что данных по Турбо нет, и назови только билеты/час в рейтинге.

## Проверка успеха

- Код выхода 0, в stdout есть блок `🔥 ВЕРДИКТ`.
- В обоих режимах число матчей больше нуля и средняя длина больше нуля.
- Если матчей мало (меньше ~20 в режиме), предупреди, что WR статистически ненадёжен.

## Частые ошибки

| Симптом | Причина и решение |
|---|---|
| `No data received from any API. Check account ID and try again.` (exit 1) | Неверный ID (например, дан SteamID64), профиль скрыт или за 365 дней нет рейтинговых игр и нет токена STRATZ |
| `OpenDota error: HTTP Error 429` | Лимит запросов OpenDota: подожди минуту и повтори |
| `STRATZ ranked/turbo error: HTTP Error 401/403` | Токен неверный или истёк: попроси человека выпустить новый |
| Турбо = 0 при наличии токена | Нет Турбо-матчей за год или ошибка STRATZ (смотри stderr) |
| `error: argument account_id: invalid int value` | Передан не числовой ID (ник или ссылка): попроси числовой ID |
