from imagekitio import ImageKit
from app.resources.config import IMAGEKIT_PUBLIC_KEY, IMAGEKIT_PRIVATE_KEY, IMAGEKIT_URL_ENDPOINT

imagekit = ImageKit(
	private_key=IMAGEKIT_PRIVATE_KEY, 
	public_key=IMAGEKIT_PUBLIC_KEY, 
	url_endpoint=IMAGEKIT_URL_ENDPOINT,
)

def upload(name: str, file: str):
	upload = imagekit.upload_file(file=file, file_name=name)
	response = upload.response_metadata.raw
	
	if not response:
		return None

	return response.get("url")

def upload_base64_image(*, name: str, base64Str: str):
	try:
		upload_url = upload(name=f"{name}.jpg", file=base64Str)
		return upload_url
	except Exception as e:
		print(f"Error uploading image: {e}")
		return None
