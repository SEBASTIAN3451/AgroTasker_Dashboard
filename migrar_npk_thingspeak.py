import argparse
import json
import time
import urllib.parse
import urllib.request

THINGSPEAK_FEEDS_URL = "https://api.thingspeak.com/channels/{channel_id}/feeds.json"
THINGSPEAK_UPDATE_URL = "https://api.thingspeak.com/update"


def to_float(value):
    try:
        if value is None or value == "":
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def fetch_source_feeds(channel_id, read_key=None, results=8000):
    params = {"results": str(results)}
    if read_key:
        params["api_key"] = read_key

    url = THINGSPEAK_FEEDS_URL.format(channel_id=channel_id) + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": "AgroTasker-Migrator"})

    with urllib.request.urlopen(req, timeout=20) as resp:
        payload = json.loads(resp.read().decode("utf-8"))

    return payload.get("feeds", [])


def build_npk_rows(feeds, include_zero=False):
    rows = []
    for f in feeds:
        n = to_float(f.get("field5"))
        p = to_float(f.get("field6"))
        k = to_float(f.get("field7"))

        if n is None and p is None and k is None:
            continue

        if not include_zero and (n or 0) == 0 and (p or 0) == 0 and (k or 0) == 0:
            continue

        rows.append(
            {
                "created_at": f.get("created_at"),
                "field5": 0.0 if n is None else n,
                "field6": 0.0 if p is None else p,
                "field7": 0.0 if k is None else k,
            }
        )

    return rows


def send_to_target(write_key, row, dry_run=False):
    payload = {
        "api_key": write_key,
        "field5": f"{row['field5']:.2f}",
        "field6": f"{row['field6']:.2f}",
        "field7": f"{row['field7']:.2f}",
    }

    if row.get("created_at"):
        payload["created_at"] = row["created_at"]

    if dry_run:
        return True, "dry-run"

    data = urllib.parse.urlencode(payload).encode("utf-8")
    req = urllib.request.Request(THINGSPEAK_UPDATE_URL, data=data, method="POST")

    with urllib.request.urlopen(req, timeout=15) as resp:
        entry_id = resp.read().decode("utf-8").strip()

    if entry_id and entry_id != "0":
        return True, entry_id

    return False, entry_id


def main():
    parser = argparse.ArgumentParser(description="Migrar NPK (field5-7) de ThingSpeak origen a ThingSpeak destino")
    parser.add_argument("--source-channel", required=True, help="ID del canal origen")
    parser.add_argument("--source-read-key", default="", help="Read API key del canal origen (si es privado)")
    parser.add_argument("--target-write-key", required=True, help="Write API key del canal destino")
    parser.add_argument("--results", type=int, default=8000, help="Cantidad de feeds a leer del origen")
    parser.add_argument("--include-zero", action="store_true", help="Incluir filas NPK en cero")
    parser.add_argument("--dry-run", action="store_true", help="No escribe en destino, solo simula")
    parser.add_argument("--interval", type=float, default=16.0, help="Segundos entre updates (min 15s en free)")
    args = parser.parse_args()

    feeds = fetch_source_feeds(args.source_channel, args.source_read_key, args.results)
    rows = build_npk_rows(feeds, include_zero=args.include_zero)

    print(f"Feeds origen: {len(feeds)}")
    print(f"Filas NPK candidatas: {len(rows)}")

    if not rows:
        print("No hay filas NPK utiles para migrar.")
        return

    ok_count = 0
    fail_count = 0

    for idx, row in enumerate(rows, start=1):
        ok, detail = send_to_target(args.target_write_key, row, dry_run=args.dry_run)
        stamp = row.get("created_at") or "sin_created_at"
        if ok:
            ok_count += 1
            print(f"[{idx}/{len(rows)}] OK {stamp} -> {detail}")
        else:
            fail_count += 1
            print(f"[{idx}/{len(rows)}] FAIL {stamp} -> {detail}")

        if not args.dry_run and idx < len(rows):
            time.sleep(max(args.interval, 15.0))

    print("---")
    print(f"Completado. OK={ok_count}, FAIL={fail_count}")


if __name__ == "__main__":
    main()
