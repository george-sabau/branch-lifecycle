import numpy as np
from datetime import timedelta

def analyze_and_print_outliers(results, include_outlier_percent=50):
    if not results:
        print("No data to analyze.")
        return []

    durations_hours = [r[1].total_seconds() / 3600 for r in results]
    Q1 = np.percentile(durations_hours, 25)
    Q3 = np.percentile(durations_hours, 75)
    IQR = Q3 - Q1

    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR

    print(f"Q1={Q1:.2f} hours, Q3={Q3:.2f} hours, IQR={IQR:.2f} hours")
    print(f"Lower bound for outliers: {lower_bound:.2f} hours")
    print(f"Upper bound for outliers: {upper_bound:.2f} hours\n")

    sorted_by_duration = sorted(results, key=lambda x: x[1])

    print("Top 100 shortest durations:")
    for name, dur in sorted_by_duration[:100]:
        days, hours, minutes = dur.days, dur.seconds // 3600, (dur.seconds % 3600) // 60
        print(f"- Branch '{name}': {days}d {hours}h {minutes}m")

    print("\nTop 100 longest durations:")
    for name, dur in sorted_by_duration[-100:][::-1]:
        days, hours, minutes = dur.days, dur.seconds // 3600, (dur.seconds % 3600) // 60
        print(f"- Branch '{name}': {days}d {hours}h {minutes}m")

    outliers = [(name, dur) for name, dur in results if dur.total_seconds() / 3600 < lower_bound or dur.total_seconds() / 3600 > upper_bound]

    total_outliers = len(outliers)
    print(f"\nFound {total_outliers} outlier branches")

    num_to_include = int((include_outlier_percent / 100.0) * total_outliers)
    outliers_sorted = sorted(outliers, key=lambda x: x[1].total_seconds(), reverse=True)
    included_outliers = set(outliers_sorted[:num_to_include])

    print(f"Including top {include_outlier_percent}% of outliers: {num_to_include} branches")

    filtered = [
        (name, dur) for (name, dur) in results
        if (lower_bound <= dur.total_seconds() / 3600 <= upper_bound) or (name, dur) in included_outliers
    ]

    if not filtered:
        print("No branches left after filtering to compute average.")
        return []

    total_duration = sum((dur for _, dur in filtered), timedelta())
    avg_duration = total_duration / len(filtered)
    avg_days = avg_duration.days
    avg_hours, remainder = divmod(avg_duration.seconds, 3600)
    avg_minutes, _ = divmod(remainder, 60)

    print(f"\n🎯 Average duration including top {include_outlier_percent}% outliers "
          f"({len(filtered)} branches): {avg_days} days, {avg_hours} hours, {avg_minutes} minutes")

    return filtered