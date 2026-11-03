import os
import math
import pandas as pd
import matplotlib.pyplot as plt

DEFAULT_CSV = "hotel_sales.csv"


def load_data(filename):
    """Read the CSV, validate rows, and calculate revenue."""
    if not os.path.isfile(filename):
        print(f"Error: File '{filename}' not found.")
        return None

    try:
        raw = pd.read_csv(filename, dtype=str, encoding="utf-8-sig")
    except (OSError, UnicodeError, pd.errors.ParserError) as exc:
        print(f"Error: Unable to read file: {exc}")
        return None

    raw.columns = raw.columns.str.strip()
    required = ["Date", "RoomType", "RoomsSold", "Rate"]
    missing = [col for col in required if col not in raw.columns]
    if missing:
        print("Error: Missing required columns: " + ", ".join(missing))
        return None

    valid = []
    valid_count = 0

    for row_number, (_, row) in enumerate(raw.iterrows(), start=1):
        date_text = str(row["Date"]).strip()
        room_type = str(row["RoomType"]).strip()
        rooms = pd.to_numeric(row["RoomsSold"], errors="coerce")
        rate = pd.to_numeric(row["Rate"], errors="coerce")

        if (not date_text or date_text.lower() == "nan"
                or not room_type or room_type.lower() == "nan"
                or pd.isna(rooms) or pd.isna(rate)
                or not math.isfinite(float(rooms))
                or not math.isfinite(float(rate))):
            print(f"Warning: Row {row_number} skipped - Missing or non-numeric values.")
            continue

        if rooms < 0:
            print(f"Warning: Row {row_number} skipped - RoomsSold must be 0 or more.")
            continue

        if rate < 0:
            print(f"Warning: Row {row_number} skipped - Rate must be 0 or more.")
            continue

        parsed_date = pd.to_datetime(date_text, errors="coerce")
        if pd.isna(parsed_date):
            print(f"Warning: Row {row_number} skipped - Invalid date.")
            continue

        if float(rooms) != int(rooms) or float(rate) != int(rate):
            print(f"Warning: Row {row_number} skipped - RoomsSold and Rate must be whole numbers.")
            continue

        valid.append({
            "Date": parsed_date.strftime("%Y-%m-%d"),
            "RoomType": room_type,
            "RoomsSold": int(rooms),
            "Rate": int(rate),
            "Revenue": int(rooms) * int(rate),
        })
        valid_count += 1

    print(f"Valid records analysed: {valid_count}")
    return pd.DataFrame(valid, columns=required + ["Revenue"])


def show_daily_revenue(df):
    if df.empty:
        print("No valid data available.")
        return

    daily = df.groupby("Date")["Revenue"].sum().sort_index()
    print("\n--- DAILY REVENUE ---")
    for date, revenue in daily.items():
        print(f"{date} : Rs. {int(revenue)}")

    total = int(df["Revenue"].sum())
    print(f"\nTotal revenue: Rs. {total}")

    best_revenue = daily.max()
    best_days = daily[daily == best_revenue]
    for date, revenue in best_days.items():
        print(f"Best day: {date} (Rs. {int(revenue)})")


def show_room_type_revenue(df):
    if df.empty:
        print("No valid data available.")
        return

    room_revenue = df.groupby("RoomType")["Revenue"].sum().sort_index()
    total = int(df["Revenue"].sum())
    print("\n--- REVENUE BY ROOM TYPE ---")

    for room_type, revenue in room_revenue.items():
        share = (float(revenue) / total * 100) if total else 0.0
        print(f"{room_type} : Rs. {int(revenue)} ({share:.2f}%)")

    print(f"Total revenue: Rs. {total}")


def show_charts(df):
    if df.empty:
        print("No valid data available for charts.")
        return

    daily = df.groupby("Date")["Revenue"].sum().sort_index()
    by_room = df.groupby("RoomType")["Revenue"].sum().sort_index()

    plt.figure(figsize=(9, 5))
    daily.plot(kind="bar")
    plt.title("Hotel Daily Revenue")
    plt.xlabel("Date")
    plt.ylabel("Revenue (Rs.)")
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()

    if by_room.sum() > 0:
        plt.figure(figsize=(7, 7))
        by_room.plot(kind="pie", autopct="%1.2f%%", startangle=90)
        plt.title("Revenue Share by Room Type")
        plt.ylabel("")
        plt.tight_layout()
    else:
        print("No positive room-type revenue available for a pie chart.")

    plt.show()


def main():
    print("=" * 42)
    print("       HOTEL REVENUE ANALYZER")
    print("=" * 42)

    filename = input(f"Enter CSV filename [{DEFAULT_CSV}]: ").strip()
    if not filename:
        filename = DEFAULT_CSV

    df = load_data(filename)
    if df is None:
        return
    if df.empty:
        print("There is no valid data to analyze.")
        return

    while True:
        print("\n========== MAIN MENU ==========")
        print("1. Daily Revenue and Best Day")
        print("2. Revenue by Room Type")
        print("3. Display Charts")
        print("4. Exit")
        choice = input("Enter your choice (1-4): ").strip()

        if choice == "1":
            show_daily_revenue(df)
        elif choice == "2":
            show_room_type_revenue(df)
        elif choice == "3":
            show_charts(df)
        elif choice == "4":
            print("Thank you for using Hotel Revenue Analyzer!")
            break
        else:
            print("Invalid choice. Please enter 1, 2, 3, or 4.")


if __name__ == "__main__":
    main()
