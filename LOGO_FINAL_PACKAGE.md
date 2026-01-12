# PrimeHaul OS - Final Logo Package

## Selected Logo: Concept 1 (Speed Arrow + Box)

**Design Rationale:**
- Immediately communicates speed and efficiency
- Box element clearly relates to moving/removals
- Modern, tech-forward aesthetic
- Scalable from favicon to billboard
- Works in single color for dark backgrounds
- Professional yet approachable

---

## Logo Files

All logo files are located in `/app/static/`:

### Primary Logos

1. **`logo.svg`** - Full color logo (200×200px)
   - Use: Primary logo, general use
   - Colors: Prime Green gradient (#2EE59D to #34C759)

2. **`logo-icon.svg`** - Icon only version (100×100px)
   - Use: Favicons, app icons, social media profiles
   - Colors: Prime Green gradient

3. **`logo-wordmark.svg`** - Full logo with wordmark (400×120px)
   - Use: Website headers, business cards, marketing materials
   - Includes: Icon + "PrimeHaul OS" text

### Variations

4. **`logo-monochrome.svg`** - Single color version
   - Use: Single-color printing, embroidery, dark backgrounds
   - Color: Deep Charcoal (#1A1A1C)

5. **`logo-white.svg`** - White version
   - Use: Dark backgrounds, reversed applications
   - Color: White (#FFFFFF)

6. **`favicon.svg`** - Simplified favicon version (32×32px)
   - Use: Browser favicon, small icons
   - Optimized for small sizes

---

## Usage Guidelines

### Minimum Sizes

- **Full Logo:** 120px width minimum
- **Icon Only:** 32px × 32px minimum
- **Wordmark:** 100px width minimum

### Clear Space

- Maintain clear space equal to **2x the logo height** on all sides
- Never place logo closer than this distance to other elements

### Color Applications

**Light Backgrounds:**
- Use: `logo.svg` or `logo-wordmark.svg`
- Logo appears in Prime Green
- Text appears in Deep Charcoal (#1A1A1C)

**Dark Backgrounds:**
- Use: `logo-white.svg` or white version of wordmark
- Logo appears in White
- Text appears in White or Light Gray (#F5F5F7)

**Single Color Printing:**
- Use: `logo-monochrome.svg`
- Appears in Deep Charcoal or Black

### Do's and Don'ts

**DO:**
✓ Maintain aspect ratio
✓ Use high-resolution versions
✓ Maintain clear space
✓ Use approved colors only
✓ Scale proportionally

**DON'T:**
✗ Stretch or distort logo
✗ Rotate logo
✗ Change colors
✗ Add effects (shadows, gradients) without approval
✗ Place on busy backgrounds without clear space
✗ Use below minimum sizes

---

## Implementation Examples

### Website Header
```html
<img src="/static/logo-wordmark.svg" alt="PrimeHaul OS" style="height: 40px;">
```

### Favicon
```html
<link rel="icon" type="image/svg+xml" href="/static/favicon.svg">
```

### App Icon
- Use `logo-icon.svg` at 1024×1024px for iOS
- Use `logo-icon.svg` at 512×512px for Android

### Business Card
- Use `logo-wordmark.svg` at 60mm width
- Position: Top left or center

### Email Signature
- Use `logo-wordmark.svg` at 180px width
- Position: Left side

### Social Media
- Profile Picture: Use `logo-icon.svg` (square crop)
- Cover Image: Use `logo-wordmark.svg` (horizontal)

---

## Brand Colors Reference

- **Prime Green:** #2EE59D (Primary brand color)
- **Deep Charcoal:** #1A1A1C (Text, monochrome)
- **Light Gray:** #F5F5F7 (Backgrounds)
- **White:** #FFFFFF (Reversed logos)

---

## File Formats

All logos are provided as **SVG** (Scalable Vector Graphics):
- Scalable to any size without quality loss
- Small file sizes
- Works in all modern browsers
- Can be converted to PNG, PDF, or other formats as needed

### Converting to Other Formats

**PNG (for web):**
```bash
# Using ImageMagick or similar tool
convert logo.svg -resize 512x512 logo.png
```

**PDF (for print):**
```bash
# Using Inkscape or similar tool
inkscape logo.svg --export-pdf=logo.pdf
```

---

## Logo Variations Summary

| File | Use Case | Size | Colors |
|------|----------|------|--------|
| `logo.svg` | General use | 200×200 | Prime Green |
| `logo-icon.svg` | Icons, favicons | 100×100 | Prime Green |
| `logo-wordmark.svg` | Headers, marketing | 400×120 | Prime Green + Text |
| `logo-monochrome.svg` | Single color | 200×200 | Deep Charcoal |
| `logo-white.svg` | Dark backgrounds | 200×200 | White |
| `favicon.svg` | Browser favicon | 32×32 | Prime Green |

---

## Next Steps

1. ✅ Logo selected and finalized
2. ✅ All variations created
3. ⏳ Implement in website templates
4. ⏳ Update favicon in HTML
5. ⏳ Create app icons (iOS/Android)
6. ⏳ Update social media profiles
7. ⏳ Add to email signatures
8. ⏳ Create business card design

---

*PrimeHaul OS Logo Package v1.0*  
*Final Logo: Concept 1 - Speed Arrow + Box*
