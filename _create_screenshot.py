import base64

png_data = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
)

with open("docs/screenshots/dashboard.png", "wb") as f:
    f.write(png_data)

print(f"Created dashboard.png ({len(png_data)} bytes)")
