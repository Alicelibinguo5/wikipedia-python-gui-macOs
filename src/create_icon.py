from PIL import Image, ImageDraw, ImageFont
import os

def create_wiki_icon():
    # Create a 256x256 image with white background
    img = Image.new('RGBA', (256, 256), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw blue circle background
    draw.ellipse([20, 20, 236, 236], fill='#3498DB')
    
    # Draw white 'W' in the center
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 140)
    except:
        font = ImageFont.load_default()
    
    # Add white 'W'
    draw.text((65, 45), "W", fill='white', font=font)
    
    # Add magnifying glass
    draw.ellipse([140, 140, 180, 180], outline='white', width=8)
    draw.line([170, 170, 200, 200], fill='white', width=8)
    
    # Save the icon
    if not os.path.exists('src'):
        os.makedirs('src')
    img.save('src/wiki_icon.png')

if __name__ == "__main__":
    create_wiki_icon()