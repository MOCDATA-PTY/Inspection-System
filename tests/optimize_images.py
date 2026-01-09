"""
Optimize background images to reduce file size and improve page load speed
"""
import os
from PIL import Image

print('\n' + '='*80)
print(' OPTIMIZING BACKGROUND IMAGES')
print('='*80)

# Define images to optimize with their target max dimensions
images_to_optimize = {
    'static/img/food_safety_background.png': {
        'max_width': 1920,  # Full HD width is enough for backgrounds
        'quality': 85,  # Good balance between quality and size
        'output': 'static/img/food_safety_background.png'
    },
    'static/img/Pricing Report Page 1.png': {
        'max_width': 1200,  # Smaller for report pages
        'quality': 85,
        'output': 'static/img/Pricing Report Page 1.png'
    }
}

total_saved = 0

for img_path, settings in images_to_optimize.items():
    if not os.path.exists(img_path):
        print(f'\n[SKIP] {img_path} not found')
        continue

    # Get original file size
    original_size = os.path.getsize(img_path)
    print(f'\n[PROCESSING] {img_path}')
    print(f'  Original size: {original_size / 1024:.1f} KB')

    # Create backup
    backup_path = img_path + '.backup'
    if not os.path.exists(backup_path):
        import shutil
        shutil.copy2(img_path, backup_path)
        print(f'  Backup created: {backup_path}')

    # Open and optimize image
    try:
        img = Image.open(img_path)

        # Get original dimensions
        orig_width, orig_height = img.size
        print(f'  Original dimensions: {orig_width}x{orig_height}')

        # Calculate new dimensions maintaining aspect ratio
        max_width = settings['max_width']
        if orig_width > max_width:
            ratio = max_width / orig_width
            new_width = max_width
            new_height = int(orig_height * ratio)
        else:
            new_width = orig_width
            new_height = orig_height

        # Resize if needed
        if new_width != orig_width:
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            print(f'  Resized to: {new_width}x{new_height}')

        # Convert to RGB if necessary (for PNG with transparency)
        if img.mode in ('RGBA', 'LA', 'P'):
            # Create white background
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = background

        # Save optimized image
        img.save(
            settings['output'],
            'JPEG',  # Convert to JPEG for better compression
            quality=settings['quality'],
            optimize=True
        )

        # Update extension to .jpg
        new_path = settings['output'].replace('.png', '.jpg')
        if new_path != settings['output']:
            os.rename(settings['output'], new_path)
            print(f'  Converted to JPEG: {new_path}')
            settings['output'] = new_path

        # Get new file size
        new_size = os.path.getsize(settings['output'])
        saved = original_size - new_size
        saved_percent = (saved / original_size) * 100
        total_saved += saved

        print(f'  New size: {new_size / 1024:.1f} KB')
        print(f'  Saved: {saved / 1024:.1f} KB ({saved_percent:.1f}%)')

    except Exception as e:
        print(f'  [ERROR] Failed to optimize: {e}')
        # Restore from backup if optimization failed
        if os.path.exists(backup_path):
            import shutil
            shutil.copy2(backup_path, img_path)
            print(f'  Restored from backup')

print('\n' + '='*80)
print(f' TOTAL SAVED: {total_saved / 1024:.1f} KB ({total_saved / (1024*1024):.2f} MB)')
print('='*80)

print('\n[IMPORTANT] Next steps:')
print('1. Update template files to use .jpg extension instead of .png')
print('2. Test the pages to ensure backgrounds load correctly')
print('3. Delete .backup files once confirmed working')

print('\n' + '='*80 + '\n')
