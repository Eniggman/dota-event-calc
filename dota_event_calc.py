#!/usr/bin/env python3
import json, sys, urllib.request, time, argparse
from datetime import datetime

def fetch(url, headers=None):
    hdrs = {
        "User-Agent": "DotaEventCalc/1.0",
        **(headers or {}),
    }
    req = urllib.request.Request(url, headers=hdrs)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())

def fetch_stratz(token, query):
    req = urllib.request.Request(
        "https://api.stratz.com/graphql",
        data=json.dumps({"query": query}).encode(),
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": "DotaEventCalc/1.0",
        },
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())

def paginate_stratz_matches(token, account_id, game_mode_ids, lobby_type_ids, start_dt):
    all_matches = []
    skip = 0
    while True:
        a = [f"gameModeIds: {json.dumps(game_mode_ids)}"]
        if lobby_type_ids is not None:
            a.append(f"lobbyTypeIds: {json.dumps(lobby_type_ids)}")
        a += [f"startDateTime: {start_dt}", f"skip: {skip}", "take: 100"]
        gql = f"{{ player(steamAccountId: {account_id}) {{ m: matches(request: {{{', '.join(a)}}}) {{ id startDateTime durationSeconds didRadiantWin players {{ steamAccountId isRadiant }} }} }} }}"
        data = fetch_stratz(token, gql)
        batch = data.get("data", {}).get("player", {}).get("m", [])
        if not batch:
            break
        all_matches.extend(batch)
        if len(batch) < 100:
            break
        skip += 100
    return all_matches

def calc_stats(matches, account_id):
    if not matches:
        return {"count": 0, "wins": 0, "avg_dur": 0, "wr": 0}
    durs = [m["durationSeconds"] for m in matches if m.get("durationSeconds")]
    avg_dur = sum(durs) / len(durs) / 60 if durs else 0
    wins = 0
    for m in matches:
        for pl in m.get("players", []):
            if pl.get("steamAccountId") == account_id:
                if pl.get("isRadiant") == m.get("didRadiantWin"):
                    wins += 1
                break
    return {"count": len(matches), "wins": wins, "avg_dur": avg_dur, "wr": wins / len(matches) * 100}

def tickets_per_min(wr, avg_dur, tickets_win, tickets_loss):
    tpm = (wr / 100 * tickets_win + (1 - wr / 100) * tickets_loss)
    return tpm / avg_dur if avg_dur > 0 else 0

def fmt_post(od_ranked, st_ranked, st_turbo, has_stratz):
    lines = []
    lines.append("📊 ГДЕ ВЫГОДНЕЕ ФАРМИТЬ БИЛЕТЫ?")
    lines.append("🏆 Ивент Dark Carnival (Clownfall) — Рейтинг vs Турбо")
    lines.append("")
    lines.append("━━━━━━━━━━━━━━━━━━━━━━")
    lines.append("")

    lines.append("🔴 РЕЙТИНГ (All Pick)")
    if od_ranked["count"]:
        lines.append("──────── OpenDota ────────")
        lines.append(f"Побед: {od_ranked['wins']} | Поражений: {od_ranked['count'] - od_ranked['wins']}")
        lines.append(f"Винрейт: {od_ranked['wr']:.1f}% | Средняя длина: {od_ranked['avg_dur']:.1f} мин")

    if st_ranked["count"]:
        lines.append("──────── STRATZ ──────────")
        lines.append(f"Побед: {st_ranked['wins']} | Поражений: {st_ranked['count'] - st_ranked['wins']}")
        lines.append(f"Винрейт: {st_ranked['wr']:.1f}% | Средняя длина: {st_ranked['avg_dur']:.1f} мин")

    r_tpm = tickets_per_min(st_ranked["wr"] if st_ranked["count"] else od_ranked["wr"], st_ranked["avg_dur"] if st_ranked["count"] else od_ranked["avg_dur"], 3, 1)
    r_tpm_total = r_tpm * 60
    lines.append("")
    lines.append("💰 +3 билета за победу / +1 за поражение")
    lines.append(f"✅ {r_tpm:.3f} билета/мин — {r_tpm_total:.1f} билетов/час")
    lines.append("")
    lines.append("━━━━━━━━━━━━━━━━━━━━━━")
    lines.append("")

    lines.append("🟢 ТУРБО")
    src = st_turbo
    lines.append("──────── STRATZ ──────────")
    lines.append(f"Побед: {src['wins']} | Поражений: {src['count'] - src['wins']}")
    lines.append(f"Винрейт: {src['wr']:.1f}% | Средняя длина: {src['avg_dur']:.1f} мин")
    t_tpm = tickets_per_min(src["wr"], src["avg_dur"], 2, 0)
    t_tpm_total = t_tpm * 60
    lines.append("")
    lines.append("💰 +2 билета за победу / +0 за поражение")
    lines.append(f"✅ {t_tpm:.3f} билета/мин — {t_tpm_total:.1f} билетов/час")
    lines.append("")
    lines.append("━━━━━━━━━━━━━━━━━━━━━━")
    lines.append("")

    lines.append("📈 СРАВНЕНИЕ")
    lines.append("")
    lines.append(f"Рейтинг: {r_tpm:.3f} билета/мин")
    lines.append(f"Турбо:   {t_tpm:.3f} билета/мин")
    lines.append("")
    diff = (r_tpm / t_tpm - 1) * 100 if t_tpm > 0 else 0
    best, best_name = ("РЕЙТИНГ", "Рейтинг") if r_tpm > t_tpm else ("ТУРБО", "Турбо")
    lines.append(f"📌 {best_name} выгоднее на {abs(diff):.0f}%")
    lines.append("")
    lines.append("━━━━━━━━━━━━━━━━━━━━━━")
    lines.append("")

    lines.append("🧮 РАСЧЁТ")
    w_r = st_ranked["wr"] / 100 if st_ranked["count"] else od_ranked["wr"] / 100
    d_r = st_ranked["avg_dur"] if st_ranked["count"] else od_ranked["avg_dur"]
    w_t = src["wr"] / 100
    d_t = src["avg_dur"]
    lines.append(f"Рейтинг: ({w_r:.3f}×3 + {1-w_r:.3f}×1) ÷ {d_r:.1f} мин = {r_tpm:.3f}")
    lines.append(f"Турбо:   ({w_t:.3f}×2 + {1-w_t:.3f}×0) ÷ {d_t:.1f} мин = {t_tpm:.3f}")
    lines.append("")
    lines.append("━━━━━━━━━━━━━━━━━━━━━━")
    lines.append("")

    breakeven = r_tpm * d_t / 2 * 100
    lines.append(f"⚠️ ПОРОГ ОКУПАЕМОСТИ ТУРБО:")
    lines.append(f"Турбо станет выгоднее только при WR > {breakeven:.0f}%")
    if src["wr"] < breakeven:
        lines.append(f"Сейчас {src['wr']:.1f}% — нужно поднять на +{breakeven - src['wr']:.0f}%")
    lines.append("")
    lines.append(f"🔥 ВЕРДИКТ: Играй в {best} — на {abs(diff):.0f}% больше билетов!")

    return "\n".join(lines)

def main():
    parser = argparse.ArgumentParser(description="Dota 2 Dark Carnival (Clownfall) event efficiency calculator")
    parser.add_argument("account_id", type=int, help="Steam account ID (numeric)")
    parser.add_argument("--stratz-token", help="STRATZ API bearer token")
    args = parser.parse_args()

    aid = args.account_id
    now_ts = int(time.time())
    year_ago = now_ts - 365 * 86400

    print("Fetching data...", file=sys.stderr)

    od_ranked = {"count": 0, "wins": 0, "avg_dur": 0, "wr": 0}
    st_ranked = {"count": 0, "wins": 0, "avg_dur": 0, "wr": 0}
    st_turbo = {"count": 0, "wins": 0, "avg_dur": 0, "wr": 0}

    # OpenDota: ranked
    try:
        url = f"https://api.opendota.com/api/players/{aid}/matches?game_mode=22&lobby_type=7&date=365&limit=1000"
        data = fetch(url)
        if isinstance(data, list):
            durs = [m["duration"] for m in data if m.get("duration")]
            wins = sum(1 for m in data if m.get("radiant_win") == (m.get("player_slot") < 128))
            od_ranked = {
                "count": len(data),
                "wins": wins,
                "avg_dur": sum(durs) / len(durs) / 60 if durs else 0,
                "wr": wins / len(data) * 100 if data else 0,
            }
    except Exception as e:
        print(f"OpenDota error: {e}", file=sys.stderr)

    if args.stratz_token:
        try:
            st_ranked_m = paginate_stratz_matches(args.stratz_token, aid, [22], [7], year_ago)
            st_ranked = calc_stats(st_ranked_m, aid)
        except Exception as e:
            print(f"STRATZ ranked error: {e}", file=sys.stderr)

        try:
            st_turbo_m = paginate_stratz_matches(args.stratz_token, aid, [23], None, year_ago)
            st_turbo = calc_stats(st_turbo_m, aid)
        except Exception as e:
            print(f"STRATZ turbo error: {e}", file=sys.stderr)

    if not od_ranked["count"] and not st_ranked["count"] and not st_turbo["count"]:
        print("No data received from any API. Check account ID and try again.")
        sys.exit(1)

    result = fmt_post(od_ranked, st_ranked, st_turbo, bool(args.stratz_token))
    print("\n" + result)

if __name__ == "__main__":
    main()
