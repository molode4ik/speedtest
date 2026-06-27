#!/usr/bin/env python3
import urllib.request
import urllib.error
import time
import sys
import argparse


def format_size(bytes_count: int) -> str:
    for unit in ("Б", "КБ", "МБ", "ГБ"):
        if bytes_count < 1024:
            return f"{bytes_count:.1f} {unit}"
        bytes_count /= 1024
    return f"{bytes_count:.1f} ТБ"


def download_once(url: str, timeout: int = 30) -> tuple[float, int]:
    req = urllib.request.Request(url, headers={"User-Agent": "SpeedTest/1.0"})
    start = time.perf_counter()
    with urllib.request.urlopen(req, timeout=timeout) as response:
        data = response.read()
    elapsed = time.perf_counter() - start
    return elapsed, len(data)


def run_speedtest(url: str, count: int = 10, delay: float = 0.0) -> None:
    times: list[float] = []
    sizes: list[int] = []

    for i in range(1, count + 1):
        try:
            elapsed, size = download_once(url)
            times.append(elapsed)
            sizes.append(size)
            speed_mbps = (size / elapsed) / (1024 * 1024)
            print(f"[{i:>2}/{count}]  {elapsed:6.2f} с  {format_size(size):>10}  {speed_mbps:7.2f} МБ/с")
        except urllib.error.HTTPError as exc:
            retry_after = exc.headers.get("Retry-After")
            if exc.code == 429 and retry_after:
                wait = int(retry_after)
                print(f"[{i:>2}/{count}]  429 — жду {wait} с...")
                time.sleep(wait)
                i -= 1
                continue
            print(f"[{i:>2}/{count}]  ОШИБКА: {exc}")
        except Exception as exc:
            print(f"[{i:>2}/{count}]  ОШИБКА: {exc}")

        if delay and i < count:
            time.sleep(delay)

    if not times:
        print("Все запросы завершились ошибкой.")
        sys.exit(1)

    avg_time  = sum(times) / len(times)
    avg_size  = sum(sizes) / len(sizes)
    avg_speed = (avg_size / avg_time) / (1024 * 1024)
    min_speed = min((s / t) / (1024 * 1024) for s, t in zip(sizes, times))
    max_speed = max((s / t) / (1024 * 1024) for s, t in zip(sizes, times))

    print(f"\nСредняя скорость : {avg_speed:.2f} МБ/с")
    print(f"Минимум          : {min_speed:.2f} МБ/с")
    print(f"Максимум         : {max_speed:.2f} МБ/с")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("url")
    parser.add_argument("--count", "-n", type=int, default=10)
    parser.add_argument("--delay", "-d", type=float, default=0.0)
    args = parser.parse_args()
    run_speedtest(args.url, args.count, args.delay)


if __name__ == "__main__":
    main()