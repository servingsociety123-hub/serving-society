#!/usr/bin/env python3
"""
Generate contact section image using fal.ai OmniGen:
- Uploads the Serving Society logo to fal.ai storage
- Asks OmniGen to place the logo on an office wall backdrop in a scene
"""

import json, os, time, subprocess, base64, tempfile

FAL_KEY = "644df6fc-b68f-4f20-acf1-84c585b0bad7:8f70c52537846bf2b3ab9193e7c5404f"
IMG_DIR  = os.path.join(os.path.dirname(os.path.abspath(__file__)), "images")
LOGO_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Logo Serving Society.png")
OUTPUT   = os.path.join(IMG_DIR, "contact-office.png")

def curl(args):
    result = subprocess.run(["curl", "-s"] + args, capture_output=True)
    return result.stdout

# ── Step 1: Upload logo to fal.ai storage ──────────────────────────────────
print("Uploading logo to fal.ai storage...")
upload_resp = curl([
    "-X", "POST",
    "https://fal.run/fal-ai/storage/upload",
    "-H", f"Authorization: Key {FAL_KEY}",
    "-F", f"file=@{LOGO_PATH};type=image/png",
])
try:
    upload_data = json.loads(upload_resp)
    logo_url = upload_data.get("url") or upload_data.get("file_url") or upload_data.get("access_url")
    print(f"Logo uploaded: {logo_url}")
except Exception as e:
    print(f"Upload response: {upload_resp.decode()}")
    logo_url = None

# ── Step 2: Generate image with OmniGen (image+text compositing) ───────────
if logo_url:
    print("Generating with OmniGen (logo compositing)...")
    prompt = (
        "A welcoming modern office reception area for a disability support organisation. "
        "On the back wall behind the reception desk, there is a large backlit frosted glass sign "
        "displaying <img><image 1></img> as the company logo. The reception area has a clean white "
        "and purple colour scheme, indoor plants, comfortable seating. Warm professional lighting. "
        "Photorealistic, 4k, Australian office, welcoming atmosphere."
    )
    payload = json.dumps({
        "model_name": "Shitao/OmniGen-v1",
        "prompt": prompt,
        "input_images": [logo_url],
        "width": 1280,
        "height": 720,
        "num_inference_steps": 50,
        "guidance_scale": 2.5,
        "img_guidance_scale": 1.6,
        "num_images": 1,
        "use_input_image_size_as_output": False,
    })
    resp = curl([
        "-X", "POST",
        "https://queue.fal.run/fal-ai/omnigen-v1",
        "-H", f"Authorization: Key {FAL_KEY}",
        "-H", "Content-Type: application/json",
        "-d", payload,
    ])
else:
    # Fallback: Nano Banana 2 with very descriptive prompt (no logo compositing)
    print("Logo upload failed, falling back to Nano Banana 2...")
    prompt = (
        "A welcoming modern office reception area for 'Serving Society', an Australian NDIS disability support provider. "
        "On the back wall there is a large purple circular logo with a heart symbol and the text 'Serving Society' in purple. "
        "Clean white and deep purple colour scheme, indoor plants, comfortable seating area. "
        "Warm professional lighting, photorealistic, 4k, Australian office, welcoming."
    )
    payload = json.dumps({
        "prompt": prompt,
        "image_size": "landscape_16_9",
        "num_inference_steps": 28,
        "guidance_scale": 3.5,
        "num_images": 1,
        "enable_safety_checker": False,
    })
    resp = curl([
        "-X", "POST",
        "https://queue.fal.run/fal-ai/nano-banana-2",
        "-H", f"Authorization: Key {FAL_KEY}",
        "-H", "Content-Type: application/json",
        "-d", payload,
    ])

try:
    data = json.loads(resp)
    request_id  = data.get("request_id")
    status_url  = data.get("status_url")
    response_url = data.get("response_url")
    print(f"Request ID: {request_id}")
except Exception:
    print("Queue response:", resp.decode())
    exit(1)

# ── Step 3: Poll for completion ────────────────────────────────────────────
print("Polling for result...")
for attempt in range(60):
    time.sleep(5)
    status_resp = curl([
        status_url or f"https://queue.fal.run/fal-ai/omnigen-v1/requests/{request_id}/status",
        "-H", f"Authorization: Key {FAL_KEY}",
    ])
    try:
        s = json.loads(status_resp)
        status = s.get("status", "")
        print(f"  [{attempt+1}] Status: {status}")
        if status == "COMPLETED":
            break
        elif status in ("FAILED", "CANCELLED"):
            print("Generation failed:", s)
            exit(1)
    except Exception:
        print("  Status parse error:", status_resp.decode()[:200])

# ── Step 4: Fetch result ───────────────────────────────────────────────────
result_resp = curl([
    response_url or f"https://queue.fal.run/fal-ai/omnigen-v1/requests/{request_id}",
    "-H", f"Authorization: Key {FAL_KEY}",
])
try:
    result = json.loads(result_resp)
    images = result.get("images") or result.get("output", {}).get("images", [])
    if not images:
        print("No images in response:", result_resp.decode()[:500])
        exit(1)
    img_url = images[0].get("url") or images[0]
    print(f"Image URL: {img_url}")
except Exception:
    print("Result parse error:", result_resp.decode()[:500])
    exit(1)

# ── Step 5: Download image ─────────────────────────────────────────────────
print(f"Downloading to {OUTPUT}...")
curl(["-o", OUTPUT, img_url])
print("Done! contact-office.png saved.")
