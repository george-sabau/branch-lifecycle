import json
from datetime import datetime, timedelta

def serialize_results(results, filename='results.json'):
    def converter(o):
        if isinstance(o, datetime):
            return o.isoformat()
        if isinstance(o, timedelta):
            return o.total_seconds()
        raise TypeError(f"Type {type(o)} not serializable")

    with open(filename, 'w') as f:
        json.dump(results, f, default=converter, indent=2)

def deserialize_results(filename='results.json'):
    try:
        with open(filename, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"❌ No cache file found: {filename}")
        raise  # force recomputation
    except json.JSONDecodeError:
        print(f"⚠️ Could not decode JSON from: {filename}")
        return []

    if not data:
        print(f"⚠️ No data in results file: {filename}")
        return []

    results = []
    for item in data:
        try:
            created_at = datetime.fromisoformat(item['created_at'])
            merged_at = datetime.fromisoformat(item['merged_at'])

            duration_seconds = item['duration_seconds']
            duration = timedelta(seconds=duration_seconds)

            days = duration.days
            hours, remainder = divmod(duration.seconds, 3600)
            minutes, _ = divmod(remainder, 60)

            results.append({
                'branch': item['branch'],
                'created_at': created_at,
                'merged_at': merged_at,
                'duration_days': days,
                'duration_hours': hours,
                'duration_minutes': minutes,
                'duration_seconds': duration_seconds,
                'duration': duration
            })
        except Exception as e:
            print(f"❌ Error parsing item: {item}\n{e}")

    return results  # <- MAKE SURE this always happens

