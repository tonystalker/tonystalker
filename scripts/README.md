# Setup

1. Put a photo of yourself as `source-photo.jpg` in this folder, then:
   ```
   pip install -r scripts/requirements.txt
   python scripts/prep_photo.py source-photo.jpg
   python scripts/make_ascii_svg.py
   ```
2. Edit the `ROWS` list in `scripts/make_info_card.py` if you want to change
   what the neofetch card says, then:
   ```
   python scripts/make_info_card.py
   ```
3. Commit and push the updated files to your profile repository.
