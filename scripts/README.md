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
3. Edit `YOUR_USERNAME` in `.github/workflows/update-profile-art.yml`, then
   run once locally to seed the first heatmap:
   ```
   python scripts/fetch_contributions.py YOUR_USERNAME
   python scripts/render_heatmap_svg.py
   ```
4. Push everything to a repo named exactly your GitHub username (public).
   The workflow re-runs the heatmap daily and commits the refreshed SVG.
