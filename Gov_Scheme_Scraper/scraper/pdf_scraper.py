import io
import re
import requests
import pdfplumber


def scrape_pdf(url):
	"""Download a PDF from `url`, extract text, and return a scheme dict.

	The returned dict follows the same shape as `scraper.html_scraper.scrape_html`.
	"""
	headers = {"User-Agent": "Mozilla/5.0"}
	try:
		resp = requests.get(url, headers=headers, timeout=20)
		resp.raise_for_status()
	except Exception:
		return {
			"title": None,
			"details": None,
			"eligibility": None,
			"benefits": None,
			"exclusion": None,
			"documents_required": None,
			"application_process": None,
			"category": "Government Scheme",
			"state": "Maharashtra",
			"department": None,
			"status": "Unknown",
			"start_date": None,
			"end_date": None,
			"launch_date": None,
			"min_income": None,
			"max_income": None,
			"gender": "All",
			"min_age": None,
			"max_age": None,
			"target_group": "Citizens",
			"last_date_to_apply": None,
			"application_link": url,
		}

	text = ""
	try:
		with pdfplumber.open(io.BytesIO(resp.content)) as pdf:
			pages = []
			for p in pdf.pages:
				try:
					pages.append(p.extract_text() or "")
				except Exception:
					# fallback: try extracting via to_image -> OCR not available here
					pages.append("")
			text = "\n".join(pages)
	except Exception:
		text = ""

	# Normalize whitespace
	text = re.sub(r"\r\n", "\n", text or "")
	lines = [ln.strip() for ln in text.splitlines() if ln.strip()]

	title = lines[0] if lines else None

	# Initialize sections
	details = eligibility = benefits = documents_required = application_process = exclusion = None

	current_section = "details"
	for line in lines:
		lower = line.lower()
		if "eligib" in lower or "who can apply" in lower:
			current_section = "eligibility"
			continue
		if "benefit" in lower or "benefits" in lower:
			current_section = "benefits"
			continue
		if "document" in lower or "required" in lower:
			current_section = "documents_required"
			continue
		if "apply" in lower or "application" in lower or "how to apply" in lower:
			current_section = "application_process"
			continue
		if "exclusion" in lower or "not eligible" in lower:
			current_section = "exclusion"
			continue

		if current_section == "details":
			details = (details or "") + line + "\n"
		elif current_section == "eligibility":
			eligibility = (eligibility or "") + line + "\n"
		elif current_section == "benefits":
			benefits = (benefits or "") + line + "\n"
		elif current_section == "documents_required":
			documents_required = (documents_required or "") + line + "\n"
		elif current_section == "application_process":
			application_process = (application_process or "") + line + "\n"
		elif current_section == "exclusion":
			exclusion = (exclusion or "") + line + "\n"

	text_all = (details or "") + (eligibility or "") + (benefits or "") + (application_process or "")

	# Smart extraction
	min_age = max_age = None
	min_income = max_income = None
	last_date = None

	age_match = re.findall(r"(\d{1,2})\s*-\s*(\d{1,3})\s*years", text_all)
	if age_match:
		min_age, max_age = age_match[0]

	income_match = re.findall(r'₹?\s*(\d+[\,0-9]*)', text_all)
	if income_match:
		min_income = income_match[0]

	date_match = re.search(r"(\d{1,2}/\d{1,2}/\d{4})", text_all)
	if date_match:
		last_date = date_match.group(1)

	status = None
	if re.search(r'\b(active|ongoing|currently implemented)\b', text_all.lower()):
		status = "Active"
	elif re.search(r'\b(closed|discontinued|expired|inactive)\b', text_all.lower()):
		status = "Inactive"
	else:
		status = "Unknown"

	scheme = {
		"title": title,
		"details": details[:3000] if details else None,
		"eligibility": eligibility[:1500] if eligibility else None,
		"benefits": benefits[:1500] if benefits else None,
		"exclusion": exclusion[:1000] if exclusion else None,
		"documents_required": documents_required[:1500] if documents_required else None,
		"application_process": application_process[:1500] if application_process else None,

		"category": "Government Scheme",
		"state": "Maharashtra",
		"department": None,
		"status": status,

		"start_date": None,
		"end_date": None,
		"launch_date": None,

		"min_income": min_income,
		"max_income": max_income,

		"gender": "All",
		"min_age": min_age,
		"max_age": max_age,

		"target_group": "Citizens",
		"last_date_to_apply": last_date,

		"application_link": url
	}

	return scheme

