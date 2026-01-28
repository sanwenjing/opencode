---
name: pptx-pro
description: "Professional PowerPoint creation with comprehensive typography and layout standards. Enhanced version with complete design guidelines, typography rules, color theory, layout principles, and accessibility compliance."
license: Proprietary
---

# Professional PowerPoint Presentation Generator with Comprehensive Standards

## Overview

This skill provides professional PowerPoint presentation creation capabilities with comprehensive design standards implementation. It ensures every generated presentation follows industry best practices for typography, layout, color theory, and accessibility.

## Key Features

### 🎨 **Typography Standards**
- **Font Hierarchy**: Clear hierarchy with title (44pt), header (28pt), body (18pt), small (14pt), minimum (12pt)
- **Professional Fonts**: Microsoft YaHei (中文), Arial (英文), Calibri (显示)
- **Text Density**: Maximum 8 lines per slide, 25 Chinese characters or 50 English characters per line
- **Line Spacing**: 1.2x line height, 6-12pt paragraph spacing
- **Content Validation**: Automatic validation and adjustment for readability

### 🎯 **Layout Principles**
- **16:9 Standard**: Modern 1920×1080px or 10×5.625 inches
- **Grid System**: 12-column grid with 0.5-inch safe margins
- **Content Areas**: Structured content zones with proper spacing
- **Two-Column Layout**: 40%/60% split for balanced content presentation
- **Visual Hierarchy**: 60% primary, 30% secondary, 10% decorative elements

### 🌈 **Color Theory & Palettes**
- **Professional Palettes**: Pre-defined color schemes for different contexts
  - **Business**: Deep blue primary, red accent, clean grays
  - **Tech**: Deep purple primary, bright blue accent, modern feel
  - **Academic**: Academic blue primary, orange accent, scholarly look
  - **Finance**: Financial blue primary, gold accent, corporate feel
  - **Healthcare**: Medical blue primary, teal accent, healthcare theme
- **Accessibility Compliance**: WCAG 2.1 AA standards (4.5:1 contrast ratio)
- **Color Limits**: Maximum 5-6 colors per presentation
- **Consistency**: Uniform color application throughout

### 📐 **Visual Design Standards**
- **Negative Space**: 20-40% of slide space reserved for breathing room
- **Element Spacing**: 1-2em between elements
- **Alignment Rules**: Consistent alignment (left for body, center for titles)
- **Contrast Requirements**: Minimum contrast ratios for readability
- **Professional Imaging**: High-resolution images (150-300 DPI)

### ♿ **Accessibility Standards**
- **Font Size Minimum**: 12pt minimum, 18pt recommended for body text
- **Color Contrast**: WCAG AA compliance for all text/background combinations
- **Screen Reader Support**: Proper structure for accessibility tools
- **Keyboard Navigation**: Logical content flow and structure

### 📊 **Data Visualization Standards**
- **Chart Selection**: Appropriate chart types for different data purposes
- **Label Clarity**: Clear data labels and legends
- **Color Consistency**: Charts use presentation color palette
- **Minimal Gridlines**: Clean, uncluttered data presentation

## Workflows

### 1. Creating New Presentations

**Standard Professional Workflow:**

```python
# Quick professional presentation creation
from pptx_pro import ProfessionalPresentation

# Initialize with business palette
pres = ProfessionalPresentation("business")

# Add slides with automatic standards
pres.add_title_slide(title, subtitle)
pres.add_content_slide(title, content, source)
pres.add_two_column_slide(title, left_content, right_content)
pres.add_summary_slide(title, summary, key_takeaway)

# Save with validation report
pres.save("presentation_name")
```

**Available Color Palettes:**
- `business` - Corporate professional
- `tech` - Modern technology  
- `academic` - Educational presentations
- `finance` - Financial/corporate
- `healthcare` - Medical/health topics

### 2. Content Validation

**Automatic Standards Checking:**
- Line count validation (max 8 lines/slide)
- Character count validation (25 chars/line Chinese, 50 chars/line English)
- Font size verification (minimum 12pt)
- Color contrast analysis
- Content density recommendations

### 3. Professional Layout Templates

**Built-in Layout Options:**
- **Title Slide**: Centered title with optional subtitle
- **Content Slide**: Title + body text with optional source
- **Two-Column**: Balanced 40%/60% split layout
- **Summary Slide**: Main points + highlighted key takeaway
- **TOC Slide**: Numbered list with professional formatting

## Implementation Guidelines

### Typography Rules

```css
/* Font Hierarchy */
Title: 44pt, Bold, Primary Color
Header: 28pt, Bold, Primary Color  
Body: 18pt, Regular, Text Color
Small: 14pt, Regular, Gray Color
Minimum: 12pt, Regular, Text Color

/* Spacing Standards */
Line Height: 1.2x font size
Paragraph Spacing: 6-12pt
Section Spacing: 12-18pt
Safe Margins: 0.5 inches (12.7mm)

/* Content Density */
Max Lines: 8 per slide
Chinese Chars: 25 per line max
English Chars: 50 per line max
```

### Layout Standards

```css
/* 16:9 Layout Grid */
Width: 10 inches (25.4cm)
Height: 5.625 inches (14.3cm)
Safe Area: 9×5.125 inches (with 0.5" margins)
Content Grid: 12-column system

/* Two-Column Split */
Left Column: 40% width (4 inches)
Right Column: 60% width (6 inches)
Spacing: 0.3 inches between columns

/* Visual Hierarchy */
Primary Content: 60% visual weight
Secondary Content: 30% visual weight  
Decorative Elements: 10% visual weight
```

### Color Application

```css
/* Business Palette Example */
Primary: #1a365d (Deep Blue)
Secondary: #4a90e2 (Light Blue)  
Accent: #e74c3c (Red Accent)
Text: #34495e (Dark Gray)
Background: #ffffff (White)

/* Accessibility Contrast */
Text on Background: Minimum 4.5:1 ratio
Large Text: Minimum 3:1 ratio
Color Blind Friendly: Avoid red-green combinations
```

## Advanced Features

### Content Optimization
- **Automatic Text Splitting**: Long content automatically divided across multiple slides
- **Line Break Optimization**: Intelligent line breaking for readability
- **Character Count Validation**: Real-time character count checking
- **Density Warnings**: Alerts when content becomes too dense

### Professional Formatting
- **Consistent Typography**: Automatic font and size application
- **Color Harmony**: Pre-validated color combinations
- **Alignment Standards**: Proper text and element alignment
- **Spacing Rules**: Professional spacing between elements

### Quality Assurance
- **Standards Compliance**: Every slide validated against professional standards
- **Readability Testing**: Content density and legibility checks
- **Accessibility Verification**: WCAG compliance validation
- **Visual Consistency**: Uniform application of design elements

## Usage Examples

### Basic Professional Presentation

```python
# Create professional news summary
from pptx_pro import ProfessionalPresentation

pres = ProfessionalPresentation("business")

# Title slide
pres.add_title_slide(
    title="Q4 2025 Financial Report",
    subtitle="Comprehensive Business Analysis"
)

# Content slides
pres.add_content_slide(
    title="Revenue Growth",
    content="Company revenue increased by 15% year-over-year, driven by strong product demand and market expansion.",
    source="Source: Financial Department"
)

# Two-column comparison
pres.add_two_column_slide(
    title="Regional Performance",
    left_content="North America: +18%\nEurope: +12%\nAsia: +22%",
    right_content="Total Revenue: $2.5M\nMarket Share: 12.3%\nCustomer Satisfaction: 94%"
)

# Summary
pres.add_summary_slide(
    title="Key Takeaways",
    summary="Strong quarter with across-the-board growth in all regions. Product innovation and market expansion driving positive results.",
    key_takeaway="Q4 Performance Exceeds Expectations - Positioning for Strong 2026"
)

pres.save("Q4_2025_Financial_Report")
```

### Academic Presentation

```python
# Create academic presentation
pres = ProfessionalPresentation("academic")

pres.add_title_slide(
    title="Machine Learning Applications",
    subtitle="Research Methodology and Findings"
)

# Add research content with automatic validation
pres.add_content_slide(
    title="Research Methodology",
    content="Study employed supervised learning algorithms with dataset of 10,000 samples. Cross-validation used to ensure model reliability and prevent overfitting.",
    source="Source: Data Science Lab, 2025"
)

pres.save("ML_Research_Presentation")
```

## Validation Features

### Real-time Standards Checking
- **Typography Validation**: Font sizes and families checked
- **Layout Compliance**: Spacing and alignment verified  
- **Color Accessibility**: Contrast ratios validated
- **Content Density**: Readability standards enforced

### Professional Quality Metrics
- **Typography Score**: Font hierarchy consistency
- **Layout Score**: Grid system compliance
- **Color Score**: Palette harmony and accessibility
- **Overall Score**: Composite quality rating

### Improvement Recommendations
- **Font Optimization**: Suggested font size adjustments
- **Layout Enhancement**: Spacing and alignment tips
- **Color Refinement**: Contrast and harmony suggestions
- **Content Organization**: Structure and flow recommendations

## File Integration

This enhanced skill integrates with:
- **Standard pptx module**: Python-pptx for PowerPoint generation
- **Validation scripts**: Automated standards compliance checking
- **Template library**: Pre-defined professional layouts
- **Color management**: Centralized palette system

## Output Standards

Every generated presentation includes:
- ✅ Professional typography hierarchy
- ✅ Consistent color palette application  
- ✅ Layout grid system compliance
- ✅ Content density optimization
- ✅ Accessibility standard adherence
- ✅ Visual design consistency
- ✅ Quality assurance validation report

## Dependencies

```json
{
  "python-pptx": "^1.0.2",
  "additional_features": [
    "Content validation and optimization",
    "Professional typography standards", 
    "Layout grid system",
    "Color theory implementation",
    "Accessibility compliance checking",
    "Quality assurance metrics"
  ]
}
```

This enhanced skill ensures every PowerPoint presentation meets professional design standards while providing automated validation and optimization features for consistently high-quality output.