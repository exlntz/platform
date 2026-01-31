def calculate_changes(obj, new_data: dict) -> str | None:

    changes = []
    for key, new_value in new_data.items():
        old_value = getattr(obj, key, None)

        if old_value != new_value:
            changes.append(f"{key}: {old_value} -> {new_value}")

    return ", ".join(changes) if changes else None